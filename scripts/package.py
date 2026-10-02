#!/usr/bin/env python3
"""Packages one plugin folder and records it in registry.json.

    scripts/package.py <slug>                 # zip into dist/ and print the archive, size and SHA-256
    scripts/package.py <slug> --tag <tag>     # also check the tag is <slug>-v<version>
    scripts/package.py <slug> --register      # also add the version to registry.json (keeps the newest 3)

The archive holds one folder named after the plugin id, so BashCut can check it matches the registry entry.
"""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = os.environ.get("GITHUB_REPOSITORY", "dongnguyenvie/bashcut-plugins")
KEEP_VERSIONS = 3
LISTING_FIELDS = ("name", "nameVi", "summary", "summaryVi", "publisher", "category", "homepage")


def fail(message):
    sys.exit(f"error: {message}")


def manifest_for(slug):
    folder = ROOT / "plugins" / slug
    path = folder / "plugin.json"
    if not path.is_file():
        fail(f"no plugins/{slug}/plugin.json")
    manifest = json.loads(path.read_text())
    if manifest.get("schema") != "bashcut.plugin/1":
        fail("schema must be bashcut.plugin/1")
    if not re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)+", manifest.get("id", "")):
        fail("id must be reverse-domain style")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?", manifest.get("version", "")):
        fail("version must be semantic")
    entrypoint = folder / manifest.get("entrypoint", "")
    if not os.access(entrypoint, os.X_OK):
        fail(f"entrypoint {entrypoint} is missing or not executable")
    listing = json.loads((folder / "listing.json").read_text()) if (folder / "listing.json").is_file() else {}
    return folder, manifest, listing


def package(slug, folder, manifest):
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    archive = dist / f'{manifest["id"]}-{manifest["version"]}.zip'
    archive.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as staging:
        staged = pathlib.Path(staging) / manifest["id"]
        shutil.copytree(folder, staged, ignore=shutil.ignore_patterns("listing.json", "__pycache__", ".DS_Store", "tests"))
        subprocess.run(["ditto", "-c", "-k", "--norsrc", "--keepParent", str(staged), str(archive)], check=True)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (archive.parent / (archive.name + ".sha256")).write_text(f"{digest}  {archive.name}\n")
    return archive, digest


def register(slug, manifest, listing, archive, digest):
    path = ROOT / "registry.json"
    registry = json.loads(path.read_text())
    entry = next((p for p in registry["plugins"] if p["id"] == manifest["id"]), None)
    if entry is None:
        entry = {"id": manifest["id"], "versions": []}
        registry["plugins"].append(entry)
    entry.update({key: listing[key] for key in LISTING_FIELDS if key in listing})
    entry.setdefault("name", manifest["name"])
    entry.setdefault("publisher", "bashcut")
    entry["capabilities"] = manifest.get("capabilities", [])
    entry["actions"] = [a["id"] for a in manifest.get("contributes", {}).get("actions", [])]
    entry["hooks"] = [h if isinstance(h, str) else h["event"] for h in manifest.get("contributes", {}).get("hooks", [])]
    tag = f'{slug}-v{manifest["version"]}'
    version = {
        "version": manifest["version"],
        "apiVersion": manifest["apiVersion"],
        "minApiVersion": manifest.get("minApiVersion", manifest["apiVersion"]),
        "minAppVersion": listing.get("minAppVersion", "0.0.1"),
        "platforms": listing.get("platforms", ["macos-arm64", "macos-x86_64"]),
        "url": f"https://github.com/{REPO}/releases/download/{tag}/{archive.name}",
        "sha256": digest,
        "signature": None,
        "size": archive.stat().st_size,
        "downloadBytes": listing.get("downloadBytes", 0),
        "releasedAt": datetime.date.today().isoformat(),
    }
    if any(v["version"] == version["version"] and v["sha256"] != digest for v in entry["versions"]):
        fail(f'{manifest["id"]} {version["version"]} is already registered with a different archive')
    entry["versions"] = [v for v in entry["versions"] if v["version"] != version["version"]] + [version]
    entry["versions"].sort(key=lambda v: [int(x) if x.isdigit() else x for x in re.split(r"[.+-]", v["version"])])
    entry["versions"] = entry["versions"][-KEEP_VERSIONS:]
    registry["plugins"].sort(key=lambda p: p["id"])
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("--tag")
    parser.add_argument("--register", action="store_true")
    args = parser.parse_args()
    folder, manifest, listing = manifest_for(args.slug)
    if args.tag and args.tag != f'{args.slug}-v{manifest["version"]}':
        fail(f'tag {args.tag} does not match {args.slug}-v{manifest["version"]}')
    archive, digest = package(args.slug, folder, manifest)
    if args.register:
        register(args.slug, manifest, listing, archive, digest)
    print(json.dumps({"archive": str(archive), "sha256": digest, "size": archive.stat().st_size}))


if __name__ == "__main__":
    main()
