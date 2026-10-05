

class OptionsTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def run_action(self, options):
        return call(self.folder, "plugin.action", {"action": "{{ACTION_ID}}", "params": {}, "options": options,
                                                   "context": {"project": {"rev": 1}, "playhead": 0},
                                                   "outputDirectory": self.folder})["result"]

    def test_reads_every_option(self):
        result = self.run_action({"greeting": "Xin chào", "style": "long", "repeat": 2, "shout": False,
                                  "apiKey": "sk-test-123"})
        self.assertEqual(result["data"], {"greeting": "Xin chào Xin chào", "style": "long", "apiKeySet": True})
        self.assertEqual(result["message"], "Xin chào Xin chào (style long, API key set)")

    def test_never_returns_the_secret(self):
        result = self.run_action({"greeting": "Hi", "style": "long", "repeat": 1, "shout": True, "apiKey": "sk-test-123"})
        self.assertNotIn("sk-test-123", json.dumps(result))
        self.assertEqual(result["data"]["greeting"], "HI")

    def test_defaults(self):
        result = self.run_action({})
        self.assertEqual(result["data"], {"greeting": "Hello", "style": "short", "apiKeySet": False})


if __name__ == "__main__":
    unittest.main()
