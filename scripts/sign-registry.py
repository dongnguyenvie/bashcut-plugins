#!/usr/bin/env python3
"""Signs published versions (plugins/<slug>/versions.json) that have no signature yet (archives published before signing existed).

    BASHCUT_SIGNING_KEY=… scripts/sign-registry.py

Each archive is downloaded from its release and checked against the registry SHA-256 first, so only the bytes users
actually get are signed.
"""
import hashlib
import json
import subprocess
import sys

from registry_tools import ROOT, VERSIONS, sign, write_json, write_registry


def main():
    sources = {path: json.loads(path.read_text()) for path in sorted((ROOT / "plugins").glob(f"*/{VERSIONS}"))}
    pending = [(data["id"], v) for data in sources.values() for v in data["versions"] if not v.get("signature")]
    for plugin, version in pending:
        data = subprocess.run(["curl", "-fsSL", version["url"]], check=True, capture_output=True).stdout
        digest = hashlib.sha256(data).hexdigest()
        if digest != version["sha256"]:
            sys.exit(f"error: {plugin} {version['version']}: the published archive does not match versions.json")
    signatures = sign([v["sha256"] for _, v in pending])
    if pending and signatures is None:
        sys.exit("error: set BASHCUT_SIGNING_KEY")
    for (plugin, version), signature in zip(pending, signatures or []):
        version["signature"] = signature
        print(f"signed {plugin} {version['version']}")
    for path, data in sources.items():
        write_json(path, data)
    write_registry()


if __name__ == "__main__":
    main()
