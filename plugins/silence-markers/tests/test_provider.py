"""Runs the provider like BashCut does on generated audio: tone, 0.8 s silence, tone, 0.2 s silence, tone."""
import json
import math
import pathlib
import struct
import subprocess
import tempfile
import unittest
import wave

PROVIDER = pathlib.Path(__file__).resolve().parent.parent / "bin" / "provider"


def make_audio(folder):
    rate, samples = 48000, []
    for seconds, on in [(1.0, 1), (0.8, 0), (1.0, 1), (0.2, 0), (1.0, 1)]:
        samples += [int(8000 * math.sin(2 * math.pi * 440 * i / rate)) if on else 0 for i in range(int(rate * seconds))]
    wav = folder / "gap.wav"
    with wave.open(str(wav), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(rate)
        audio.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    m4a = folder / "gap.m4a"
    subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", str(wav), str(m4a)], check=True)
    return m4a


def call(params):
    request = {"id": "r1", "apiVersion": 2, "method": "plugin.action", "params": params}
    output = subprocess.run([str(PROVIDER), "rpc"], input=json.dumps(request) + "\n", capture_output=True, text=True,
                            check=True, timeout=60)
    return json.loads(output.stdout)


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.folder = pathlib.Path(tempfile.mkdtemp())
        self.media = make_audio(self.folder)

    def params(self, minimum_ms=400, item=None):
        return {
            "action": "bashcut.silence-markers.mark",
            "params": {"thresholdDb": -40, "minSilenceMs": minimum_ms},
            "options": {"labelPrefix": "Pause"},
            "context": {
                "project": {"rev": 4, "fps": [30, 1]},
                "selection": item or {"id": "c1", "at": 100, "dur": 120, "in": 0},
                "media": {"fps": [30, 1], "absolutePath": str(self.media)},
            },
        }

    def test_marks_long_silences_in_timeline_frames(self):
        result = call(self.params())["result"]
        self.assertEqual(result["baseRev"], 4)
        self.assertEqual([op["op"] for op in result["operations"]], ["upsertSection"])
        self.assertEqual(result["operations"][0]["label"], "Pause 0.8s")
        self.assertAlmostEqual(result["operations"][0]["atFrame"], 130, delta=1)
        self.assertEqual(result["pluginData"]["lastRun"]["count"], 1)

    def test_shorter_minimum_finds_both(self):
        result = call(self.params(minimum_ms=150))["result"]
        self.assertEqual(len(result["data"]["silences"]), 2)

    def test_trim_and_speed_map_to_the_clip(self):
        # Clip starts 2 s into the source at 2x speed: only the second gap (2.8 s) is inside, at (2.8-2)/2 s.
        item = {"id": "c2", "at": 0, "dur": 60, "in": 60, "speed": 2}
        silences = call(self.params(minimum_ms=150, item=item))["result"]["data"]["silences"]
        self.assertEqual(len(silences), 1)
        self.assertAlmostEqual(silences[0]["start"], round((2.8 - 2.0) / 2 * 30), delta=1)

    def test_errors_are_reported(self):
        params = self.params()
        params["context"]["media"] = None
        self.assertEqual(call(params)["error"]["code"], "failed")


if __name__ == "__main__":
    unittest.main()
