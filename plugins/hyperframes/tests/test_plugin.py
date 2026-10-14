"""Smoke tests for HyperFrames Graphics: run the entrypoint the way BashCut does, with sample requests.

    python3 -m unittest discover -s tests -v

Build first when the plugin has a build.sh. These tests use only the Python standard library and are not shipped.
"""
import hashlib
import json
import math
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

    def __init__(self, folder, features=None):
        self.process = subprocess.Popen([str(ENTRYPOINT), "session"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, text=True, cwd=ROOT, env=environment(folder))
        hello = {"type": "hello", "apiVersion": MANIFEST["apiVersion"], "host": "BashCut", "pluginId": MANIFEST["id"]}
        if features is not None:
            hello["features"] = features
        self.send(hello)
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

    def test_places_are_measured_on_the_sphere_minus_holes(self):
        script = (
            "import('" + (ROOT / "lib" / "osm-map.mjs").as_uri() + "').then(({measure}) => {"
            "const sq = (a, b) => [[a, a], [b, a], [b, b], [a, b], [a, a]];"
            "const lake = measure({type: 'Polygon', coordinates: [sq(0, 0.01)]});"
            "const ring = measure({type: 'Polygon', coordinates: [sq(0, 0.01), sq(0.004, 0.006)]});"
            "const road = measure({type: 'LineString', coordinates: [[0, 0], [0, 0.01]]});"
            "console.log(JSON.stringify({lake, ring, road}));})")
        with tempfile.TemporaryDirectory() as folder:
            node = subprocess.run([str(ROOT / "bin" / "find-node")], capture_output=True, text=True,
                                  env=environment(folder)).stdout.strip()
            if not node:
                self.skipTest("Node.js is not installed")
            out = subprocess.run([node, "--input-type=module", "-e", script], capture_output=True, text=True, timeout=30)
        self.assertEqual(0, out.returncode, out.stderr)
        result = json.loads(out.stdout)
        side = 6371008.8 * 3.141592653589793 / 180 * 0.01  # metres in 0.01° at the equator
        self.assertAlmostEqual(side * side, result["lake"]["areaM2"], delta=side * side * 0.001)
        self.assertAlmostEqual(result["lake"]["areaM2"] * (1 - 0.04), result["ring"]["areaM2"], delta=side * side * 0.001)
        self.assertAlmostEqual(4 * side / 1000, result["lake"]["perimeterKm"], places=3)
        self.assertIsNone(result["road"]["areaM2"])

    def test_places_alone_need_no_folder(self):
        out = self.run_map("--places", "")
        self.assertIn("--dir", out.stderr, "an empty --places is no places")

    def run_module(self, body):
        """`body` run with osm-map.mjs's exports in scope; returns what it prints as JSON."""
        script = "import('" + (ROOT / "lib" / "osm-map.mjs").as_uri() + "').then((m) => {" + body + "})"
        with tempfile.TemporaryDirectory() as folder:
            node = subprocess.run([str(ROOT / "bin" / "find-node")], capture_output=True, text=True,
                                  env=environment(folder)).stdout.strip()
            if not node:
                self.skipTest("Node.js is not installed")
            out = subprocess.run([node, "--input-type=module", "-e", script], capture_output=True, text=True, timeout=30,
                                 env=environment(folder))
        self.assertEqual(0, out.returncode, out.stderr)
        return json.loads(out.stdout)

    # Around 21.0655,105.8255: 0.001° of latitude is ~111 m.
    PLACES = [
        {"type": "node", "id": 1, "lat": 21.0662, "lon": 105.8255, "tags": {"amenity": "school", "name": "Quang An"}},
        {"type": "way", "id": 2, "center": {"lat": 21.0663, "lon": 105.8256},
         "tags": {"amenity": "school", "name": "Quang An"}},
        {"type": "way", "id": 3, "center": {"lat": 21.0700, "lon": 105.8255}, "tags": {"amenity": "kindergarten"}},
        {"type": "node", "id": 4, "lat": 21.0800, "lon": 105.8255, "tags": {"amenity": "school", "name": "Far"}},
        {"type": "way", "id": 5, "center": {"lat": 21.0630, "lon": 105.8255}, "tags": {"leisure": "park"}},
        {"type": "relation", "id": 6, "center": {"lat": 21.0600, "lon": 105.8255},
         "tags": {"leisure": "park", "name": "Lakeside"}},
        {"type": "node", "id": 7, "lat": 21.0656, "lon": 105.8255, "tags": {"amenity": "cafe", "name": "Not asked"}},
    ]

    def test_one_overpass_query_asks_for_every_kind_around_the_point(self):
        query = self.run_module("console.log(JSON.stringify(m.overpassQuery(['school', 'park', 'hospital'],"
                                " {lat: 21.0655, lon: 105.8255}, 1000)));")
        self.assertEqual(1, query.count("out center"), "one query for all kinds")
        self.assertIn('nwr["amenity"~"^(school)$"](around:1000,21.06550,105.82550);', query)
        self.assertIn('nwr["leisure"~"^(park)$"]', query)
        self.assertIn('nwr["healthcare"~"^(hospital)$"]', query)
        self.assertTrue(query.startswith("[out:json][timeout:"), query)

    def test_amenities_are_counted_inside_the_radius_and_the_nearest_named(self):
        result = self.run_module(
            "const r = m.countAmenities(" + json.dumps(self.PLACES) + ", ['school', 'park', 'hospital'],"
            " {lat: 21.0655, lon: 105.8255}, 1000); console.log(JSON.stringify(r));")
        kinds = {k["kind"]: k for k in result["kinds"]}
        self.assertEqual(1, kinds["school"]["count"], "the same name twice within 300 m is one place; Far is out")
        self.assertEqual("Quang An", kinds["school"]["nearest"]["name"])
        self.assertAlmostEqual(0.08, kinds["school"]["nearest"]["km"], delta=0.01)
        self.assertEqual(2, kinds["park"]["count"], "a way or relation counts by its centre")
        self.assertEqual("Lakeside", kinds["park"]["nearest"]["name"], "the nearest named one, past an unnamed park")
        self.assertEqual({"kind": "hospital", "count": 0, "nearest": None}, kinds["hospital"])
        self.assertEqual(["school", "park", "park"], [marker["kind"] for marker in result["markers"]])
        self.assertNotIn("Not asked", json.dumps(result), "kinds not asked for are left out")

    def test_amenity_tags_are_strict_and_a_clinic_tagged_hospital_counts_as_clinic(self):
        tags = {
            "sos": {"amenity": "hospital", "healthcare": "hospital", "name": "Phòng Khám Y Tế Nha Khoa Quốc Tế SOS"},
            "general": {"amenity": "hospital", "name": "Bệnh viện Đa khoa Hồng Ngọc"},
            "dentist": {"amenity": "hospital", "healthcare": "dentist", "name": "Smile"},
            "dental speciality": {"healthcare": "hospital", "healthcare:speciality": "orthodontics;dentistry"},
            "pharmacy": {"amenity": "pharmacy", "healthcare": "pharmacy"},
            "school": {"amenity": "school", "name": "Trường THPT chuyên Ngoại ngữ"},
            "language centre": {"amenity": "school", "name": "Trung tâm Anh ngữ ILA"},
            "driving": {"amenity": "school", "name": "Trường dạy lái xe Hà Nội"},
            "mall": {"shop": "department_store"},
            "supermarket": {"shop": "supermarket"},
            "park": {"leisure": "park"},
            "private park": {"leisure": "park", "access": "private"},
            "garden": {"leisure": "garden"},
            "playground": {"leisure": "playground"},
        }
        kinds = ["hospital", "clinic", "pharmacy", "school", "language_school", "driving_school", "mall", "supermarket",
                 "park", "playground"]
        found = self.run_module("const tags = " + json.dumps(tags) + "; const kinds = " + json.dumps(kinds) + ";"
                                "console.log(JSON.stringify(Object.fromEntries(Object.entries(tags)"
                                ".map(([k, t]) => [k, kinds.filter((kind) => m.isKind(t, kind))]))));")
        self.assertEqual({
            "sos": ["clinic"], "general": ["hospital"], "dentist": ["clinic"], "dental speciality": ["clinic"],
            "pharmacy": ["pharmacy"], "school": ["school"], "language centre": ["language_school"],
            "driving": ["driving_school"], "mall": ["mall"], "supermarket": ["supermarket"], "park": ["park"],
            "private park": [], "garden": [], "playground": ["playground"],
        }, found)
        query = self.run_module("console.log(JSON.stringify(m.overpassQuery(['clinic'], {lat: 21, lon: 105}, 500)));")
        self.assertIn('nwr["amenity"~"^(hospital)$"]', query, "clinic also asks for places tagged hospital")
        query = self.run_module("console.log(JSON.stringify(m.overpassQuery(['hospital'], {lat: 21, lon: 105}, 500)));")
        self.assertNotIn("clinic", query)

    def test_a_dental_clinic_tagged_hospital_is_not_counted_as_a_hospital(self):
        places = [{"type": "way", "id": 9, "center": {"lat": 21.0680, "lon": 105.8255},
                   "tags": {"amenity": "hospital", "healthcare": "hospital", "name": "Nha Khoa SOS"}}]
        result = self.run_module("const r = m.countAmenities(" + json.dumps(places) + ", ['hospital', 'clinic'],"
                                 " {lat: 21.0655, lon: 105.8255}, 1000); console.log(JSON.stringify(r));")
        self.assertEqual([("hospital", 0), ("clinic", 1)], [(k["kind"], k["count"]) for k in result["kinds"]])
        self.assertEqual(["clinic"], [marker["kind"] for marker in result["markers"]])

    def test_amenity_markers_land_on_canvas_pixels(self):
        result = self.run_module(
            "const centre = {lat: 21.0655, lon: 105.8255, label: 'Home'};"
            "const local = ([x, y]) => [x - 1000, y - 2000];"
            "const r = m.placeAmenities([{lat: 21.0655, lon: 105.8355, kind: 'park', name: 'East', km: 1.04}],"
            " centre, 1000, 15, local);"
            "console.log(JSON.stringify(r));")
        scale = 256 * 2 ** 15
        x = (105.8255 + 180) / 360 * scale - 1000
        mpp = 2 * math.pi * 6378137 * math.cos(math.radians(21.0655)) / scale
        self.assertAlmostEqual(x, result["centre"]["x"], places=3)
        self.assertEqual("Home", result["centre"]["label"])
        self.assertAlmostEqual(1000 / mpp, result["radius"], delta=0.1)
        marker = result["markers"][0]
        self.assertAlmostEqual(0.01 / 360 * scale, marker["x"] - result["centre"]["x"], places=3)
        self.assertAlmostEqual(result["centre"]["y"], marker["y"], places=6)
        self.assertEqual({"kind": "park", "name": "East", "km": 1.04}, {k: marker[k] for k in ("kind", "name", "km")})

    def test_a_route_line_is_cut_into_one_line_per_leg(self):
        legs = self.run_module(
            "console.log(JSON.stringify(m.splitLine([[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]],"
            " [{lat: 0, lon: 0}, {lat: 0.1, lon: 2.1}, {lat: 0, lon: 4}])));")
        self.assertEqual([[[0, 0], [0, 1], [0, 2]], [[0, 2], [0, 3], [0, 4]]], legs)

    def test_rejects_unknown_amenities_a_bad_radius_and_a_bad_leg_shape(self):
        out = self.run_map("--points", "21.03,105.83,A", "--amenities", "school,spaceport")
        self.assertEqual(2, out.returncode, out.stderr)
        self.assertIn("spaceport", out.stderr)
        self.assertIn("hospital", out.stderr, "the error lists the kinds there are")
        out = self.run_map("--points", "21.03,105.83,A", "--amenities", "school", "--radius", "20000")
        self.assertEqual(2, out.returncode, out.stderr)
        self.assertIn("--radius", out.stderr)
        with tempfile.TemporaryDirectory() as target:
            out = self.run_map("--dir", target, "--points", "21.03,105.83,A;21.04,105.84,B", "--legs", "ring")
        self.assertEqual(2, out.returncode, out.stderr)
        self.assertIn("--legs", out.stderr)

    def test_amenities_print_counts_from_the_cache_without_the_network(self):
        query = self.run_module("console.log(JSON.stringify(m.overpassQuery(['school', 'park'],"
                                " {lat: 21.0655, lon: 105.8255}, 1000)));")
        with tempfile.TemporaryDirectory() as folder:
            env = environment(folder)
            cached = pathlib.Path(env["BASHCUT_PLUGIN_CACHE"], "osm-amenities")
            cached.mkdir(parents=True)
            name = hashlib.sha256(query.encode()).hexdigest()[:20] + ".json"
            (cached / name).write_text(json.dumps(self.PLACES))
            env["OSM_OVERPASS_URL"] = "http://127.0.0.1:9/api/interpreter"  # nothing listens: a cache miss would fail
            out = subprocess.run([str(ROOT / "bin" / "osm-map"), "--points", "21.0655,105.8255,Home",
                                  "--amenities", "school,park", "--radius", "1000"],
                                 capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(0, out.returncode, out.stderr)
        result = json.loads(out.stdout)
        self.assertEqual([("school", 1), ("park", 2)],
                         [(k["kind"], k["count"]) for k in result["amenities"]["kinds"]])
        self.assertEqual("Home", result["amenities"]["centre"]["label"])
        self.assertIn("OpenStreetMap", result["attribution"])

    def test_amenity_radius_reads_the_data_osm_map_writes(self):
        html = (ROOT / "examples" / "amenity-radius" / "index.html").read_text()
        self.assertIn('<script src="map-data.js"></script>', html)
        self.assertIn("data.attribution", html)
        self.assertIn('data-fit="canvas"', html)
        stand_in = (ROOT / "examples" / "amenity-radius" / "map-data.js").read_text()
        self.assertIn("© OpenStreetMap contributors", stand_in)
        data = json.loads(stand_in[stand_in.index("{"):stand_in.rindex("}") + 1])
        self.assertTrue(data["amenities"]["markers"] and data["amenities"]["radius"] > 0)
        self.assertTrue(all(len(leg["line"]) > 1 for leg in data["legs"]))

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

    def test_lottie_web_is_copied_next_to_a_page_that_loads_it(self):
        data, cache = pathlib.Path(self.folder, "data"), pathlib.Path(self.folder, "cache")
        modules = data / "runtime" / "node_modules"
        for path, text in [(modules / "hyperframes/bin/hyperframes.mjs", "process.exit(1);\n"), (cache / "chrome/path", "/no/chrome"),
                           (modules / "gsap/dist/gsap.min.js", "// gsap\n")]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        composition = pathlib.Path(self.folder, "accent")
        shutil.copytree(ROOT / "examples" / "lottie", composition)
        response = self.render({"composition": str(composition)})
        self.assertEqual("dependency_missing", response["error"]["code"])
        self.assertIn("lottie-web", response["error"]["message"])
        player = modules / "lottie-web/build/player/lottie_svg.min.js"
        player.parent.mkdir(parents=True)
        player.write_text("// lottie\n")
        response = self.render({"composition": str(composition)})
        self.assertEqual("render_failed", response["error"]["code"])  # the fake CLI cannot render
        self.assertEqual("// lottie\n", (composition / "lottie.min.js").read_text())


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
    import re
    page = os.path.join(entry["params"]["composition"], "index.html")
    if os.path.exists(page):
        found = re.search(r'data-composition-id="main"[^>]*data-duration="([\d.]+)"', open(page).read())
        entry["pageDuration"] = float(found.group(1)) if found else None
        sized = re.search(r'data-composition-id="main"[^>]*data-width="(\d+)" data-height="(\d+)"', open(page).read())
        entry["pageSize"] = [int(sized.group(1)), int(sized.group(2))] if sized else None
        framed = re.search(r'\(function build\(frame\)[\s\S]*?\}\)\((\{.*?\})\);</script>', open(page).read())
        entry["pageFrame"] = json.loads(framed.group(1)) if framed else None
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
elif command == "knowledge lessons":
    out = state.get("lessons", [])
elif command == "fonts list":
    out = state.get("fonts", [])
elif command == "context get":
    out = {"project": state.get("projectFile"), "rev": 7}
elif command == "plan check":
    out = state["check"]
elif command == "media import":
    out = {"media": "media-" + os.path.basename(args[2]).split(".")[0], "rev": 9}
elif command == "plan apply":
    entry["patch"] = json.loads(option("--patch")) if option("--patch") else None
    out = {"ok": True, "rev": 11, "clips": 0}
elif command == "library get":
    file = state.get("files", {}).get(args[2]) or state.get("logo")
    out = {"id": args[2], "kind": "sticker", "fileURL": "file://" + file} if file else {"id": args[2]}
else:
    out = {}
state.setdefault("calls", []).append(entry)
json.dump(state, open(state_path, "w"))
print(json.dumps(out))
"""


class InspectorViewTests(unittest.TestCase):
    """The Inspector view "graphic": fields for a graphic this plugin rendered, nothing for other items."""

    def view(self, folder, media, values=None, event=None, features=None):
        """Without features: an older BashCut (one-shot, no hello features). With them: a session whose hello lists
        them, as BashCut sends it."""
        params = {"view": "graphic", "context": {"selection": {"id": "item-1"}, "media": media},
                  "values": values or {}, "state": None}
        if event:
            params["event"] = event
        method = "view.event" if event else "view.render"
        if features is None:
            return rpc(folder, method, params)["result"]
        session = Session(folder, features)
        try:
            return session.request("v1", method, params)[1]["result"]
        finally:
            session.close()

    def graphic_media(self, folder, variables):
        composition = pathlib.Path(folder, "graphics", "lower-third")
        shutil.copytree(ROOT / "examples" / "lower-third", composition, dirs_exist_ok=True)
        return {"id": "m1", "data": {"graphics": {"composition": str(composition), "name": "lower-third",
                                                  "variables": variables}}}

    @staticmethod
    def nodes(body):
        return {n.get("id"): n for n in body + [c for n in body for c in n.get("children", [])] if n.get("id")}

    def test_other_items_get_an_empty_view(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual([], self.view(folder, {"id": "m1", "kind": "video"})["body"])

    def test_a_rendered_graphic_shows_its_variables_and_a_render_button(self):
        with tempfile.TemporaryDirectory() as folder:
            composition = pathlib.Path(folder, "graphics", "lower-third")
            shutil.copytree(ROOT / "examples" / "lower-third", composition)
            media = {"id": "m1", "data": {"graphics": {"composition": str(composition), "name": "lower-third",
                                                       "variables": {"name": "Samantha Abrams", "accent": "#FF3B30"}}}}
            body = self.view(folder, media)["body"]
            nodes = {n.get("id"): n for n in body + [c for n in body for c in n.get("children", [])] if n.get("id")}
            self.assertEqual("Samantha Abrams", nodes["name"]["value"])  # the recorded value, not the default
            self.assertEqual("Head roaster", nodes["role"]["value"])  # the declared default
            self.assertEqual("toggle", nodes["glint"]["type"])
            self.assertEqual("#FF3B30", nodes["accent"]["value"])  # look fields sit in their own section
            self.assertEqual("textField", nodes["headingFont"]["type"])  # brand fonts are editable too
            self.assertEqual("textField", nodes["accent"]["type"])  # a BashCut without the pickers gets text fields
            self.assertEqual("button", nodes["render"]["type"])
            clicked = self.view(folder, media, values={"name": "Samantha Abrams"}, event={"node": "render", "type": "click"})
            self.assertIn("Nothing changed.", [n.get("text") for n in clicked["body"]])
            params = {"view": "graphic", "locale": "vi", "context": {"selection": {"id": "item-1"}, "media": media}}
            vietnamese = rpc(folder, "view.render", params)["result"]
            self.assertEqual(("Đồ hoạ", "Render lại"), (vietnamese["title"], vietnamese["body"][-1]["title"]))

    def test_pickers_when_the_host_has_them(self):
        with tempfile.TemporaryDirectory() as folder:
            media = self.graphic_media(folder, {"name": "Samantha Abrams", "accent": "#ff3b30", "headingFont": "Inter"})
            features = ["views", "views.colorPicker", "views.fontPicker"]
            nodes = self.nodes(self.view(folder, media, features=features)["body"])
            self.assertEqual({"type": "colorPicker", "id": "accent", "value": "#ff3b30"},
                             {k: nodes["accent"][k] for k in ("type", "id", "value")})
            self.assertEqual(("fontPicker", "Inter", "family"),
                             (nodes["headingFont"]["type"], nodes["headingFont"]["value"], nodes["headingFont"]["by"]))
            self.assertEqual("fontPicker", nodes["bodyFont"]["type"])
            self.assertEqual("textField", nodes["name"]["type"])
            # Only the colour well: fonts stay text fields on a host that lists one feature and not the other.
            nodes = self.nodes(self.view(folder, media, features=["views.colorPicker"])["body"])
            self.assertEqual(("colorPicker", "textField"), (nodes["accent"]["type"], nodes["headingFont"]["type"]))
            # A hello without the features (an app before them) keeps text fields.
            nodes = self.nodes(self.view(folder, media, features=["views"])["body"])
            self.assertEqual(("textField", "textField"), (nodes["accent"]["type"], nodes["headingFont"]["type"]))

    def test_colour_wells_take_hex_only(self):
        script = ("import('" + (ROOT / "lib" / "inspector.mjs").as_uri() + "').then(({fields, hexColor}) => {"
                  "const declared = [{id: 'accent', type: 'color', default: '#FFF'},"
                  " {id: 'text', type: 'color', default: 'rgba(0,0,0,0.5)'}, {id: 'shade', type: 'color', default: '#11223380'}];"
                  "const body = fields(declared, {variables: {}}, {}, null, {look: 'Look', render: 'Render'},"
                  " new Set(['views.colorPicker']));"
                  "console.log(JSON.stringify({kinds: body.find((n) => n.type === 'section').children.map((n) => [n.type, n.value, n.alpha ?? false]),"
                  " own: body.filter((n) => n.id === 'shade').map((n) => [n.type, n.alpha]), bad: hexColor('red')}));})")
        out = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=60)
        self.assertEqual(0, out.returncode, out.stderr)
        result = json.loads(out.stdout)
        self.assertEqual([["colorPicker", "#FFFFFF", False], ["textField", "rgba(0,0,0,0.5)", False]], result["kinds"])
        self.assertEqual([["colorPicker", True]], result["own"])
        self.assertIsNone(result["bad"])

    def test_picked_colour_in_upper_case_is_not_a_change(self):
        script = ("import('" + (ROOT / "lib" / "inspector.mjs").as_uri() + "').then(({changedVariables}) => {"
                  "const declared = [{id: 'accent', type: 'color', default: '#ff3b30'}, {id: 'text', type: 'color', default: '#fff'}];"
                  "console.log(JSON.stringify(changedVariables(declared, {}, {accent: '#FF3B30', text: '#FFFFFE'})));})")
        out = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=60)
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertEqual({"text": "#FFFFFE"}, json.loads(out.stdout))

    def test_only_edited_fields_are_sent_typed(self):
        script = ("import('" + (ROOT / "lib" / "inspector.mjs").as_uri() + "').then(({changedVariables}) => {"
                  "const declared = [{id: 'name', type: 'string', default: 'A'}, {id: 'bottom', type: 'number', default: 520},"
                  " {id: 'glint', type: 'boolean', default: true}, {id: 'role', type: 'string', default: 'R'}];"
                  "console.log(JSON.stringify(changedVariables(declared, {name: 'B'},"
                  " {name: 'B', bottom: '600', glint: false, role: 'R'})));})")
        out = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=60)
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertEqual({"bottom": 600, "glint": False}, json.loads(out.stdout))


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

    def plan_project(self, media=(), graphics=None):
        project = self.project(media=media)
        project["plan"] = {"cut": {"voiceover": [{"id": "l1", "text": "Năm trăm hai mươi tám héc ta"}],
                                   "graphics": graphics or [{"id": "g1", "on": "l1", "render": {
                                       "composition": "graphics/calendar", "set": {"title": "Hồ Tây", "month": "@hai mươi"}}}]}}
        return project

    def plan_check(self, short=None):
        row = {"id": "g1", "at": 1.0, "seconds": 3.2, "track": "overlay",
               "words": [{"text": "Năm", "at": 0.1}, {"text": "trăm", "at": 0.3}, {"text": "hai", "at": 0.6},
                         {"text": "mươi", "at": 0.8}, {"text": "tám", "at": 1.0}]}
        if short:
            row["short"] = short
        return {"ok": False, "graphics": [row], "problems": [{"id": "graphic-no-media", "entry": "g1"}]}

    def test_plan_renders_each_graphic_to_its_span_and_applies_once(self):
        state = {"projects": [self.plan_project()], "check": self.plan_check(), "projectFile": str(self.folder / "project.bashcut.json")}
        out, calls = self.run_graphic(state, "plan")
        self.assertEqual(0, out.returncode, out.stderr)
        result = json.loads(out.stdout)
        self.assertEqual(["g1"], [r["id"] for r in result["rendered"]])
        invoke = next(c for c in calls if c["args"][:2] == ["plugins", "invoke"])
        params = invoke["params"]
        self.assertEqual(0.6, params["variables"]["month"], "@hai mươi → seconds from the graphic's start")
        self.assertEqual(str(self.composition), params["composition"], "the folder itself, with one root page")
        html = (self.composition / "index.html").read_text()
        self.assertIn('data-duration="5.5"', html, "index.html is put back after the render")
        self.assertFalse((self.composition / ".index.html.plan-original").exists())
        apply = next(c for c in calls if c["args"][:2] == ["plan", "apply"])
        self.assertEqual({"graphics": {"g1": {"media": "media-calendar"}}}, apply["patch"])
        record = next(c for c in calls if c["args"][:2] == ["timeline", "apply"])["ops"][0]
        self.assertEqual("media-calendar", record["media"])
        self.assertEqual(3.2, record["patch"]["graphics"]["seconds"])
        self.assertTrue(record["patch"]["graphics"]["hash"])

    def test_plan_keeps_a_graphic_whose_inputs_did_not_change(self):
        first = {"projects": [self.plan_project()], "check": self.plan_check(), "projectFile": str(self.folder / "p.json")}
        out, calls = self.run_graphic(first, "plan")
        recorded = next(c for c in calls if c["args"][:2] == ["timeline", "apply"])["ops"][0]["patch"]["graphics"]
        media = {"id": "media-calendar", "data": {"graphics": recorded}}
        graphics = [{"id": "g1", "on": "l1", "media": "media-calendar", "render": {
            "composition": "graphics/calendar", "set": {"title": "Hồ Tây", "month": "@hai mươi"}}}]
        again = {"projects": [self.plan_project(media=[media], graphics=graphics)], "check": self.plan_check(),
                 "projectFile": str(self.folder / "p.json")}
        out, calls = self.run_graphic(again, "plan")
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertEqual({"rendered": [], "kept": ["g1"]}, {k: json.loads(out.stdout)[k] for k in ("rendered", "kept")})
        self.assertFalse(any(c["args"][:2] == ["plugins", "invoke"] for c in calls))
        self.assertIsNone(next(c for c in calls if c["args"][:2] == ["plan", "apply"])["patch"])

    def test_plan_refuses_words_that_are_not_said_during_the_graphic(self):
        graphics = [{"id": "g1", "on": "l1", "render": {"composition": "graphics/calendar", "set": {"month": "@mười bảy"}}}]
        state = {"projects": [self.plan_project(graphics=graphics)], "check": self.plan_check(),
                 "projectFile": str(self.folder / "p.json")}
        out, calls = self.run_graphic(state, "plan")
        self.assertEqual(2, out.returncode)
        self.assertIn("mười bảy", json.loads(out.stderr)["error"])
        self.assertFalse(any(c["args"][:2] == ["plugins", "invoke"] for c in calls))

    def test_examples_list_their_own_variables_apart_from_the_brand(self):
        out, calls = self.run_graphic({"projects": [self.project()]}, "examples")
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertLess(len(out.stdout), 9600, "the list is short: one line per example")
        rows = {row["name"]: row for row in json.loads(out.stdout)}
        self.assertEqual(sorted(p.name for p in (ROOT / "examples").iterdir() if (p / "index.html").exists()), sorted(rows))
        self.assertIn("items:string", rows["bar-chart"]["variables"].split())
        self.assertNotIn("accent", rows["bar-chart"]["variables"])
        self.assertTrue(rows["bar-chart"]["about"].endswith("."))
        self.assertEqual([], calls, "no BashCut call")
        out, _ = self.run_graphic({"projects": [self.project()], "fail": "knowledge lessons"}, "examples", "bar-chart")
        row = json.loads(out.stdout)[0]
        self.assertIn("items", [v["id"] for v in row["variables"]])
        self.assertIn("accent", row["brand"])
        self.assertTrue(rows["stat-counter"]["mascot"])
        self.assertNotIn("pose", rows["stat-counter"]["variables"])
        out, _ = self.run_graphic({"projects": [self.project()], "fail": "knowledge lessons"}, "examples", "paper-card")
        row = json.loads(out.stdout)[0]
        self.assertEqual({"mascot", "pose"}, {"mascot", "pose"} & set(row["brand"]))
        self.assertNotIn("pose", [v["id"] for v in row["variables"]])
        out, _ = self.run_graphic({"projects": [self.project()]}, "examples", "nope")
        self.assertEqual(2, out.returncode)

    def test_one_example_carries_its_pitfalls_and_learned_lessons(self):
        lessons = [{"id": "l-1", "title": "Count slower", "fix": "countSeconds 1.6", "check": "Can the number be read?",
                    "tags": ["block:stat-counter"]}]
        out, calls = self.run_graphic({"projects": [self.project()], "lessons": lessons}, "examples", "stat-counter")
        self.assertEqual(0, out.returncode, out.stderr)
        row = json.loads(out.stdout)[0]
        self.assertTrue(row["pitfalls"] and all(isinstance(line, str) for line in row["pitfalls"]))
        self.assertEqual([{"id": "l-1", "title": "Count slower", "fix": "countSeconds 1.6", "check": "Can the number be read?"}],
                         row["lessons"])
        self.assertEqual(["knowledge", "lessons", "--tag", "block:stat-counter", "--status", "active"], calls[0]["args"])
        out, _ = self.run_graphic({"projects": [self.project()], "fail": "knowledge lessons"}, "examples", "stat-counter")
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertNotIn("lessons", json.loads(out.stdout)[0])

    def test_example_exits_follow_the_composition_length(self):
        for page in (ROOT / "examples").glob("*/index.html"):
            html = page.read_text()
            if "tl.to(" in html and "opacity: 0" in html:
                self.assertIn("END - ", html, page.parent.name)

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

    def test_place_renders_a_copy_of_a_plugin_example_in_the_project(self):
        project_file = self.folder / "project" / "project.bashcut.json"
        project_file.parent.mkdir()
        before = sorted(p.name for p in (ROOT / "examples" / "calendar").iterdir())
        state = {"projects": [self.project(), self.project(rev=7)], "projectFile": str(project_file)}
        out, calls = self.run_graphic(state, "place", str(ROOT / "examples" / "calendar"), "--set", "title=Tháng đẹp")
        self.assertEqual(0, out.returncode, out.stderr)
        rendered = pathlib.Path(next(c for c in calls if c["args"][:2] == ["plugins", "invoke"])["params"]["composition"])
        self.assertEqual(project_file.parent / "graphics", rendered.parent)
        self.assertTrue(rendered.name.startswith("calendar-"))
        self.assertTrue((rendered / "index.html").is_file())
        self.assertEqual(before, sorted(p.name for p in (ROOT / "examples" / "calendar").iterdir()))  # plugin untouched
        recorded = next(c for c in calls if c["args"][:2] == ["timeline", "apply"])["ops"][0]["patch"]["graphics"]
        self.assertEqual(str(rendered), recorded["composition"])  # rerender finds the copy after a plugin update

    def test_place_duration_sets_the_composition_length_and_rerender_keeps_it(self):
        page = (self.composition / "index.html").read_text()
        out, calls = self.run_graphic({"projects": [self.project(), self.project(rev=7)]}, "place", str(self.composition),
                                      "--duration", "75")
        self.assertEqual(0, out.returncode, out.stderr)
        invoke = next(c for c in calls if c["args"][:2] == ["plugins", "invoke"])
        self.assertEqual(2.5, invoke["pageDuration"])  # 75 frames at 30 fps, while it rendered
        self.assertEqual(page, (self.composition / "index.html").read_text())  # put back afterwards
        recorded = next(c for c in calls if c["args"][:2] == ["timeline", "apply"])["ops"][0]["patch"]["graphics"]
        self.assertEqual(2.5, recorded["seconds"])
        media = {**self.recorded_media({}), "data": {"graphics": {**self.recorded_media({})["data"]["graphics"], "seconds": 2.5}}}
        item = {"id": "item-1", "at": 0, "dur": 75, "media": "media-old", "sourceIn": 0}
        state = {"projects": [self.project(media=[media], items=[item])]}
        out, calls = self.run_graphic(state, "rerender", "item-1", "--set", "title=Mới")
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertEqual(2.5, next(c for c in calls if c["args"][:2] == ["plugins", "invoke"])["pageDuration"])

    def test_place_draws_the_frame_for_the_render_and_rerender_keeps_it(self):
        page = (self.composition / "index.html").read_text()
        frame = {"backdrop": "texture", "chip": "2/4", "callout": {"text": "*1,54 km*", "at": 1.2}, "scale": 1.3}
        out, calls = self.run_graphic({"projects": [self.project(), self.project(rev=7)]}, "place", str(self.composition),
                                      "--frame", json.dumps(frame))
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertEqual(frame, next(c for c in calls if c["args"][:2] == ["plugins", "invoke"])["pageFrame"])
        self.assertEqual(page, (self.composition / "index.html").read_text())  # put back afterwards
        recorded = next(c for c in calls if c["args"][:2] == ["timeline", "apply"])["ops"][0]["patch"]["graphics"]
        self.assertEqual(frame, recorded["frame"])
        media = {**self.recorded_media({}), "data": {"graphics": {**self.recorded_media({})["data"]["graphics"], "frame": frame}}}
        item = {"id": "item-1", "at": 0, "dur": 165, "media": "media-old", "sourceIn": 0}
        out, calls = self.run_graphic({"projects": [self.project(media=[media], items=[item])]}, "rerender", "item-1",
                                      "--frame", '{"chip": "3/4", "scale": null}')
        self.assertEqual(0, out.returncode, out.stderr)
        drawn = next(c for c in calls if c["args"][:2] == ["plugins", "invoke"])["pageFrame"]
        self.assertEqual({"backdrop": "texture", "chip": "3/4", "callout": {"text": "*1,54 km*", "at": 1.2}}, drawn)

    def test_place_refuses_a_bad_frame_before_rendering(self):
        for frame, words in (('{"chip": "1/4", "border": 2}', "border"), ('{"backdrop": "blur"}', "backdrop"),
                             ('{"scale": 4}', "scale"), ('{"callout": {"text": "x", "at": "@hai"}}', "plan")):
            out, calls = self.run_graphic({"projects": [self.project()]}, "place", str(self.composition), "--frame", frame)
            self.assertEqual(2, out.returncode, frame)
            self.assertIn(words, json.loads(out.stderr)["error"])
            self.assertEqual([], calls)

    def test_plan_frame_lands_its_callout_on_words_and_counts_in_the_hash(self):
        graphics = [{"id": "g1", "on": "l1", "render": {"composition": "graphics/calendar", "set": {"title": "Hồ Tây"},
                                                         "frame": {"chip": "1/4", "callout": {"text": "Hồ *Tây*", "at": "@hai mươi"}}}}]
        state = {"projects": [self.plan_project(graphics=graphics)], "check": self.plan_check(), "projectFile": str(self.folder / "p.json")}
        out, calls = self.run_graphic(state, "plan")
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertEqual({"chip": "1/4", "callout": {"text": "Hồ *Tây*", "at": 0.6}},
                         next(c for c in calls if c["args"][:2] == ["plugins", "invoke"])["pageFrame"])
        recorded = next(c for c in calls if c["args"][:2] == ["timeline", "apply"])["ops"][0]["patch"]["graphics"]
        plain = {"projects": [self.plan_project()], "check": self.plan_check(), "projectFile": str(self.folder / "p.json")}
        _, calls = self.run_graphic(plain, "plan")
        other = next(c for c in calls if c["args"][:2] == ["timeline", "apply"])["ops"][0]["patch"]["graphics"]
        self.assertNotEqual(recorded["hash"], other["hash"])

    def test_place_refuses_an_undeclared_variable_before_rendering(self):
        out, calls = self.run_graphic({"projects": [self.project()]}, "place", str(self.composition), "--set", "colour=#fff")
        self.assertEqual(2, out.returncode)
        self.assertIn("accent", json.loads(out.stderr)["error"])  # lists what it has
        self.assertNotIn("plugins", [call["args"][0] for call in calls])

    def test_plan_takes_an_example_by_name_and_leaves_out_a_brand_id_it_does_not_use(self):
        graphics = [{"id": "g1", "on": "l1", "render": {"composition": "calendar", "set": {
            "title": "Hồ Tây", "disclosure": "Ảnh tạo bằng AI"}, "frame": {"backdrop": "paper", "float": True}}}]
        project_file = self.folder / "project" / "project.bashcut.json"
        project_file.parent.mkdir()
        state = {"projects": [self.plan_project(graphics=graphics)], "check": self.plan_check(), "projectFile": str(project_file)}
        out, calls = self.run_graphic(state, "plan")
        self.assertEqual(0, out.returncode, out.stderr)
        invoke = next(c for c in calls if c["args"][:2] == ["plugins", "invoke"])
        self.assertEqual(project_file.parent / "graphics" / "g1-calendar", pathlib.Path(invoke["params"]["composition"]))
        self.assertNotIn("disclosure", invoke["params"]["variables"])
        self.assertEqual({"backdrop": "paper", "float": True}, invoke["pageFrame"])
        self.assertTrue(any("disclosure" in w for w in json.loads(out.stdout)["warnings"]))

    def test_runs_through_a_symlinked_plugin_folder(self):
        link = self.folder / "linked-plugin"
        link.symlink_to(ROOT)
        out = subprocess.run([str(link / "bin" / "graphic"), "draw"], capture_output=True, text=True,
                             env=environment(self.folder), timeout=60)
        self.assertEqual(2, out.returncode, out.stderr)  # it ran (usage error) instead of exiting silently
        self.assertIn("usage", json.loads(out.stderr)["error"])

    def test_brand_logo_is_copied_into_a_composition_that_declares_logo(self):
        page = self.composition / "index.html"
        html = page.read_text()
        page.write_text(html.replace("data-composition-variables='[", """data-composition-variables='[{"id":"logo","type":"image","label":"Logo","default":""},""", 1))
        logo = self.folder / "Acme Logo.png"
        logo.write_bytes(b"\x89PNG\r\n\x1a\n")
        state = {"projects": [self.project(brand={**self.brand, "logo": "acme-logo"})], "logo": str(logo)}
        out, calls = self.run_graphic(state, "place", str(self.composition), "--dry-run")
        self.assertEqual(0, out.returncode, out.stderr)
        result = json.loads(out.stdout)
        self.assertEqual("brand-logo.png", result["variables"]["logo"])
        self.assertIn("logo", result["brand"])
        self.assertTrue((self.composition / "brand-logo.png").exists())
        self.assertIn(["library", "get", "acme-logo"], [call["args"][:3] for call in calls])

    def test_brand_mascot_pose_is_copied_into_a_composition_that_declares_mascot(self):
        composition = self.folder / "graphics" / "paper"
        shutil.copytree(ROOT / "examples" / "paper-card", composition)
        pose = self.folder / "wave.png"
        pose.write_bytes(b"png")
        brand = {**self.brand, "mascot": {"default": "sticker-idle", "wave": "sticker-wave"}}
        state = {"projects": [self.project(brand=brand)], "logo": str(pose)}
        out, calls = self.run_graphic(state, "place", str(composition), "--set", "mascotPose=wave", "--dry-run")
        self.assertEqual(0, out.returncode, out.stderr)
        result = json.loads(out.stdout)
        self.assertEqual("brand-mascot-wave.png", result["variables"]["mascot"])
        self.assertIn("mascot", result["brand"])
        self.assertTrue((composition / "brand-mascot-wave.png").exists())
        self.assertIn(["library", "get", "sticker-wave"], [c["args"] for c in calls])

    def test_set_pose_picks_the_brand_pose_and_a_missing_one_lists_the_poses(self):
        composition = self.folder / "graphics" / "stat"
        shutil.copytree(ROOT / "examples" / "stat-counter", composition)
        files = {}
        for pose in ("default", "thinking", "pointing"):
            files[f"sticker-{pose}"] = str(self.folder / f"{pose}.png")
            pathlib.Path(files[f"sticker-{pose}"]).write_bytes(pose.encode())
        brand = {**self.brand, "mascot": {p: f"sticker-{p}" for p in ("default", "thinking", "pointing")}}
        state = {"projects": [self.project(brand=brand)], "files": files}
        out, _ = self.run_graphic(state, "place", str(composition), "--set", "pose=thinking", "--dry-run")
        self.assertEqual(0, out.returncode, out.stderr)
        result = json.loads(out.stdout)
        self.assertEqual("brand-mascot-thinking.png", result["variables"]["mascot"])
        self.assertEqual(b"thinking", (composition / "brand-mascot-thinking.png").read_bytes())
        self.assertNotIn("warnings", result)
        out, _ = self.run_graphic(state, "place", str(composition), "--set", "pose=waving", "--dry-run")
        result = json.loads(out.stdout)
        self.assertEqual("brand-mascot-default.png", result["variables"]["mascot"])
        self.assertIn("default, pointing, thinking", result["warnings"][0])
        # A brand without poses leaves the slot empty (the page hides it) and says why only when a pose was asked.
        out, _ = self.run_graphic({"projects": [self.project(brand=self.brand)]}, "place", str(composition), "--dry-run")
        result = json.loads(out.stdout)
        self.assertNotIn("mascot", result["variables"])
        self.assertNotIn("warnings", result)
        out, _ = self.run_graphic({"projects": [self.project(brand=self.brand)]}, "place", str(composition), "--set", "pose=thinking", "--dry-run")
        self.assertIn("no mascot poses", json.loads(out.stdout)["warnings"][0])

    def test_rerender_all_with_a_new_brand_redraws_every_mascot_in_one_apply(self):
        old, new = self.folder / "old.png", self.folder / "new.png"
        old.write_bytes(b"old")
        new.write_bytes(b"new")
        media, items = [], []
        for index, (example, pose) in enumerate((("stat-counter", "thinking"), ("checklist-card", None), ("lower-third", "pointing"))):
            composition = self.folder / "graphics" / example
            shutil.copytree(ROOT / "examples" / example, composition)
            (composition / "brand-mascot-default.png").write_bytes(b"old")  # what the first place copied in
            recorded = self.recorded_media({"pose": pose} if pose else {})
            recorded["id"] = f"media-{index}"
            recorded["data"]["graphics"]["composition"] = str(composition)
            media.append(recorded)
            items.append({"id": f"item-{index}", "media": f"media-{index}", "at": index * 200, "dur": 165, "in": 0})
        brand = {**self.brand, "mascot": {"default": "new-default", "thinking": "new-thinking"}}
        state = {"projects": [self.project(media=media, items=items, brand=brand)],
                 "files": {"new-default": str(new), "new-thinking": str(new)}}
        out, calls = self.run_graphic(state, "rerender", "--all", "--brand", "--set", "pose=default")
        self.assertEqual(0, out.returncode, out.stderr)
        renders = [c["params"]["variables"] for c in calls if c["args"][:2] == ["plugins", "invoke"]]
        # --set pose=default reaches every graphic with a mascot; each one gets the new brand's file.
        self.assertEqual(["brand-mascot-default.png"] * 3, [r["mascot"] for r in renders])
        for example in ("stat-counter", "checklist-card", "lower-third"):
            self.assertEqual(b"new", (self.folder / "graphics" / example / "brand-mascot-default.png").read_bytes())
        applies = [c for c in calls if c["args"][:2] == ["timeline", "apply"]]
        self.assertEqual(1, len(applies), "one undo step")
        self.assertEqual(["item-0", "item-1", "item-2"], [op["item"] for op in applies[0]["ops"] if op["op"] == "setSource"])
        recorded = [op["patch"]["graphics"]["variables"] for op in applies[0]["ops"] if op["op"] == "setMediaData"]
        self.assertTrue(all("mascot" not in r for r in recorded), "the brand's mascot is not frozen into the inputs")
        # Without --set, each keeps its recorded pose; one the new brand lacks falls back with the poses listed.
        out, calls = self.run_graphic(state, "rerender", "--all", "--brand")
        self.assertEqual(0, out.returncode, out.stderr)
        renders = [c["params"]["variables"]["mascot"] for c in calls if c["args"][:2] == ["plugins", "invoke"]]
        self.assertEqual(["brand-mascot-thinking.png", "brand-mascot-default.png", "brand-mascot-default.png"], renders)
        self.assertTrue(any("pointing" in w and "default, thinking" in w for w in json.loads(out.stdout)["warnings"]))

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

    def test_a_file_path_value_is_copied_next_to_the_composition(self):
        lottie = self.folder / "graphics" / "lottie"
        shutil.copytree(ROOT / "examples" / "lottie", lottie)
        pick = self.folder / "project" / "media" / "lottie" / "check-ua-checkmark.json"
        pick.parent.mkdir(parents=True)
        pick.write_text('{"fr": 30}')
        state = {"projects": [self.project()]}
        out, _ = self.run_graphic(state, "place", str(lottie), "--set", f"file={pick}", "--dry-run")
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertEqual("check-ua-checkmark.json", json.loads(out.stdout)["variables"]["file"])
        self.assertEqual('{"fr": 30}', (lottie / pick.name).read_text())
        out, _ = self.run_graphic(state, "place", "lottie", "--set", f"file={pick}", "--dry-run")
        self.assertEqual(str(pick), json.loads(out.stdout)["variables"]["file"])  # a plugin example is left alone
        self.assertFalse((ROOT / "examples" / "lottie" / pick.name).exists())

    def diagram_project(self, width=1920, height=1080):
        project = self.project()
        project["format"] = {"width": width, "height": height, "fps": [30, 1]}
        project["tracks"].append({"id": "vo", "kind": "audio", "role": "voiceover", "items": [
            {"id": "l1", "at": 300, "dur": 60}, {"id": "l2", "at": 390, "dur": 75}, {"id": "l3", "at": 480, "dur": 90}]})
        project["markers"] = [{"id": "m1", "at": 0, "kind": "section", "label": "Hook"},
                              {"id": "m2", "at": 450, "kind": "section", "label": "How"}]
        return project

    def test_place_times_steps_on_voice_lines_from_a_data_file_at_the_project_canvas(self):
        data = {"nodes": [{"id": "a", "label": "App"}, {"id": "b", "label": "API"}], "edges": [{"from": "a", "to": "b"}],
                "steps": [{"focus": ["a"]}, {"focus": ["b"]}, {"at": "section:How", "focus": []}]}
        (self.folder / "diagram.json").write_text(json.dumps(data))
        flow = self.folder / "graphics" / "flow"
        shutil.copytree(ROOT / "examples" / "flow-diagram", flow)
        state = {"projects": [self.diagram_project(), self.diagram_project()]}
        out, calls = self.run_graphic(state, "place", str(flow), "--set", f"data=@{self.folder / 'diagram.json'}",
                                      "--steps-from-voice")
        self.assertEqual(0, out.returncode, out.stderr)
        invoke = next(c for c in calls if c["args"][:2] == ["plugins", "invoke"])
        self.assertEqual([1920, 1080], invoke["pageSize"])  # data-fit="canvas": rendered at the project's size
        sent = json.loads(invoke["params"]["variables"]["data"])
        # Starts 0.4 s (12 frames) before the first line (300), so the steps land 0.4 s, 3.4 s and 5 s in.
        self.assertEqual([0.4, 3.4, 5.4], [s["at"] for s in sent["steps"]])
        place = next(c for c in calls if c["args"][:2] == ["library", "place"])["args"]
        self.assertEqual("288", place[place.index("--at-frame") + 1])
        self.assertEqual(str(570 - 288 + 15), place[place.index("--duration") + 1])  # section How runs to the end, 570
        self.assertIn('data-width="1080"', (flow / "index.html").read_text())  # the page is put back

    def test_steps_beyond_the_voice_lines_are_refused_before_rendering(self):
        data = {"nodes": [{"id": "a", "label": "A"}], "steps": [{"focus": ["a"]}] * 4}
        (self.folder / "d.json").write_text(json.dumps(data))
        state = {"projects": [self.diagram_project()]}
        out, calls = self.run_graphic(state, "place", str(ROOT / "examples" / "mind-map"), "--set",
                                      f"data=@{self.folder / 'd.json'}", "--steps-from", "voice", "--at-frame", "380")
        self.assertEqual(2, out.returncode, out.stderr)
        self.assertIn("only 2 voice lines", json.loads(out.stderr)["error"])
        self.assertEqual([], [c for c in calls if c["args"][:2] == ["plugins", "invoke"]])
        out, _ = self.run_graphic(state, "place", str(ROOT / "examples" / "mind-map"), "--set", "data=@missing.json")
        self.assertEqual(2, out.returncode)

    def test_rerender_with_a_new_label_keeps_the_step_times(self):
        recorded = {"nodes": [{"id": "a", "label": "App"}], "steps": [{"at": 1.2, "focus": ["a"]}]}
        media = self.recorded_media({"data": json.dumps(recorded)})
        flow = self.folder / "graphics" / "flow"
        shutil.copytree(ROOT / "examples" / "flow-diagram", flow)
        media["data"]["graphics"]["composition"] = str(flow)
        item = {"id": "item-1", "at": 300, "dur": 165, "media": "media-old", "sourceIn": 0}
        changed = {"nodes": [{"id": "a", "label": "Mobile app"}], "steps": [{"focus": ["a"]}]}
        out, calls = self.run_graphic({"projects": [self.project(media=[media], items=[item])]}, "rerender", "item-1",
                                      "--variables", json.dumps({"data": changed}))
        self.assertEqual(0, out.returncode, out.stderr)
        sent = json.loads(next(c for c in calls if c["args"][:2] == ["plugins", "invoke"])["params"]["variables"]["data"])
        self.assertEqual(("Mobile app", 1.2), (sent["nodes"][0]["label"], sent["steps"][0]["at"]))
        self.assertEqual(1, len([c for c in calls if c["args"][:2] == ["timeline", "apply"]]))  # one undo step


class DiagramLayoutTests(unittest.TestCase):
    """lib/diagram.js lays diagrams out from data: no two node boxes may overlap (up to 12 nodes, 9:16 and 16:9)."""

    SCRIPT = r"""
const d = require(process.argv[1]);
const words = ["Khách hàng", "API Gateway", "Auth", "Database", "Cache", "Queue", "Worker service", "Email",
  "Thanh toán online", "CDN", "Analytics dashboard", "Search"];
const out = [];
for (const [W, H] of [[1080, 1920], [1920, 1080]]) {
  const u = Math.min(W, H) / 1080;
  const area = d.areaFor(W, H, u, true);
  for (let n = 1; n <= 12; n++) for (const shape of ["chain", "tree", "fan", "mesh"]) {
    const nodes = Array.from({ length: n }, (_, i) => ({ id: "n" + i, label: words[i], icon: i % 3 ? undefined : "x" }));
    const edges = [];
    for (let i = 1; i < n; i++) edges.push({ from: "n" + (shape === "chain" ? i - 1 : shape === "fan" ? 0 : shape === "tree" ? Math.floor((i - 1) / 3) : Math.max(0, i - 1 - (i % 3))), to: "n" + i });
    if (shape === "mesh" && n > 4) edges.push({ from: "n4", to: "n1" });
    for (const kind of ["flow", "mind", "iso"]) {
      const L = kind === "flow" ? d.flowLayout({ nodes, edges }, area, u) : kind === "mind" ? d.mindLayout({ nodes, edges }, area, u) : d.isoLayout({ nodes, edges }, area, u);
      const outside = L.nodes.filter((b) => b.x - b.w / 2 < area.x - 1 || b.x + b.w / 2 > area.x + area.w + 1 || b.y - b.h / 2 < area.y - 1 || b.y + b.h / 2 > area.y + area.h + 1).length;
      out.push({ W, kind, shape, n, count: L.nodes.length, overlaps: d.overlapping(L.nodes).length, outside, font: Math.min(...L.nodes.map((b) => b.font / u)) });
    }
  }
  const c = d.canvasLayout({ nodes: words.map((w, i) => ({ id: "n" + i, label: w })), edges: words.slice(1).map((w, i) => ({ from: i < 3 ? "n0" : "n" + (1 + (i % 3)), to: "n" + (i + 1) })) }, W, H, 2);
  out.push({ W, kind: "canvas", shape: "tree", n: 12, count: c.nodes.length, overlaps: d.overlapping(c.nodes).length, outside: 0, font: 99 });
}
console.log(JSON.stringify(out));
"""

    def test_no_two_nodes_overlap_up_to_twelve_nodes(self):
        node = subprocess.run([str(ROOT / "bin" / "find-node")], capture_output=True, text=True).stdout.strip() or "node"
        out = subprocess.run([node, "-e", self.SCRIPT, str(ROOT / "lib" / "diagram.js")], capture_output=True, text=True, timeout=60)
        self.assertEqual(0, out.returncode, out.stderr)
        rows = json.loads(out.stdout)
        self.assertEqual(2 * 12 * 4 * 3 + 2, len(rows))
        for row in rows:
            self.assertEqual(row["n"], row["count"], row)
            self.assertEqual(0, row["overlaps"], row)
            self.assertEqual(0, row["outside"], row)
            self.assertGreaterEqual(row["font"], 20, row)

    def test_flow_runs_the_canvas_way_and_a_long_edge_goes_round_the_middle_node(self):
        node = subprocess.run([str(ROOT / "bin" / "find-node")], capture_output=True, text=True).stdout.strip() or "node"
        script = r"""
const d = require(process.argv[1]);
const data = { nodes: ["req", "check", "fraud", "pay", "bank", "mail"].map((id) => ({ id, label: id === "pay" ? "Payment gateway" : id })),
  edges: [["req", "check"], ["check", "fraud"], ["check", "pay"], ["fraud", "pay"], ["pay", "bank"], ["pay", "mail"]].map(([from, to]) => ({ from, to })) };
const out = [];
for (const [W, H] of [[1080, 1920], [1920, 1080]]) {
  const u = Math.min(W, H) / 1080;
  const L = d.flowLayout(data, d.areaFor(W, H, u, true, true), u);
  const fraud = L.nodes.find((n) => n.id === "fraud");
  const via = L.edges.find((e) => e.from === "check" && e.to === "pay").via ?? [];
  out.push({ direction: L.direction, via: via.length, clear: via.every((w) => d.overlapping([w, fraud]).length === 0) });
}
console.log(JSON.stringify(out));
"""
        out = subprocess.run([node, "-e", script, str(ROOT / "lib" / "diagram.js")], capture_output=True, text=True, timeout=30)
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertEqual([{"direction": "tb", "via": 1, "clear": True}, {"direction": "lr", "via": 1, "clear": True}], json.loads(out.stdout))

    def test_steps_without_times_are_spread_and_sorted(self):
        node = subprocess.run([str(ROOT / "bin" / "find-node")], capture_output=True, text=True).stdout.strip() or "node"
        script = 'const d = require(process.argv[1]); console.log(JSON.stringify(d.timedSteps([{at: 4, focus: "b"}, {focus: ["a"]}, {focus: []}], 8).map((s) => [s.at, s.focus])))'
        out = subprocess.run([node, "-e", script, str(ROOT / "lib" / "diagram.js")], capture_output=True, text=True, timeout=30)
        self.assertEqual([[0.9, ["a"]], [4, ["b"]], [4.1, []]], json.loads(out.stdout))


class AmenityLayoutTests(unittest.TestCase):
    """lib/amenity-map.js lays amenity markers out: no two icons overlap at the scale they are seen at."""

    SCRIPT = r"""
const a = require(process.argv[1]);
// A fixed pseudo-random spread (no Math.random: the layout must be the same every run).
let seed = 7;
const next = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const kinds = ["school", "hospital", "mall", "park", "clinic", "supermarket"];
const out = [];
for (const [W, H] of [[1080, 1920], [1920, 1080]]) {
  const u = Math.min(W, H) / 1080;
  const size = 46 * u;
  for (const [n, spread, scale] of [[10, 40, 2.7], [30, 60, 2.7], [60, 112, 1.2], [24, 8, 3.5], [40, 112, 0.6]]) {
    const markers = Array.from({ length: n }, (_, i) => ({ x: 500 + (next() - 0.5) * 2 * spread,
      y: 800 + (next() - 0.5) * 2 * spread, kind: kinds[i % kinds.length], km: Math.round(next() * 1000) / 1000 }));
    // The project's dot and its name tag to the right of it.
    const tag = { x: 500, y: 800, left: 40 * u, top: -30 * u, w: 180 * u, h: 60 * u };
    const fixed = [{ x: 500, y: 800, r: 30 * u }, tag];
    const layout = a.declutter(markers, scale, size, fixed);
    const again = a.declutter(markers, scale, size, fixed);
    const onDot = layout.filter((l, i) => l.shown
      && Math.hypot(markers[i].x * scale + l.dx - 500 * scale, markers[i].y * scale + l.dy - 800 * scale) < 30 * u + size / 2 - 0.5).length;
    const onTag = layout.filter((l, i) => {
      const [x, y] = [markers[i].x * scale + l.dx, markers[i].y * scale + l.dy];
      const [x0, y0] = [500 * scale + tag.left, 800 * scale + tag.top];
      return l.shown && Math.hypot(x - Math.max(x0, Math.min(x0 + tag.w, x)), y - Math.max(y0, Math.min(y0 + tag.h, y))) < size / 2 - 0.5;
    }).length;
    out.push({ W, n, spread, overlaps: a.overlapping(markers, layout, scale, size).length, onDot, onTag,
      counted: layout.reduce((sum, l) => sum + l.count, 0), shown: layout.filter((l) => l.shown).length,
      same: JSON.stringify(layout) === JSON.stringify(again),
      merged: layout.every((l, i) => !l.shown || layout.every((m, j) => j === i || !m.shown || markers[j].kind !== markers[i].kind
        || Math.hypot((markers[j].x - markers[i].x) * scale, (markers[j].y - markers[i].y) * scale) >= size)) });
  }
}
// Two kinds on one spot: both stay, nudged apart; three schools within a few metres: one marker counting 3.
const pair = a.declutter([{ x: 0, y: 0, kind: "school", km: 0.1 }, { x: 0, y: 0, kind: "mall", km: 0.2 }], 2, 46);
const three = a.declutter([0, 1, 2].map((i) => ({ x: i * 3, y: 0, kind: "school", km: i / 10 })), 2, 46);
console.log(JSON.stringify({ out, pair, three }));
"""

    def run_layout(self):
        node = subprocess.run([str(ROOT / "bin" / "find-node")], capture_output=True, text=True).stdout.strip() or "node"
        out = subprocess.run([node, "-e", self.SCRIPT, str(ROOT / "lib" / "amenity-map.js")], capture_output=True,
                             text=True, timeout=60)
        self.assertEqual(0, out.returncode, out.stderr)
        return json.loads(out.stdout)

    def test_no_two_markers_overlap_in_9_16_and_16_9(self):
        result = self.run_layout()
        self.assertEqual(10, len(result["out"]))
        for row in result["out"]:
            self.assertEqual(0, row["overlaps"], row)
            self.assertEqual(0, row["onDot"], f"a marker covers the project's dot: {row}")
            self.assertEqual(0, row["onTag"], f"a marker hides under the project's name: {row}")
            self.assertEqual(row["n"], row["counted"], f"every place is counted once: {row}")
            self.assertTrue(row["same"], f"deterministic: {row}")
            self.assertTrue(row["merged"], f"places of one kind that would touch are one marker: {row}")
        self.assertLess(result["out"][3]["shown"], 24, "a tight spread merges")

    def test_same_kind_merges_with_a_count_and_kinds_apart_get_a_leader_offset(self):
        result = self.run_layout()
        pair, three = result["pair"], result["three"]
        self.assertTrue(pair[0]["shown"] and pair[1]["shown"])
        self.assertGreaterEqual(math.hypot(pair[1]["dx"] - pair[0]["dx"], pair[1]["dy"] - pair[0]["dy"]), 46 - 0.5)
        self.assertEqual([True, False, False], [m["shown"] for m in three])
        self.assertEqual(3, three[0]["count"])
        self.assertEqual((0, 0), (three[0]["dx"], three[0]["dy"]), "a lone marker stays on its place")


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
