"""VieNeu TTS provider for BashCut (`voice.synthesize`, plugin API 2).

`provider session` keeps the model loaded and answers NDJSON requests; `provider rpc` answers one request.
VIENEU_FAKE=1 writes short tones instead of running the model (tests and CI).
"""
import json
import math
import os
import struct
import sys
import traceback
import wave

PROVIDER_ID = "bashcut.vieneu-tts.local"
DEFAULT_VOICE = "Hải Đăng"
_engine = None


def log(message):
    print(message, file=sys.stderr, flush=True)


def engine():
    """Loads the model once per process; the session transport keeps it warm between requests."""
    global _engine
    if _engine is None:
        try:
            from vieneu import Vieneu
        except ImportError as error:
            raise RuntimeError("VieNeu is not installed yet: open Plugins and install the VieNeu dependency") from error
        log("loading VieNeu model…")
        _engine = Vieneu()
    return _engine


def fake_take(path, index, text):
    """A tone whose length follows the text, so pace scoring behaves like real speech."""
    rate, seconds = 24000, max(0.5, len(text.split()) / 2.5)
    frequency = 220 + 40 * index
    samples = [int(6000 * math.sin(2 * math.pi * frequency * i / rate)) for i in range(int(rate * seconds))]
    with wave.open(path, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(rate)
        audio.writeframes(struct.pack(f"<{len(samples)}h", *samples))


def synthesize(params, progress):
    text = (params.get("text") or "").strip()
    if not text:
        raise ValueError("text is required")
    language = params.get("language") or "vi"
    if not language.startswith("vi") and not language.startswith("en"):
        raise ValueError(f"VieNeu speaks Vietnamese and English, not {language}")
    output = params["outputDirectory"]
    count = int(params.get("takeCount", 1))
    offset = int(params.get("takeOffset", 0))
    options = params.get("options") or {}
    voice = options.get("voice") or DEFAULT_VOICE
    reference = (options.get("referenceAudio") or "").strip()
    if reference and not os.path.isfile(reference):
        raise ValueError(f"Reference audio not found: {reference}")
    # BashCut sends cloneConsent (P0-C7); older hosts do not, and keep working as before.
    if reference and params.get("cloneConsent") is False:
        raise ValueError("Cloning a voice needs the person's consent: ask them, then pass clone consent")
    fake = os.environ.get("VIENEU_FAKE") == "1"
    takes = []
    for index in range(count):
        number = offset + index + 1
        path = os.path.join(output, f"take-{number}.wav")
        progress(index / count, f"Take {number}")
        if fake:
            fake_take(path, number, text)
        else:
            model = engine()
            arguments = {"ref_audio": reference} if reference else {"voice": voice}
            arguments["temperature"] = float(options.get("variation", 0.8))
            audio = model.infer(text, **arguments)
            model.save(audio, path)
        takes.append({"audioPath": os.path.basename(path)})
    progress(1, "Done")
    return {"takes": takes}


def handle(request, progress):
    method = request.get("method")
    try:
        if method != "voice.synthesize":
            return {"id": request["id"], "error": {"code": "unknown_method", "message": str(method)}}
        return {"id": request["id"], "result": synthesize(request.get("params") or {}, progress)}
    except Exception as error:  # noqa: BLE001 - every failure goes back to BashCut
        log(traceback.format_exc())
        return {"id": request["id"], "error": {"code": "failed", "message": str(error)}}


def send(message):
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "rpc"
    if mode == "rpc":
        send(handle(json.loads(sys.stdin.readline()), lambda *_: None))
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
            send(handle(message, progress))


if __name__ == "__main__":
    main()
