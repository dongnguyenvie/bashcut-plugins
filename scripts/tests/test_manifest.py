"""The manifest and view checks in scripts/plugin_manifest.py follow the app's rules for the newer API parts:
providers[].maxTakes, views[].when, packs without an entrypoint and the view components.

    python3 -m unittest discover -s scripts/tests -v
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from plugin_manifest import manifest_problems, view_problems  # noqa: E402

BASE = {"schema": "bashcut.plugin/1", "id": "me.thing", "name": "Thing", "version": "0.0.1", "apiVersion": 9,
        "entrypoint": "bin/provider"}


def voice(max_takes, api=9, capability="voice.synthesize"):
    return {**BASE, "apiVersion": api, "minApiVersion": min(api, 8) if api >= 8 else api, "capabilities": [capability],
            "providers": [{"id": "me.thing.voice", "capability": capability, "name": "Voice", "maxTakes": max_takes}]}


class MaxTakesTests(unittest.TestCase):
    def test_paid_voice_asks_for_one_take(self):
        self.assertEqual(manifest_problems(voice(1)), [])
        self.assertEqual(manifest_problems(voice(8)), [])

    def test_limits(self):
        for bad in (0, 9, "1", True, 1.5):
            with self.subTest(bad=bad):
                self.assertTrue(any("maxTakes is 1–8" in p for p in manifest_problems(voice(bad))))
        self.assertTrue(any("for voice.synthesize" in p
                            for p in manifest_problems(voice(1, capability="captions.transcribe"))))
        self.assertTrue(any("maxTakes needs apiVersion 8" in p for p in manifest_problems(voice(1, api=7))))


class InspectorWhenTests(unittest.TestCase):
    def manifest(self, view):
        return {**BASE, "transport": "session", "capabilities": [], "features": ["views"],
                "contributes": {"views": [{"id": "graphic", "title": "Graphic", **view}]}}

    def test_when_on_an_inspector_view(self):
        self.assertEqual(manifest_problems(self.manifest({"location": "inspector",
                                                          "when": "selection.kind == video"})), [])

    def test_when_elsewhere_or_empty(self):
        self.assertIn("view graphic: when is for inspector views",
                      manifest_problems(self.manifest({"location": "dock", "when": "selection.kind == video"})))
        self.assertTrue(any("when must be a condition" in p
                            for p in manifest_problems(self.manifest({"location": "inspector", "when": " "}))))


class WindowViewTests(unittest.TestCase):
    def manifest(self, api):
        return {**BASE, "apiVersion": api, "transport": "session", "capabilities": [], "features": ["views"],
                "contributes": {"views": [{"id": "browse", "title": "Browse", "location": "window"}]}}

    def test_window_needs_api_11(self):
        self.assertEqual(manifest_problems(self.manifest(11)), [])
        self.assertIn("view browse: location window needs apiVersion 11", manifest_problems(self.manifest(10)))


class ExportStepTests(unittest.TestCase):
    STEP = {"id": "finalise-graphics", "title": {"en": "Finalise draft graphics", "vi": "Hoàn thiện đồ hoạ nháp"},
            "command": {"executable": "bin/graphic", "arguments": ["finalise"]}, "when": "media.data.graphics.draft"}

    def manifest(self, api=12, **step):
        return {**BASE, "apiVersion": api, "capabilities": ["graphics.render"],
                "contributes": {"exportSteps": [{**self.STEP, **step}]}}

    def test_a_step_needs_api_12(self):
        self.assertEqual(manifest_problems(self.manifest()), [])
        self.assertIn("contributes.exportSteps needs apiVersion 12", manifest_problems(self.manifest(api=11)))

    def test_bad_steps(self):
        for step in ({"command": {"executable": "node"}}, {"command": {"executable": "/bin/sh"}},
                     {"command": {"executable": "bin/../x"}}, {"when": "selection.kind"}, {"when": "media.data"},
                     {"timeoutSeconds": 5}, {"title": ""}, {"id": "bad id"}):
            with self.subTest(step=step):
                self.assertTrue(any(p.startswith("export step") for p in manifest_problems(self.manifest(**step))))


class DataOnlyTests(unittest.TestCase):
    PACK = {"schema": "bashcut.plugin/1", "id": "me.my-skills", "name": "My skills", "version": "0.1.0",
            "apiVersion": 7, "category": "agents", "contributes": {"skills": [{"path": "skills/beat-cut"}]}}

    def test_skill_pack_without_entrypoint_or_capabilities(self):
        self.assertEqual(manifest_problems(self.PACK), [])
        library = {**self.PACK, "contributes": {"library": [{"path": "packs/party"}]}}
        self.assertEqual(manifest_problems(library), [])

    def test_needs_api_7_and_skills_or_library(self):
        self.assertTrue(any("apiVersion 7" in p for p in manifest_problems({**self.PACK, "apiVersion": 6})))
        self.assertTrue(any("must ship contributes.skills" in p
                            for p in manifest_problems({**self.PACK, "contributes": {}})))

    def test_nothing_that_runs(self):
        for extra in ({"capabilities": ["audio.beats"]}, {"options": [{"id": "a", "title": "A", "type": "bool"}]},
                      {"transport": "session"},
                      {"contributes": {"skills": [{"path": "skills/a"}], "actions": [{"id": "me.my-skills.x"}]}}):
            with self.subTest(extra=extra):
                problems = manifest_problems({**self.PACK, **extra})
                self.assertTrue(any("can only ship skills and library packs" in p for p in problems), problems)


class ViewTests(unittest.TestCase):
    def test_new_components(self):
        answer = {"body": [
            {"type": "colorPicker", "id": "accent", "label": "Accent", "value": "#FF8800"},
            {"type": "colorPicker", "id": "shade", "value": "#ff880080", "alpha": True},
            {"type": "fontPicker", "id": "font", "value": "Inter", "by": "family"},
            {"type": "list", "id": "files", "items": [{"id": "a", "title": "A", "file": "/tmp/a.mov"}]},
            {"type": "image", "path": "/tmp/a.png", "file": "/tmp/a.mov"},
            {"type": "hologram", "text": "unknown types draw a placeholder"},
        ]}
        self.assertEqual(view_problems(answer), [])

    def test_refused_components(self):
        answer = {"body": [
            {"type": "colorPicker", "id": "accent", "value": "orange"},
            {"type": "fontPicker", "id": "font", "by": "style"},
            {"type": "list", "id": "files", "items": [{"id": "a", "file": 3}, {"title": "no id"}]},
            {"type": "image", "path": "/tmp/a.png", "file": ["/tmp/a.mov"]},
            {"type": "button", "title": "No id"},
            {"type": "section", "children": [{"type": "toggle", "id": "accent", "label": "Twice"}]},
        ]}
        problems = view_problems(answer)
        for expected in ("value must be #RRGGBB", "by must be font or family", "item a file must be a path",
                         "items need an id", "image _3: file must be a path", "button _4: needs an id",
                         "id is used twice"):
            self.assertTrue(any(expected in p for p in problems), (expected, problems))
        self.assertEqual(view_problems({"title": "no body"}), ["a view answer needs a body array of components"])

    def test_split_and_nav(self):
        column = {"type": "section", "children": [{"type": "text", "text": "x"}]}
        good = {"body": [{"type": "split", "widths": [200, "flex", 280], "children": [column, column, column]},
                         {"type": "nav", "id": "types", "value": "a", "groups": [{"items": [{"id": "a", "count": 3}]}]}]}
        self.assertEqual(view_problems(good), [])
        bad = {"body": [{"type": "split", "children": [column]},
                        {"type": "split", "widths": [20, "flex"], "children": [column, column]},
                        {"type": "nav", "groups": [{"items": [{"title": "no id"}]}]}]}
        problems = view_problems(bad)
        for expected in ("needs 2 or 3 children", 'points or "flex"', "nav _2: needs an id", "entries need an id"):
            self.assertTrue(any(expected in p for p in problems), (expected, problems))


if __name__ == "__main__":
    unittest.main()
