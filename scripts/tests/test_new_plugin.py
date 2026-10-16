"""Generates every template in every language into a temporary folder, checks its manifest and runs its smoke tests,
so the templates never drift from the plugin API.

    python3 -m unittest discover -s scripts/tests -v

Swift templates need swiftc (skipped without it), Node templates a Node.js 22+ (skipped without one).
"""
import contextlib
import importlib.util
import io
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("new_plugin", SCRIPTS / "new-plugin.py")
new_plugin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(new_plugin)
from plugin_manifest import manifest_problems, skill_problems, view_problems  # noqa: E402

CASES = [(template, lang) for template in new_plugin.TEMPLATE_NAMES for lang in new_plugin.LANGUAGES
         if template not in new_plugin.DATA_TEMPLATES
         and not (lang == "shell" and template in new_plugin.SESSION_TEMPLATES)]
CASES += [(template, None) for template in sorted(new_plugin.DATA_TEMPLATES)]


def node_available():
    finder = SCRIPTS / "plugin-templates" / "node" / "find-node"
    return subprocess.run([str(finder)], capture_output=True).returncode == 0


def make(folder, slug, *extra):
    with contextlib.redirect_stdout(io.StringIO()):
        new_plugin.main([slug, "--out", str(folder), *extra])
    return pathlib.Path(folder, slug)


class TemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = pathlib.Path(tempfile.mkdtemp())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def check(self, plugin, lang):
        manifest = json.loads((plugin / "plugin.json").read_text())
        self.assertEqual(manifest_problems(manifest), [])
        self.assertEqual(skill_problems(plugin, manifest), [])
        self.assertFalse((plugin / "listing.json").exists(), "a plugin outside plugins/ has no listing")
        text = "".join(p.read_text() for p in plugin.rglob("*") if p.is_file() and p.suffix != ".wav")
        self.assertNotIn("{{", text)
        self.assertNotIn("@@", text)
        if lang == "swift":
            if not shutil.which("swiftc"):
                self.skipTest("swiftc is not installed")
            subprocess.run([str(plugin / "build.sh")], check=True, capture_output=True)
        if lang == "node" and not node_available():
            self.skipTest("Node.js 22 is not installed")
        out = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(plugin / "tests")],
                             capture_output=True, text=True, timeout=600)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertFalse((plugin / "bin" / "__pycache__").exists(), "bytecode next to the plugin breaks Trust")

    def test_every_template_and_language(self):
        for template, lang in CASES:
            with self.subTest(template=template, lang=lang):
                lang_args = ["--lang", lang] if lang else []
                self.check(make(self.root, f"{template}-{lang or 'data'}", "--template", template, *lang_args), lang)

    def test_every_capability(self):
        for capability in new_plugin.PROVIDED_CAPABILITIES:
            for lang in ("python", "shell"):
                with self.subTest(capability=capability, lang=lang):
                    slug = f"cap-{capability.replace('.', '-')}-{lang}"
                    plugin = make(self.root, slug, "--template", "capability", "--capability", capability,
                                  "--lang", lang)
                    self.check(plugin, lang)


class ViewsTemplateTests(unittest.TestCase):
    """The views template's answers pass the view checks BashCut applies, with and without the newer components."""

    def test_answers_follow_the_view_rules(self):
        root = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, True)
        plugin = make(root, "panel-python", "--template", "views", "--lang", "python")
        manifest = json.loads((plugin / "plugin.json").read_text())
        self.assertEqual(manifest["transport"], "session")
        self.assertEqual([v.get("location", "panel") for v in manifest["contributes"]["views"]],
                         ["panel", "dock", "sheet", "window"])
        self.assertEqual((manifest["apiVersion"], manifest["minApiVersion"]), (new_plugin.API_CURRENT, 11),
                         "a window view needs API 11")
        self.assertNotIn("views.colorPicker", manifest["features"], "optional features stay out of features")
        views = [v["id"] for v in manifest["contributes"]["views"]]
        for features in ([], ["views", "views.colorPicker", "views.split", "views.nav"]):
            hello = {"type": "hello", "apiVersion": 11, "features": features}
            lines = [hello] + [{"type": "request", "id": f"r{i}", "method": "view.render",
                                # Media already in state: no host call to answer in this one-way session.
                                "params": {"view": view, "values": {}, "state": {"media": []}}}
                               for i, view in enumerate(views)] + [{"type": "shutdown"}]
            out = subprocess.run([str(plugin / "bin/provider"), "session"], capture_output=True, text=True, timeout=60,
                                 input="".join(json.dumps(line) + "\n" for line in lines))
            replies = [json.loads(line) for line in out.stdout.splitlines()][1:]
            self.assertEqual(len(replies), len(views), out.stderr)
            for reply in replies:
                self.assertEqual(view_problems(reply["result"]), [], reply)


class DataTemplateTests(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, True)

    def test_skills_pack_has_no_entrypoint(self):
        plugin = make(self.root, "my-skills", "--template", "skills")
        manifest = json.loads((plugin / "plugin.json").read_text())
        self.assertNotIn("entrypoint", manifest)
        self.assertEqual(manifest["contributes"], {"skills": [{"path": "skills/my-skills"}]})
        self.assertEqual((manifest["category"], manifest["minApiVersion"]), ("agents", 7))
        self.assertFalse((plugin / "bin").exists())
        self.assertIn("without code", (plugin / "README.md").read_text())

    def test_library_pack_with_a_skill(self):
        plugin = make(self.root, "party", "--template", "library", "--skill")
        manifest = json.loads((plugin / "plugin.json").read_text())
        self.assertEqual(set(manifest["contributes"]), {"library", "skills"})
        pack = json.loads((plugin / "packs/party/pack.json").read_text())
        self.assertEqual({item["kind"] for item in pack["items"]},
                         {"audio", "sticker", "text-preset", "look", "transition-preset"})
        self.assertTrue(all(item["id"].startswith("party-") for item in pack["items"]))
        self.assertTrue((plugin / "packs/party/files/party-click.wav").is_file())

    def test_data_templates_take_no_language(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            new_plugin.main(["x", "--template", "skills", "--lang", "python", "--out", str(self.root)])


class BehaviourTests(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, True)

    def test_refuses_an_existing_folder(self):
        make(self.root, "twice", "--template", "hook", "--lang", "python")
        with self.assertRaises(SystemExit):
            make(self.root, "twice", "--template", "hook", "--lang", "python")

    def test_refuses_an_id_used_in_the_repo(self):
        with self.assertRaises(SystemExit):
            make(self.root, "copy", "--template", "action", "--id", "bashcut.director")

    def test_refuses_bad_input(self):
        for argv in (["Bad_Slug", "--template", "action"],
                     ["ok", "--template", "chat-agent", "--lang", "shell"],
                     ["ok", "--template", "views", "--lang", "shell"],
                     ["ok", "--template", "action", "--capability", "audio.beats"],
                     ["ok", "--template", "action", "--name", 'Say "hi"']):
            with self.subTest(argv=argv), self.assertRaises(SystemExit), \
                    contextlib.redirect_stderr(io.StringIO()):
                new_plugin.main([*argv, "--out", str(self.root)])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_private_defaults(self):
        plugin = make(self.root, "my-voice", "--template", "capability", "--capability", "voice.synthesize",
                      "--private", "--lang", "shell")
        manifest = json.loads((plugin / "plugin.json").read_text())
        self.assertEqual(manifest["id"], "local.my-voice")
        self.assertEqual(manifest["providers"][0]["id"], "local.my-voice.synthesize")
        self.assertIn("ln -sfn", (plugin / "README.md").read_text())

    def test_skill(self):
        plugin = make(self.root, "clip-skill", "--template", "action", "--lang", "shell", "--skill")
        manifest = json.loads((plugin / "plugin.json").read_text())
        self.assertEqual(manifest["contributes"]["skills"], [{"path": "skills/clip-skill"}])
        self.assertGreaterEqual(manifest["apiVersion"], 7)
        self.assertEqual(manifest_problems(manifest), [])
        self.assertEqual(skill_problems(plugin, manifest), [])
        text = (plugin / "skills/clip-skill/SKILL.md").read_text()
        self.assertIn("name: clip-skill", text)
        self.assertNotIn("{{", text)

    def test_skill_problems(self):
        plugin = self.root / "skilled"
        manifest = {"contributes": {"skills": [{"path": f"skills/{name}"} for name in
                                               ("good", "wrong", "bare", "missing", "huge")]}}
        texts = {"good": "---\nname: good\ndescription: Use when.\n---\n",
                 "wrong": "---\nname: other\ndescription: Use when.\n---\n",
                 "bare": "# No front matter\n",
                 "huge": "---\nname: huge\ndescription: Use when.\n---\n" + "x" * 70000}
        for name, text in texts.items():
            (plugin / "skills" / name).mkdir(parents=True)
            (plugin / "skills" / name / "SKILL.md").write_text(text)
        problems = skill_problems(plugin, manifest)
        self.assertEqual(len(problems), 5, problems)  # bare misses both name and description
        self.assertTrue(any("must match the folder" in p for p in problems))
        self.assertTrue(any("skills/missing" in p and "no SKILL.md" in p for p in problems))
        self.assertTrue(any("skills/huge" in p for p in problems))
        old = {"schema": "bashcut.plugin/1", "id": "a.b", "name": "A", "version": "0.0.1", "apiVersion": 6,
               "entrypoint": "bin/provider", "capabilities": [], "contributes": {"skills": [{"path": "skills/a"}]}}
        self.assertIn("contributes.skills needs apiVersion 7", manifest_problems(old))
        self.assertTrue(any("inside the plugin" in p for p in manifest_problems(
            {**old, "apiVersion": 7, "contributes": {"skills": [{"path": "../x"}]}})))

    def test_registry_layout(self):
        args = new_plugin.parse(["fresh-thing", "--template", "chat-agent", "--name", "Fresh", "--name-vi", "Tươi"])
        self.assertTrue(args.registry)
        self.assertEqual((args.id, args.category, args.lang), ("bashcut.fresh-thing", "agents", "swift"))
        staging = self.root / "staging"
        manifest = new_plugin.generate(args, True, staging)
        self.assertEqual(manifest["name"], {"en": "Fresh", "vi": "Tươi"})
        listing = json.loads((staging / "listing.json").read_text())
        self.assertEqual(listing["category"], "agents")
        self.assertEqual(json.loads((staging / "versions.json").read_text())["versions"], [])
        self.assertIn("scripts/dev-link.sh fresh-thing", (staging / "README.md").read_text())

    def test_views_listing_needs_the_app_with_api_11(self):
        args = new_plugin.parse(["fresh-panel", "--template", "views", "--lang", "node"])
        new_plugin.generate(args, True, self.root / "staging")
        listing = json.loads((self.root / "staging/listing.json").read_text())
        self.assertEqual(listing["minAppVersion"], "0.0.25")


if __name__ == "__main__":
    unittest.main()
