

class ActionTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def run_action(self, params):
        context = {"app": {"apiVersion": MANIFEST["apiVersion"], "language": "en"}, "author": "user",
                   "project": {"rev": 7, "fps": [30, 1]}, "playhead": 90, "pluginData": None}
        return call(self.folder, "plugin.action", {"action": "{{ACTION_ID}}", "params": params, "options": {},
                                                   "context": context, "outputDirectory": self.folder})

    def test_proposes_a_marker_at_the_playhead(self):
        result = self.run_action({"label": "Chapter \"1\""})["result"]
        self.assertEqual(result["baseRev"], 7)
        operation = result["operations"][0]
        self.assertEqual((operation["op"], operation["label"], operation["atFrame"]), ("upsertSection", "Chapter \"1\"", 90))
        self.assertTrue(operation["id"])
        self.assertEqual(result["ui"], {"reveal": 90})

    def test_default_label(self):
        self.assertEqual(self.run_action({})["result"]["operations"][0]["label"], "Marker")


if __name__ == "__main__":
    unittest.main()
