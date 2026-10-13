"""Plugin bundles (bundles.json): generated into registry.json and checked, since one approval installs them all."""
import importlib.util
import pathlib
import sys
import unittest

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build_registry = load("build_registry", "build-registry.py")
from registry_tools import build_registry as generate  # noqa: E402


def registry(*bundles):
    return {
        "publishers": {"bashcut": {"verified": True}, "someone": {"verified": False}},
        "plugins": [{"id": "bashcut.a", "publisher": "bashcut"}, {"id": "someone.b", "publisher": "someone"}],
        "bundles": list(bundles),
    }


def bundle(**fields):
    value = {"id": "starter", "name": {"en": "Recommended"}, "summary": "Everything",
             "plugins": [{"id": "bashcut.a", "default": True}]}
    value.update(fields)
    return value


class BundleTests(unittest.TestCase):
    def test_the_registry_bundles_are_valid(self):
        generated = generate()
        self.assertTrue(generated["bundles"])
        self.assertEqual(build_registry.bundle_problems(generated), [])

    def test_a_valid_bundle_passes(self):
        self.assertEqual(build_registry.bundle_problems(registry(bundle())), [])

    def test_bundles_name_only_verified_registry_plugins(self):
        problems = build_registry.bundle_problems(registry(bundle(plugins=[
            {"id": "bashcut.missing"}, {"id": "someone.b"}, {"id": "bashcut.a"}, {"id": "bashcut.a"}])))
        self.assertEqual(problems, [
            "bundles.json: bundle starter: bashcut.missing is not in the registry",
            "bundles.json: bundle starter: someone.b is not from a verified publisher",
            "bundles.json: bundle starter: bashcut.a is listed twice",
        ])

    def test_ids_texts_and_defaults_are_checked(self):
        problems = build_registry.bundle_problems(registry(
            bundle(), bundle(), bundle(id="Starter Pack", name={"vi": "Gói"}, summary="",
                                       plugins=[{"id": "bashcut.a", "default": "yes"}]),
            bundle(id="empty", plugins=[])))
        self.assertEqual(problems, [
            "bundles.json: bundle starter: id is used twice",
            "bundles.json: bundle Starter Pack: id must be lowercase words joined by '-'",
            "bundles.json: bundle Starter Pack: name must be a string or a language map with en",
            "bundles.json: bundle Starter Pack: summary must be a string or a language map with en",
            "bundles.json: bundle Starter Pack: bashcut.a: default must be true or false",
            "bundles.json: bundle empty: plugins must list at least one plugin",
        ])


if __name__ == "__main__":
    unittest.main()
