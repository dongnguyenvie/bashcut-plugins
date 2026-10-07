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

    def remove(self, minimum_ms=400, padding_ms=100, item=None):
        params = self.params(minimum_ms=minimum_ms, item=item)
        params["action"] = "bashcut.silence-markers.remove"
        params["params"]["paddingMs"] = padding_ms
        return call(params)

    def test_remove_cuts_the_silence_with_padding(self):
        result = self.remove()["result"]
        ops = result["operations"]
        # Silence 1.0–1.8 s; 0.1 s padding keeps 1.0–1.1 and 1.7–1.8: cut frames 133–151 of a clip at 100.
        self.assertEqual([op["op"] for op in ops], ["split", "split", "delete"])
        self.assertAlmostEqual(ops[0]["atFrame"], 151, delta=1)
        self.assertAlmostEqual(ops[1]["atFrame"], 133, delta=1)
        self.assertEqual(ops[2], {"op": "delete", "item": ops[1]["newID"], "ripple": True})
        self.assertTrue(all(op["item"] == "c1" for op in ops[:2]))
        self.assertEqual(result["ui"]["select"], "c1")
        self.assertIn("Removed 1 silences", result["message"])

    def test_remove_runs_right_to_left(self):
        # 50 ms padding leaves 0.1 s of the 0.2 s silence to cut (100 ms would leave nothing).
        ops = self.remove(minimum_ms=150, padding_ms=50)["result"]["operations"]
        splits = [op["atFrame"] for op in ops if op["op"] == "split"]
        self.assertEqual(splits, sorted(splits, reverse=True))
        self.assertEqual(sum(op["op"] == "delete" for op in ops), 2)

    def test_remove_at_the_clip_edges_needs_no_padding(self):
        # The clip starts inside the first silence (source 1.2 s) and ends inside the second (source 2.9 s).
        item = {"id": "c3", "at": 0, "dur": 51, "in": 36}
        ops = self.remove(minimum_ms=50, item=item)["result"]["operations"]
        self.assertEqual(ops[0]["op"], "split")
        self.assertEqual(ops[-1], {"op": "delete", "item": "c3", "ripple": True})

    def test_remove_lists_spans_longest_first(self):
        data = self.remove(minimum_ms=150, padding_ms=50)["result"]["data"]
        seconds = [span["seconds"] for span in data["removed"]]
        self.assertEqual(seconds, sorted(seconds, reverse=True))
        self.assertAlmostEqual(data["removed"][0]["sourceStart"], 1.05, delta=0.04)
        self.assertEqual(data["detection"]["method"], "level")

    def test_one_shot_has_no_speech_map(self):
        params = self.params()
        params["params"]["detect"] = "auto"
        detection = call(params)["result"]["data"]["detection"]
        self.assertEqual(detection["method"], "level")
        self.assertFalse(detection["speechMap"]["used"])

    def test_errors_are_reported(self):
        params = self.params()
        params["context"]["media"] = None
        self.assertEqual(call(params)["error"]["code"], "failed")


class SessionTests(unittest.TestCase):
    """The session transport with a fake BashCut that answers media.speech-map host calls."""

    def setUp(self):
        self.folder = pathlib.Path(tempfile.mkdtemp())
        self.media = make_audio(self.folder)

    def run_session(self, action, values, speech_map, api_version=8):
        process = subprocess.Popen([str(PROVIDER), "session"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        calls = []

        def send(message):
            process.stdin.write(json.dumps(message) + "\n")
            process.stdin.flush()

        send({"type": "hello", "apiVersion": api_version, "host": "BashCut", "pluginId": "bashcut.silence-markers"})
        self.assertEqual(json.loads(process.stdout.readline())["type"], "hello")
        send({"type": "request", "id": "r1", "apiVersion": api_version, "method": "plugin.action", "params": {
            "action": action, "params": values, "options": {},
            "context": {
                "project": {"rev": 4, "fps": [30, 1]},
                "selection": {"id": "c1", "at": 100, "dur": 120, "in": 0},
                "media": {"id": "m1", "fps": [30, 1], "absolutePath": str(self.media)},
            }}})
        while True:
            message = json.loads(process.stdout.readline())
            if message.get("type") == "call":
                calls.append(message)
                reply = {"type": "callResult", "callId": message["callId"]}
                reply.update({"error": {"code": -32602, "message": speech_map}} if isinstance(speech_map, str)
                             else {"result": speech_map})
                send(reply)
                continue
            send({"type": "shutdown"})
            process.wait(timeout=10)
            process.stdin.close()
            process.stdout.close()
            return message, calls

    def test_auto_uses_the_speech_map_gaps(self):
        speech_map = {"calibration": {"separation": "clear"}, "gaps": [
            {"start": 0.0, "end": 0.1}, {"start": 1.5, "end": 3.0}, {"start": 3.3, "end": 3.6}]}
        response, calls = self.run_session(
            "bashcut.silence-markers.remove", {"detect": "auto", "minSilenceMs": 200, "paddingMs": 0}, speech_map)
        self.assertEqual(calls[0]["method"], "media.speech-map")
        self.assertEqual(calls[0]["params"], {"media": "m1"})
        data = response["result"]["data"]
        self.assertEqual(data["detection"]["method"], "speechMap")
        # 0.1 s at the start is below the minimum; 1.5–3.0 s comes before 3.3–3.6 s, longest first.
        self.assertEqual([(span["start"], span["end"]) for span in data["removed"]], [(145, 190), (199, 208)])
        self.assertEqual(data["removed"][0]["sourceStart"], 1.5)

    def test_auto_falls_back_to_level_when_speech_does_not_separate(self):
        speech_map = {"calibration": {"separation": "none"}, "gaps": None, "reason": "classes 0.8 dB apart"}
        response, _ = self.run_session("bashcut.silence-markers.mark", {"detect": "auto"}, speech_map)
        detection = response["result"]["data"]["detection"]
        self.assertEqual(detection["method"], "level")
        self.assertEqual(detection["speechMap"]["reason"], "classes 0.8 dB apart")
        self.assertEqual(len(response["result"]["data"]["silences"]), 1)

    def test_speech_map_only_reports_why_it_cannot(self):
        response, _ = self.run_session(
            "bashcut.silence-markers.mark", {"detect": "speechMap"}, "Media m1 has no measured sound")
        self.assertIn("Media m1 has no measured sound", response["error"]["message"])

    def test_older_hosts_get_no_host_calls(self):
        response, calls = self.run_session("bashcut.silence-markers.mark", {}, {"gaps": []}, api_version=7)
        self.assertEqual(calls, [])
        self.assertEqual(response["result"]["data"]["detection"]["method"], "level")


if __name__ == "__main__":
    unittest.main()
