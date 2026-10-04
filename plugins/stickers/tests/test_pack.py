"""Checks the pack as BashCut reads it: the manifest's sticker folders exist inside the plugin and hold images."""
import json
import os
import pathlib
import unittest

PLUGIN = pathlib.Path(__file__).resolve().parent.parent
IMAGES = {".png", ".gif"}


class StickerPackTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((PLUGIN / "plugin.json").read_text())

    def test_manifest_declares_packs_for_api_6(self):
        self.assertGreaterEqual(self.manifest["apiVersion"], 6)
        self.assertGreaterEqual(self.manifest["minApiVersion"], 6)
        packs = self.manifest["contributes"]["stickers"]
        self.assertTrue(packs)
        self.assertEqual(len({pack["id"] for pack in packs}), len(packs))
        for pack in packs:
            self.assertTrue(pack["id"].startswith(self.manifest["id"] + "."))
            self.assertIn("en", pack["title"])
            self.assertFalse(pack["path"].startswith("/") or ".." in pathlib.PurePosixPath(pack["path"]).parts)

    def test_entrypoint_is_executable(self):
        self.assertTrue(os.access(PLUGIN / self.manifest["entrypoint"], os.X_OK))

    def test_pack_folders_hold_only_readable_images(self):
        for pack in self.manifest["contributes"]["stickers"]:
            files = sorted(path for path in (PLUGIN / pack["path"]).iterdir() if not path.name.startswith("."))
            self.assertTrue(files, pack["id"])
            for path in files:
                self.assertIn(path.suffix, IMAGES, path.name)
                head = path.read_bytes()[:6]
                self.assertTrue(head.startswith(b"\x89PNG") if path.suffix == ".png" else head[:3] == b"GIF", path.name)

    def test_starter_pack_counts(self):
        names = [path.name for path in (PLUGIN / "stickers").iterdir()]
        self.assertEqual(sum(name.endswith(".png") for name in names), 61)
        self.assertEqual(sum(name.endswith(".gif") for name in names), 20)


if __name__ == "__main__":
    unittest.main()
