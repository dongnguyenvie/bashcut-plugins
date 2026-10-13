

def nodes(body):
    """Every component of a view answer, depth first."""
    for node in body:
        yield node
        yield from nodes(node.get("children", []))


class ViewTests(unittest.TestCase):
    """The views answer view.render and view.event like BashCut sends them, and call BashCut over the host channel."""

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.calls = []
        self.answers = {}

    def answer(self, call):
        self.calls.append((call["method"], call["params"]))
        reply = self.answers.get(call["method"], {})
        return {"result": reply(call["params"]) if callable(reply) else reply}

    def view(self, view, state=None, values=None, event=None, features=()):
        params = {"view": view, "state": state, "values": values or {}, "locale": "en", "options": {},
                  "context": {"project": {"name": "Trip"}, "playhead": 12}}
        if event:
            params["event"] = event
        session = Session(self.folder, features)
        try:
            lines, reply = session.request("v1", "view.event" if event else "view.render", params, on_call=self.answer)
        finally:
            session.close()
        self.assertNotIn("error", reply, reply)
        return lines, reply["result"]

    def test_manifest_declares_three_places(self):
        views = {view["id"]: view.get("location", "panel") for view in MANIFEST["contributes"]["views"]}
        self.assertEqual(views, {"main": "panel", "media": "dock", "form": "sheet"})
        self.assertIn("icon", MANIFEST["contributes"]["container"])

    def test_main_counts_in_state(self):
        _, first = self.view("main", event={"node": "add", "type": "click"})
        self.assertEqual(first["state"]["count"], 1)
        _, second = self.view("main", state=first["state"], event={"node": "add", "type": "click"})
        self.assertEqual(second["state"]["count"], 2)
        ids = [node["id"] for node in nodes(second["body"]) if "id" in node]
        self.assertEqual(len(ids), len(set(ids)))

    def test_main_reads_the_timeline_while_showing_progress(self):
        self.answers["timeline.get"] = {"tracks": [{"id": "v1"}, {"id": "a1"}]}
        lines, result = self.view("main", event={"node": "timeline", "type": "click"})
        renders = [line["event"] for line in lines if line["type"] == "event"]
        self.assertEqual(renders[0]["kind"], "render")
        self.assertEqual(result["state"]["message"], "The timeline has 2 layers.")

    def test_main_opens_the_sheet(self):
        self.view("main", event={"node": "openForm", "type": "click"})
        self.assertEqual(self.calls[-1], ("plugins.show-view", {"plugin": MANIFEST["id"], "view": "form"}))

    def test_media_rows_drag_and_measure_with_a_job(self):
        self.answers.update({
            "media.list": {"media": [{"id": "m1", "name": "voice.wav", "kind": "audio", "path": "/tmp/voice.wav"},
                                     {"id": "m2", "name": "clip.mov", "kind": "video", "path": "media/clip.mov"}]},
            "plugins.invoke": {"job": "j1", "state": "running"},
            "jobs.status": {"state": "completed", "result": {"plugin": "bashcut.audio-analysis",
                                                             "result": {"integratedLUFS": -16.5}}},
        })
        _, first = self.view("media")
        rows = next(node for node in nodes(first["body"]) if node.get("id") == "media")["items"]
        self.assertEqual([row.get("file") for row in rows], ["/tmp/voice.wav", None])
        _, measured = self.view("media", state=first["state"],
                                event={"node": "media", "type": "action", "value": {"item": "m1", "action": "loudness"}})
        self.assertEqual([call[0] for call in self.calls], ["media.list", "plugins.invoke", "jobs.status"])
        self.assertEqual(self.calls[1][1], {"capability": "audio.loudness", "params": {"mediaPath": "/tmp/voice.wav"}})
        self.assertEqual(measured["state"]["message"], "voice.wav: -16.5 LUFS")

    def test_form_checks_then_closes(self):
        _, empty = self.view("form", values={"title": ""}, event={"node": "save", "type": "click"})
        self.assertNotIn("close", empty)
        self.assertIn("Write a title first.", json.dumps(empty))
        _, done = self.view("form", values={"title": "Chapter 1", "color": "#112233"},
                            event={"node": "save", "type": "click"})
        self.assertTrue(done["close"])
        self.assertEqual(self.calls[-1][0], "ui.action")
        self.assertIn("Saved Chapter 1", self.calls[-1][1]["target"])
        _, cancelled = self.view("form", event={"node": "cancel", "type": "click"})
        self.assertTrue(cancelled["close"])

    def test_colour_well_only_when_the_host_has_it(self):
        _, older = self.view("form")
        _, newer = self.view("form", features=["views", "views.colorPicker"])
        kind = lambda result: next(node for node in nodes(result["body"]) if node.get("id") == "color")["type"]
        self.assertEqual((kind(older), kind(newer)), ("textField", "colorPicker"))

    def test_action_opens_the_form(self):
        session = Session(self.folder)
        try:
            _, reply = session.request("a1", "plugin.action", {"action": "{{ACTION_ID}}", "params": {}, "options": {},
                                                               "context": {}}, on_call=self.answer)
        finally:
            session.close()
        self.assertEqual(reply["result"]["message"], "Opened the form")
        self.assertEqual(self.calls[-1][0], "plugins.show-view")


if __name__ == "__main__":
    unittest.main()
