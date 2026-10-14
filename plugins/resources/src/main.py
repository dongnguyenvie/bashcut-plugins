#!/usr/bin/env python3
"""Entrypoint of Online Resources (bashcut.resources): `provider session`. The protocol is in bashcut_plugin.py, the
actions and the sheet in resources.py, the fetchers in ../scripts (the same files the agent kit runs)."""
import os
import sys

# Bytecode next to the plugin would change its files, and BashCut would ask for Trust again.
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bashcut_plugin  # noqa: E402
import resources  # noqa: E402

if __name__ == "__main__":
    resources.start()
    bashcut_plugin.run(resources.handle)
