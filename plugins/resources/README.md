# Online Resources (`bashcut.resources`)

Search and download open resources into the BashCut library from one browser window (**Online resources**: the rail icon,
Plugins menu, or the Media, Audio, Stickers, Text and Filters panels): photos and video (Wikimedia, Openverse, NASA,
Internet Archive; Pexels and Pixabay with a key), music (Openverse), sound effects (Mixkit, Openverse; Freesound with a
key), illustrations (Open Peeps, Open Doodles, Humaaans, unDraw), emoji (Noto Animated, OpenMoji), logos (Simple
Icons), fonts (Fontsource, with a specimen of your text), LUT packs (G'MIC, RawTherapee) and Lottie animations
(useAnimations, Noto, LottieFiles; saved into the project's `media/lottie` for the HyperFrames `lottie` widget, as the
library refuses Lottie stickers). The library is searched
first and results already in it are marked; downloads are saved with tags (and audio is measured), so the agent finds
them with `library list` before fetching anything.

Since 0.0.5 (BashCut plugin API 11) the browser is a non-modal window, so the editor stays usable behind it, with
**Dock** to show it over the viewer instead. It has three columns: the types (Photos, Video, Music, SFX, Fonts, LUTs,
Illustrations, Emoji, Logos, Lottie) and the chosen type's sources on the left; a large search field, labelled
filters (Orientation starts with the project's shape, portrait for a 9:16 project) and recent searches above the
results grid in the middle; and an inspector on the right with a big preview, licence, author, source, size and fit
(whether the picture fills the project frame or is cropped), plus **Add to timeline** (download, then place at the
playhead), **Add to project** and **Save to library** (My library, on this Mac). Drag a result onto the timeline and
it is downloaded and placed where it was dropped; the window stays open. The query, results, selection and recent
searches are kept when the window closes, until the project closes. An empty browser offers three example searches
for the chosen type, and placeholder tiles stand where results will be while a search runs. Licence and author are
shown for you to check; nothing is written on the video (credits stay optional).

Older BashCut apps (plugin API 8–10) keep 0.0.4, the sheet version, through `minApiVersion`.

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
