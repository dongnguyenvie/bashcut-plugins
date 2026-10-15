---
name: hyperframes
description: Design and render animated graphics as HTML/CSS + GSAP compositions (kinetic type, counters, charts, tables, OpenStreetMap routes, cursors, cards, diagrams), placed with alpha. Use when bc:motion-graphics wants a graphic native text cannot make. Triggers: "đồ hoạ", "motion graphic", "chữ chuyển động", "số chạy", "biểu đồ", "bản đồ".
---

# HyperFrames graphics

Reply in the user's language. This plugin gives you hands, not a style: HyperFrames renders whatever HTML, CSS and
GSAP you write, deterministically, frame by frame. Design each graphic for this video, from what the speaker says and
how the reference or channel looks (`bc:style-study` profile, reference frames), not from the examples' looks.
Whether a sentence needs a graphic, when it lands and how long it holds is `bc:motion-graphics`; this skill is how to
make it.

## 1. What you have

`P="$HOME/Library/Application Support/BashCut/Plugins/bashcut.hyperframes"` (where BashCut installs it; this SKILL.md
may be a copy elsewhere). `osm-map --help` lists its options.

| Tool | What it does |
|---|---|
| `"$P/bin/hf" catalog [words] --json` | Search 392 ready blocks and components (transitions, typography, captions, overlays, lower thirds, data, mock UI, cursors, counters, shaders, 3D) |
| `"$P/bin/hf" add NAME --dir D` | Install one into composition folder D; mount it with `data-composition-src` |
| `"$P/bin/hf" lint D` / `check D` | Validate; `check` also runs it in Chrome and measures contrast and overflow |
| `"$P/bin/hf" snapshot D --at 0.3,0.8,1.6 --no-end -o OUT` | PNG frames and a contact sheet; `--against ref.mp4` pairs each with a reference frame; `--zoom "#card"` crops one element |
| `"$P/bin/hf" docs compositions\|data-attributes\|gsap` | The runtime's own rules |
| `"$P/bin/graphic" examples [NAME]` | One line per example (what it draws, seconds, its variables): choose without reading HTML. With NAME every variable's label and default, its `pitfalls` and the `lessons` tagged `block:NAME` |
| `… --snapshot 1.5,4,9.2 [-o OUT]` on `plan --only g1`, `place D …`, `rerender ITEM …` | Look before you render: the row exactly as it would render (its `set`, `"@words"` times, brand, frame, span, canvas) as PNGs and a contact sheet in seconds; nothing rendered, imported or placed. Seconds count from the graphic's start (a scene slice: the row's). `place --snapshot` needs no open project |
| `"$P/bin/graphic" plan [--only g1,g2]` | Renders every `plan.cut` graphic with `render` {composition, set, frame} to the span plan check gives it, imports, writes the media into plan.cut and runs `plan apply`: a graphics edit in one call. A `set` value `"@words"` is the seconds from the graphic's start to those words in the voiceover; unchanged graphics are not rendered again |
| `--frame JSON` (`place`, `rerender`) / `render.frame` (`plan`) | Chrome around any composition, no HTML edit: `backdrop` `texture`\|`paper`\|`plain` (paper: kraft with a kraft-brown brand background, notebook with a cream one), `fadeIn`, `drift`, `float` (after ~1.2 s the widget bobs to the end: a held card passes review's frozen-picture check; drift alone does not), `chip` ("2/4"), `credit` (source line, only when the user asks), `callout` {text, at, top} (`*word*` in the accent), `scale` 0.5–2.5. Brand colours and fonts apply; chip and credit move aside when they would cover the widget |
| `"$P/bin/graphic" place D --at-frame F [--set k=v …]` | Render and place full canvas on the Overlay layer in one call, recording the inputs. `rerender ITEM [--set …]` renders again and swaps every use in one undo step |
| `--set data=@file.json` + `--steps-from voice\|sections` (`place`) | The JSON-data widgets: data in a file, never HTML or coordinates (the script lays out for 9:16 or 16:9). `--steps-from voice` gives step i the start of the i-th voice line (`sections`: section markers); `"at": "line:3"` / `"section:Label"` picks one; without `--at-frame`/`--duration` the graphic starts 0.4 s before the first step and ends after the last line. One widget = one `place` call |
| flow-diagram, mind-map, isometric-system | Data `{title, nodes, edges, steps:[{focus, reveal, note?}]}`; a node in no `reveal` shows from the start; `focus` lights it and dims the rest. ≤12 nodes, labels 1–3 words; one diagram per section, steps = its voice lines |
| growing-diagram | One diagram that grows over the whole video (never one per section, never hand-written HTML): `nodes:[{id, label, at:"@words"}]`, `edges:[{from, to, at?}]`; each lands and lights up, dots run on new edges; `look` flow\|iso. One `plan` row over the span, or one row per section with the same `render.scene` (slices meet exactly). Knobs, never page edits: `ghosts` (default on: later blocks faint and dashed from the start, so a "6 khối" hook shows six), `recap` (second or `"@words"`: every block lit, every edge runs dots, staggered, to the end), `bottomSafe` (nothing below: 0–1 of the height or px; 0 = 0.62 on 9:16, above captions at ~69 %). A closing edge (last → first) goes round the column in `look flow` (iso warns). Grid background: `render.frame` `{"backdrop": "texture"}`; size: leave the layout to `bottomSafe` (`frame.scale` zooms about the centre, back into the captions) |
| big-canvas | A whole video as one hand-drawn canvas (mind-map data + `stops`): placed once over the full span; each stop ≥ 2 s; a 60 s render takes about a minute. Look at one contact sheet (`hf snapshot --frames 8`), not frame by frame |
| formula, matrix-grid, scale-compare, bar-chart rows | formula: KaTeX with `\\hl{id}{tex}` terms; matrix-grid: rows, cols, values, steps; scale-compare: numbers from your source; bar-chart `layout=rows look=paper highlight=N`: a paper benchmark table |
| `"$P/bin/osm-map"` | OpenStreetMap tiles and a real route into a composition folder; prints `km`, `minutes` and per-stop `legs` to put on screen. `--places` looks up named places and prints area and perimeter (alone, it only measures). `--legs star` routes from the first point to each other; `--amenities … --radius` counts places around the first point and prints per kind `count` and the `nearest` (markers for `amenity-radius`; a kind with 0 is listed in `none` and left off its legend). Tags are strict: `hospital` never counts a clinic, dentist or pharmacy (ask `clinic`), `school` leaves out driving and language centres, `mall` is `shop=mall\|department_store` (ask `supermarket` apart), `park` is `leisure=park`. `--style dark` makes map-route/amenity-radius dark (no CSS edits). A failure names the request and reason; tiles fall back to other OSM servers by themselves, so never probe with curl: a failed `--places` lookup means give `--points`. Needs network; the render then needs none. Coordinates come from the user, the brief or a named source, never from memory |
| `$P/examples/` | Lint-clean raw material: keyword-pop, stat-counter, cursor-click, paper-card, checklist-card, bar-chart, cost-table, timeline, calendar, map-route and amenity-radius (run `osm-map` on the copy first), headline-reveal, quote-card, lower-third, spotlight-card, logo-lockup, progress-ring, stack-list, typewriter-doc, focus-frame, mock-video-app (never a real platform's brand), corner-curl-card, the diagrams, big-canvas, formula, matrix-grid, scale-compare, lottie (one accent: `file=` the path `fetch_lottie.py --pick` prints, `color=accent` only for a `mono` pick). Data widgets take rows with an `at` each: the second the row lands on its word |

When `bin/hf` exits 3 or the render says `dependency_missing`, the user chooses **Install Dependencies…** for
HyperFrames Graphics in Plugins (you cannot); say so and fall back to native text.

## 2. The loop: design, build, look, render, place, check

**Fewest tokens first.** When an example does the job, do not read or edit its HTML: its motion is tuned and its
content and look are variables. `graphic examples NAME` gives variables, `pitfalls` (values that broke it) and
`lessons`; go straight to step 4 with `"$P/examples/NAME"` (`place` and `plan` copy it into `<project>/graphics/`
and render the copy; in `plan` the bare name is the example; copy it yourself only to edit HTML). A series of cards
gets one look from the same `frame` on every row (`scale` 1.2–1.4 for numbers read on a phone). A brand id in `set`
that a composition does not declare is dropped with a warning. Never read `lib/*.mjs` or an example's HTML to learn
a variable: this table and `examples NAME` say it. Edit HTML only when no variable or frame key reaches it, and when
a value broke a block, record it (`knowledge add-lesson … --tags block:NAME`).

1. **Brief.** One line per graphic: the words it serves (`transcript words --from F --to F2`), the payoff word's frame
   W, what the viewer should see that the words do not show, and the look taken from the reference or the video's
   own titles. Vary the device across the video.
2. **Build** in `<project>/graphics/<name>/` from an example, a catalog block or a blank `index.html`:
   - Canvas = the project (width, height, fps) on `html`, `body`, the root's `data-width`/`data-height`; length =
     the root's `data-duration` (entrance + hold + exit).
   - Time it to speech: seconds from the overlay's start to each word (`(wordFrame − overlayStart) / fps`) go in as
     variables (`keywordAt`, each line's `at`), so the motion lands on the word.
   - Declare every variable on `<html data-composition-variables='[{"id","type","label","default"}…]'>` (string,
     number, color, boolean, enum, font, image); lists as a JSON string.
   - Images, the user's logos, screenshots and fonts: copied into the folder, relative paths. No network at render.
3. **Look.** `snapshot` at the entrance, the landing word and the hold; read the PNGs (`--against` with a reference).
   A `plan.cut` row or a `place` call with its values: add `--snapshot S1,S2,… -o OUT` to the same `graphic` command
   (`hf snapshot D` alone shows only the page's defaults). Look before every `plan` render, not after it.
   Check: words read at phone size, the face stays clear (`media subjects`), nothing in the platform's bottom band
   (`platforms get`), Vietnamese tone marks render (a font without them falls back mid-word). Two or three rounds is
   normal.
4. **Render and place**: `graphic place <dir> --at-frame <W − entrance frames> [--duration N] --set … --variables
   '{…}'`. `--duration` (frames) is also the composition's length (its exit lands at the end). `--set` is typed by
   the declarations (undeclared ids refused); fix lint errors it prints. A 3–5 s card renders in 10–15 s, a 6 s map
   about 1 min; one render at a time. `--dry-run` prints the request.
5. **Change it later**: `graphic rerender <item> --set …` (`--unset k` drops an override) renders from the recorded inputs and
   repoints every use as one edit; an item that played the whole graphic follows the new length (`--keep-length` keeps it).
6. **Check in BashCut**: `ui frame W --phone` on the landing frame and `review window W --span 12` across the
   entrance (with the words heard); after re-cutting that range, re-read the words and move or `rerender` with new
   `at`s. Several graphics: one `timeline sheet --at F1,F2,F3 --outputs <output>` instead of a frame each.

## 3. Composition rules (or frames come out wrong)

- Every frame is a pure function of time: one `gsap.timeline({paused: true})` registered as
  `window.__timelines["main"]` (the root's `data-composition-id`), positions in absolute seconds. No `Date`,
  `Math.random`, timers, CSS animations or `requestAnimationFrame`; seed any randomness yourself.
- `fromTo` renders its start state at once: a later `fromTo` that starts visible needs `immediateRender: false`, or
  it shows from frame 0.
- Text cannot be tweened: count numbers with one `tl.set(el, {textContent: …}, t)` per frame (see `stat-counter`),
  and set the first value before the count starts.
- The body stays transparent for overlays; a full-frame card paints its own background. Plates (opacity 0.75–0.9)
  and shadows carry legibility over busy footage. Keep 60 px+ from the edges for anything to be read.
- Time the exit from the root's `data-duration` (`END - 0.5`), as the examples do: `graphic plan` sets it to the
  graphic's span, so the card holds until its section ends.
- `hf snapshot` and `check` do not copy GSAP: copy `"$P/bin/hf" --gsap` next to `index.html` first, or every frame
  shows the end state ("Timeline did not advance under seek"); likewise `$P/lib/diagram.js` for the diagrams and
  `$P/lib/amenity-map.js` for amenity-radius (render copies them when missing).
- No credit, source or licence line on the picture by default: it makes the video look unnatural. Only when the
  user asks, set the composition's own variable (`map-route` / `amenity-radius` › `credit`, e.g. the
  `attribution` osm-map prints; `bar-chart` › `source`) or `--frame` › `credit`. Keep where numbers come from in your
  notes, not on screen.

## 4. Brand

`place` and `rerender` fill the standard variables a composition declares from the project's brand: `accent`,
`background`, `text`, `secondary`, `headingFont`, `bodyFont`, `disclosure`; `--set` wins. Declare the same ids in your
own compositions (copy the examples' "Brand look" lines). After a brand change, `rerender --all --brand` restyles
every placed graphic in one edit. Fonts: a family or PostScript name on this Mac, `System-<Weight>`, or a project
font (`fonts import` a .ttf/.otf, not .ttc). A composition declaring `logo` (image) gets the kit's logo; one declaring
`mascot` gets the pose picked by `--set pose=thinking` (else `default`, else the first; a missing one warns with the
poses the brand has). A mascot picture with a background: `bashcut image cutout … --crop`, look at it, add it to the
library as a sticker and set it as the pose in the Brand panel.

## 5. Moves that combine a graphic with BashCut

Footage stays in BashCut (editable, re-cut without re-rendering); compositions draw only graphics.

- **Speaker shrinks into a card**: render the card background (a `paper-card` without lines, or any composition) onto
  a new video layer *behind* Main (`addTrack` at index 0) for the range. Split the Main clip at the range and on that
  piece keyframe `zoom` 1 → about 0.6 and `tilt` over 0.25–0.4 s, with rounded corners (`crop.radius` about 0.06).
  The voice stays on Main's sound. Look with `review window` across the move.
- **A page or card that turns in over the cut**: the graphic's own entrance (`paper-card`); no BashCut transition. A
  catalog shader transition (`hf catalog transition`) is a full-frame block rendered as an overlay at the cut. A
  graphic placed as an overlay can also take any BashCut transition kind as its own In and Out (`bc:effects`).
- **Scene change in an explainer**: data widgets exit by swinging away in 3D (`rotationY` about the left edge,
  0.45 s); place the next card 0.3–0.45 s before the previous one ends.
- **A pointer clicking something**: `cursor-click` with the target's pixel position read from `ui frame`.
- **A screen or app page**: built in HTML around the user's own screenshot; never draw a real brand's logo or
  interface from memory and present it as theirs.

## 6. The catalog

`hf catalog cursor --json`, `--tag transition`, `--type component`. Blocks are whole scenes; components are parts to
mount (registry: the HyperFrames repository, Apache-2.0). Leave out items built around a real company or person
unless the user asks, and snapshot a block before relying on it: WebGL and WebGPU blocks may render blank in software
mode.

## Report

Per graphic: the words it serves and why, the design choices and where they came from, the example or block it
started from, the frames you looked at and what you changed, render numbers, where it sits (frame, layer), and what
was left bare on purpose.
