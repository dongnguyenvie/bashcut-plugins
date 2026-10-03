"""Runs the provider like BashCut does, in WHISPER_FAKE mode (no model), and tests caption shaping directly."""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

BIN = pathlib.Path(__file__).resolve().parent.parent / "bin"
PROVIDER = BIN / "provider"
ENV = {**os.environ, "WHISPER_FAKE": "1", "BASHCUT_PLUGIN_DATA": tempfile.mkdtemp(),
       "BASHCUT_PLUGIN_CACHE": tempfile.mkdtemp()}
sys.path.insert(0, str(BIN))
import whisper_provider  # noqa: E402


def session(*requests):
    lines = [json.dumps({"type": "hello", "apiVersion": 2})]
    lines += [json.dumps({"type": "request", "id": f"r{i}", "apiVersion": 2, **r}) for i, r in enumerate(requests)]
    output = subprocess.run([str(PROVIDER), "session"], input="\n".join(lines) + "\n", capture_output=True,
                            text=True, env=ENV, timeout=60, check=True)
    return [json.loads(line) for line in output.stdout.splitlines()]


def word(text, start, end):
    return {"word": " " + text, "start": start, "end": end}


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.output = tempfile.mkdtemp()
        self.media = os.path.join(tempfile.mkdtemp(), "clip 1.mp4")
        pathlib.Path(self.media).write_bytes(b"not decoded in fake mode")

    def request(self, **params):
        base = {"mediaPath": self.media, "language": "vi", "outputDirectory": self.output}
        return {"method": "captions.transcribe", "provider": "bashcut.whisper-captions.local",
                "params": {**base, **params}}

    def test_writes_an_srt_in_the_request_folder(self):
        messages = session(self.request(options={"maxCharacters": 42}))
        self.assertEqual(messages[0], {"type": "hello", "apiVersion": 2})
        result = next(m for m in messages if m.get("id") == "r0" and "result" in m)["result"]
        self.assertEqual(result, {"srtPath": "clip 1.srt"})
        text = pathlib.Path(self.output, "clip 1.srt").read_text(encoding="utf-8")
        self.assertIn("00:00:00,500 --> 00:00:01,700\nXin chào các bạn.\n", text)
        self.assertIn("Hôm nay mình đi Buôn Đôn chơi", text)
        self.assertNotIn("Ghiền Mì Gõ", text)
        kinds = [m.get("type", "reply") for m in messages[1:]]
        self.assertEqual(kinds[-1], "reply")
        self.assertIn("progress", kinds)

    def test_errors_are_reported(self):
        missing = self.request(mediaPath="/nonexistent/clip.mp4")
        messages = session(missing, self.request(outputDirectory=""), {"method": "voice.synthesize", "params": {}})
        codes = [m["error"]["code"] for m in messages if "error" in m]
        self.assertEqual(codes, ["failed", "failed", "unknown_method"])
        self.assertIn("Media not found", next(m for m in messages if "error" in m)["error"]["message"])

    def test_one_shot_rpc(self):
        request = {"id": "x", "apiVersion": 2, **self.request()}
        output = subprocess.run([str(PROVIDER), "rpc"], input=json.dumps(request) + "\n", capture_output=True,
                                text=True, env=ENV, timeout=60, check=True)
        self.assertEqual(json.loads(output.stdout)["result"]["srtPath"], "clip 1.srt")


class CaptionShapeTests(unittest.TestCase):
    def test_long_speech_splits_at_the_character_limit(self):
        words = [word(f"từ{i}", i * 0.3, i * 0.3 + 0.25) for i in range(20)]
        cues = whisper_provider.cues_from([{"text": "x", "start": 0, "end": 6, "words": words}], 20)
        self.assertTrue(all(len(text) <= 20 for _, _, text in cues))
        self.assertEqual(" ".join(text for _, _, text in cues), " ".join(f"từ{i}" for i in range(20)))

    def test_a_long_sentence_splits_into_even_lines(self):
        text = "Ở Buôn Đôn luôn, ủa em tưởng là Buôn Ma Thuột chứ"
        words = [word(w, i * 0.25, i * 0.25 + 0.2) for i, w in enumerate(text.split())]
        cues = whisper_provider.cues_from([{"text": text, "start": 0, "end": 3, "words": words}], 42)
        lines = [line for _, _, line in cues]
        self.assertEqual(" ".join(lines), text)
        self.assertEqual(len(lines), 2)
        self.assertLess(abs(len(lines[0]) - len(lines[1])), 12)

    def test_pauses_and_sentence_ends_start_new_captions(self):
        words = [word("Một", 0, 0.3), word("hai.", 0.3, 0.6), word("Ba", 0.7, 1.0), word("bốn", 3.0, 3.3)]
        cues = whisper_provider.cues_from([{"text": "x", "start": 0, "end": 3.3, "words": words}], 8)
        self.assertEqual([text for _, _, text in cues], ["Một hai.", "Ba", "bốn"])

    def test_short_captions_stay_readable_without_overlapping(self):
        words = [word("A.", 1.0, 1.1), word("B", 1.15, 1.2)]
        cues = whisper_provider.cues_from([{"text": "x", "start": 1, "end": 1.2, "words": words}], 2)
        self.assertEqual(cues[0][1] - cues[0][0], whisper_provider.MIN_SECONDS)
        self.assertGreaterEqual(cues[1][0], cues[0][1])

    def test_doubtful_outros_are_dropped_but_spoken_ones_kept(self):
        spoken = {"text": "Nhớ đăng ký kênh nha", "start": 0, "end": 2, "no_speech_prob": 0.05, "words": []}
        doubtful = {"text": "Hãy đăng ký kênh", "start": 5, "end": 7, "no_speech_prob": 0.5, "words": []}
        cues = whisper_provider.cues_from([spoken, doubtful], 42)
        self.assertEqual([text for _, _, text in cues], ["Nhớ đăng ký kênh nha"])

    def test_timestamps(self):
        self.assertEqual(whisper_provider.timestamp(3725.5), "01:02:05,500")

class HeartbeatTests(unittest.TestCase):
    def test_reports_progress_while_whisper_runs(self):
        seen = []
        original = whisper_provider.HEARTBEAT_SECONDS
        whisper_provider.HEARTBEAT_SECONDS = 0.05
        try:
            with whisper_provider.heartbeat(lambda fraction, text: seen.append((fraction, text)), 600):
                import time
                time.sleep(0.3)
        finally:
            whisper_provider.HEARTBEAT_SECONDS = original
        count = len(seen)
        self.assertGreaterEqual(count, 2)
        self.assertTrue(all(0.15 <= f <= 0.9 and t.startswith("Transcribing") for f, t in seen))
        import time
        time.sleep(0.15)
        self.assertEqual(len(seen), count)  # stops when Whisper returns


if __name__ == "__main__":
    unittest.main()
