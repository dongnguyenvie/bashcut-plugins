"""Runs bin/setup against a stand-in installer that parses flags like Google's install.sh (no network)."""
import os
import pathlib
import stat
import subprocess
import tempfile
import unittest

PLUGIN = pathlib.Path(__file__).resolve().parent.parent
SETUP = PLUGIN / "bin" / "setup"

# Same option parsing as https://antigravity.google/cli/install.sh: only -d/--dir and -h/--help.
INSTALLER = r'''#!/bin/bash
set -euo pipefail
TARGET_DIR="$HOME/.local/bin"
while [ "$#" -gt 0 ]; do
    case $1 in
        -d|--dir) TARGET_DIR="$2"; shift ;;
        -h|--help) exit 0 ;;
        *) echo "[ERROR] Unknown parameter: $1" >&2; exit 1 ;;
    esac
    shift
done
mkdir -p "$TARGET_DIR"
printf '#!/bin/sh\necho agy 1.0\n' > "$TARGET_DIR/agy"
chmod +x "$TARGET_DIR/agy"
'''


class SetupTests(unittest.TestCase):
    def test_setup_passes_only_flags_the_installer_accepts(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = pathlib.Path(scratch)
            fake_bin = root / "fake-bin"
            fake_bin.mkdir()
            (root / "install.sh").write_text(INSTALLER)
            curl = fake_bin / "curl"
            # Stand-in curl: copy the local installer to the path after -o.
            curl.write_text('#!/bin/sh\nwhile [ "$#" -gt 0 ]; do\n  if [ "$1" = "-o" ]; then cp "%s" "$2"; fi\n  shift\ndone\n'
                            % (root / "install.sh"))
            curl.chmod(curl.stat().st_mode | stat.S_IEXEC)
            home = root / "home"
            home.mkdir()
            environment = dict(os.environ, HOME=str(home), PATH=f"{fake_bin}:/usr/bin:/bin")
            result = subprocess.run([str(SETUP)], capture_output=True, text=True, env=environment)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("Unknown parameter", result.stderr)
            self.assertTrue((home / ".local" / "bin" / "agy").exists())
            self.assertIn("::progress 1.0", result.stdout)


if __name__ == "__main__":
    unittest.main()
