"""Only non-secret preferences and cache references are stored here."""
import json
import os
import threading
import tempfile
from pathlib import Path

LOCK = threading.RLock()


def folder(cache=False):
    key = 'BASHCUT_PLUGIN_CACHE' if cache else 'BASHCUT_PLUGIN_DATA'
    fallback = Path.home() / ('Library/Caches/BashCut/PluginData' if cache else
                               'Library/Application Support/BashCut/PluginData') / 'bashcut.ai-media-studio'
    path = Path(os.environ.get(key, fallback))
    path.mkdir(parents=True, exist_ok=True)
    return path


def read():
    with LOCK:
        try:
            return json.loads((folder() / 'preferences.json').read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}


def update(**patch):
    # Explicit allowlist: API credentials and option dictionaries never touch disk.
    allowed = {'selectedVoice', 'favorites', 'lastTake', 'watermark', 'lastFolders'}
    if not patch.keys() <= allowed:
        raise ValueError('Unsupported preference.')
    with LOCK:
        value = read()
        value.update(patch)
        with tempfile.NamedTemporaryFile('w', dir=folder(), delete=False) as handle:
            json.dump(value, handle, ensure_ascii=False)
            tmp = handle.name
        os.replace(tmp, folder() / 'preferences.json')
    return value
