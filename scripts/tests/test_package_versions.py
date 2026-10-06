"""package.py refuses a Node plugin whose package.json or lockfile version differs from plugin.json."""
import importlib.util
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("package", SCRIPTS / "package.py")
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class PackageVersionTests(unittest.TestCase):
    def setUp(self):
        self.folder = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.folder, ignore_errors=True)

    def write(self, package_version, lock_version, root_version):
        (self.folder / "package.json").write_text(json.dumps({"version": package_version}))
        (self.folder / "package-lock.json").write_text(
            json.dumps({"version": lock_version, "packages": {"": {"version": root_version}}}))

    def test_matching_versions_pass(self):
        self.write("0.0.3", "0.0.3", "0.0.3")
        package.check_package_versions(self.folder, "0.0.3")

    def test_a_plugin_without_npm_files_passes(self):
        package.check_package_versions(self.folder, "1.2.3")

    def test_each_stale_version_is_refused(self):
        for versions in [("0.0.2", "0.0.3", "0.0.3"), ("0.0.3", "0.0.2", "0.0.3"), ("0.0.3", "0.0.3", "0.0.2")]:
            self.write(*versions)
            with self.assertRaises(SystemExit) as raised:
                package.check_package_versions(self.folder, "0.0.3")
            self.assertIn("bump them together", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
