#!/usr/bin/env python3
"""Packages one plugin folder and records it in registry.json.

    scripts/package.py <slug>                 # zip into dist/ and print the archive, size and SHA-256
    scripts/package.py <slug> --tag <tag>     # also check the tag is <slug>-v<version>
    scripts/package.py <slug> --register      # also record the version in plugins/<slug>/versions.json (keeps the
                                              # newest 3) and regenerate registry.json

The archive holds one folder named after the plugin id, so BashCut can check it matches the registry entry. With
BASHCUT_SIGNING_KEY set (the release workflow's secret), the archive's SHA-256 is signed with the BashCut ed25519
key: the signature goes into registry.json and next to the archive as `<archive>.sig`.
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

from plugin_manifest import CATEGORIES
from registry_tools import load_versions, save_versions, sign, write_registry

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = os.environ.get("GITHUB_REPOSITORY", "dongnguyenvie/bashcut-plugins")
KEEP_VERSIONS = 3
LISTING_FIELDS = ("name", "summary", "publisher", "category", "homepage")
LOCALIZED_FIELDS = ("name", "summary")
# Tools every Mac has without Xcode, Homebrew or Python. `python3`, `git`, `swift`, `make` and `clang` are left out
# on purpose: on a fresh Mac they are shims that ask to install the Command Line Tools.
MACOS_BUILT_INS = {
    "sh", "bash", "zsh", "env", "curl", "tar", "gzip", "unzip", "ditto", "xattr", "shasum", "codesign",
    "afconvert", "afinfo", "afplay", "sips", "osascript", "plutil", "defaults", "mdls", "say", "avconvert",
}


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
    build(folder)
    entrypoint = folder / manifest.get("entrypoint", "")
    if not os.access(entrypoint, os.X_OK):
        fail(f"entrypoint {entrypoint} is missing or not executable")
    listing = json.loads((folder / "listing.json").read_text()) if (folder / "listing.json").is_file() else {}
    check_localized(manifest, "plugin.json")
    check_dependencies(manifest)
    for field in LOCALIZED_FIELDS:
        if field in listing:
            check_text(listing[field], f"listing.json {field}")
    for source, value in (("plugin.json", manifest.get("category")), ("listing.json", listing.get("category"))):
        if value is not None and value not in CATEGORIES:
            fail(f"{source} category must be one of {', '.join(CATEGORIES)}")
    return folder, manifest, listing


def check_dependencies(manifest):
    """Users never install tools by hand: a dependency is a macOS built-in or has an install recipe."""
    for dependency in manifest.get("dependencies", []):
        probe = dependency.get("probe", {}).get("executable", "")
        bundled = "/" in probe
        if dependency.get("install") or bundled or probe in MACOS_BUILT_INS:
            continue
        fail(f'dependency {dependency.get("id")}: "{probe}" is not on every Mac; bundle it, add an install '
             f'recipe that downloads it into BASHCUT_PLUGIN_DATA, or drop it')


def build(folder):
    """Runs the plugin's build.sh (compiled helpers) when it has one."""
    script = folder / "build.sh"
    if script.is_file():
        # Build output goes to stderr: stdout carries only the JSON result the release workflow reads.
        subprocess.run([str(script)], check=True, stdout=sys.stderr)


def check_text(value, where):
    """Display text is a string (English) or {"en": ..., "vi": ...}; several languages need "en"."""
    if isinstance(value, str):
        ok = bool(value.strip())
    else:
        ok = (isinstance(value, dict) and value and (len(value) == 1 or "en" in value)
              and all(re.fullmatch(r"[a-z]{2,3}(-[A-Za-z0-9]{2,8})?", k) and isinstance(v, str) and v.strip()
                      for k, v in value.items()))
    if not ok:
        fail(f"{where} must be a nonempty string or a language map with \"en\"")


def check_localized(manifest, where):
    """Checks every display field and rejects the old *Vi fields."""
    check_text(manifest.get("name"), f"{where} name")
    items = list(manifest.get("options", []))
    for action in manifest.get("contributes", {}).get("actions", []):
        items.append(action)
        items.extend(action.get("params", []))
    for item in items:
        if any(key.endswith("Vi") for key in item):
            fail(f'{where} {item.get("id")}: use "title": {{"en": ..., "vi": ...}} instead of *Vi fields')
        for field in ("title", "help", "confirm"):
            if field in item:
                check_text(item[field], f'{where} {item.get("id")} {field}')


def package(slug, folder, manifest):
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    archive = dist / f'{manifest["id"]}-{manifest["version"]}.zip'
    archive.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as staging:
        staged = pathlib.Path(staging) / manifest["id"]
        shutil.copytree(folder, staged, ignore=shutil.ignore_patterns(
            "listing.json", "versions.json", "__pycache__", ".DS_Store", "tests", "src", "build.sh",
            # Node build inputs: build.sh bundles src/ and its locked dependencies into one file that ships instead.
            "node_modules", "package.json", "package-lock.json", "tsconfig.json"))
        subprocess.run(["ditto", "-c", "-k", "--norsrc", "--keepParent", str(staged), str(archive)], check=True)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (archive.parent / (archive.name + ".sha256")).write_text(f"{digest}  {archive.name}\n")
    signature = (sign([digest]) or [None])[0]
    signature_file = archive.parent / (archive.name + ".sig")
    signature_file.unlink(missing_ok=True)
    if signature:
        signature_file.write_text(signature + "\n")
    return archive, digest, signature


def register(slug, manifest, listing, archive, digest, signature):
    existing = load_versions(slug)
    if existing and existing.get("id") != manifest["id"]:
        fail(f'plugins/{slug}/versions.json is for {existing.get("id")}, not {manifest["id"]}')
    # The listing is rebuilt from the released listing and manifest each time, so renamed or removed fields never
    # linger; only the version history carries over. Unreleased changes on main stay out of the registry.
    entry = {"versions": existing["versions"] if existing else []}
    entry.update({key: listing[key] for key in LISTING_FIELDS if key in listing})
    entry.setdefault("name", manifest["name"])
    for field in LOCALIZED_FIELDS:
        if isinstance(entry.get(field), str):
            entry[field] = {"en": entry[field]}
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
        "signature": signature,
        "size": archive.stat().st_size,
        "downloadBytes": listing.get("downloadBytes", 0),
        "releasedAt": datetime.date.today().isoformat(),
    }
    if any(v["version"] == version["version"] and v["sha256"] != digest for v in entry["versions"]):
        fail(f'{manifest["id"]} {version["version"]} is already registered with a different archive')
    if any(v["version"] == version["version"] and v.get("yanked") for v in entry["versions"]):
        fail(f'{manifest["id"]} {version["version"]} was yanked; bump the version')
    entry["versions"] = [v for v in entry["versions"] if v["version"] != version["version"]] + [version]
    entry["versions"].sort(key=lambda v: [int(x) if x.isdigit() else x for x in re.split(r"[.+-]", v["version"])])
    entry["versions"] = entry["versions"][-KEEP_VERSIONS:]
    versions = entry.pop("versions")
    save_versions(slug, {"id": manifest["id"], "listing": entry, "versions": versions})
    write_registry()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("--tag")
    parser.add_argument("--register", action="store_true")
    args = parser.parse_args()
    folder, manifest, listing = manifest_for(args.slug)
    if args.tag and args.tag != f'{args.slug}-v{manifest["version"]}':
        fail(f'tag {args.tag} does not match {args.slug}-v{manifest["version"]}')
    archive, digest, signature = package(args.slug, folder, manifest)
    if args.register:
        register(args.slug, manifest, listing, archive, digest, signature)
    print(json.dumps({"archive": str(archive), "sha256": digest, "size": archive.stat().st_size,
                      "signed": signature is not None}))


if __name__ == "__main__":
    main()
