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
from plugin_manifest import manifest_problems  # noqa: E402

CASES = [(template, lang) for template in new_plugin.TEMPLATE_NAMES for lang in new_plugin.LANGUAGES
         if not (lang == "shell" and template in new_plugin.SESSION_TEMPLATES)]


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
        self.assertFalse((plugin / "listing.json").exists(), "a plugin outside plugins/ has no listing")
        text = "".join(p.read_text() for p in plugin.rglob("*") if p.is_file())
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
                self.check(make(self.root, f"{template}-{lang}", "--template", template, "--lang", lang), lang)

    def test_every_capability(self):
        for capability in new_plugin.PROVIDED_CAPABILITIES:
            for lang in ("python", "shell"):
                with self.subTest(capability=capability, lang=lang):
                    slug = f"cap-{capability.replace('.', '-')}-{lang}"
                    plugin = make(self.root, slug, "--template", "capability", "--capability", capability,
                                  "--lang", lang)
                    self.check(plugin, lang)


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


if __name__ == "__main__":
    unittest.main()
