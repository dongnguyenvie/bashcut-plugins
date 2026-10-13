#!/usr/bin/env python3
"""Generates registry.json from publishers.json and plugins/<slug>/versions.json.

    scripts/build-registry.py           # write registry.json
    scripts/build-registry.py --check   # fail when registry.json differs from what the sources give (CI)

Both modes refuse a category outside CATEGORIES (scripts/plugin_manifest.py), in any plugin.json, listing.json or
versions.json, so BashCut never meets one it cannot group, and a bundle (bundles.json) that names a plugin the registry
does not have or one from an unverified publisher: approving a bundle installs every plugin in it.

Never edit registry.json by hand: change the sources (package.py, yank.py, sign-registry.py do) and run this.
After a merge conflict in registry.json, take either side and run this again.
"""
import argparse
import json
import re
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


def text_problems(where, value):
    """A display text is a plain string or a language map with `en`."""
    if isinstance(value, str) and value:
        return []
    if isinstance(value, dict) and value and "en" in value and all(isinstance(v, str) and v for v in value.values()):
        return []
    return [f"{where} must be a string or a language map with en"]


def bundle_problems(registry):
    """Every problem with the registry's bundles."""
    plugins = {entry["id"]: entry for entry in registry["plugins"]}
    verified = {key for key, publisher in registry["publishers"].items() if publisher.get("verified")}
    problems, seen = [], set()
    for index, bundle in enumerate(registry.get("bundles", [])):
        bundle_id = bundle.get("id")
        where = f"bundles.json: bundle {bundle_id or index}"
        if not isinstance(bundle_id, str) or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", bundle_id):
            problems.append(f"{where}: id must be lowercase words joined by '-'")
        elif bundle_id in seen:
            problems.append(f"{where}: id is used twice")
        seen.add(bundle_id)
        problems += text_problems(f"{where}: name", bundle.get("name"))
        problems += text_problems(f"{where}: summary", bundle.get("summary"))
        members = bundle.get("plugins")
        if not isinstance(members, list) or not members:
            problems.append(f"{where}: plugins must list at least one plugin")
            continue
        ids = set()
        for member in members:
            if not isinstance(member, dict):
                problems.append(f"{where}: each plugin must be {{\"id\", \"default\"}}")
                continue
            plugin_id = member.get("id")
            if not isinstance(member.get("default", True), bool):
                problems.append(f"{where}: {plugin_id}: default must be true or false")
            if plugin_id in ids:
                problems.append(f"{where}: {plugin_id} is listed twice")
            ids.add(plugin_id)
            entry = plugins.get(plugin_id)
            if entry is None:
                problems.append(f"{where}: {plugin_id} is not in the registry")
            elif entry.get("publisher") not in verified:
                problems.append(f"{where}: {plugin_id} is not from a verified publisher")
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    problems = category_problems()
    if problems:
        sys.exit("error: " + "\n       ".join(problems))
    registry = build_registry()
    problems = bundle_problems(registry)
    if problems:
        sys.exit("error: " + "\n       ".join(problems))
    expected = render(registry)
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
