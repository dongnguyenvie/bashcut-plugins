---
name: hyperframes
description: Design and render any animated graphic for a BashCut edit with HyperFrames — kinetic type and keyword pops, stat counters, bar charts, cost tables, timelines, calendars of good months or days, a map with a route drawn from OpenStreetMap, a pointer that clicks, mock screens, full-frame paper or colour cards, lower thirds, quote cards, diagrams and other blocks — as an HTML/CSS + GSAP composition you write or assemble, looked at frame by frame, rendered to a .mov with alpha and placed on the timeline; plus the speaker-shrinks-into-a-card move done with BashCut's own layers. Use when bc:motion-graphics decided a sentence needs a graphic, when native text cannot make the look, or when the user wants the graphics of a reference video. Triggers: "đồ hoạ", "motion graphic", "chữ chuyển động", "kinetic text", "số chạy", "counter", "biểu đồ", "bản đồ", "tuyến đường", "bảng chi phí", "timeline", "lịch", "tháng đẹp", "con trỏ chuột", "thẻ giấy", "thu nhỏ người nói", "làm giống video mẫu", "hyperframes".
---

# HyperFrames graphics

Reply in the user's language. This plugin gives you hands, not a style: HyperFrames renders whatever HTML, CSS and
GSAP you write, deterministically, frame by frame. Design each graphic for this video, from what the speaker says and
how the reference or the channel looks (`bc:style-study` profile, reference frames), not from the examples' looks.
Whether a sentence needs a graphic, when it lands and how long it holds is `bc:motion-graphics`; this skill is how
to make it.

## 1. What you have

`P` is this plugin's folder: `P="$HOME/Library/Application Support/BashCut/Plugins/bashcut.hyperframes"` (where
BashCut installs it; this SKILL.md may be a copy elsewhere).

| Tool | What it does |
|---|---|
| `"$P/bin/hf" catalog [words] --json` | Search 392 ready blocks and components (transitions, typography, captions, overlays, lower thirds, data, mock UI, cursors, counters, shaders, 3D) |
| `"$P/bin/hf" add NAME --dir D` | Install one into composition folder D (`compositions/…/NAME.html`); mount it with `data-composition-src`. It also copies a snippet to the clipboard |
| `"$P/bin/hf" lint D` / `check D` | Validate; `check` also runs it in Chrome and measures contrast and overflow |
| `"$P/bin/hf" snapshot D --at 0.3,0.8,1.6 --no-end -o OUT` | PNG frames and a `contact-sheet.jpg` to look at; `--against ref.mp4` pairs each with a reference frame; `--zoom "#card"` crops one element sharp |
| `"$P/bin/hf" docs compositions\|data-attributes\|gsap` | The runtime's own rules |
| `"$P/bin/hf" --gsap` | Path of GSAP to copy next to `index.html` (render copies it when missing) |
| `"$P/bin/graphic" examples [NAME]` | One line per example: what it draws, seconds, its own variables as `id:type` (the brand ids apart): choose without reading HTML. With NAME every variable's label and default, its `pitfalls` and the active `lessons` tagged `block:NAME` |
| `"$P/bin/graphic" plan [--only g1,g2]` | Renders every `plan.cut` graphic with `render` {composition, set, frame} to the span plan check gives it, imports the movies, writes their media into plan.cut and runs `plan apply`: an edit made of graphics in one call. A `set` value `"@words"` is the seconds from the graphic's start to those words in the voiceover; unchanged graphics are not rendered again |
| `--frame JSON` (`place`, `rerender`) / `render.frame` (`plan`) | Chrome drawn around any composition while it renders, no HTML edit: `backdrop` `"texture"`\|`"paper"`\|`"plain"` (full frame, brand background; texture adds accent glows and a faint grid, paper adds grain, fibres and a vignette: kraft with a kraft-brown brand background, notebook with a cream one), `fadeIn` s, `drift` true (backdrop pans, widget slides a few px), `float` true (after ~1.2 s the widget bobs and breathes to the end: a held card passes review's frozen-picture check; drift alone does not), `chip` (`"2/4"`, top left), `credit` (source line above the chip), `callout` {text, at, top} (a plate under the widget, or over it when there is no room, landing at `at`, `"@words"` in plan; `*word*` in the accent), `scale` 0.5–2.5 (widget size, kept 60 px inside). Brand colours and fonts apply; chip and credit move to the right, or push the widget down, when they would cover it. `rerender --frame '{"chip":"3/4","scale":null}'` changes keys |
| `"$P/bin/graphic" place D --at-frame F [--set k=v …]` | Render, wait and place full canvas on the Overlay layer in one call; records the inputs on the media. `rerender ITEM [--set k=v …]` renders it again with changed data and swaps every use in one undo step |
| `--set data=@file.json` + `--steps-from voice\|sections` (`place`) | The JSON-data widgets: write the data to a file, never HTML or coordinates (the script lays out for 9:16 or 16:9). `--steps-from voice` gives step i the start of the i-th voice line from `--at-frame` on (`sections`: section markers); `"at": "line:3"` / `"section:Label"` picks one; without `--at-frame`/`--duration` the graphic starts 0.4 s before the first step and ends after the last line. One widget = one `place` call; `rerender ITEM --set data=@file.json` with a changed label keeps the step times |
| flow-diagram, mind-map, isometric-system | Data `{title, nodes:[{id,label,icon?,group?}], edges:[{from,to,label?}], steps:[{focus:[ids], reveal:[ids], note?}]}`: flow = layered boxes (`direction` lr\|tb), mind-map = centre + branches (`root`, `--set sketch=true` hand-drawn), isometric = blocks on a grid with packets. A node in no `reveal` shows from the start; `focus` lights it and dims the rest until the next step; packets run on its edges. ≤12 nodes, labels 1–3 words; one diagram per section, steps = its voice lines |
| big-canvas | A whole video as one hand-drawn canvas (mind-map data + `stops:[{focus: id, note?}]`, `summary`): the pen draws each branch as the camera lands on it, ends zoomed out on the whole map. Place once over the full span (`--steps-from voice` or `sections`, `--duration` = video length); give each stop ≥ 2 s; a 60 s render takes about a minute. Look at one contact sheet (`hf snapshot --frames 8`), not frame by frame |
| formula, matrix-grid, scale-compare, bar-chart rows | formula: `{latex, steps:[{terms:[ids], note}]}`, mark terms `\\hl{id}{tex}` (KaTeX, no network). matrix-grid: `{rows, cols, values:[[…]], order, steps:[{row\|col\|cell:[r,c], note}]}`. scale-compare: `{start, factor, count, units, refs:[{label,value}], steps:[{at start},{at end}]}`, numbers from your source. bar-chart `--set layout=rows --set look=paper --set highlight=N`: a paper benchmark table with one row banded |
| `"$P/bin/osm-map" --dir D --points "lat,lon,Name;…" [--route car\|bike\|foot\|none] [--places "Name, City;…"]` | OpenStreetMap tiles and a real route into composition D (`map/`, `map-data.js` in canvas pixels; `--width`/`--height` = the project). Prints `km`, `minutes` and per-stop `legs` to put on screen. `--places` looks named places up (Nominatim) and prints each one's `areaHa`, `areaKm2`, `perimeterKm`; with `--dir` their outlines go into `MAP_DATA.places` (drawn by `map-route`). `--places` alone, without `--dir`, only measures. Needs network; the render then needs none. Coordinates come from the user, the brief or a source you name, never from memory |
| `$P/examples/` | Raw material, each lint-clean: keyword-pop, stat-counter, cursor-click, paper-card, checklist-card, bar-chart, cost-table, timeline, calendar, map-route (run `osm-map` on the copy first), headline-reveal, quote-card, lower-third, spotlight-card, logo-lockup, progress-ring, stack-list, typewriter-doc, focus-frame, mock-video-app (never a real platform's brand), corner-curl-card, flow-diagram, mind-map, isometric-system, big-canvas, formula, matrix-grid, scale-compare. `graphic examples` says what each draws. The data widgets take their rows as a JSON list with an `at` per row: the second from the overlay's start when that row lands on its word |

When `bin/hf` exits 3 or the render says `dependency_missing`, the user chooses **Install Dependencies…** for
HyperFrames Graphics in Plugins (you cannot); say so and fall back to native text.

## 2. The loop: design, build, look, render, place, check

**Fewest tokens first.** When an example does the job, do not read or edit its HTML: its motion is tuned and its
content and look are variables. `"$P/bin/graphic" examples NAME` gives its variables, its `pitfalls` (values that
broke it, the range that works) and the `lessons` learned on it (tagged `block:NAME`); go straight to step 4 with
`"$P/examples/NAME"` and `--set` / `--variables` (`place` and `plan` copy an example into `<project>/graphics/`
first and render the copy; in `plan` the bare name, `"composition": "stat-counter"`, is the example; copy it yourself only to edit its HTML). The brand fills colours and fonts. A series of
cards (an explainer's sections) gets one look from the same `frame` on every row: backdrop (paper for a kraft or notebook
look), float, a section chip, the source credit, a callout line on the payoff word, a bigger widget (`scale` 1.2–1.4 for
numbers read on a phone). Colours and fonts come from the project's brand; a brand id given in `set` that a
composition does not declare is left out with a warning. Never read `lib/*.mjs` or an example's HTML
to find what a variable or the frame does: this table and `examples NAME` say it. Edit HTML only when neither a
variable nor the frame reaches what this video needs, and when a value broke a block, record it (`bashcut knowledge
add-lesson … --tags block:NAME`).

1. **Brief.** One line per graphic: the words it serves (`bashcut transcript words --from F --to F2`), the payoff
   word's frame W, what the viewer should see that the words do not show, and the look (fonts, colours, motion
   energy) taken from the reference or the video's own titles. Vary the device across the video.
2. **Build** in `<project>/graphics/<name>/`: start from an example (`cp -R "$P/examples/keyword-pop" …`), a catalog
   block, or a blank `index.html`. Then make it this video's:
   - Canvas = the project (`bashcut project get`: width, height, fps) on `html`, `body`, the root's `data-width`,
     `data-height`; length = the root's `data-duration` (entrance + hold + exit, seconds).
   - Time it to speech: seconds from the overlay's start to each word (`(wordFrame − overlayStart) / fps`) go in as
     variables (`keywordAt`, the `at` of each line), so the motion lands on the word, not near it.
   - Declare every variable on `<html data-composition-variables='[{"id","type","label","default"}…]'>`; types are
     string, number, color, boolean, enum, font, image. Lists go in a string holding JSON (`JSON.parse` in the page).
   - Images, logos the user owns, screenshots and fonts: copy the files into the folder and use relative paths
     (`<img src="shot.png">`, `@font-face { src: url(font.woff2) }`). No network at render.
3. **Look.** `snapshot` at the entrance, the landing word and the hold; read the PNGs. With a reference,
   `--against`. Check: the words read at phone size, the face stays clear (`bashcut media subjects` boxes), nothing
   sits in the platform's bottom band (`bashcut platforms get <id>` › safe zones), Vietnamese tone marks render (a
   font without them falls back to another face mid-word). Fix and look again; two or three rounds is normal.
4. **Render and place** in one call:
   `"$P/bin/graphic" place <project>/graphics/<name> --at-frame <W − entrance frames> [--duration N] --set title=… --variables '{"rows":[…]}'`.
   `--duration N` (frames) is also the composition's length (its exit lands at the end; no `data-duration` edit). It renders at the project's fps, places the alpha .mov full canvas on the Overlay layer and prints `{item, media,
   frames, path, brand, lint?}`; fix lint errors. `--set` is typed by the declarations (undeclared ids are refused);
   lists go in `--variables` as JSON. A 3–5 s card takes 10–15 s, a 6 s map about 1 min; one render runs at a time.
   `--dry-run` prints the request (brand applied) without rendering.
5. **Change it later**: `"$P/bin/graphic" rerender <item> --set total=…` (`--unset k` drops an override) renders
   again from the recorded inputs and points every use at the new file as one edit. An item that played the whole
   graphic follows the new length (the result's `note` says so); `--keep-length` keeps lengths.
6. **Check in BashCut**: `bashcut ui frame W --phone` on the landing frame and `bashcut review window W --span 12`
   across the entrance (it also shows the words heard there); after re-cutting that range, re-read the words and
   move it or `rerender` it with the new `at`s. Several graphics (or the bare footage before placing them): one
   `bashcut timeline sheet --at F1,F2,F3 --outputs <output>` puts every landing frame on one sheet with the
   platform's covered zones, one image to read instead of a frame per graphic.

## 3. Composition rules (or frames come out wrong)

- Every frame is a pure function of time: one `gsap.timeline({paused: true})` registered as
  `window.__timelines["main"]` (the root's `data-composition-id`), positions given in absolute seconds. No
  `Date`, `Math.random`, timers, CSS animations or `requestAnimationFrame`; seed any randomness yourself.
- `fromTo` renders its start state at once: a later `fromTo` that starts visible (a ripple at 0.9 opacity) needs
  `immediateRender: false`, or it shows from frame 0.
- Text cannot be tweened: count numbers with one `tl.set(el, {textContent: …}, t)` per frame (see `stat-counter`),
  and set the first value before the count starts.
- The body stays transparent for overlays; a full-frame card paints its own background. Shadows and plates carry
  legibility over busy footage (plate opacity 0.75–0.9).
- Keep 60 px+ from the frame edges for anything to be read.
- Time the exit from the root's `data-duration` (`const END = Number(root.dataset.duration)`; exit at `END - 0.5`),
  as the examples do: `bin/graphic plan` sets it to the graphic's span, so the card holds until its section ends.
- `bin/hf snapshot` and `check` do not copy GSAP: copy `"$P/bin/hf" --gsap` next to `index.html` first, or every
  frame shows the end state ("Timeline did not advance under seek").
- Data on screen keeps its credit: a map keeps "© OpenStreetMap contributors" visible (`map-route` does); a chart
  or table from a source carries its source line (`bar-chart` › `source`). Illustrative numbers are said to be
  illustrative, in the words or on the card.

## 4. Brand

`place` and `rerender` fill the standard variables a composition declares from the project's brand (`project get`
› `brand`): `accent`, `background`, `text`, `secondary` (palette), `headingFont`, `bodyFont` (fonts), `disclosure`;
`--set` wins. Every example uses them (copy the "Brand look" lines); declare the same ids in your own compositions.
After a brand change, `rerender --all --brand` restyles every placed graphic in one edit. Fonts: a family or
PostScript name on this Mac, `System-<Weight>`, or a project font (`bashcut fonts import` a .ttf/.otf, not .ttc),
copied into the composition's `fonts/`. A composition that declares `logo` (type image) gets the kit's logo sticker
copied in as `brand-logo.<ext>`; one that declares `mascot` (type image) gets the kit's mascot pose named by its
`mascotPose` (else `default`, else the first) as `brand-mascot-<pose>.<ext>` (`paper-card` shows it). A mascot
picture with a background: `bashcut image cutout <sticker or file> --crop`, look at it, then `bashcut library add
--kind sticker --file <path>` and set that ID as the pose in the Brand panel.

## 5. Moves that combine a graphic with BashCut

Footage stays in BashCut (editable, re-cut without re-rendering); compositions draw only graphics.

- **Speaker shrinks into a card** (the reference look: the speaker becomes a rounded picture on paper): render the
  card background (a `paper-card` without lines, or any composition) and put it on a video layer *behind* Main:
  `{"op":"addTrack","track":{"id":"card-bg","kind":"video","role":"overlay","name":"Card background","items":[]},"atIndex":0}`
  (or `moveTrack` to `toIndex` 0), then place the render on it for the range. Split the Main clip at the range and
  on that piece keyframe `zoom` 1 → about 0.6 and `tilt` over 0.25–0.4 s (`bashcut clip keyframe`), and give it
  rounded corners with `{"op":"setProperties","item":"ID","patch":{"crop":{"radius":0.06}}}`. The voice stays on
  Main's sound. Look at it with `review window` across the move.
- **A page or card that turns in over the cut**: the graphic's own entrance (`paper-card`); no BashCut transition
  needed. A catalog shader transition (`hf catalog transition`) is a full-frame block: render it as an overlay at the
  cut.
- **Scene change in an explainer**: the data widgets exit by swinging away in 3D (`rotationY` about the left edge,
  0.45 s) the way card explainers change scene; the next card enters as this one leaves, so place it 0.3–0.45 s
  before the previous one ends.
- **A pointer clicking something on screen**: `cursor-click` with the target's pixel position read from
  `bashcut ui frame` on that frame.
- **A screen or app page**: build it in HTML around the user's own screenshot or thumbnail; never draw a real
  brand's logo or interface from memory and present it as theirs.

## 6. The catalog

`hf catalog cursor --json`, `hf catalog --tag transition`, `--type component`. Blocks are whole scenes; components
are parts to mount. The registry lives in the HyperFrames repository (Apache-2.0). Leave out items built around a
real company or person (product ads, named creators) unless the user asks, and snapshot a block before relying on
it: WebGL and WebGPU blocks need the GPU and may render blank in software mode.

## Report

Per graphic: the words it serves and why, the design choices and where they came from (reference, style profile,
the video), example or block it started from, the frames you looked at and what you changed, render numbers, where
it sits (frame, layer), and what was left bare on purpose.
