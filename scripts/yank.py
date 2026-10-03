#!/usr/bin/env python3
"""Withdraws (or restores) a published version in registry.json.

    scripts/yank.py <plugin-id> <version> "<reason shown to users>"
    scripts/yank.py <plugin-id> <version> --undo

BashCut never offers a yanked version; users who have it see the reason and Updates offers the newest good one.
The GitHub Release stays, so the archive and its checksum remain inspectable; a yanked version is never re-published
with different contents.
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plugin")
    parser.add_argument("version")
    parser.add_argument("reason", nargs="?")
    parser.add_argument("--undo", action="store_true")
    args = parser.parse_args()
    if not args.undo and not (args.reason or "").strip():
        sys.exit("error: give a reason users will see, or --undo")
    path = ROOT / "registry.json"
    registry = json.loads(path.read_text())
    entry = next((p for p in registry["plugins"] if p["id"] == args.plugin), None)
    version = next((v for v in (entry or {}).get("versions", []) if v["version"] == args.version), None)
    if version is None:
        sys.exit(f"error: {args.plugin} {args.version} is not in registry.json")
    if args.undo:
        version.pop("yanked", None)
    else:
        version["yanked"] = args.reason.strip()
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n")
    state = "restored" if args.undo else f"yanked: {version['yanked']}"
    print(f"{args.plugin} {args.version} {state}")


if __name__ == "__main__":
    main()
