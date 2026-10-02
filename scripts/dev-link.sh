#!/bin/sh
# Links plugins/<slug> into BashCut's user plugin folder for local testing (no release, no download).
#   scripts/dev-link.sh vieneu-tts          link
#   scripts/dev-link.sh vieneu-tts --remove unlink
# Open Plugins in BashCut and choose Trust once. Editing plugin.json or the entrypoint asks for Trust again;
# other files (for example a Python module the entrypoint runs) can change freely while you iterate.
set -eu
root="$(cd "$(dirname "$0")/.." && pwd)"
slug="${1:?usage: dev-link.sh <slug> [--remove]}"
source="$root/plugins/$slug"
id="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["id"])' "$source/plugin.json")"
target="$HOME/Library/Application Support/BashCut/Plugins/$id"
if [ "${2:-}" = "--remove" ]; then
    [ -L "$target" ] && rm "$target" && echo "Unlinked $id"
    exit 0
fi
if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "error: $target is an installed copy; remove it in BashCut first" >&2
    exit 1
fi
mkdir -p "$(dirname "$target")"
ln -sfn "$source" "$target"
echo "Linked $id → $source"
echo "Reopen Plugins in BashCut (or reopen the project), then choose Trust."
