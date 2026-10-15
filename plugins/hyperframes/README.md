# HyperFrames Graphics

Animated graphics of any design for BashCut, made with [HyperFrames](https://github.com/heygen-com/hyperframes)
(Apache-2.0): a composition is HTML/CSS + GSAP, rendered frame by frame in headless Chrome. The plugin gives agents
the tools and leaves the design to them; the agent kit's `bc:motion-graphics` decides when a sentence needs a
graphic, the plugin's skill (`bashcut.hyperframes:hyperframes`) says how to make one.

Plugin id `bashcut.hyperframes`, plugin API 7, Node.js.

## What it adds

- **`graphics.render`** (provider `bashcut.hyperframes.render`): a composition folder → a `.mov` with alpha (HEVC
  with alpha, or ProRes 4444) in the request's output folder, with the composition's lint findings. Agents call it
  with `bashcut plugins invoke graphics.render --params '{"composition": "/abs/folder", "variables": {…}}'`.
- **`bin/graphic`**: one call per graphic for agents. `place D --at-frame F --set k=v` renders composition D, waits,
  places the .mov full canvas on the Overlay layer (`library add` + `library place`) and records the render inputs on
  the media (`setMediaData` › `graphics`). `rerender ITEM --set k=v` (or `--all`) renders again from those inputs and
  points every item at the new movie as one `timeline apply` (`addMedia` with alpha, `setSource`, `trim` when the
  length changed, which the result reports). Both fill the standard variables (`accent`, `background`, `text`,
  `secondary`, `headingFont`, `bodyFont`, `disclosure`) from the project's `brand`, explicit values winning, so a brand
  change restyles placed graphics with `rerender --all --brand`. Uses `$BASHCUT_CLI`, else `bashcut` on PATH.
  A composition that declares `mascot` gets the brand's mascot pose (`--set pose=thinking`; five examples have one).
- **`bin/hf`**: the pinned HyperFrames CLI with telemetry off and the plugin's own Chrome: `catalog`, `add`, `lint`,
  `check`, `snapshot` (frames to look at, optionally against a reference video), `docs`.
- **`bin/osm-map`**: an OpenStreetMap map and a route for a composition: tiles (cached in the plugin cache folder)
  and `map-data.js` in canvas pixels, plus `km`, `minutes` and per-stop legs as JSON. Routes from OSRM on
  routing.openstreetmap.de (FOSSGIS); tiles from tile.openstreetmap.org with the plugin's User-Agent, two at a time,
  under the [tile usage policy](https://operations.osmfoundation.org/policies/tiles/). Map data © OpenStreetMap
  contributors (ODbL), kept as `attribution` in the data; `map-route` and `amenity-radius` draw no credit unless their
  `credit` variable is set (only when the user asks). `--amenities` counts schools,
  hospitals, malls, parks… around the first point with one Overpass API query (90 s timeout, cached, same User-Agent).
  Strict tags (`AMENITIES` and `EXCLUDE` in `lib/osm-map.mjs`): `hospital` = `amenity=hospital` or
  `healthcare=hospital` but never a clinic, doctor, dentist or pharmacy, by tag or by name ("Phòng khám", "Nha khoa",
  "Dental"…), which counts as `clinic` when asked; `school` = `amenity=school` without driving or language centres
  (`driving_school`, `language_school`); `mall` = `shop=mall|department_store` (not `supermarket`); `park` =
  `leisure=park`, not private ones, gardens or playgrounds.
- **`examples/`**: starting points that pass `hf lint` and `hf check`: `keyword-pop`, `stat-counter`,
  `cursor-click`, `paper-card`, `checklist-card`, and the data widgets explainers build scenes from: `bar-chart`,
  `cost-table`, `timeline`, `calendar`, `map-route`, `amenity-radius`; mock screens (`mock-video-app`) and cards such as
  `corner-curl-card`; diagrams laid out from JSON data (`flow-diagram`, `mind-map`, `isometric-system`, and
  `big-canvas`, one hand-drawn canvas for a whole video with a camera path) and science widgets (`formula` with
  KaTeX, `matrix-grid`, `scale-compare`); `lottie` plays one Lottie accent picked with resources'
  `fetch_lottie.py`. All take the brand variables `bin/graphic` fills. Those with `data-fit="canvas"` render at the
  project's size (9:16 or 16:9); the diagrams share `lib/diagram.js` and `amenity-radius` uses `lib/amenity-map.js`
  (markers that would touch merge into a count or are nudged apart with a leader line), which `graphics.render` copies
  next to the page like GSAP.
- **The skill** `skills/hyperframes/SKILL.md`: the design → build → look → render → place → check loop, the
  composition rules, and moves that combine a graphic with BashCut's own layers (the speaker shrinking into a card).

## Dependencies

**Install Dependencies…** runs `bin/setup` after the user approves:

1. Node.js 22.19+: one already on the Mac (Homebrew, nvm, Volta, BashCut's shared folder), or the official Node.js 22
   LTS from nodejs.org, checked against its SHA-256, into `BASHCUT_SHARED_DATA/node`.
2. HyperFrames 0.8.140, GSAP 3.14.2, KaTeX 0.16.47 and lottie-web 5.13.0 (MIT; copied into a `formula` or
   `lottie` composition at render, so it needs no network) with `npm ci` from `runtime/package-lock.template.json`
   into `BASHCUT_PLUGIN_DATA/runtime` (about 135 MB).
3. Chrome headless shell (HyperFrames' `browser ensure`) into `BASHCUT_PLUGIN_CACHE/chrome` (about 210 MB).

No FFmpeg is needed: HyperFrames writes RGBA PNG frames and `bin/encode-alpha` (built from `src/encode-alpha.swift`
by `build.sh`, AVFoundation) encodes them. Telemetry is off in every run (`HYPERFRAMES_NO_TELEMETRY`, `DO_NOT_TRACK`).
GSAP has its own free licence and is installed, not bundled.

To move to another HyperFrames version, change `runtime/package.template.json`, regenerate the lockfile
(`npm install --package-lock-only` in a copy named `package.json`) and run `bin/setup` again.

## Test

```sh
./build.sh
python3 -m unittest discover -s tests -v
# with a runtime bin/setup installed somewhere, the live render test too:
HYPERFRAMES_TEST_DATA=<data> HYPERFRAMES_TEST_CACHE=<cache> python3 -m unittest discover -s tests -v
```

## Try it in BashCut

```sh
scripts/dev-link.sh hyperframes            # from the repo root; then Plugins › Trust and Install Dependencies…
scripts/dev-link.sh hyperframes --remove
```
