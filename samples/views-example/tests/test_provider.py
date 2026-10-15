"""Drives the sample like BashCut does: a session with hello, view requests, and answers to its host calls."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PROVIDER = os.path.join(HERE, "..", "bin", "provider")
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
from plugin_manifest import manifest_problems, skill_problems, view_problems  # noqa: E402


class Refused(Exception):
    """An answer that makes BashCut refuse the host call."""


class Session:
    def __init__(self, answers=None, features=("views", "views.list")):
        env = dict(os.environ, BASHCUT_PLUGIN_CACHE=tempfile.mkdtemp(), VIEWS_EXAMPLE_COUNT_SECONDS="0.01")
        self.process = subprocess.Popen([PROVIDER, "session"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        text=True, env=env)
        self.answers = answers or {}
        self.calls, self.events, self.updates = [], [], []
        self.write({"type": "hello", "apiVersion": 8, "features": list(features)})
        assert self.read()["type"] == "hello"

    def write(self, message):
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def read(self):
        return json.loads(self.process.stdout.readline())

    def request(self, method, params):
        self.write({"type": "request", "id": "r1", "apiVersion": 8, "method": method, "params": params})
        while True:
            message = self.read()
            if message.get("type") == "call":
                self.calls.append((message["method"], message["params"]))
                answer = self.answers.get(message["method"], {})
                result = answer(message["params"]) if callable(answer) else answer
                if isinstance(result, Refused):
                    self.write({"type": "callResult", "callId": message["callId"],
                                "error": {"code": -32602, "message": str(result)}})
                else:
                    self.write({"type": "callResult", "callId": message["callId"], "result": result})
            elif message.get("type") == "event":
                self.events.append(message["event"])
            elif message.get("type") in ("viewUpdate", "overlays"):
                self.updates.append(message)  # lines outside a request may arrive at any time
            else:
                return message

    def view(self, view, state=None, values=None, event=None, options=None):
        params = {"view": view, "state": state, "values": values or {}, "locale": "en",
                  "context": {"project": {"name": "Trip"}, "playhead": 12},
                  "options": {"greeting": "Xin chào", **(options or {})}}
        if event:
            params["event"] = event
        reply = self.request("view.event" if event else "view.render", params)
        return reply

    def close(self):
        self.write({"type": "shutdown"})
        self.process.wait(timeout=5)
        self.process.stdin.close()
        self.process.stdout.close()


def nodes(body):
    for node in body:
        yield node
        yield from nodes(node.get("children", []))


class ManifestTests(unittest.TestCase):
    def test_manifest_and_skill_follow_the_rules(self):
        folder = os.path.join(HERE, "..")
        with open(os.path.join(folder, "plugin.json")) as handle:
            manifest = json.load(handle)
        self.assertEqual(manifest_problems(manifest), [])
        browser = next(view for view in manifest["contributes"]["views"] if view["id"] == "browser")
        self.assertEqual(browser["location"], "window")
        self.assertGreaterEqual(manifest["minApiVersion"], 11)
        self.assertEqual(skill_problems(folder, manifest), [])


class GalleryTests(unittest.TestCase):
    def setUp(self):
        self.session = Session()

    def tearDown(self):
        self.session.close()

    def test_render_uses_every_component(self):
        result = self.session.view("gallery")["result"]
        types = {node["type"] for node in nodes(result["body"])}
        self.assertTrue({"section", "row", "divider", "text", "badge", "keyValue", "progress", "image",
                         "imageCompare", "audio", "list", "button", "textField", "textArea", "toggle", "picker",
                         "slider"} <= types)
        image = next(node for node in nodes(result["body"]) if node["type"] == "image")
        self.assertTrue(os.path.exists(image["path"]))
        ids = [node["id"] for node in nodes(result["body"]) if "id" in node]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(view_problems(result), [])
        self.assertTrue(os.path.exists(image["file"]), "the image drags its file")
        accent = next(node for node in nodes(result["body"]) if node.get("id") == "accent")
        self.assertEqual(accent["type"], "textField", "an older BashCut gets a text field")

    def test_pickers_when_the_host_has_them(self):
        session = Session(features=("views", "views.colorPicker", "views.fontPicker"))
        try:
            result = session.view("gallery")["result"]
        finally:
            session.close()
        by_id = {node.get("id"): node for node in nodes(result["body"])}
        self.assertEqual((by_id["accent"]["type"], by_id["accent"]["value"]), ("colorPicker", "#FF8800"))
        self.assertEqual((by_id["font"]["type"], by_id["font"]["by"]), ("fontPicker", "family"))
        self.assertEqual(view_problems(result), [])

    def test_events_change_state(self):
        first = self.session.view("gallery", event={"node": "add", "type": "click"})["result"]
        self.assertEqual(first["state"]["count"], 1)
        second = self.session.view("gallery", state=first["state"], event={"node": "add", "type": "click"})["result"]
        self.assertEqual(second["state"]["count"], 2)
        searched = self.session.view("gallery", state=second["state"], values={"query": "coffee"},
                                     event={"node": "query", "type": "change", "value": "coffee"})["result"]
        shots = next(node for node in nodes(searched["body"]) if node.get("id") == "shots")
        self.assertEqual([item["id"] for item in shots["items"]], ["s2"])
        starred = self.session.view("gallery", state=searched["state"],
                                    event={"node": "shots", "type": "action", "value": {"item": "s3", "action": "star"}})
        self.assertEqual(starred["result"]["state"]["starred"], ["s3"])


class TitleCardTests(unittest.TestCase):
    def test_gallery_button_opens_the_sheet(self):
        session = Session({"plugins.show-view": {"location": "sheet"}})
        try:
            session.view("gallery", event={"node": "openSheet", "type": "click"})
            self.assertEqual(session.calls[-1], ("plugins.show-view", {"plugin": "bashcut.views-example", "view": "titleCard"}))
        finally:
            session.close()

    def test_form_checks_then_closes(self):
        session = Session({"ui.action": {}})
        try:
            empty = session.view("titleCard", values={"title": ""}, event={"node": "create", "type": "click"})["result"]
            self.assertFalse(empty.get("close", False))
            self.assertIn("Write a title first.", json.dumps(empty))
            done = session.view("titleCard", values={"title": "Chapter 1", "style": "neon", "seconds": 4},
                                event={"node": "create", "type": "click"})["result"]
            self.assertTrue(done["close"])
            self.assertEqual(session.calls[-1][0], "ui.action")
            self.assertEqual(session.calls[-1][1]["action"], "notify")
            cancelled = session.view("titleCard", event={"node": "cancel", "type": "click"})["result"]
            self.assertTrue(cancelled["close"])
        finally:
            session.close()

    def test_action_opens_the_sheet(self):
        session = Session({"plugins.show-view": {}})
        try:
            reply = session.request("plugin.action", {"action": "bashcut.views-example.title-card", "params": {},
                                                      "options": {}, "context": {}})
            self.assertEqual(reply["result"]["message"], "Opened the title card form")
            self.assertEqual(session.calls[-1][0], "plugins.show-view")
        finally:
            session.close()


VOICES = {"capability": "voice.synthesize", "available": True, "providers": [
    {"id": "bashcut.vieneu-tts.synthesize", "plugin": "bashcut.vieneu-tts", "name": "VieNeu TTS", "paid": False},
    {"id": "example.cloud.voice", "plugin": "example.cloud", "name": "Cloud voice", "paid": True}]}


class VoiceTests(unittest.TestCase):
    def test_the_chosen_voice_plugin_is_saved_in_an_option(self):
        session = Session({"capabilities.get": VOICES, "plugins.option": {"value": "example.cloud.voice", "rev": 0},
                           "voice.speak": {"job": "j1"}, "jobs.status": {"state": "completed", "result": {"takes": []}}},
                          features=("views", "options.set"))
        try:
            first = session.view("voice")["result"]
            picker = next(node for node in nodes(first["body"]) if node.get("id") == "provider")
            self.assertEqual([o["value"] for o in picker["options"]],
                             ["", "bashcut.vieneu-tts.synthesize", "example.cloud.voice"])
            self.assertEqual(picker["options"][2]["label"], "Cloud voice (paid)")
            chosen = session.view("voice", state=first["state"], values={"provider": "example.cloud.voice"},
                                  event={"node": "provider", "type": "change", "value": "example.cloud.voice"})
            self.assertEqual(session.calls[-1], ("plugins.option", {"plugin": "bashcut.views-example",
                                                                    "option": "provider", "value": "example.cloud.voice"}))
            session.view("voice", state=chosen["result"]["state"], values={"text": "Xin chào"},
                         event={"node": "speak", "type": "click"})
            self.assertIn(("voice.speak", {"text": "Xin chào", "takes": 2, "provider": "example.cloud.voice"}),
                          session.calls)
            self.assertEqual([c[0] for c in session.calls].count("capabilities.get"), 1, "providers are kept in state")
        finally:
            session.close()
        # Next time the view opens, the option holds the choice.
        session = Session({"capabilities.get": VOICES})
        try:
            reopened = session.view("voice", options={"provider": "example.cloud.voice"})["result"]
            picker = next(node for node in nodes(reopened["body"]) if node.get("id") == "provider")
            self.assertEqual(picker["value"], "example.cloud.voice")
            # Clearing it resets the option (null), but an app without options.set only keeps it in state.
            session.view("voice", state=reopened["state"], event={"node": "provider", "type": "change", "value": ""})
            self.assertNotIn("plugins.option", [c[0] for c in session.calls])
        finally:
            session.close()

    def test_takes_come_from_voice_speak_and_loudness_from_invoke(self):
        take = os.path.join(tempfile.mkdtemp(), "take-1.wav")
        session = Session({
            "voice.speak": {"job": "j1", "state": "running"},
            "jobs.status": {"state": "completed", "result": {"takes": [{"path": take, "score": 0.8, "seconds": 1.5}]}},
            "plugins.invoke": {"plugin": "bashcut.audio-analysis", "result": {"integratedLUFS": -16.2}},
            "voice.place": {"rev": 8, "item": "vo-1"},
        })
        try:
            spoken = session.view("voice", values={"text": "Xin chào"}, event={"node": "speak", "type": "click"})
            state = spoken["result"]["state"]
            self.assertEqual([take["path"] for take in state["takes"]], [take])
            self.assertEqual(session.calls[0][0], "capabilities.get")
            self.assertEqual(session.calls[1], ("voice.speak", {"text": "Xin chào", "takes": 2}))
            self.assertEqual(session.events[0]["kind"], "render")
            measured = session.view("voice", state=state, event={
                "node": "takes", "type": "action", "value": {"item": take, "action": "measure"}})
            self.assertEqual(session.calls[-1][0], "plugins.invoke")
            self.assertEqual(session.calls[-1][1]["capability"], "audio.loudness")
            self.assertAlmostEqual(measured["result"]["state"]["takes"][0]["lufs"], -16.2)
            session.view("voice", state=measured["result"]["state"], event={
                "node": "takes", "type": "action", "value": {"item": take, "action": "use"}})
            self.assertEqual(session.calls[-1], ("voice.place", {"take": take}))
        finally:
            session.close()

    def test_a_refused_call_becomes_an_error(self):
        session = Session()
        try:
            session.write({"type": "request", "id": "r2", "apiVersion": 8, "method": "view.event", "params": {
                "view": "voice", "values": {"text": "Hi"}, "event": {"node": "speak", "type": "click"}}})
            while True:
                message = session.read()
                if message.get("type") == "call":
                    session.write({"type": "callResult", "callId": message["callId"],
                                   "error": {"code": -32603, "message": "Install a plugin that provides voice.synthesize"}})
                elif message.get("type") != "event":
                    break
            self.assertIn("voice.synthesize", message["error"]["message"])
        finally:
            session.close()


class LiveTests(unittest.TestCase):
    def test_marks_go_on_the_timeline_and_clear(self):
        session = Session({"plugins.set-overlays": {"count": 3}}, features=("views", "overlays", "viewUpdate"))
        try:
            session.view("live", event={"node": "mark", "type": "click"})
            method, params = session.calls[-1]
            self.assertEqual(method, "plugins.set-overlays")
            self.assertEqual(params["plugin"], "bashcut.views-example")
            self.assertEqual([(o["kind"], o["start"]) for o in params["overlays"]],
                             [("marker", 12), ("range", 12), ("region", 12)])
            session.view("live", event={"node": "clear", "type": "click"})
            self.assertEqual(session.calls[-1], ("plugins.set-overlays", {"plugin": "bashcut.views-example",
                                                                          "overlays": []}))
        finally:
            session.close()

    def test_background_job_redraws_with_view_updates(self):
        session = Session(features=("views", "overlays", "viewUpdate"))
        try:
            reply = session.view("live", event={"node": "count", "type": "click"})["result"]
            self.assertIn("Counting in the background…", json.dumps(reply, ensure_ascii=False))
            updates = session.updates + [session.read() for _ in range(5 - len(session.updates))]
            self.assertEqual({u["type"] for u in updates}, {"viewUpdate"})
            self.assertEqual({u["view"] for u in updates}, {"live"})
            progress = [next(n for n in nodes(u["body"]) if n["type"] == "progress")["value"] for u in updates]
            self.assertEqual(progress, [0.2, 0.4, 0.6, 0.8, 1.0])
            self.assertEqual(updates[-1]["notify"], "Counted to five")
            self.assertEqual(updates[-1]["state"]["message"], "Done: counted to five.")
            for update in updates:
                self.assertEqual(view_problems(update), [])
        finally:
            session.close()

    def test_older_host_has_no_mark_buttons(self):
        session = Session()
        try:
            result = session.view("live", event={"node": "mark", "type": "click"})["result"]
            self.assertNotIn("mark", [node.get("id") for node in nodes(result["body"])])
            self.assertEqual(session.calls, [])
        finally:
            session.close()


class BrowserTests(unittest.TestCase):
    """The window view (API 11): a split with a nav, a grid whose tiles download when dropped, an inspector."""

    def setUp(self):
        self.added = []
        self.session = Session(answers={
            "library.get": lambda params: Refused("No library item"),
            "library.add": lambda params: self.added.append(params) or {"id": params["id"]},
            "library.place": {"itemID": "i1"},
        }, features=("views", "views.split", "views.nav", "views.grid", "views.drag"))

    def tearDown(self):
        self.session.close()

    def test_three_columns_with_a_nav(self):
        result = self.session.view("browser")["result"]
        self.assertEqual(view_problems(result), [])
        split = result["body"][0]
        self.assertEqual(split["type"], "split")
        self.assertEqual(split["widths"], [200, "flex", 260])
        self.assertEqual(len(split["children"]), 3)
        nav = next(node for node in nodes(result["body"]) if node["type"] == "nav")
        self.assertEqual(nav["value"], "warm")
        self.assertEqual([entry["id"] for entry in nav["groups"][0]["items"]], ["warm", "cool", "mono"])
        grid = next(node for node in nodes(result["body"]) if node["type"] == "grid")
        self.assertEqual(grid["drag"], "download")
        cool = self.session.view("browser", state=result["state"],
                                 event={"node": "groups", "type": "select", "value": "cool"})["result"]
        self.assertEqual(cool["state"]["group"], "cool")

    def test_a_dropped_tile_is_saved_and_named_for_the_host(self):
        state = self.session.view("browser")["result"]["state"]
        dropped = self.session.view("browser", state=state,
                                    event={"node": "tiles", "type": "drag", "value": {"item": "sunset"}})["result"]
        self.assertEqual(dropped["libraryItem"], "project:views-example-sunset")
        self.assertEqual(len(self.added), 1)
        self.assertTrue(os.path.exists(self.added[0]["file"]))
        self.assertNotIn("library.place", [method for method, _ in self.session.calls], "BashCut places a drop")
        tile = next(node for node in nodes(dropped["body"]) if node["type"] == "grid")["items"][0]
        self.assertEqual(tile["libraryItem"], "project:views-example-sunset", "a saved tile drags the item itself")

    def test_inspector_adds_at_the_playhead(self):
        state = self.session.view("browser")["result"]["state"]
        picked = self.session.view("browser", state=state, event={"node": "tiles", "type": "select", "value": "ember"})
        inspector = picked["result"]["body"][0]["children"][2]
        self.assertIn("Licence", json.dumps(inspector))
        self.session.view("browser", state=picked["result"]["state"], event={"node": "add", "type": "click"})
        self.assertIn(("library.place", {"id": "project:views-example-ember", "atFrame": 12, "baseRev": "last"}), self.session.calls)


class ActionTests(unittest.TestCase):
    def test_hello_calls_back(self):
        session = Session({"context.get": {"rev": 3}, "ui.action": {}})
        try:
            reply = session.request("plugin.action", {"action": "bashcut.views-example.hello", "params": {},
                                                      "options": {"greeting": "Chào"}, "context": {}})
            self.assertEqual(reply["result"]["message"], "Chào")
            self.assertEqual(session.calls[-1], ("ui.action", {"action": "notify",
                                                               "target": "Chào! The project is at revision 3."}))
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main()
