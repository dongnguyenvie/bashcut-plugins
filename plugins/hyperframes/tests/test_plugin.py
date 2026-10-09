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
        self.assertGreaterEqual(len(EXAMPLES), 5)

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
