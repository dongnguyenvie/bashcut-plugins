

class CapabilityTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.output = pathlib.Path(self.folder, "request")
        self.output.mkdir(mode=0o700)

    def run_capability(self, params):
        response = call(self.folder, "{{CAPABILITY}}", {**params, "options": {}}, provider="{{PROVIDER_ID}}")
        self.assertNotIn("error", response, response)
        return response["result"]
# @@ voice.synthesize

    def test_takes_are_audio_files_in_the_output_folder(self):
        result = self.run_capability({"text": "Hello from BashCut", "language": "en", "takeCount": 2, "takeOffset": 0,
                                      "outputDirectory": str(self.output)})
        self.assertEqual(len(result["takes"]), 2)
        for take in result["takes"]:
            path = pathlib.Path(self.output, take["audioPath"])
            self.assertTrue(path.resolve().is_relative_to(self.output.resolve()))
            self.assertGreater(path.stat().st_size, 0)
# @@ captions.transcribe

    def test_writes_subrip_in_the_output_folder(self):
        result = self.run_capability({"mediaPath": "/tmp/missing.m4a", "language": "en", "startSeconds": 3,
                                      "endSeconds": 9, "outputDirectory": str(self.output)})
        srt = pathlib.Path(self.output, result["srtPath"])
        self.assertTrue(srt.resolve().is_relative_to(self.output.resolve()))
        self.assertIn("00:00:03,000 --> 00:00:05,000", srt.read_text(encoding="utf-8"))
# @@ audio.beats

    def test_beats_increase(self):
        result = self.run_capability({"mediaPath": "/tmp/missing.m4a"})
        self.assertTrue(20 <= result["bpm"] <= 400)
        beats = result["beatsSeconds"]
        self.assertTrue(beats and all(a < b for a, b in zip(beats, beats[1:])))
# @@ audio.loudness

    def test_loudness_is_in_range(self):
        result = self.run_capability({"mediaPath": "/tmp/missing.m4a"})
        self.assertTrue(-100 <= result["integratedLUFS"] <= 10)
        self.assertTrue(-100 <= result["truePeakDbTP"] <= 20)
# @@ audio.sync

    def test_offset_and_correlation(self):
        result = self.run_capability({"mediaPath": "/tmp/a.m4a", "otherPath": "/tmp/b.m4a"})
        self.assertIsInstance(result["offsetSeconds"], (int, float))
        self.assertTrue(-1 <= result["correlation"] <= 1)
# @@ end


if __name__ == "__main__":
    unittest.main()
