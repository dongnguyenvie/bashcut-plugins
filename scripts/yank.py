#!/usr/bin/env python3
"""Withdraws (or restores) a published version: edits plugins/<slug>/versions.json and regenerates registry.json.

    scripts/yank.py <plugin-id> <version> "<reason shown to users>"
    scripts/yank.py <plugin-id> <version> --undo

BashCut never offers a yanked version; users who have it see the reason and Updates offers the newest good one.
The GitHub Release stays, so the archive and its checksum remain inspectable; a yanked version is never re-published
with different contents.
"""
import argparse
import sys

from registry_tools import load_versions, save_versions, slug_for, write_registry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plugin")
    parser.add_argument("version")
    parser.add_argument("reason", nargs="?")
    parser.add_argument("--undo", action="store_true")
    args = parser.parse_args()
    if not args.undo and not (args.reason or "").strip():
        sys.exit("error: give a reason users will see, or --undo")
    slug = slug_for(args.plugin)
    data = load_versions(slug)
    version = next((v for v in data["versions"] if v["version"] == args.version), None)
    if version is None:
        sys.exit(f"error: {args.plugin} {args.version} is not in plugins/{slug}/versions.json")
    if args.undo:
        version.pop("yanked", None)
    else:
        version["yanked"] = args.reason.strip()
    save_versions(slug, data)
    write_registry()
    state = "restored" if args.undo else f"yanked: {version['yanked']}"
    print(f"{args.plugin} {args.version} {state}")


if __name__ == "__main__":
    main()
