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
from plugin_manifest import manifest_problems, skill_problems  # noqa: E402


class Session:
    def __init__(self, answers=None):
        env = dict(os.environ, BASHCUT_PLUGIN_CACHE=tempfile.mkdtemp())
        self.process = subprocess.Popen([PROVIDER, "session"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        text=True, env=env)
        self.answers = answers or {}
        self.calls, self.events = [], []
        self.write({"type": "hello", "apiVersion": 8, "features": ["views", "views.list"]})
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
                self.write({"type": "callResult", "callId": message["callId"], "result": result})
            elif message.get("type") == "event":
                self.events.append(message["event"])
            else:
                return message

    def view(self, view, state=None, values=None, event=None):
        params = {"view": view, "state": state, "values": values or {}, "locale": "en",
                  "context": {"project": {"name": "Trip"}, "playhead": 12}, "options": {"greeting": "Xin chào"}}
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
        session = Session({"ui.notify": {}})
        try:
            empty = session.view("titleCard", values={"title": ""}, event={"node": "create", "type": "click"})["result"]
            self.assertFalse(empty.get("close", False))
            self.assertIn("Write a title first.", json.dumps(empty))
            done = session.view("titleCard", values={"title": "Chapter 1", "style": "neon", "seconds": 4},
                                event={"node": "create", "type": "click"})["result"]
            self.assertTrue(done["close"])
            self.assertEqual(session.calls[-1][0], "ui.notify")
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


class VoiceTests(unittest.TestCase):
    def test_takes_come_from_voice_speak_and_loudness_from_invoke(self):
        take = os.path.join(tempfile.mkdtemp(), "take-1.wav")
        session = Session({
            "voice.speak": {"job": "j1", "state": "running"},
            "jobs.status": {"state": "completed", "result": {"takes": [{"path": take, "score": 0.8, "seconds": 1.5}]}},
            "plugins.invoke": {"plugin": "bashcut.audio-analysis", "result": {"integratedLUFS": -16.2}},
            "context.get": {"rev": 7},
            "media.import": {"rev": 8},
        })
        try:
            spoken = session.view("voice", values={"text": "Xin chào"}, event={"node": "speak", "type": "click"})
            state = spoken["result"]["state"]
            self.assertEqual([take["path"] for take in state["takes"]], [take])
            self.assertEqual(session.calls[0], ("voice.speak", {"text": "Xin chào", "takes": 2, "keepTakes": True}))
            self.assertEqual(session.events[0]["kind"], "render")
            measured = session.view("voice", state=state, event={
                "node": "takes", "type": "action", "value": {"item": take, "action": "measure"}})
            self.assertEqual(session.calls[-1][0], "plugins.invoke")
            self.assertEqual(session.calls[-1][1]["capability"], "audio.loudness")
            self.assertAlmostEqual(measured["result"]["state"]["takes"][0]["lufs"], -16.2)
            session.view("voice", state=measured["result"]["state"], event={
                "node": "takes", "type": "action", "value": {"item": take, "action": "use"}})
            self.assertEqual(session.calls[-1], ("media.import", {"path": take, "place": True, "baseRev": 7}))
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


class ActionTests(unittest.TestCase):
    def test_hello_calls_back(self):
        session = Session({"context.get": {"rev": 3}, "ui.notify": {}})
        try:
            reply = session.request("plugin.action", {"action": "bashcut.views-example.hello", "params": {},
                                                      "options": {"greeting": "Chào"}, "context": {}})
            self.assertEqual(reply["result"]["message"], "Chào")
            self.assertEqual(session.calls[-1], ("ui.notify", {"message": "Chào! The project is at revision 3."}))
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main()
