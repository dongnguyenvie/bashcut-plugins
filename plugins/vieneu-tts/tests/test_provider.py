"""Runs the provider like BashCut does, in VIENEU_FAKE mode (no model): handshake, takes, progress, errors."""
import json
import os
import pathlib
import subprocess
import tempfile
import unittest
import wave

PROVIDER = pathlib.Path(__file__).resolve().parent.parent / "bin" / "provider"
ENV = {**os.environ, "VIENEU_FAKE": "1", "BASHCUT_PLUGIN_DATA": tempfile.mkdtemp(), "BASHCUT_PLUGIN_CACHE": tempfile.mkdtemp()}


def session(*requests):
    lines = [json.dumps({"type": "hello", "apiVersion": 2})]
    lines += [json.dumps({"type": "request", "id": f"r{i}", "apiVersion": 2, **r}) for i, r in enumerate(requests)]
    output = subprocess.run([str(PROVIDER), "session"], input="\n".join(lines) + "\n", capture_output=True,
                            text=True, env=ENV, timeout=60, check=True)
    return [json.loads(line) for line in output.stdout.splitlines()]


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.output = tempfile.mkdtemp()

    def synth(self, **params):
        base = {"text": "Xin chào các bạn", "language": "vi", "outputDirectory": self.output,
                "takeCount": 2, "takeOffset": 0, "options": {"voice": "Hải Đăng"}}
        return {"method": "voice.synthesize", "provider": "bashcut.vieneu-tts.local", "params": {**base, **params}}

    def test_takes_are_audio_files_in_the_request_folder(self):
        messages = session(self.synth(takeOffset=3))
        self.assertEqual(messages[0], {"type": "hello", "apiVersion": 2})
        result = next(m for m in messages if m.get("id") == "r0" and "result" in m)["result"]
        self.assertEqual([t["audioPath"] for t in result["takes"]], ["take-4.wav", "take-5.wav"])
        for take in result["takes"]:
            with wave.open(os.path.join(self.output, take["audioPath"])) as audio:
                self.assertGreater(audio.getnframes(), 0)

    def test_progress_comes_before_the_reply(self):
        messages = session(self.synth())
        kinds = [m.get("type", "reply") for m in messages[1:]]
        self.assertEqual(kinds[-1], "reply")
        self.assertIn("progress", kinds[:-1])

    def test_errors_are_reported(self):
        messages = session(self.synth(text="  "), self.synth(language="fr"), {"method": "audio.beats", "params": {}})
        codes = [m["error"]["code"] for m in messages if "error" in m]
        self.assertEqual(codes, ["failed", "failed", "unknown_method"])

    def test_missing_reference_audio_is_reported(self):
        messages = session(self.synth(options={"referenceAudio": "/nonexistent/voice.wav"}))
        error = next(m["error"] for m in messages if "error" in m)
        self.assertIn("Reference audio not found", error["message"])

    def test_one_shot_rpc(self):
        request = {"id": "x", "apiVersion": 2, **self.synth(takeCount=1)}
        output = subprocess.run([str(PROVIDER), "rpc"], input=json.dumps(request) + "\n", capture_output=True,
                                text=True, env=ENV, timeout=60, check=True)
        self.assertEqual(json.loads(output.stdout)["result"]["takes"][0]["audioPath"], "take-1.wav")


if __name__ == "__main__":
    unittest.main()
