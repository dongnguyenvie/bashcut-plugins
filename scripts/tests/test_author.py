"""Plugin authors: the manifest's optional author {name, url} is checked and copied into the registry listing."""
import pathlib
import sys
import unittest

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from plugin_manifest import author_problems, manifest_problems  # noqa: E402
from registry_tools import LISTING_KEYS  # noqa: E402

BASE = {"schema": "bashcut.plugin/1", "id": "example.author", "name": "Author", "version": "0.0.1",
        "apiVersion": 2, "entrypoint": "bin/provider", "capabilities": ["audio.beats"]}


class AuthorTests(unittest.TestCase):
    def test_valid_authors(self):
        for author in ({"name": "Luan Tran", "url": "https://github.com/luantran069"},
                       {"name": "Luan Tran", "url": None}, {"name": "Luan Tran"}):
            self.assertEqual(manifest_problems({**BASE, "author": author}), [], author)
        self.assertEqual(manifest_problems(BASE), [])

    def test_invalid_authors(self):
        for author in ("Luan Tran", {"name": ""}, {"name": " Luan"}, {"name": "a\nb"}, {"name": "x" * 81},
                       {"name": "Luan", "url": "javascript:alert(1)"}, {"name": "Luan", "url": "github.com/luan"},
                       {"name": "Luan", "url": "file:///etc/passwd"}):
            self.assertTrue(author_problems(author), author)

    def test_the_registry_listing_keeps_the_author(self):
        self.assertIn("author", LISTING_KEYS)


if __name__ == "__main__":
    unittest.main()
