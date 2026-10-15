"""The plugin around the fetch scripts: session protocol, the `bashcut` bridge, search/download and the sheet.
No network: the scripts' searches and downloads are replaced, and a fake host answers the host calls."""
import contextlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parents[1] / "scripts"))

import plugin_manifest  # noqa: E402
import resources  # noqa: E402


class FakeHost:
    def __init__(self, library=(), project=None):
        self.library, self.calls, self.renders, self.project = list(library), [], [], project

    def call(self, method, params=None):
        self.calls.append((method, params))
        if method == "library.list":
            return {"items": self.library}
        if method == "cli":
            argv = params["argv"]
            if argv[:2] == ["library", "add"]:
                wanted = argv[argv.index("--id") + 1]
                return {"item": {"id": wanted, "reference": f"project:{wanted}"}}
            if argv[:2] == ["context", "get"] and self.project:
                return {"project": self.project}
            return {"argv": argv}
        return {}

    def progress(self, fraction=None, message=None):
        pass

    def render(self, body, title=None):
        self.renders.append(body)


ROWS = [{"id": "11", "source": "pixabay", "kind": "photo", "tags": "clay pot", "size": "1920x1280",
         "preview": "https://cdn.example/11-small.jpg", "url": "https://cdn.example/11.jpg", "license": "Pixabay"},
        {"id": "12", "source": "pixabay", "kind": "photo", "tags": "coffee cup", "size": "1920x1280",
         "preview": "https://cdn.example/12-small.jpg", "url": "https://cdn.example/12.jpg", "license": "Pixabay"}]


class PluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        resources.start()

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        patch = mock.patch.dict(os.environ, {"BASHCUT_SHARED_CACHE": self.tmp})
        patch.start()
        self.addCleanup(patch.stop)
        self.stock = resources.module("fetch_stock")
        for name, value in (("get", lambda url, headers=None, timeout=30: b"jpeg-bytes"),
                            ("pick_source", lambda name, kind="photo": name or "pixabay")):
            patcher = mock.patch.object(self.stock, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = mock.patch.dict(self.stock.SEARCH, {"pixabay": lambda *a, **k: [dict(r) for r in ROWS]})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_the_bridge_runs_bashcut_words_as_the_host_call_cli(self):
        host = FakeHost()
        with resources.working(host, {}):
            out = subprocess.run(["bashcut", "library", "list", "--kind", "clip"], capture_output=True, text=True,
                                 env=os.environ)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout), {"argv": ["library", "list", "--kind", "clip"]})
        self.assertEqual(host.calls, [("cli", {"argv": ["library", "list", "--kind", "clip"]})])

    def test_bridge_errors_look_like_the_cli(self):
        host = FakeHost()
        host.call = mock.Mock(side_effect=resources.PluginError("-32601", "Plugins cannot run export.start"))
        with resources.working(host, {}):
            out = subprocess.run(["bashcut", "export", "start"], capture_output=True, text=True, env=os.environ)
        self.assertEqual(out.returncode, 1)
        self.assertEqual(json.loads(out.stderr)["error"], {"code": -32601, "message": "Plugins cannot run export.start"})

    def test_keys_come_from_secret_options_only_while_working(self):
        with resources.working(FakeHost(), {"pexelsKey": " abc "}):
            self.assertEqual(os.environ.get("PEXELS_API_KEY"), "abc")
        self.assertNotEqual(os.environ.get("PEXELS_API_KEY"), "abc")

    def test_search_lists_the_library_first_and_marks_downloaded_results(self):
        host = FakeHost(library=[{"id": "pixabay-11", "scope": "project", "name": "clay pot", "tags": ["stock"]}])
        found = resources.search(host, {}, "photo", "clay pot", "pixabay")
        self.assertEqual(found["source"], "pixabay")
        self.assertEqual([i["id"] for i in found["items"]], ["pixabay-11", "pixabay-12"])
        self.assertEqual(found["items"][0]["inLibrary"], "project:pixabay-11")
        self.assertNotIn("inLibrary", found["items"][1])
        self.assertEqual(found["library"][0]["libraryId"], "project:pixabay-11")
        self.assertTrue(Path(found["items"][0]["preview"]).is_file())
        self.assertIsNone(found["next"])

    def test_download_saves_with_the_scripts_tags_and_ids(self):
        host = FakeHost()
        resources.search(host, {}, "photo", "clay pot", "pixabay")
        rows = resources.download(host, {}, "photo", "clay pot", "pixabay-12")
        self.assertEqual(rows[0]["libraryId"], "project:pixabay-12")
        argv = next(p["argv"] for m, p in host.calls if m == "cli")
        self.assertEqual(argv[:3], ["library", "add", "--kind"])
        tags = argv[argv.index("--tags") + 1].split(",")
        self.assertEqual(tags[:3], ["stock", "clay-pot", "clay"])
        self.assertTrue(Path(rows[0]["file"]).is_file())

    def test_actions_answer_with_data_for_plugins_run(self):
        answer = resources.handle("plugin.action", {"action": "bashcut.resources.search", "params": {
            "kind": "photo", "query": "clay pot", "source": "pixabay"}, "options": {}}, FakeHost())
        self.assertEqual(len(answer["data"]["items"]), 2)
        ran = resources.handle("plugin.action", {"action": "bashcut.resources.fetch", "params": {
            "script": "stock", "args": "--help"}}, FakeHost())
        self.assertIn("--query", ran["data"]["output"])
        with self.assertRaises(resources.PluginError):
            resources.handle("plugin.action", {"action": "bashcut.resources.fetch", "params": {"script": "nope"}},
                             FakeHost())

    def test_open_shows_the_sheet_and_leaves_no_status_message(self):
        host = FakeHost()
        answer = resources.handle("plugin.action", {"action": "bashcut.resources.open"}, host)
        self.assertEqual(host.calls, [("plugins.show-view", {"plugin": "bashcut.resources", "view": "browse"})])
        self.assertNotIn("message", answer)

    def test_the_sheet_searches_selects_and_downloads(self):
        host = FakeHost()
        params = {"view": "browse", "locale": "en", "options": {}}
        first = resources.handle("view.render", {**params, "values": {}}, host)
        self.assertEqual(plugin_manifest.view_problems(first), [])
        values = {"kind": "photo", "query": "clay pot", "source": "pixabay"}
        found = resources.handle("view.event", {**params, "state": first["state"], "values": values,
                                                "event": {"node": "search", "type": "click"}}, host)
        self.assertEqual(plugin_manifest.view_problems(found), [])
        grid = find(found["body"], "results")
        self.assertEqual([i["id"] for i in grid["items"]], ["pixabay-11", "pixabay-12"])
        picked = resources.handle("view.event", {**params, "state": found["state"], "values": values,
                                                 "event": {"node": "results", "type": "select", "value": "pixabay-12"}},
                                  host)
        self.assertEqual(find(picked["body"], "results")["selected"], ["pixabay-12"])
        saved = resources.handle("view.event", {**params, "state": picked["state"], "values": values,
                                                "event": {"node": "download", "type": "click"}}, host)
        cell = next(i for i in find(saved["body"], "results")["items"] if i["id"] == "pixabay-12")
        self.assertEqual(cell["libraryItem"], "project:pixabay-12")
        self.assertIn("1 saved", saved["state"]["message"])

    def test_the_empty_sheet_labels_its_filters_and_offers_example_searches(self):
        host = FakeHost()
        params = {"view": "browse", "locale": "en", "options": {},
                  "context": {"project": {"width": 1080, "height": 1920}}}
        first = resources.handle("view.render", {**params, "values": {}}, host)
        self.assertEqual(plugin_manifest.view_problems(first), [])
        self.assertNotIn("title", first)  # the sheet header already names the view
        pickers = {n["id"]: n for n in first["body"][0]["children"] if n["type"] == "picker"}
        self.assertEqual({k: v["label"] for k, v in pickers.items()},
                         {"kind": "Type", "source": "Source", "orientation": "Orientation"})
        self.assertEqual(pickers["source"]["options"][0]["label"], "Any free source")
        self.assertEqual(pickers["orientation"]["value"], "portrait")  # a 9:16 project
        self.assertEqual(find(first["body"], "example.0")["title"], "coffee")
        found = resources.handle("view.event", {**params, "state": first["state"], "values": {"kind": "photo"},
                                                "event": {"node": "example.0", "type": "click"}}, host)
        self.assertEqual(found["state"]["query"], "coffee")
        self.assertEqual(find(found["body"], "query")["value"], "coffee")
        self.assertIsNotNone(find(found["body"], "results"))
        skeleton = find(host.renders[-1], "loading")  # the render while the search ran
        self.assertEqual(len(skeleton["items"]), resources.SKELETON_TILES)
        self.assertEqual(plugin_manifest.view_problems({"body": host.renders[-1]}), [])

    def test_lottie_tab_saves_picks_into_the_project_not_the_library(self):
        lottie = resources.module("fetch_lottie")
        shared, project = tempfile.mkdtemp(), Path(tempfile.mkdtemp())
        animation = Path(shared) / "check.json"
        animation.write_text('{"v": "5.6.5", "fr": 30, "ip": 0, "op": 30, "w": 32, "h": 32, "layers": []}')
        rows = [{"key": "ua-checkmark", "source": "useanimations", "id": "checkmark", "name": "Checkmark",
                 "tags": ["check"], "order": 0}]

        def strip(text, out, tile=220):
            out.write_bytes(b"png")
            return {"fps": 30.0, "frames": 30, "seconds": 1.0, "width": 32, "height": 32}
        for name, value in (("ingest", lambda refresh=False, fetch=None: (rows, None)),
                            ("lottiefiles", lambda *a, **k: []), ("lottie_file", lambda row, fetch=None: animation),
                            ("frame_strip", strip), ("draw_sheets", lambda shown, dest, slots: [])):
            patcher = mock.patch.object(lottie, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        host = FakeHost(project=str(project / "Demo.bashcut"))
        params = {"view": "browse", "locale": "en", "options": {}}
        values = {"kind": "lottie", "query": "check", "source": "all"}
        found = resources.handle("view.event", {**params, "state": {}, "values": values,
                                                "event": {"node": "search", "type": "click"}}, host)
        self.assertEqual(plugin_manifest.view_problems(found), [])
        cell = find(found["body"], "results")["items"][0]
        self.assertEqual((cell["id"], cell["title"], cell["subtitle"]), ("check=1", "Checkmark",
                                                                         "useanimations · 1.0 s · MIT"))
        self.assertNotIn("library.list", [m for m, _ in host.calls])  # no library kind for Lottie
        picked = resources.handle("view.event", {**params, "state": found["state"], "values": values,
                                                 "event": {"node": "results", "type": "select", "value": "check=1"}},
                                  host)
        saved = resources.handle("view.event", {**params, "state": picked["state"], "values": values,
                                                "event": {"node": "download", "type": "click"}}, host)
        self.assertTrue((project / "media/lottie/check-ua-checkmark.json").is_file())
        self.assertEqual(find(saved["body"], "results")["items"][0]["badge"], "In library")
        self.assertIn("1 saved to the project", saved["state"]["message"])
        self.assertFalse(any(p and p.get("argv", [""])[0] == "library" for m, p in host.calls if m == "cli"))
        again = resources.search(host, {}, "lottie", "check", "all")
        self.assertEqual(again["items"][0]["inLibrary"], str(project / "media/lottie/check-ua-checkmark.json"))

    def test_session_transport(self):
        out = subprocess.run([str(ROOT / "bin" / "provider"), "session"], input="\n".join(json.dumps(m) for m in [
            {"type": "hello", "apiVersion": 8, "features": ["views.grid"]},
            {"type": "request", "id": "r1", "apiVersion": 8, "method": "plugin.action",
             "params": {"action": "bashcut.resources.fetch", "params": {"script": "logos", "args": "--help"}}},
            {"type": "shutdown"}]) + "\n", capture_output=True, text=True, timeout=60,
            env={**os.environ, "BASHCUT_PLUGIN_DATA": self.tmp})
        lines = [json.loads(line) for line in out.stdout.splitlines() if line.strip()]
        self.assertEqual(lines[0]["type"], "hello")
        self.assertIn("--brands", lines[-1]["result"]["data"]["output"])


def find(body, node_id):
    for node in body:
        if node.get("id") == node_id:
            return node
        with contextlib.suppress(LookupError):
            return find(node.get("children") or [], node_id)
    raise LookupError(node_id)


if __name__ == "__main__":
    unittest.main()
