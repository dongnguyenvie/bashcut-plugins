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
    def __init__(self, library=()):
        self.library, self.calls, self.renders = list(library), [], []

    def call(self, method, params=None):
        self.calls.append((method, params))
        if method == "library.list":
            return {"items": self.library}
        if method == "cli":
            argv = params["argv"]
            if argv[:2] == ["library", "add"]:
                wanted = argv[argv.index("--id") + 1]
                return {"item": {"id": wanted, "reference": f"project:{wanted}"}}
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
