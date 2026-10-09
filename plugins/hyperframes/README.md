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
- **`bin/hf`**: the pinned HyperFrames CLI with telemetry off and the plugin's own Chrome: `catalog`, `add`, `lint`,
  `check`, `snapshot` (frames to look at, optionally against a reference video), `docs`.
- **`examples/`**: starting points that pass `hf lint`: `keyword-pop`, `stat-counter`, `cursor-click`,
  `paper-card`, `checklist-card`.
- **The skill** `skills/hyperframes/SKILL.md`: the design → build → look → render → place → check loop, the
  composition rules, and moves that combine a graphic with BashCut's own layers (the speaker shrinking into a card).

## Dependencies

**Install Dependencies…** runs `bin/setup` after the user approves:

1. Node.js 22.19+: one already on the Mac (Homebrew, nvm, Volta, BashCut's shared folder), or the official Node.js 22
   LTS from nodejs.org, checked against its SHA-256, into `BASHCUT_SHARED_DATA/node`.
2. HyperFrames 0.8.140 and GSAP 3.14.2 with `npm ci` from `runtime/package-lock.template.json` into
   `BASHCUT_PLUGIN_DATA/runtime` (about 130 MB).
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
