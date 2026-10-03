"""Whisper captions provider for BashCut (`captions.transcribe`, plugin API 2).

`provider session` keeps the model loaded and answers NDJSON requests; `provider rpc` answers one request.
WHISPER_FAKE=1 skips the model and decoder and uses a fixed transcript (tests and CI).
"""
import json
import math
import os
import re
import sys
import traceback

PROVIDER_ID = "bashcut.whisper-captions.local"
MODEL = "mlx-community/whisper-large-v3-turbo"
SAMPLE_RATE = 16000

# Caption shape: a new caption after a pause, at sentence ends once the line is fairly full, and never longer
# than the character limit or MAX_SECONDS on screen.
MAX_SECONDS = 6.0
PAUSE_SECONDS = 0.6
MIN_SECONDS = 0.7

# Lines Whisper invents over silence or music, from video outros in its training data. The credit line is never
# real speech; the outro phrases can be (vloggers say them), so they go only where speech is doubtful.
CREDITS = re.compile(r"ghiền mì gõ|subtitles by|amara\.org", re.IGNORECASE)
OUTROS = re.compile(
    r"subscribe|đăng ký kênh|hãy like|cảm ơn các bạn đã (theo dõi|xem)|thanks for watching", re.IGNORECASE)


def log(message):
    print(message, file=sys.stderr, flush=True)


def load_audio(path):
    """The first audio track as 16 kHz mono float32, decoded with PyAV (no ffmpeg on the Mac needed)."""
    import av
    import numpy as np

    try:
        container = av.open(path)
    except Exception as error:  # noqa: BLE001 - PyAV raises several error types
        raise ValueError(f"Cannot open media: {error}") from error
    with container:
        if not container.streams.audio:
            raise ValueError("This media has no audio track")
        resampler = av.AudioResampler(format="flt", layout="mono", rate=SAMPLE_RATE)
        chunks = []
        for frame in container.decode(audio=0):
            chunks.extend(out.to_ndarray().reshape(-1) for out in resampler.resample(frame))
        chunks.extend(out.to_ndarray().reshape(-1) for out in resampler.resample(None))
    if not chunks:
        raise ValueError("The audio track is empty")
    return np.concatenate(chunks).astype(np.float32)


def fake_segments():
    words = [("Xin", 0.5, 0.8), ("chào", 0.8, 1.1), ("các", 1.1, 1.3), ("bạn.", 1.3, 1.7),
             ("Hôm", 2.6, 2.8), ("nay", 2.8, 3.0), ("mình", 3.0, 3.2), ("đi", 3.2, 3.4), ("Buôn", 3.4, 3.7),
             ("Đôn", 3.7, 4.0), ("chơi", 4.0, 4.4)]
    return [
        {"start": 0.5, "end": 4.4, "text": " ".join(w for w, _, _ in words), "no_speech_prob": 0.0,
         "avg_logprob": -0.2, "words": [{"word": " " + w, "start": s, "end": e} for w, s, e in words]},
        {"start": 9.0, "end": 11.0, "text": "Hãy subscribe cho kênh Ghiền Mì Gõ", "no_speech_prob": 0.1,
         "avg_logprob": -0.3, "words": []},
    ]


class Transcriber:
    def __init__(self):
        self.loaded = False

    def segments(self, path, language, vocabulary, progress):
        if os.environ.get("WHISPER_FAKE") == "1":
            if not os.path.isfile(path):
                raise ValueError(f"Media not found: {path}")
            return fake_segments()
        try:
            import mlx_whisper
        except ImportError as error:
            raise RuntimeError(
                "Whisper is not installed yet: open Plugins and install the Whisper dependency") from error
        progress(0.05, "Reading audio")
        audio = load_audio(path)
        progress(0.15, "Loading Whisper" if not self.loaded else "Transcribing")
        options = {
            "path_or_hf_repo": MODEL, "word_timestamps": True, "condition_on_previous_text": False,
            "verbose": None,
        }
        if language:
            options["language"] = language
        if vocabulary:
            # Whisper reads the prompt as preceding text, so the names it lists are spelled the same way.
            options["initial_prompt"] = vocabulary
        result = mlx_whisper.transcribe(audio, **options)
        self.loaded = True
        return result.get("segments") or []


def spoken(segment):
    """Drops silence Whisper filled in, and its stock outro lines."""
    text = (segment.get("text") or "").strip()
    if not text or CREDITS.search(text):
        return False
    doubtful = segment.get("no_speech_prob", 0)
    if OUTROS.search(text) and doubtful > 0.3:
        return False
    return not (doubtful > 0.6 and segment.get("avg_logprob", 0) < -1.0)


def phrases(words):
    """Runs of words between pauses and sentence ends."""
    runs, current = [], []
    for word in words:
        if current:
            paused = word["start"] - current[-1]["end"] > PAUSE_SECONDS
            sentence = current[-1]["word"].strip()[-1:] in (".", "?", "!", "…")
            if paused or sentence:
                runs.append(current)
                current = []
        current.append(word)
    if current:
        runs.append(current)
    return runs


def split_evenly(words, max_characters):
    """A phrase as few captions as fit the limits, about equally long, so no word is left alone on a line."""
    text = lambda group: " ".join(w["word"].strip() for w in group)  # noqa: E731
    length = len(text(words))
    seconds = words[-1]["end"] - words[0]["start"]
    count = max(math.ceil(length / max_characters), math.ceil(seconds / MAX_SECONDS), 1)
    while True:
        target = length / count
        groups, current = [], []
        for word in words:
            line = text(current + [word])
            if current and (len(line) > max_characters or (len(groups) < count - 1 and len(line) > target * 1.15)):
                groups.append(current)
                current = []
            current.append(word)
        groups.append(current)
        if len(groups) <= count or count >= len(words):
            return groups
        count += 1


def cues_from(segments, max_characters):
    """Readable captions: words grouped by pauses and sentence ends, then split evenly within the character limit and
    MAX_SECONDS."""
    cues = []
    for segment in filter(spoken, segments):
        words = [w for w in segment.get("words") or [] if (w.get("word") or "").strip()]
        if not words:
            words = [{"word": segment["text"], "start": segment["start"], "end": segment["end"]}]
        for phrase in phrases(words):
            cues.extend(split_evenly(phrase, max_characters))
    result = []
    for words in cues:
        start = float(words[0]["start"])
        end = max(float(words[-1]["end"]), start + MIN_SECONDS)
        if result and start < result[-1][1]:
            start = result[-1][1]
            end = max(end, start + 0.2)
        text = " ".join(w["word"].strip() for w in words)
        if result and result[-1][2] == text:  # a loop Whisper sometimes repeats
            continue
        result.append((start, end, text))
    return result


def timestamp(seconds):
    milliseconds = int(round(seconds * 1000))
    hours, rest = divmod(milliseconds, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    secs, millis = divmod(rest, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def srt(cues):
    blocks = [f"{index}\n{timestamp(start)} --> {timestamp(end)}\n{text}\n"
              for index, (start, end, text) in enumerate(cues, start=1)]
    return "\n".join(blocks)


def transcribe(params, progress, transcriber):
    path = params.get("mediaPath") or ""
    output = params.get("outputDirectory") or ""
    if not path or not output:
        raise ValueError("mediaPath and outputDirectory are required")
    language = (params.get("language") or "").split("-")[0].lower()
    if language in ("", "auto", "und"):
        language = None
    options = params.get("options") or {}
    vocabulary = (options.get("vocabulary") or "").strip()
    max_characters = int(options.get("maxCharacters") or 42)
    segments = transcriber.segments(path, language, vocabulary, progress)
    cues = cues_from(segments, max_characters)
    if not cues:
        raise ValueError("No speech found in this media")
    progress(0.95, f"{len(cues)} captions")
    name = os.path.splitext(os.path.basename(path))[0] + ".srt"
    with open(os.path.join(output, name), "w", encoding="utf-8") as file:
        file.write(srt(cues))
    progress(1, "Done")
    return {"srtPath": name}


def handle(request, progress, transcriber):
    method = request.get("method")
    try:
        if method != "captions.transcribe":
            return {"id": request["id"], "error": {"code": "unknown_method", "message": str(method)}}
        return {"id": request["id"], "result": transcribe(request.get("params") or {}, progress, transcriber)}
    except Exception as error:  # noqa: BLE001 - every failure goes back to BashCut
        log(traceback.format_exc())
        return {"id": request["id"], "error": {"code": "failed", "message": str(error)}}


def send(message):
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    transcriber = Transcriber()
    mode = sys.argv[1] if len(sys.argv) > 1 else "rpc"
    if mode == "rpc":
        send(handle(json.loads(sys.stdin.readline()), lambda *_: None, transcriber))
        return
    for line in sys.stdin:
        if not line.strip():
            continue
        message = json.loads(line)
        kind = message.get("type")
        if kind == "hello":
            send({"type": "hello", "apiVersion": 2})
        elif kind == "shutdown":
            return
        elif kind == "cancel":
            continue
        else:
            def progress(fraction, text, request_id=message.get("id")):
                send({"type": "progress", "id": request_id, "progress": fraction, "message": text})
            send(handle(message, progress, transcriber))


if __name__ == "__main__":
    main()
