# Online Resources (`bashcut.resources`)

Search and download open resources into the BashCut library from one sheet (**Online resources**: the rail icon,
Plugins menu, or the Media, Audio, Stickers, Text and Filters panels): photos and video (Wikimedia, Openverse, NASA,
Internet Archive; Pexels and Pixabay with a key), music (Openverse), sound effects (Mixkit, Openverse; Freesound with a
key), illustrations (Open Peeps, Open Doodles, Humaaans, unDraw), emoji (Noto Animated, OpenMoji), logos (Simple
Icons), fonts (Fontsource, with a specimen of your text) and LUT packs (G'MIC, RawTherapee). The library is searched
first and results already in it are marked; downloads are saved with tags (and audio is measured), so the agent finds
them with `library list` before fetching anything.

One implementation for people and agents: `scripts/fetch_*.py` are the fetchers the agent kit runs (its skills keep
thin shims that run these files), and every button is an action:

```sh
bashcut plugins run bashcut.resources.search   --params '{"kind": "photo", "query": "coffee"}'
bashcut plugins run bashcut.resources.download --params '{"kind": "photo", "query": "coffee", "ids": "wikimedia-41936"}'
bashcut plugins run bashcut.resources.fetch    --params '{"script": "audio", "args": "--dest /abs/media/audio --sfx whoosh"}'
bashcut plugins show-view bashcut.resources --view browse
```

Inside the plugin the scripts' `bashcut …` calls go through `bin/bridge/bashcut` to the session, which runs them as
the host call `cli` (checked by BashCut like any plugin call). Previews and downloads are kept in
`BASHCUT_SHARED_CACHE/resources`; indexes stay in `BASHCUT_SHARED_DATA` as the scripts keep them. API keys are secret
options (Settings › Plugins › Online Resources › Options), never environment variables of the app.

Tests: `python3 -m unittest discover -s plugins/resources/tests` (no network).
