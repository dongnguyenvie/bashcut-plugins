"""Helpers shared by the registry scripts.

Sources of truth (edited by the scripts, reviewed in PRs):

    publishers.json                 schemaVersion and publishers
    plugins/<slug>/versions.json    one plugin's listing at its last release and its published versions

registry.json, the file BashCut downloads, is generated from them by `build_registry` (scripts/build-registry.py):
a release or a yank only touches its own plugin's versions.json, so concurrent changes to different plugins never
conflict, and a conflict in registry.json is fixed by generating it again.
"""
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERSIONS = "versions.json"
# Entry fields in registry order; `id` and `versions` come first.
LISTING_KEYS = ("name", "summary", "publisher", "category", "homepage", "capabilities", "actions", "hooks")


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def versions_path(slug):
    return ROOT / "plugins" / slug / VERSIONS


def load_versions(slug):
    """The plugin's versions.json, or None before its first release."""
    path = versions_path(slug)
    return json.loads(path.read_text()) if path.is_file() else None


def save_versions(slug, data):
    write_json(versions_path(slug), data)


def slug_for(plugin_id):
    """The folder of a published plugin id."""
    for path in sorted((ROOT / "plugins").glob(f"*/{VERSIONS}")):
        if json.loads(path.read_text()).get("id") == plugin_id:
            return path.parent.name
    sys.exit(f"error: no plugins/*/{VERSIONS} for {plugin_id}")


def build_registry():
    """registry.json as BashCut reads it: publishers plus every plugin with at least one version, sorted by id."""
    header = json.loads((ROOT / "publishers.json").read_text())
    plugins = []
    for path in sorted((ROOT / "plugins").glob(f"*/{VERSIONS}")):
        data = json.loads(path.read_text())
        if not data.get("versions"):
            continue
        entry = {"id": data["id"], "versions": data["versions"]}
        entry.update({key: data["listing"][key] for key in LISTING_KEYS if key in data.get("listing", {})})
        plugins.append(entry)
    plugins.sort(key=lambda entry: entry["id"])
    return {"schemaVersion": header["schemaVersion"], "publishers": header["publishers"], "plugins": plugins}


def render(registry):
    return json.dumps(registry, indent=2, ensure_ascii=False) + "\n"


def write_registry():
    (ROOT / "registry.json").write_text(render(build_registry()))


def sign(digests):
    """`ed25519:BASE64` signatures for SHA-256 hex digests, or None when BASHCUT_SIGNING_KEY is not set."""
    if not os.environ.get("BASHCUT_SIGNING_KEY") or not digests:
        return None
    out = subprocess.run(["swift", str(ROOT / "scripts" / "sign.swift"), *digests], check=True,
                         capture_output=True, text=True)
    signatures = out.stdout.split()
    if len(signatures) != len(digests):
        sys.exit("error: sign.swift returned the wrong number of signatures")
    return signatures
