"""Plugin categories: one fixed list (CATEGORIES), checked in manifests, listings and the generated registry."""
import contextlib
import importlib.util
import io
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build_registry = load("build_registry", "build-registry.py")
new_plugin = load("new_plugin", "new-plugin.py")
from plugin_manifest import CATEGORIES, manifest_problems  # noqa: E402


class CategoryTests(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def write(self, path, value):
        target = self.root / "plugins" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value))

    def test_the_registry_uses_known_categories(self):
        self.assertEqual(build_registry.category_problems(), [])

    def test_unknown_categories_are_refused_wherever_they_appear(self):
        self.write("a/listing.json", {"category": "agents"})
        self.write("a/plugin.json", {"category": "games"})
        self.write("b/versions.json", {"id": "x.b", "listing": {"category": "misc"}, "versions": []})
        self.write("c/listing.json", {"name": "No category"})
        problems = build_registry.category_problems(self.root)
        self.assertEqual(len(problems), 2)
        self.assertIn("plugins/a/plugin.json", problems[0])
        self.assertIn("'misc'", problems[1])

    def test_manifests_may_name_a_known_category(self):
        with contextlib.redirect_stdout(io.StringIO()):
            new_plugin.main(["sorter", "--template", "action", "--lang", "shell", "--category", "effects",
                             "--out", str(self.root)])
        manifest = json.loads((self.root / "sorter" / "plugin.json").read_text())
        self.assertEqual(manifest["category"], "effects")
        self.assertEqual(manifest_problems(manifest), [])
        manifest["category"] = "games"
        self.assertEqual(manifest_problems(manifest), [f"category must be one of {', '.join(CATEGORIES)}"])


if __name__ == "__main__":
    unittest.main()
