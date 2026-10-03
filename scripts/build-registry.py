#!/usr/bin/env python3
"""Generates registry.json from publishers.json and plugins/<slug>/versions.json.

    scripts/build-registry.py           # write registry.json
    scripts/build-registry.py --check   # fail when registry.json differs from what the sources give (CI)

Never edit registry.json by hand: change the sources (package.py, yank.py, sign-registry.py do) and run this.
After a merge conflict in registry.json, take either side and run this again.
"""
import argparse
import sys

from registry_tools import ROOT, build_registry, render


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(build_registry())
    path = ROOT / "registry.json"
    if args.check:
        if not path.is_file() or path.read_text() != expected:
            sys.exit("error: registry.json is out of date; run scripts/build-registry.py and commit it")
        print("registry.json matches its sources")
        return
    path.write_text(expected)
    print("wrote registry.json")


if __name__ == "__main__":
    main()
