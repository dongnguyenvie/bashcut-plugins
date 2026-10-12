"""Checks for {{NAME}}, a skill pack without code: the skills read the way BashCut reads them.

    python3 -m unittest discover -s tests -v

Python standard library only; not shipped.
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = json.loads((ROOT / "plugin.json").read_text())


def front_matter(text):
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields.setdefault(key.strip(), value.strip().strip("\"'"))
    return {}


class PackTests(unittest.TestCase):
    def test_nothing_runs(self):
        self.assertNotIn("entrypoint", MANIFEST)
        for field in ("capabilities", "providers", "options", "dependencies", "transport"):
            self.assertFalse(MANIFEST.get(field), f"a pack without an entrypoint cannot have {field}")
        self.assertGreaterEqual(MANIFEST["apiVersion"], 7)

    def test_every_skill_reads(self):
        skills = MANIFEST.get("contributes", {}).get("skills", [])
        self.assertTrue(skills or MANIFEST.get("contributes", {}).get("library"))
        for entry in skills:
            folder = (ROOT / entry["path"]).resolve()
            with self.subTest(skill=entry["path"]):
                self.assertIn(ROOT.resolve(), folder.parents)
                text = (folder / "SKILL.md").read_text()
                self.assertLessEqual(len(text.encode()), 64 * 1024)
                fields = front_matter(text)
                self.assertEqual(fields.get("name"), folder.name, "front matter name must be the folder name")
                self.assertTrue(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", folder.name))
                self.assertTrue(0 < len(fields.get("description", "")) <= 1024)


if __name__ == "__main__":
    unittest.main()
