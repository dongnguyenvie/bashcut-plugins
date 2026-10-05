

class HookTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def run_hook(self, event, payload, plugin_data=None):
        context = {"project": {"rev": 3}, "playhead": 0, "pluginData": plugin_data}
        return call(self.folder, "plugin.hook", {"event": event, "payload": {"event": event, **payload}, "options": {},
                                                 "context": context, "outputDirectory": self.folder})["result"]

    def test_export_finished_counts_exports(self):
        result = self.run_hook("export.finished", {"output": "/p/render/trip.mp4", "preset": "1080p", "rev": 3},
                               plugin_data={"exports": 2})
        self.assertEqual(result["pluginData"], {"lastExport": "/p/render/trip.mp4", "exports": 3})
        self.assertIn("trip.mp4", result["message"])

    def test_first_export(self):
        result = self.run_hook("export.finished", {"output": "/p/a.mp4"})
        self.assertEqual(result["pluginData"]["exports"], 1)

    def test_media_imported(self):
        result = self.run_hook("media.imported", {"author": "user", "media": [{"id": "m1"}, {"id": "m2"}]})
        self.assertEqual(result["message"], "Imported 2 media")

    def test_other_events_do_nothing(self):
        self.assertEqual(self.run_hook("project.saved", {"path": "/p", "rev": 1}), {})


if __name__ == "__main__":
    unittest.main()
