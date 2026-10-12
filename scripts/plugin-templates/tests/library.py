"""Checks for {{NAME}}, a library pack without code: the packs and skills read the way BashCut reads them.

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


KINDS = {"audio", "text-preset", "sticker", "effect-preset", "transition-preset", "look", "voice", "clip", "brand"}


class LibraryTests(unittest.TestCase):
    def test_every_pack_reads(self):
        packs = MANIFEST["contributes"]["library"]
        self.assertTrue(1 <= len(packs) <= 32)
        for entry in packs:
            folder = (ROOT / entry["path"]).resolve()
            with self.subTest(pack=entry["path"]):
                self.assertIn(ROOT.resolve(), folder.parents)
                pack = json.loads((folder / "pack.json").read_text())
                self.assertEqual(pack["format"], 1)
                self.assertTrue(pack["name"])
                ids = [item["id"] for item in pack["items"]]
                self.assertEqual(len(ids), len(set(ids)), "item ids are unique")
                for item in pack["items"]:
                    self.assertIn(item["kind"], KINDS)
                    self.assertTrue(item["name"])
                    for field in ("file", "preview"):
                        if field in item:
                            path = (folder / item[field]).resolve()
                            self.assertIn(folder, path.parents, f"{item['id']} {field} must stay in the pack")
                            self.assertTrue(path.is_file(), f"{item['id']}: {item[field]} is missing")

    def test_sound_is_a_wav(self):
        import wave
        pack_folder = ROOT / MANIFEST["contributes"]["library"][0]["path"]
        pack = json.loads((pack_folder / "pack.json").read_text())
        for item in pack["items"]:
            if item["kind"] == "audio" and item["file"].endswith(".wav"):
                with wave.open(str(pack_folder / item["file"])) as sound:
                    self.assertGreater(sound.getnframes(), 0)


if __name__ == "__main__":
    unittest.main()
