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
        self.assertEqual({k: result[k] for k in ("srtPath", "wordsPath", "segmentsPath")},
                         {"srtPath": "clip 1.srt", "wordsPath": "clip 1.words.json",
                          "segmentsPath": "clip 1.segments.json"})
        self.assertEqual(result["reliable"], {"noSpeechProb": True, "avgLogprob": True, "compressionRatio": True})
        # The credit line and the invented "Thank you." are left out.
        self.assertEqual(result["droppedSegments"], 2)
        text = pathlib.Path(self.output, "clip 1.srt").read_text(encoding="utf-8")
        words = json.loads(pathlib.Path(self.output, "clip 1.words.json").read_text(encoding="utf-8"))
        self.assertEqual([w["text"] for w in words[:4]], ["Xin", "chào", "các", "bạn."])
        self.assertTrue(all(w["start"] <= w["end"] for w in words))
        self.assertEqual((words[0]["confidence"], words[0]["noSpeechProb"], words[0]["avgLogprob"],
                          words[0]["compressionRatio"]), (0.9, 0.0, -0.2, 1.2))
        self.assertNotIn("Thank you.", text)
        report = json.loads(pathlib.Path(self.output, "clip 1.segments.json").read_text(encoding="utf-8"))
        self.assertEqual([row.get("dropped") for row in report["segments"]], [None, "credits", "avgLogprob"])
        self.assertEqual(report["filter"]["minAvgLogprob"], -1.0)
        # Word for word with the caption text, so BashCut can use the timings as they are.
        captions = [block.split("\n", 2)[2] for block in text.strip().split("\n\n")]
        self.assertEqual(len(words), sum(len(line.split()) for line in captions))
        self.assertIn("00:00:00,500 --> 00:00:01,700\nXin chào các bạn.\n", text)
        self.assertIn("Hôm nay mình đi Buôn Đôn chơi", text)
        self.assertNotIn("Ghiền Mì Gõ", text)
        kinds = [m.get("type", "reply") for m in messages[1:]]
        self.assertEqual(kinds[-1], "reply")
        self.assertIn("progress", kinds)

    def test_the_language_heard_is_returned_when_none_was_asked(self):
        asked = next(m for m in session(self.request()) if m.get("id") == "r0" and "result" in m)["result"]
        self.assertNotIn("language", asked)
        heard = next(m for m in session(self.request(language="")) if m.get("id") == "r0" and "result" in m)["result"]
        self.assertEqual(heard["language"], "vi")

    def test_the_doubt_filter_can_be_turned_off(self):
        session(self.request(options={"dropDoubtful": False}))
        text = pathlib.Path(self.output, "clip 1.srt").read_text(encoding="utf-8")
        self.assertIn("Thank you.", text)
        session(self.request(options={"minAvgLogprob": -3.0}))
        self.assertIn("Thank you.", pathlib.Path(self.output, "clip 1.srt").read_text(encoding="utf-8"))

    def test_a_range_transcribes_only_that_stretch_in_media_time(self):
        messages = session(self.request(startSeconds=2.5, endSeconds=5))
        self.assertTrue(any("result" in m for m in messages if m.get("id") == "r0"))
        text = pathlib.Path(self.output, "clip 1.srt").read_text(encoding="utf-8")
        self.assertNotIn("Xin chào", text)
        self.assertIn("00:00:02,600 --> ", text)
        self.assertIn("Hôm nay mình đi Buôn Đôn chơi", text)
        bad = session(self.request(startSeconds=5, endSeconds=2))
        self.assertIn("error", next(m for m in bad if m.get("id") == "r0"))

    def test_stretch_times_are_moved_back_to_media_time(self):
        segments = [{"start": 0.0, "end": 1.0, "text": "a", "words": [word("a", 0.2, 0.6)]}]
        moved = whisper_provider.shifted(segments, 128.0)
        self.assertEqual((moved[0]["start"], moved[0]["end"]), (128.0, 129.0))
        self.assertEqual((moved[0]["words"][0]["start"], moved[0]["words"][0]["end"]), (128.2, 128.6))
        self.assertEqual(segments[0]["start"], 0.0)

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
    def test_a_segment_without_word_times_shares_its_time_by_length(self):
        cues = whisper_provider.cues_from([{"text": "ab cdef", "start": 1, "end": 4, "words": []}], 42)
        words = whisper_provider.word_timings(cues)
        self.assertEqual([w["text"] for w in words], ["ab", "cdef"])
        # Shared time is not Whisper's word timing: no confidence.
        self.assertNotIn("confidence", words[0])
        self.assertEqual(words[0]["start"], 1)
        self.assertEqual(words[0]["end"], words[1]["start"])
        # cdef is twice as long as ab, so it gets twice the time.
        self.assertAlmostEqual(words[1]["end"] - words[1]["start"], 2 * (words[0]["end"] - words[0]["start"]), 2)

    def test_long_speech_splits_at_the_character_limit(self):
        words = [word(f"từ{i}", i * 0.3, i * 0.3 + 0.25) for i in range(20)]
        cues = whisper_provider.cues_from([{"text": "x", "start": 0, "end": 6, "words": words}], 20)
        self.assertTrue(all(len(text) <= 20 for _, _, text, _ in cues))
        self.assertEqual(" ".join(text for _, _, text, _ in cues), " ".join(f"từ{i}" for i in range(20)))

    def test_a_long_sentence_splits_into_even_lines(self):
        text = "Ở Buôn Đôn luôn, ủa em tưởng là Buôn Ma Thuột chứ"
        words = [word(w, i * 0.25, i * 0.25 + 0.2) for i, w in enumerate(text.split())]
        cues = whisper_provider.cues_from([{"text": text, "start": 0, "end": 3, "words": words}], 42)
        lines = [line for _, _, line, _ in cues]
        self.assertEqual(" ".join(lines), text)
        self.assertEqual(len(lines), 2)
        self.assertLess(abs(len(lines[0]) - len(lines[1])), 12)

    def test_pauses_and_sentence_ends_start_new_captions(self):
        words = [word("Một", 0, 0.3), word("hai.", 0.3, 0.6), word("Ba", 0.7, 1.0), word("bốn", 3.0, 3.3)]
        cues = whisper_provider.cues_from([{"text": "x", "start": 0, "end": 3.3, "words": words}], 8)
        self.assertEqual([text for _, _, text, _ in cues], ["Một hai.", "Ba", "bốn"])

    def test_short_captions_stay_readable_without_overlapping(self):
        words = [word("A.", 1.0, 1.1), word("B", 1.15, 1.2)]
        cues = whisper_provider.cues_from([{"text": "x", "start": 1, "end": 1.2, "words": words}], 2)
        self.assertEqual(cues[0][1] - cues[0][0], whisper_provider.MIN_SECONDS)
        self.assertGreaterEqual(cues[1][0], cues[0][1])

    def test_doubtful_outros_are_dropped_but_spoken_ones_kept(self):
        spoken = {"text": "Nhớ đăng ký kênh nha", "start": 0, "end": 2, "no_speech_prob": 0.05, "words": []}
        doubtful = {"text": "Hãy đăng ký kênh", "start": 5, "end": 7, "no_speech_prob": 0.5, "words": []}
        cues = whisper_provider.cues_from([spoken, doubtful], 42)
        self.assertEqual([text for _, _, text, _ in cues], ["Nhớ đăng ký kênh nha"])

    def test_a_constant_no_speech_prob_is_not_passed_on_as_a_measurement(self):
        # mlx-whisper large-v3 turbo: no_speech_prob 0.0 in every segment, real avg_logprob.
        segments = [
            {"text": "Xin chào", "start": 0, "end": 1, "no_speech_prob": 0.0, "avg_logprob": -0.25,
             "compression_ratio": 1.0, "words": [word("Xin", 0, 0.4), word("chào", 0.4, 1)]},
            {"text": "We're back.", "start": 3, "end": 4, "no_speech_prob": 0.0, "avg_logprob": -3.1,
             "compression_ratio": 0.9, "words": [word("We're", 3, 3.5), word("back.", 3.5, 4)]},
        ]
        reliable = whisper_provider.reliability(segments)
        self.assertEqual(reliable, {"noSpeechProb": False, "avgLogprob": True, "compressionRatio": True})
        words = whisper_provider.word_timings(whisper_provider.cues_from(segments, 42))
        self.assertEqual([w["text"] for w in words], ["Xin", "chào"])
        self.assertNotIn("noSpeechProb", words[0])
        self.assertEqual(words[0]["avgLogprob"], -0.25)

    def test_missing_or_nan_scores_are_unreliable(self):
        segments = [{"text": "a", "start": 0, "end": 1, "no_speech_prob": float("nan"), "avg_logprob": -0.2},
                    {"text": "b", "start": 1, "end": 2, "no_speech_prob": 0.4, "avg_logprob": -0.3}]
        self.assertEqual(whisper_provider.reliability(segments),
                         {"noSpeechProb": False, "avgLogprob": True, "compressionRatio": False})
        self.assertEqual(whisper_provider.reliability([]),
                         {"noSpeechProb": False, "avgLogprob": False, "compressionRatio": False})

    def test_repeated_text_is_dropped_by_compression_ratio(self):
        loop = {"text": "đi đi đi đi đi đi đi đi", "start": 0, "end": 2, "avg_logprob": -0.4,
                "compression_ratio": 3.4, "words": []}
        real = {"text": "Hôm nay mình đi chợ", "start": 3, "end": 5, "avg_logprob": -0.3,
                "compression_ratio": 1.2, "words": []}
        cues = whisper_provider.cues_from([loop, real], 42)
        self.assertEqual([text for _, _, text, _ in cues], ["Hôm nay mình đi chợ"])
        kept = whisper_provider.cues_from([loop, real], 42, whisper_provider.doubt_options({"dropDoubtful": False}))
        self.assertEqual(len(kept), 2)

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
