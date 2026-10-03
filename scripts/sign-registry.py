#!/usr/bin/env python3
"""Signs registry versions that have no signature yet (archives published before signing existed).

    BASHCUT_SIGNING_KEY=… scripts/sign-registry.py

Each archive is downloaded from its release and checked against the registry SHA-256 first, so only the bytes users
actually get are signed.
"""
import hashlib
import json
import pathlib
import subprocess
import sys

from registry_tools import sign

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    path = ROOT / "registry.json"
    registry = json.loads(path.read_text())
    pending = [(p["id"], v) for p in registry["plugins"] for v in p["versions"] if not v.get("signature")]
    for plugin, version in pending:
        data = subprocess.run(["curl", "-fsSL", version["url"]], check=True, capture_output=True).stdout
        digest = hashlib.sha256(data).hexdigest()
        if digest != version["sha256"]:
            sys.exit(f"error: {plugin} {version['version']}: the published archive does not match registry.json")
    signatures = sign([v["sha256"] for _, v in pending])
    if pending and signatures is None:
        sys.exit("error: set BASHCUT_SIGNING_KEY")
    for (plugin, version), signature in zip(pending, signatures or []):
        version["signature"] = signature
        print(f"signed {plugin} {version['version']}")
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
