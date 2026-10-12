"""Smoke tests for HyperFrames Graphics: run the entrypoint the way BashCut does, with sample requests.

    python3 -m unittest discover -s tests -v

Build first when the plugin has a build.sh. These tests use only the Python standard library and are not shipped.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = json.loads((ROOT / "plugin.json").read_text())
ENTRYPOINT = ROOT / MANIFEST["entrypoint"]


def environment(folder):
    """The filtered environment BashCut gives plugin processes."""
    data, cache = pathlib.Path(folder, "data"), pathlib.Path(folder, "cache")
    data.mkdir(exist_ok=True)
    cache.mkdir(exist_ok=True)
    env = {key: os.environ[key] for key in ("HOME", "TMPDIR", "LANG", "LC_ALL") if key in os.environ}
    env.update({
        "PATH": os.environ.get("PATH", "/usr/bin:/bin:/usr/sbin:/sbin"),
        "BASHCUT_PLUGIN_ID": MANIFEST["id"],
        "BASHCUT_PLUGIN_DIR": str(ROOT),
        "BASHCUT_PLUGIN_API_VERSION": str(MANIFEST["apiVersion"]),
        "BASHCUT_PLUGIN_DATA": str(data),
        "BASHCUT_PLUGIN_CACHE": str(cache),
    })
    return env


def rpc(folder, method, params, provider=None):
    """One request over the one-shot transport (`provider rpc`)."""
    request = {"id": "r1", "apiVersion": MANIFEST["apiVersion"], "method": method, "params": params}
    if provider:
        request["provider"] = provider
    out = subprocess.run([str(ENTRYPOINT), "rpc"], input=json.dumps(request) + "\n", capture_output=True, text=True,
                         cwd=ROOT, env=environment(folder), timeout=60)
    if out.returncode != 0:
        raise AssertionError(f"exit {out.returncode}: {out.stderr}")
    response = json.loads(out.stdout)
    if response.get("id") != "r1":
        raise AssertionError(f"the response id does not match: {out.stdout}")
    return response


class Session:
    """The session transport (`provider session`): newline-delimited JSON in both directions."""

    def __init__(self, folder):
        self.process = subprocess.Popen([str(ENTRYPOINT), "session"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, text=True, cwd=ROOT, env=environment(folder))
        self.send({"type": "hello", "apiVersion": MANIFEST["apiVersion"], "host": "BashCut", "pluginId": MANIFEST["id"]})
        hello = self.read()
        if hello.get("type") != "hello":
            raise AssertionError(f"expected hello, got {hello}")

    def send(self, message):
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def read(self):
        line = self.process.stdout.readline()
        if not line:
            raise AssertionError(f"the session ended: {self.process.stderr.read()}")
        return json.loads(line)

    def request(self, request_id, method, params, provider=None, on_call=None):
        """Sends a request and returns (lines before the reply, reply). `on_call(call)` answers host calls."""
        request = {"type": "request", "id": request_id, "apiVersion": MANIFEST["apiVersion"], "method": method,
                   "params": params}
        if provider:
            request["provider"] = provider
        self.send(request)
        lines = []
        while True:
            message = self.read()
            if message.get("type") == "call" and on_call:
                self.send({"type": "callResult", "callId": message["callId"], **on_call(message)})
            if message.get("type") in ("progress", "event", "call"):
                lines.append(message)
                continue
            if message.get("id") != request_id:
                raise AssertionError(f"reply for another request: {message}")
            return lines, message

    def close(self):
        self.send({"type": "shutdown"})
        self.process.wait(timeout=10)
        self.process.stdout.close()
        self.process.stderr.close()
        self.process.stdin.close()


def call(folder, method, params, provider=None):
    """One request over the plugin's own transport; returns the response."""
    if MANIFEST.get("transport") != "session":
        return rpc(folder, method, params, provider)
    session = Session(folder)
    try:
        return session.request("r1", method, params, provider)[1]
    finally:
        session.close()


RUNTIME_DATA = os.environ.get("HYPERFRAMES_TEST_DATA")  # a data folder bin/setup filled (live render test)
RUNTIME_CACHE = os.environ.get("HYPERFRAMES_TEST_CACHE")
EXAMPLES = sorted(p for p in (ROOT / "examples").iterdir() if (p / "index.html").is_file())


class ManifestTests(unittest.TestCase):
    def test_entrypoint_is_executable(self):
        self.assertTrue(os.access(ENTRYPOINT, os.X_OK), f"{ENTRYPOINT} is missing or not executable (build first?)")

    def test_encoder_is_built(self):
        self.assertTrue(os.access(ROOT / "bin" / "encode-alpha", os.X_OK), "run build.sh first")

    def test_runtime_lockfile_matches_the_manifest(self):
        package = json.loads((ROOT / "runtime" / "package.template.json").read_text())
        lock = json.loads((ROOT / "runtime" / "package-lock.template.json").read_text())
        self.assertEqual(lock["packages"][""]["dependencies"], package["dependencies"])
        for name, version in package["dependencies"].items():
            self.assertEqual(lock["packages"][f"node_modules/{name}"]["version"], version)

    def test_unknown_method_is_an_error(self):
        with tempfile.TemporaryDirectory() as folder:
            response = call(folder, "nope.nothing", {})
        self.assertIn("error", response)


class ExampleTests(unittest.TestCase):
    """The examples are starting points agents copy: each must follow the HyperFrames rules."""

    def test_examples_exist(self):
        self.assertGreaterEqual(len(EXAMPLES), 10)
        self.assertIn("calendar", [example.name for example in EXAMPLES])

    def test_brand_variables_share_ids_and_types(self):
        """One brand restyles every widget: the standard ids mean the same thing everywhere, and old names are gone."""
        types = {"accent": "color", "background": "color", "text": "color", "secondary": "color",
                 "headingFont": "font", "bodyFont": "font"}
        for example in EXAMPLES:
            html = (example / "index.html").read_text()
            declarations = json.loads(re.search(r"data-composition-variables='(.*?)'", html, re.S).group(1))
            ids = {entry["id"]: entry["type"] for entry in declarations}
            self.assertIn("accent", ids, example.name)
            self.assertFalse({"ripple", "paper"} & set(ids), example.name)
            for key, kind in types.items():
                if key in ids:
                    self.assertEqual(kind, ids[key], f"{example.name}: {key}")
            if "headingFont" in ids:
                self.assertIn("Brand look", html, example.name)
                self.assertIn("var(--heading-font)", html, example.name)

    def test_variables_are_declared_as_an_array(self):
        for example in EXAMPLES:
            html = (example / "index.html").read_text()
            match = re.search(r"<html[^>]*data-composition-variables='(.*?)'", html, re.S)
            self.assertIsNotNone(match, example.name)
            declarations = json.loads(match.group(1))
            self.assertIsInstance(declarations, list, example.name)
            for entry in declarations:
                self.assertEqual({"id", "type", "label", "default"}, set(entry), f"{example.name}: {entry}")
                self.assertIn(entry["type"], {"string", "number", "color", "boolean", "enum", "font", "image"})

    def test_one_paused_timeline_named_main(self):
        for example in EXAMPLES:
            html = (example / "index.html").read_text()
            self.assertIn('data-composition-id="main"', html, example.name)
            self.assertIn("gsap.timeline({ paused: true })", html, example.name)
            self.assertIn('window.__timelines["main"] = tl', html, example.name)
            self.assertNotRegex(html, r"Math\.random|Date\.now|new Date|setTimeout|setInterval|https?://(?!www\.w3)",
                                example.name)


class OsmMapTests(unittest.TestCase):
    """bin/osm-map refuses bad arguments before it touches the network."""

    def run_map(self, *args):
        with tempfile.TemporaryDirectory() as folder:
            env = environment(folder)
            return subprocess.run([str(ROOT / "bin" / "osm-map"), *args], capture_output=True, text=True, env=env,
                                  timeout=30)

    def test_needs_a_folder_and_points(self):
        out = self.run_map("--points", "21.03,105.83,A")
        self.assertEqual(2, out.returncode, out.stderr)
        self.assertIn("--dir", out.stderr)

    def test_rejects_a_point_that_is_not_a_coordinate(self):
        with tempfile.TemporaryDirectory() as target:
            out = self.run_map("--dir", target, "--points", "105.83,21.03,Swapped")
        self.assertEqual(2, out.returncode, out.stderr)
        self.assertIn("latitude,longitude", out.stderr)

    def test_rejects_an_unknown_route_profile(self):
        with tempfile.TemporaryDirectory() as target:
            out = self.run_map("--dir", target, "--points", "21.03,105.83,A", "--route", "plane")
        self.assertEqual(2, out.returncode, out.stderr)

    def test_map_route_reads_the_data_osm_map_writes(self):
        html = (ROOT / "examples" / "map-route" / "index.html").read_text()
        self.assertIn('<script src="map-data.js"></script>', html)
        self.assertIn("data.attribution", html)
        stand_in = (ROOT / "examples" / "map-route" / "map-data.js").read_text()
        self.assertIn("© OpenStreetMap contributors", stand_in)


class RenderParamTests(unittest.TestCase):
    """graphics.render refuses bad requests before it needs the runtime."""

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.output = pathlib.Path(self.folder, "request")
        self.output.mkdir(mode=0o700)

    def render(self, params):
        return call(self.folder, "graphics.render", {"outputDirectory": str(self.output), **params},
                    provider="bashcut.hyperframes.render")

    def test_relative_composition_is_refused(self):
        self.assertEqual(self.render({"composition": "graphics/card"})["error"]["code"], "invalid_params")

    def test_missing_folder_is_refused(self):
        response = self.render({"composition": str(pathlib.Path(self.folder, "nothing"))})
        self.assertEqual(response["error"]["code"], "invalid_params")

    def test_bad_codec_is_refused(self):
        response = self.render({"composition": str(ROOT / "examples" / "keyword-pop"), "codec": "h264"})
        self.assertEqual(response["error"]["code"], "invalid_params")

    def test_missing_runtime_asks_for_install(self):
        composition = pathlib.Path(self.folder, "card")
        shutil.copytree(ROOT / "examples" / "keyword-pop", composition)
        response = self.render({"composition": str(composition)})  # the test data folder is empty
        self.assertEqual(response["error"]["code"], "dependency_missing")


FAKE_CLI = r"""#!/usr/bin/env python3
import json, os, sys
state_path = os.environ["FAKE_STATE"]
state = json.load(open(state_path))
args = sys.argv[1:]
entry = {"args": args}
command = " ".join(args[:2])
def option(name):
    return args[args.index(name) + 1] if name in args else None
if state.get("fail") == command:
    sys.stderr.write(json.dumps({"code": -32602, "message": "refused"}) + "\n")
    sys.exit(4)
if command == "project get":
    projects = state["projects"]
    out = projects.pop(0) if len(projects) > 1 else projects[0]
elif command == "plugins invoke":
    entry["params"] = json.loads(option("--params"))
    out = {"job": "job-1", "state": "running"}
elif command == "jobs wait":
    out = {"job": {"id": "job-1", "state": "completed", "result": {"plugin": "bashcut.hyperframes",
           "outputDirectory": os.path.dirname(state["render"]["path"]), "result": state["render"]}}}
elif command == "library add":
    out = {"id": option("--id"), "kind": "sticker"}
elif command == "library place":
    out = {"rev": 8, "item": "item-new", "track": "overlay", "media": "media-new", "duration": state["render"]["frames"]}
elif command == "timeline apply":
    entry["ops"] = json.load(open(args[2]))
    out = {"rev": int(option("--base-rev")) + 1, "changed": True}
elif command == "fonts list":
    out = state.get("fonts", [])
elif command == "context get":
    out = {"project": state.get("projectFile"), "rev": 7}
else:
    out = {}
state.setdefault("calls", []).append(entry)
json.dump(state, open(state_path, "w"))
print(json.dumps(out))
"""


class GraphicScriptTests(unittest.TestCase):
    """bin/graphic against a fake bashcut CLI that records each call: no app, no render."""

    def setUp(self):
        self.folder = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.folder, True)
        self.cli = self.folder / "bashcut"
        self.cli.write_text(FAKE_CLI)
        self.cli.chmod(0o755)
        self.composition = self.folder / "graphics" / "calendar"
        shutil.copytree(ROOT / "examples" / "calendar", self.composition)
        self.render = {"path": str(self.folder / "generated/plugins/cli/invoke/r1/calendar.mov"), "frames": 165,
                       "fps": 30, "width": 1080, "height": 1920, "lint": {"errors": 0, "warnings": 0, "findings": []}}
        self.brand = {"palette": {"accent": "#FF3366", "text": "#111111"}, "fonts": {"heading": "System-Black"},
                      "disclosure": "Ảnh tạo bằng AI"}

    def project(self, rev=7, media=(), items=(), brand=None):
        project = {"rev": rev, "format": {"width": 1080, "height": 1920, "fps": [30, 1]}, "media": list(media),
                   "tracks": [{"id": "overlay", "kind": "video", "role": "overlay", "items": list(items)}]}
        if brand:
            project["brand"] = brand
        return project

    def run_graphic(self, state, *args):
        path = self.folder / "state.json"
        path.write_text(json.dumps({"render": self.render, **state}))
        env = {**environment(self.folder), "BASHCUT_CLI": str(self.cli), "FAKE_STATE": str(path)}
        out = subprocess.run([str(ROOT / "bin" / "graphic"), *args], capture_output=True, text=True, env=env, timeout=60)
        calls = json.loads(path.read_text()).get("calls", [])
        return out, calls

    def recorded_media(self, variables, brand=True, frames=165):
        return {"id": "media-old", "path": "stickers/library-1.mov", "kind": "video", "fps": [30, 1], "frames": frames,
                "alpha": True, "data": {"graphics": {"composition": str(self.composition), "variables": variables,
                                                     "fps": 30, "codec": "hevc", "name": "calendar", "brand": brand}}}

    def test_usage_errors_exit_2(self):
        for args in (["place"], ["rerender"], ["draw", "x"], ["place", "d", "--keep-length"],
                     ["rerender", "x", "--at-frame", "3"], ["place", "d", "--variables", "[1]"],
                     ["place", "d", "--fps", "zero"], ["rerender", "x", "--all"]):
            out, calls = self.run_graphic({"projects": [self.project()]}, *args)
            self.assertEqual(2, out.returncode, (args, out.stderr))
            self.assertIn("error", json.loads(out.stderr))
            self.assertEqual([], calls, args)

    def test_place_renders_places_full_canvas_and_records_the_inputs(self):
        state = {"projects": [self.project(brand=self.brand), self.project(rev=7)]}
        out, calls = self.run_graphic(state, "place", str(self.composition), "--at-frame", "120",
                                      "--set", "title=Tháng đẹp", "--set", "month=3", "--set", "accent=#00AAFF",
                                      "--variables", '{"items": [{"month": 3, "at": 0.8}]}')
        self.assertEqual(0, out.returncode, out.stderr)
        result = json.loads(out.stdout)
        self.assertEqual(("item-new", "media-new", 165, 9), (result["item"], result["media"], result["frames"], result["rev"]))
        self.assertEqual(["headingFont", "text"], sorted(result["brand"]))  # accent was given
        commands = [" ".join(call["args"][:2]) for call in calls]
        self.assertEqual(["project get", "plugins invoke", "jobs wait", "library add", "project get", "library place",
                          "timeline apply"], commands)
        params = calls[1]["params"]
        self.assertEqual(str(self.composition), params["composition"])
        self.assertEqual((30, "hevc", "calendar"), (params["fps"], params["codec"], params["name"]))
        variables = params["variables"]
        self.assertEqual("#00AAFF", variables["accent"])  # explicit wins over the brand
        self.assertEqual(("#111111", "System-Black"), (variables["text"], variables["headingFont"]))
        self.assertEqual(3, variables["month"])  # typed by the declaration
        self.assertEqual('[{"month":3,"at":0.8}]', variables["items"])  # a list for a string is stringified
        self.assertNotIn("disclosure", variables)  # the calendar does not declare it
        place = calls[5]["args"]
        for flag, value in (("--size", "1"), ("--position", "0.5,0.5"), ("--at-frame", "120"), ("--base-rev", "7")):
            self.assertEqual(value, place[place.index(flag) + 1])
        ops = calls[6]["ops"]
        self.assertEqual("setMediaData", ops[0]["op"])
        recorded = ops[0]["patch"]["graphics"]
        self.assertEqual({"title", "month", "accent", "items"}, set(recorded["variables"]))  # brand values stay live
        self.assertTrue(recorded["brand"])

    def test_place_refuses_an_undeclared_variable_before_rendering(self):
        out, calls = self.run_graphic({"projects": [self.project()]}, "place", str(self.composition), "--set", "colour=#fff")
        self.assertEqual(2, out.returncode)
        self.assertIn("accent", json.loads(out.stderr)["error"])  # lists what it has
        self.assertNotIn("plugins", [call["args"][0] for call in calls])

    def test_place_without_brand(self):
        state = {"projects": [self.project(brand=self.brand)]}
        out, calls = self.run_graphic(state, "place", str(self.composition), "--no-brand", "--dry-run")
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertEqual({}, json.loads(out.stdout)["variables"])

    def test_rerender_merges_changes_and_repoints_items_in_one_apply(self):
        items = [{"id": "a", "media": "media-old", "at": 100, "dur": 165, "in": 0},
                 {"id": "b", "media": "media-old", "at": 400, "dur": 60, "in": 30}]
        project = self.project(rev=12, media=[self.recorded_media({"title": "Old", "accent": "#00AAFF"})], items=items,
                               brand={"palette": {"accent": "#FF3366", "background": "#222222"}})
        self.render["frames"] = 150
        out, calls = self.run_graphic({"projects": [project, project]}, "rerender", "a", "--set", "title=Mới",
                                      "--unset", "accent")
        self.assertEqual(0, out.returncode, out.stderr)
        variables = calls[1]["params"]["variables"]
        self.assertEqual({"title": "Mới", "accent": "#FF3366", "background": "#222222"}, variables)
        applies = [call for call in calls if call["args"][:2] == ["timeline", "apply"]]
        self.assertEqual(1, len(applies))
        self.assertEqual("12", applies[0]["args"][applies[0]["args"].index("--base-rev") + 1])
        ops = applies[0]["ops"]
        added = ops[0]["media"]
        self.assertEqual(("addMedia", True, "generated/plugins/cli/invoke/r1/calendar.mov", [30, 1], 150),
                         (ops[0]["op"], added["alpha"], added["path"], added["fps"], added["frames"]))
        sources = [op for op in ops if op["op"] == "setSource"]
        self.assertEqual([("a", 0), ("b", 30)], [(op["item"], op["sourceIn"]) for op in sources])
        self.assertTrue(all(op["media"] == added["id"] for op in sources))
        # a played the whole render, so it plays the whole new one; b was cut short on purpose and keeps 60 frames.
        self.assertEqual([{"op": "trim", "item": "a", "edge": "end", "toFrame": 250}], [op for op in ops if op["op"] == "trim"])
        recorded = ops[-1]
        self.assertEqual(("setMediaData", added["id"]), (recorded["op"], recorded["media"]))
        self.assertEqual({"title": "Mới"}, recorded["patch"]["graphics"]["variables"])
        result = json.loads(out.stdout)
        self.assertEqual(("media-old", 13), (result["replaced"], result["rev"]))
        self.assertIn("165→150", result["note"])

    def test_rerender_keep_length_cuts_only_what_the_new_render_lacks(self):
        items = [{"id": "a", "media": "media-old", "at": 0, "dur": 165, "in": 0}]
        project = self.project(media=[self.recorded_media({})], items=items)
        self.render["frames"] = 180
        out, calls = self.run_graphic({"projects": [project, project]}, "rerender", "media-old", "--keep-length")
        self.assertEqual(0, out.returncode, out.stderr)
        ops = [call for call in calls if call["args"][:2] == ["timeline", "apply"]][0]["ops"]
        self.assertEqual([], [op for op in ops if op["op"] == "trim"])
        self.assertNotIn("note", json.loads(out.stdout))

    def test_rerender_all_restyles_every_recorded_graphic_with_the_brand(self):
        second = dict(self.recorded_media({}, brand=True), id="media-two")
        unrecorded = {"id": "clip", "path": "a.mov", "kind": "video", "fps": [30, 1], "frames": 300}
        items = [{"id": "a", "media": "media-old", "at": 0, "dur": 165, "in": 0},
                 {"id": "b", "media": "media-two", "at": 300, "dur": 165, "in": 0},
                 {"id": "c", "media": "clip", "at": 0, "dur": 300, "in": 0}]
        project = self.project(media=[self.recorded_media({"accent": "#00AAFF"}, brand=False), second, unrecorded],
                               items=items, brand={"palette": {"accent": "#FF3366"}})
        out, calls = self.run_graphic({"projects": [project, project]}, "rerender", "--all", "--brand")
        self.assertEqual(0, out.returncode, out.stderr)
        renders = [call["params"]["variables"] for call in calls if call["args"][:2] == ["plugins", "invoke"]]
        self.assertEqual([{"accent": "#00AAFF"}, {"accent": "#FF3366"}], renders)  # explicit still wins over the brand
        applies = [call for call in calls if call["args"][:2] == ["timeline", "apply"]]
        self.assertEqual(1, len(applies))
        self.assertEqual(["a", "b"], [op["item"] for op in applies[0]["ops"] if op["op"] == "setSource"])
        self.assertEqual(2, len(json.loads(out.stdout)["graphics"]))

    def test_rerender_of_a_graphic_without_recorded_inputs_fails_loudly(self):
        project = self.project(media=[{"id": "clip", "path": "a.mov", "kind": "video", "fps": [30, 1], "frames": 30}],
                               items=[{"id": "c", "media": "clip", "at": 0, "dur": 30, "in": 0}])
        out, calls = self.run_graphic({"projects": [project]}, "rerender", "c")
        self.assertEqual(1, out.returncode)
        self.assertIn("bin/graphic place", json.loads(out.stderr)["error"])

    def test_a_refused_apply_fails_the_rerender(self):
        items = [{"id": "a", "media": "media-old", "at": 0, "dur": 165, "in": 0}]
        project = self.project(media=[self.recorded_media({})], items=items)
        out, _ = self.run_graphic({"projects": [project, project], "fail": "timeline apply"}, "rerender", "a")
        self.assertEqual(1, out.returncode)
        self.assertIn("refused", json.loads(out.stderr)["error"])

    def test_a_project_font_file_is_copied_next_to_the_composition(self):
        root = self.folder / "project"
        (root / "fonts").mkdir(parents=True)
        (root / "fonts" / "Brand-Bold.otf").write_bytes(b"font")
        state = {"projects": [self.project(brand={"fonts": {"heading": "Brand-Bold", "body": "Avenir Next"}})],
                 "fonts": [{"name": "Brand-Bold", "family": "Brand", "file": "Brand-Bold.otf", "source": "project"}],
                 "projectFile": str(root / "project.bashcut.json")}
        out, _ = self.run_graphic(state, "place", str(self.composition), "--dry-run")
        self.assertEqual(0, out.returncode, out.stderr)
        variables = json.loads(out.stdout)["variables"]
        self.assertEqual(("fonts/Brand-Bold.otf", "Avenir Next"), (variables["headingFont"], variables["bodyFont"]))
        self.assertTrue((self.composition / "fonts" / "Brand-Bold.otf").is_file())


@unittest.skipUnless(RUNTIME_DATA and RUNTIME_CACHE, "set HYPERFRAMES_TEST_DATA and HYPERFRAMES_TEST_CACHE to a setup install")
class LiveRenderTests(unittest.TestCase):
    def test_renders_an_alpha_movie(self):
        with tempfile.TemporaryDirectory() as folder:
            composition = pathlib.Path(folder, "keyword")
            shutil.copytree(ROOT / "examples" / "keyword-pop", composition)
            output = pathlib.Path(folder, "out")
            output.mkdir()
            env = {**environment(folder), "BASHCUT_PLUGIN_DATA": RUNTIME_DATA, "BASHCUT_PLUGIN_CACHE": RUNTIME_CACHE}
            request = {"id": "r1", "apiVersion": MANIFEST["apiVersion"], "method": "graphics.render",
                       "provider": "bashcut.hyperframes.render",
                       "params": {"composition": str(composition), "outputDirectory": str(output), "fps": 30,
                                  "variables": {"keyword": "Boost"}, "name": "boost"}}
            out = subprocess.run([str(ENTRYPOINT), "rpc"], input=json.dumps(request) + "\n", capture_output=True,
                                 text=True, cwd=ROOT, env=env, timeout=300)
            result = json.loads(out.stdout)["result"]
            self.assertEqual(result["path"], str(output / "boost.mov"))
            self.assertEqual((result["frames"], result["width"], result["height"]), (72, 1080, 1920))
            self.assertEqual(result["lint"]["errors"], 0)
            self.assertGreater(pathlib.Path(result["path"]).stat().st_size, 10_000)


if __name__ == "__main__":
    unittest.main()
