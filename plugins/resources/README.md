# Online Resources (`bashcut.resources`)

Search and download open resources into the BashCut library from one sheet (**Online resources**: the rail icon,
Plugins menu, or the Media, Audio, Stickers, Text and Filters panels): photos and video (Wikimedia, Openverse, NASA,
Internet Archive; Pexels and Pixabay with a key), music (Openverse), sound effects (Mixkit, Openverse; Freesound with a
key), illustrations (Open Peeps, Open Doodles, Humaaans, unDraw), emoji (Noto Animated, OpenMoji), logos (Simple
Icons), fonts (Fontsource, with a specimen of your text), LUT packs (G'MIC, RawTherapee) and Lottie animations
(useAnimations, Noto, LottieFiles; saved into the project's `media/lottie` for the HyperFrames `lottie` widget, as the
library refuses Lottie stickers). The library is searched
first and results already in it are marked; downloads are saved with tags (and audio is measured), so the agent finds
them with `library list` before fetching anything.

Every filter in the search row is labelled (Type, Source, Orientation, and Save to by the download button). Photo and
video searches start with the project's orientation (portrait for a 9:16 project), and an empty sheet offers three
example searches for the chosen type. While a search runs, placeholder tiles stand where the results will be.

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

Lottie sources (`scripts/fetch_lottie.py`, checked October 2026; keyless, reuse in videos allowed):

| Source | Licence | Where | Attribution |
| --- | --- | --- | --- |
| [useAnimations](https://useanimations.com/) (300 line icons) | MIT | npm `react-useanimations`, indexed once | not required |
| [Noto Animated Emoji](https://googlefonts.github.io/noto-emoji-animation/) | CC BY 4.0 | `fonts.gstatic.com/s/e/notoemoji/latest/<code>/lottie.json` | "Google (Noto Emoji)", CC BY 4.0 |
| [LottieFiles](https://lottiefiles.com/page/license) free animations | Lottie Simple License | public GraphQL search, per word | not required, kind: the creator |

LottieFiles' licence forbids compiling its files into a competing library, so only what a sheet shows is cached.
Left out: Lordicon (API key, attribution and plan limits), IconScout (API key), LottieFlow (no API). Sheet tiles are
drawn with rlottie (rlottie-python, LGPL-2.1, installed by setup, not bundled): a frame in milliseconds, no browser.

Tests: `python3 -m unittest discover -s plugins/resources/tests` (no network).
