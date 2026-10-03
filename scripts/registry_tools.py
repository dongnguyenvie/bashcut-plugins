"""Helpers shared by the registry scripts: signing digests with the BashCut key."""
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


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
