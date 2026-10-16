"""Tests for Translate Captions: run the entrypoint the way BashCut does, answering its host calls with fixtures and
its translation calls with a local OpenAI-compatible server.

    python3 -m unittest discover -s tests -v

Build first when the plugin has a build.sh. These tests use only the Python standard library and are not shipped.
"""
import json
import os
import pathlib
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

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


class ManifestTests(unittest.TestCase):
    def test_entrypoint_is_executable(self):
        self.assertTrue(os.access(ENTRYPOINT, os.X_OK), f"{ENTRYPOINT} is missing or not executable (build first?)")

    def test_unknown_method_is_an_error(self):
        with tempfile.TemporaryDirectory() as folder:
            response = call(folder, "nope.nothing", {})
        self.assertIn("error", response)


CAPTIONS = [
    {"id": f"cap{i}", "at": i * 60, "dur": 50, "text": f"Line number {i}", "textStyle": {"size": 0.05}}
    for i in range(45)
]
CAPTIONS[0]["words"] = [{"text": "Line", "at": 0, "dur": 10}]


def context(tracks=None, plugin_data=None):
    return {"app": {"apiVersion": MANIFEST["apiVersion"], "language": "en"}, "author": "user",
            "project": {"rev": 7, "fps": [30, 1]}, "playhead": 0, "pluginData": plugin_data,
            "tracks": tracks if tracks is not None else [{"id": "t1", "kind": "text", "role": "captions", "items": CAPTIONS}]}


class TranslationServer:
    """An OpenAI-compatible /v1/chat/completions that answers "<target> <text>" for each line, and records calls."""

    def __init__(self, drop=(), fence=False):
        self.calls = []
        server = self

        class Handler(BaseHTTPRequestHandler):
            def answer(self, status, payload):
                data = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                server.calls.append({"path": self.path, "auth": self.headers.get("Authorization")})
                self.answer(200, {"data": [{"id": "gpt-5-mini"}, {"id": "text-embedding-3-small"}, {"id": "local-model"}]})

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                server.calls.append({"path": self.path, "auth": self.headers.get("Authorization"), "body": body})
                if body["model"] == "missing-model":
                    return self.answer(404, {"error": {"message": "The model `missing-model` does not exist"}})
                lines = json.loads(body["messages"][1]["content"])["lines"]
                answer = {"lines": [{"id": line["id"], "text": "VI " + line["text"]} for line in lines
                                    if not (line["id"] in drop and len(server.calls) == 1)]}
                text = json.dumps(answer)
                if fence:
                    text = "```json\n" + text + "\n```"
                data = json.dumps({"choices": [{"message": {"content": text}}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):
                pass

        self.httpd = HTTPServer(("127.0.0.1", 0), Handler)
        self.endpoint = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def brief_host(call):
    if call["method"] == "project.data":
        return {"result": {"key": "brief", "value": {"goal": "Vietsub of a drama about Manman"}}}
    return {"error": {"code": "unexpected", "message": call["method"]}}


class TranslateTests(unittest.TestCase):
    def test_a_missing_model_lists_the_ones_the_service_has(self):
        server = TranslationServer()
        try:
            error = self.translate(options={"service": "openai", "endpoint": server.endpoint, "model": "custom",
                                            "customModel": "missing-model"})[1]["error"]
        finally:
            server.close()
        self.assertEqual(error["code"], "model_missing")
        self.assertIn("gpt-5-mini, local-model", error["message"])
        self.assertNotIn("embedding", error["message"])

    def test_a_model_of_the_other_service_is_refused(self):
        error = self.translate(options={"service": "gemini", "apiKey": "k", "model": "gpt-5-mini"})[1]["error"]
        self.assertEqual(error["code"], "wrong_model")

    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def translate(self, params=None, options=None, tracks=None, on_call=brief_host):
        session = Session(self.folder)
        try:
            return session.request("r1", "plugin.action", {
                "action": "bashcut.translate-captions.translate", "params": params or {"target": "vi"},
                "options": options or {}, "context": context(tracks), "outputDirectory": self.folder}, on_call=on_call)
        finally:
            session.close()

    def test_without_a_key_it_points_at_the_agent(self):
        error = self.translate(options={"service": "gemini"})[1]["error"]
        self.assertEqual(error["code"], "no_key")
        self.assertIn("agent", error["message"])

    def test_no_captions_is_an_error(self):
        server = TranslationServer()
        try:
            reply = self.translate(options={"service": "openai", "endpoint": server.endpoint}, tracks=[])[1]
        finally:
            server.close()
        self.assertEqual(reply["error"]["code"], "no_captions")

    def test_translates_every_caption_in_batches_and_keeps_timing(self):
        server = TranslationServer()
        try:
            lines, reply = self.translate(
                params={"target": "vi", "glossary": "Manman; grizzly = gấu xám", "maxCps": 15},
                options={"service": "openai", "endpoint": server.endpoint, "model": "local-model"})
        finally:
            server.close()
        result = reply["result"]
        self.assertEqual(result["baseRev"], 7)
        operations = result["operations"]
        self.assertEqual(len(operations), 45)
        self.assertEqual({op["op"] for op in operations}, {"setProperties"})
        self.assertEqual(operations[3], {"op": "setProperties", "item": "cap3", "patch": {"text": "VI Line number 3"}})
        # Word timings belong to the old words.
        self.assertEqual(operations[0]["patch"], {"text": "VI Line number 0", "words": None})
        self.assertEqual(len(server.calls), 2, "45 lines go in batches of 40")
        first = server.calls[0]["body"]
        self.assertEqual(first["model"], "local-model")
        self.assertNotIn("temperature", first, "GPT-5 models refuse a temperature")
        self.assertIsNone(server.calls[0]["auth"], "a local server gets no key")
        system, user = first["messages"][0]["content"], json.loads(first["messages"][1]["content"])
        self.assertIn("Vietnamese", system)
        self.assertIn("- grizzly = gấu xám", system)
        self.assertIn("Manman", system)
        self.assertIn("Vietsub of a drama", system, "the project brief is part of the instructions")
        self.assertEqual(user["lines"][0], {"id": "1", "maxChars": 25, "seconds": 1.7, "text": "Line number 0"})
        second = json.loads(server.calls[1]["body"]["messages"][1]["content"])
        self.assertEqual(second["previousLinesAlreadyTranslated"], ["VI Line number 37", "VI Line number 38", "VI Line number 39"])
        self.assertEqual(result["pluginData"]["translate"]["translated"], 45)
        self.assertTrue(any(line.get("type") == "progress" for line in lines))

    def test_lines_left_out_are_asked_again(self):
        server = TranslationServer(drop={"2", "5"}, fence=True)
        try:
            reply = self.translate(options={"service": "openai", "endpoint": server.endpoint},
                                   tracks=[{"id": "t1", "kind": "text", "role": "captions", "items": CAPTIONS[:6]}])[1]
        finally:
            server.close()
        self.assertEqual(len(reply["result"]["operations"]), 6)
        retry = json.loads(server.calls[1]["body"]["messages"][1]["content"])
        self.assertEqual([line["id"] for line in retry["lines"]], ["2", "5"])


class OptionCheckTests(unittest.TestCase):
    def check(self, value, **options):
        with tempfile.TemporaryDirectory() as folder:
            return call(folder, "options.check", {"option": "apiKey", "value": value, "options": options})["result"]

    def test_an_openai_key_on_gemini_is_refused_without_calling_the_service(self):
        result = self.check("sk-proj-abc", service="gemini")
        self.assertFalse(result["ok"])
        self.assertIn("OpenAI key", result["message"])

    def test_a_short_gemini_key_is_refused(self):
        result = self.check("abcdef", service="gemini")
        self.assertFalse(result["ok"])
        self.assertIn("39 characters; this one has 6", result["message"])

    def test_a_key_the_service_lists_models_for_is_accepted(self):
        server = TranslationServer()
        try:
            result = self.check("sk-good", service="openai", endpoint=server.endpoint)
        finally:
            server.close()
        self.assertEqual(result, {"ok": True, "message": "OpenAI accepts the key (2 text models)"})
        self.assertEqual(server.calls[0]["auth"], "Bearer sk-good")

    def test_other_options_are_not_checked(self):
        with tempfile.TemporaryDirectory() as folder:
            result = call(folder, "options.check", {"option": "model", "value": "x", "options": {}})["result"]
        self.assertEqual(result, {"ok": True})


def ocr_frames(subtitles=True, logo=True, low=0.82):
    frames = []
    for second in range(30):
        texts = []
        if logo:
            texts.append({"box": [0.78, 0.03, 0.18, 0.04], "confidence": 1, "string": "DRAMA TV"})
        if subtitles and second % 5 != 4:
            texts.append({"box": [0.2, low, 0.6, 0.04], "confidence": 1, "string": f"Sentence {second // 2} here"})
            if second % 3 == 0:
                texts.append({"box": [0.3, low + 0.045, 0.4, 0.04], "confidence": 1, "string": "second line"})
        texts.append({"box": [0.3, 0.45, 0.4, 0.05], "confidence": 1, "string": "WELCOME"} if second < 3 else None)
        frames.append({"seconds": second, "frame": second * 30, "text": [t for t in texts if t]})
    return frames


class CoverHost:
    """Answers the host calls of the cover action: a 1080×1920 project with one portrait clip that fills it."""

    def __init__(self, frames, source=(1080, 1920), base_scale=1.0, transform=None):
        clip = {"id": "clip1", "at": 0, "dur": 900, "in": 0, "media": "m1"}
        if transform:
            clip["transform"] = transform
        self.tracks = [
            {"id": "v1", "kind": "video", "role": "main", "items": [clip]},
            {"id": "v2", "kind": "video", "role": "overlay", "items": [{"id": "old-band", "at": 0, "dur": 900, "media": "b0"}]},
            {"id": "t1", "kind": "text", "role": "captions", "items": [
                {"id": "c1", "at": 30, "dur": 60, "text": "Hello", "textStyle": {"size": 0.05, "fill": "#FFFFFF"}},
                {"id": "c2", "at": 1200, "dur": 60, "text": "After the clip"}]},
        ]
        self.timeline = {"rev": 12, "format": {"width": 1080, "height": 1920, "fps": [30, 1]},
                         "media": [{"id": "m1", "kind": "video"}, {"id": "b0", "kind": "image"}], "tracks": self.tracks,
                         "scale": {"clip1": {"baseScale": base_scale, "sourceWidth": source[0], "sourceHeight": source[1]}}}
        self.frames = frames
        self.calls = []

    def __call__(self, call):
        self.calls.append(call)
        method, params = call["method"], call["params"]
        if method == "timeline.get":
            return {"result": self.timeline}
        if method == "media.ocr":
            return {"result": {"job": "ocr1", "state": "running"}}
        if method == "jobs.status":
            return {"result": {"job": {"id": "ocr1", "state": "completed", "result": {"frames": self.frames}}}}
        if method == "media.import":
            self.timeline = dict(self.timeline, rev=self.timeline["rev"] + 1)
            return {"result": {"media": f"band{len([c for c in self.calls if c['method'] == 'media.import'])}"}}
        return {"error": {"code": "unexpected", "message": method}}


class CoverTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def cover(self, host, params=None, plugin_data=None):
        session = Session(self.folder)
        try:
            return session.request("r1", "plugin.action", {
                "action": "bashcut.translate-captions.cover", "params": params or {}, "options": {},
                "context": context([], plugin_data), "outputDirectory": self.folder}, on_call=host)[1]
        finally:
            session.close()

    def test_band_over_moving_subtitles_and_captions_on_it(self):
        host = CoverHost(ocr_frames(), source=(720, 1280), base_scale=1.5)
        result = self.cover(host, plugin_data={"cover": {"items": ["old-band", "gone"]}})["result"]
        video = result["data"]["videos"][0]
        self.assertEqual(video["subtitles"]["box"][1], 0.82)
        self.assertEqual(video["subtitles"]["lines"], 2)
        self.assertEqual(video["fixedText"], ["DRAMA TV"], "text in every picture is not a subtitle")
        self.assertNotIn("WELCOME", json.dumps(video["subtitles"]), "a sign in the middle is not a subtitle")
        self.assertEqual(result["baseRev"], 13, "planned against the revision after the import")
        ops = result["operations"]
        self.assertEqual(ops[0], {"op": "delete", "item": "old-band"}, "an earlier band is replaced; a missing one ignored")
        insert = next(op for op in ops if op["op"] == "insert")
        self.assertEqual(insert["track"], "v2")
        self.assertEqual((insert["item"]["media"], insert["item"]["at"], insert["item"]["dur"]), ("band1", 0, 900))
        moved = [op for op in ops if op["op"] == "setProperties"]
        self.assertEqual([op["item"] for op in moved], ["c1"], "only captions over the covered clip move")
        style = moved[0]["patch"]["textStyle"]
        self.assertEqual((style["size"], style["fill"]), (0.05, "#FFFFFF"), "the rest of the style is kept")
        self.assertTrue(0.05 < style["positionY"] < 0.2)
        self.assertEqual(result["pluginData"]["cover"]["items"], [insert["item"]["id"]])
        self.assertEqual(len(result["files"]), 1)
        self.assertTrue(os.path.exists(result["files"][0]))
        ocr = next(call for call in host.calls if call["method"] == "media.ocr")["params"]
        self.assertEqual((ocr["media"], ocr["from"], ocr["to"]), ("m1", 0, 30))

    def test_band_picture_is_dark_where_the_subtitles_are(self):
        import struct, zlib
        host = CoverHost(ocr_frames(logo=False))
        result = self.cover(host, {"mode": "band"})["result"]
        alpha = png_alpha(result["files"][0])
        self.assertEqual(alpha(540, int(1920 * 0.84)), 255)
        self.assertEqual(alpha(540, int(1920 * 0.5)), 0)
        self.assertEqual(alpha(540, 40), 0)

    def test_no_subtitles(self):
        host = CoverHost(ocr_frames(subtitles=False))
        result = self.cover(host)["result"]
        self.assertNotIn("operations", result)
        self.assertIn("No burned-in subtitles", result["message"])
        self.assertIsNone(result["data"]["videos"][0]["subtitles"])

    def test_detect_only_changes_nothing(self):
        result = self.cover(CoverHost(ocr_frames()), {"mode": "detect"})["result"]
        self.assertNotIn("operations", result)
        self.assertEqual(result["pluginData"]["detect"]["videos"][0]["subtitles"]["lines"], 2)

    def test_low_subtitles_on_a_full_frame_picture_are_zoomed_out(self):
        host = CoverHost(ocr_frames(logo=False, low=0.92))
        result = self.cover(host, {"mode": "auto"})["result"]
        self.assertEqual(result["data"]["zoomed"], 1)
        zoom = next(op for op in result["operations"] if op["op"] == "setProperties" and op["item"] == "clip1")
        transform = zoom["patch"]["transform"]
        self.assertTrue(1 < transform["zoom"] <= 1.12)
        # Picture share 0.92 - padding lands on the frame's bottom, the top stays at the top: tilt is down (negative).
        self.assertLess(transform["tilt"], 0)
        self.assertFalse(any(op["op"] == "insert" for op in result["operations"]))

    def test_band_when_the_zoom_would_be_too_big(self):
        result = self.cover(CoverHost(ocr_frames(logo=False, low=0.7)), {"mode": "zoom"})["result"]
        self.assertEqual(result["data"]["zoomed"], 0)
        self.assertEqual(len(result["data"]["bands"]), 1)

    def test_fixed_text_is_covered_only_when_asked(self):
        host = CoverHost(ocr_frames(subtitles=False))
        result = self.cover(host, {"coverLogos": True})["result"]
        self.assertEqual(len(result["data"]["bands"]), 1)
        alpha = png_alpha(result["files"][0])
        self.assertEqual(alpha(int(1080 * 0.87), int(1920 * 0.05)), 255, "the logo is covered")
        self.assertEqual(alpha(540, int(1920 * 0.84)), 0, "no subtitle band without subtitles")


def png_alpha(path):
    """A reader of the alpha of an 8-bit RGBA PNG without filters beyond the five standard ones."""
    import struct, zlib
    data = pathlib.Path(path).read_bytes()
    width, height = struct.unpack(">II", data[16:24])
    chunks, at = b"", 8
    while at < len(data):
        length, kind = struct.unpack(">I4s", data[at:at + 8])
        if kind == b"IDAT":
            chunks += data[at + 8:at + 8 + length]
        at += 12 + length
    raw, stride, rows, previous = zlib.decompress(chunks), width * 4, [], bytearray(width * 4)
    for y in range(height):
        kind, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for x in range(stride):
            left = line[x - 4] if x >= 4 else 0
            up, corner = previous[x], previous[x - 4] if x >= 4 else 0
            if kind == 1: line[x] = (line[x] + left) & 255
            elif kind == 2: line[x] = (line[x] + up) & 255
            elif kind == 3: line[x] = (line[x] + (left + up) // 2) & 255
            elif kind == 4:
                p = left + up - corner
                pa, pb, pc = abs(p - left), abs(p - up), abs(p - corner)
                line[x] = (line[x] + (left if pa <= pb and pa <= pc else up if pb <= pc else corner)) & 255
        rows.append(line)
        previous = line
    return lambda x, y: rows[y][x * 4 + 3]


class PresetTests(unittest.TestCase):
    def test_saves_the_vietsub_preset_in_the_batch_store(self):
        with tempfile.TemporaryDirectory() as folder:
            env = environment(folder)
            env["HOME"] = folder
            request = {"id": "r1", "apiVersion": MANIFEST["apiVersion"], "method": "plugin.action", "params": {
                "action": "bashcut.translate-captions.install-preset", "params": {}, "options": {}, "context": context()}}
            out = subprocess.run([str(ENTRYPOINT), "rpc"], input=json.dumps(request) + "\n", capture_output=True,
                                 text=True, cwd=ROOT, env=env, timeout=60)
            result = json.loads(out.stdout)["result"]
            saved = pathlib.Path(folder, "Library/Application Support/BashCut/Batch/Presets/vietsub-tiktok.json")
            pipeline = json.loads(saved.read_text())
        self.assertEqual(result["data"]["preset"], "Vietsub TikTok")
        self.assertEqual(pipeline["name"], "Vietsub TikTok")
        actions = [step["action"] for step in pipeline["steps"]]
        self.assertEqual(actions, ["media.import", "captions.generate", "captions.style", "bashcut.translate-captions.cover",
                                   "bashcut.translate-captions.translate", "review.run", "export"])
        self.assertEqual(pipeline["template"]["outputs"], ["tiktok", "shorts"])
        self.assertNotIn("language", pipeline["template"], "Whisper detects the spoken language")
        # What BashCut's BatchPipeline needs to read a saved preset.
        self.assertEqual(pipeline["inputs"], [])
        self.assertTrue(all(isinstance(step["params"], dict) for step in pipeline["steps"]))


if __name__ == "__main__":
    unittest.main()
