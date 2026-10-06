import json,unittest
from support import FOLDER,Session
from plugin_manifest import manifest_problems
class SkeletonTests(unittest.TestCase):
    def test_manifest(self):
        self.assertEqual(manifest_problems(json.loads((FOLDER/'plugin.json').read_text())),[])
    def test_empty_views(self):
        s=Session()
        try:
            for name in ('studio','voices','watermark','build'):
                self.assertEqual(s.view(name)['result']['body'],[])
        finally:s.close()
