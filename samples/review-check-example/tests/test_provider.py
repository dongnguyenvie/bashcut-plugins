"""Drives the sample like BashCut does: one rpc request with a project, one answer with issues."""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PROVIDER = os.path.join(HERE, "..", "bin", "provider")
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
from plugin_manifest import manifest_problems  # noqa: E402


def text(item_id, value, at, dur, font=None):
    item = {"id": item_id, "text": value, "at": at, "dur": dur}
    if font:
        item["textStyle"] = {"font": font}
    return item


def request(items, options=None, duration=300):
    project = {"tracks": [{"id": "v1", "kind": "video", "items": []}, {"id": "t1", "kind": "text", "items": items}]}
    message = {"id": "r1", "apiVersion": 9, "method": "review.check", "provider": "example.review-check.rules",
               "params": {"project": project, "revision": 4, "fps": 30, "duration": duration,
                          "width": 1080, "height": 1920, "options": options or {}}}
    output = subprocess.run([PROVIDER, "rpc"], input=json.dumps(message), capture_output=True, text=True, check=True)
    answer = json.loads(output.stdout)
    assert answer["id"] == "r1"
    return answer["result"]["issues"]


class ReviewCheckExampleTests(unittest.TestCase):
    def test_manifest(self):
        with open(os.path.join(HERE, "..", "plugin.json"), encoding="utf-8") as file:
            self.assertEqual(manifest_problems(json.load(file)), [])

    def test_call_to_action(self):
        issues = request([text("hook", "Đà Lạt 48h?", 0, 60)])
        self.assertEqual([issue["id"] for issue in issues], ["cta"])
        self.assertEqual(issues[0]["frame"], 150)
        self.assertEqual(issues[0]["endFrame"], 300)
        self.assertEqual(request([text("end", "Theo dõi để xem phần 2", 250, 50)]), [])
        self.assertEqual(request([text("end", "Theo dõi", 0, 30)], options={"ctaSeconds": 0}), [])

    def test_brand_fonts(self):
        items = [text("a", "Một", 0, 30, "Comic Sans MS"), text("b", "Hai", 30, 30, "Comic Sans MS"),
                 text("c", "Theo dõi nhé", 270, 30, "Be Vietnam Pro")]
        issues = request(items, options={"fonts": "Be Vietnam Pro, Inter"})
        self.assertEqual([issue["id"] for issue in issues], ["font-a"])
        self.assertEqual(issues[0]["severity"], "warning")
        self.assertEqual(request(items), [])

    def test_unknown_method(self):
        message = {"id": "r2", "apiVersion": 9, "method": "voice.synthesize", "params": {}}
        output = subprocess.run([PROVIDER, "rpc"], input=json.dumps(message), capture_output=True, text=True)
        self.assertEqual(json.loads(output.stdout)["error"]["code"], "unsupported")


if __name__ == "__main__":
    unittest.main()
