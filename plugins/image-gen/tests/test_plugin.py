"""Tests for Image Generation: run the entrypoint the way BashCut does against a mock Gemini/OpenAI server.

No real key or network is used: MockService answers on 127.0.0.1 like the two APIs do.

    python3 -m unittest discover -s tests -v

Build first when the plugin has a build.sh. These tests use only the Python standard library and are not shipped.
"""
import base64
import http.server
import json
import os
import pathlib
import subprocess
import struct
import tempfile
import threading
import unittest
import zlib

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

    def __init__(self, folder, features=()):
        """`features`: the host features BashCut lists in its hello (API 8), such as "views.colorPicker"."""
        self.process = subprocess.Popen([str(ENTRYPOINT), "session"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, text=True, cwd=ROOT, env=environment(folder))
        self.send({"type": "hello", "apiVersion": MANIFEST["apiVersion"], "host": "BashCut", "pluginId": MANIFEST["id"],
                   "features": list(features)})
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


def png(width, height, rgb=(255, 128, 0)):
    """A solid PNG made with the standard library."""
    row = b"\x00" + bytes(rgb) * width
    chunk = lambda kind, data: struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(row * height)) + chunk(b"IEND", b"")


class MockService:
    """Answers generateContent (Gemini) and images/generations|edits (OpenAI); records what it was sent."""

    def __init__(self):
        self.requests = []
        mock = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                mock.requests.append({"path": self.path, "headers": dict(self.headers), "body": body})
                key = self.headers.get("x-goog-api-key") or self.headers.get("Authorization", "").removeprefix("Bearer ")
                if key == "bad":
                    return self.answer(401, {"error": {"message": "invalid key"}})
                text = body.decode("utf-8", "replace")
                if "REFUSE" in text:
                    return self.answer(400, {"error": {"message": "prompt refused"}})
                picture = base64.b64encode(png(64, 48)).decode()
                if ":generateContent" in self.path:
                    return self.answer(200, {"candidates": [{"content": {"parts": [
                        {"text": "here"}, {"inlineData": {"mimeType": "image/png", "data": picture}}]}}]})
                return self.answer(200, {"data": [{"b64_json": picture}]})

            def answer(self, status, payload):
                data = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.endpoint = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


class ManifestTests(unittest.TestCase):
    def test_entrypoint_is_executable(self):
        self.assertTrue(os.access(ENTRYPOINT, os.X_OK), f"{ENTRYPOINT} is missing or not executable (build first?)")

    def test_unknown_method_is_an_error(self):
        with tempfile.TemporaryDirectory() as folder:
            response = call(folder, "nope.nothing", {})
        self.assertIn("error", response)


class GenerateTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.output = pathlib.Path(self.folder, "request")
        self.output.mkdir(mode=0o700)
        self.service = MockService()
        self.reference = pathlib.Path(self.folder, "hero.png")
        self.reference.write_bytes(png(8, 8, (0, 0, 255)))

    def tearDown(self):
        self.service.close()

    def generate(self, service="gemini", key="test-key", references=(), prompts=None, session=None):
        params = {
            "prompts": prompts or [{"id": "s1", "prompt": "a fox in a forest"}, {"id": "s 2", "prompt": "a boat"}],
            "style": {"prompt": "crayon on paper", "references": [str(r) for r in references], "seed": 5},
            "width": 90, "height": 160, "aspectRatio": "9:16", "outputDirectory": str(self.output),
            "options": {"service": service, "apiKey": key, "model": "", "endpoint": self.service.endpoint},
        }
        if session:
            return session.request("r1", "image.generate", params, provider="bashcut.image-gen.api")
        return [], call(self.folder, "image.generate", params, provider="bashcut.image-gen.api")

    def assert_pictures(self, result, ids):
        self.assertEqual([image["id"] for image in result["images"]], ids)
        for image in result["images"]:
            data = (self.output / image["path"]).read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG"))
            self.assertEqual(struct.unpack(">II", data[16:24]), (90, 160))

    def test_gemini_batch_with_style_seed_and_reference(self):
        session = Session(self.folder)
        try:
            progress, response = self.generate(references=[self.reference], session=session)
        finally:
            session.close()
        self.assertNotIn("error", response, response)
        self.assert_pictures(response["result"], ["s1", "s 2"])
        self.assertEqual(response["result"]["images"][1]["path"], "s-2.png")
        self.assertTrue(any(line.get("type") == "progress" for line in progress))
        sent = json.loads(self.service.requests[0]["body"])
        self.assertIn("gemini-2.5-flash-image:generateContent", self.service.requests[0]["path"])
        self.assertEqual(self.service.requests[0]["headers"]["x-goog-api-key"], "test-key")
        parts = sent["contents"][0]["parts"]
        self.assertIn("crayon on paper", parts[0]["text"])
        self.assertIn("a fox in a forest", parts[0]["text"])
        self.assertEqual(base64.b64decode(parts[1]["inline_data"]["data"]), self.reference.read_bytes())
        self.assertEqual(sent["generationConfig"]["imageConfig"]["aspectRatio"], "9:16")
        self.assertEqual(sent["generationConfig"]["seed"], 5)

    def test_openai_generations_and_edits(self):
        _, response = self.generate(service="openai")
        self.assert_pictures(response["result"], ["s1", "s 2"])
        first = self.service.requests[0]
        self.assertEqual(first["path"], "/v1/images/generations")
        self.assertEqual(first["headers"]["Authorization"], "Bearer test-key")
        self.assertEqual(json.loads(first["body"])["size"], "1024x1536")
        _, response = self.generate(service="openai", references=[self.reference])
        self.assertNotIn("error", response, response)
        last = self.service.requests[-1]
        self.assertEqual(last["path"], "/v1/images/edits")
        self.assertIn(b'name="image[]"; filename="hero.png"', last["body"])

    def test_a_refused_scene_is_reported_and_the_rest_kept(self):
        prompts = [{"id": "ok", "prompt": "a cat"}, {"id": "no", "prompt": "REFUSE this"}]
        _, response = self.generate(prompts=prompts)
        self.assert_pictures(response["result"], ["ok"])
        self.assertEqual(response["result"]["failed"], [{"id": "no", "message": "prompt refused"}])

    def test_missing_or_refused_key_stops_the_batch(self):
        _, response = self.generate(key="")
        self.assertIn("API key", response["error"]["message"])
        self.assertEqual(self.service.requests, [])
        _, response = self.generate(key="bad")
        self.assertIn("refused the key", response["error"]["message"])
        self.assertEqual(len(self.service.requests), 1)

    def test_bad_requests_are_refused(self):
        _, response = self.generate(prompts=[{"id": "x"}])
        self.assertIn("prompts", response["error"]["message"])
        _, response = self.generate(references=["/nonexistent/ref.png"])
        self.assertIn("Reference picture not found", response["error"]["message"])


if __name__ == "__main__":
    unittest.main()
