#!/usr/bin/env python3
"""Generates registry.json from publishers.json and plugins/<slug>/versions.json.

    scripts/build-registry.py           # write registry.json
    scripts/build-registry.py --check   # fail when registry.json differs from what the sources give (CI)

Both modes refuse a category outside CATEGORIES (scripts/plugin_manifest.py), in any plugin.json, listing.json or
versions.json, so BashCut never meets one it cannot group.

Never edit registry.json by hand: change the sources (package.py, yank.py, sign-registry.py do) and run this.
After a merge conflict in registry.json, take either side and run this again.
"""
import argparse
import json
import sys

from plugin_manifest import CATEGORIES
from registry_tools import ROOT, VERSIONS, build_registry, render


def category_problems(root=ROOT):
    """Every plugin source file that names an unknown category."""
    problems = []
    for path in sorted((root / "plugins").glob("*/*.json")):
        if path.name not in ("plugin.json", "listing.json", VERSIONS):
            continue
        data = json.loads(path.read_text())
        category = (data.get("listing") or {}).get("category") if path.name == VERSIONS else data.get("category")
        if category is not None and category not in CATEGORIES:
            problems.append(f"{path.relative_to(root)}: unknown category {category!r} (use one of {', '.join(CATEGORIES)})")
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    problems = category_problems()
    if problems:
        sys.exit("error: " + "\n       ".join(problems))
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
