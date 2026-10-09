---
name: hyperframes
description: Design and render any animated graphic for a BashCut edit with HyperFrames — kinetic type and keyword pops, stat counters and charts, a pointer that clicks, mock screens, full-frame paper or colour cards, lower thirds, diagrams, light leaks and other catalog blocks — as an HTML/CSS + GSAP composition you write or assemble, looked at frame by frame, rendered to a .mov with alpha and placed on the timeline; plus the speaker-shrinks-into-a-card move done with BashCut's own layers. Use when bc:motion-graphics decided a sentence needs a graphic, when native text cannot make the look, or when the user wants the graphics of a reference video. Triggers: "đồ hoạ", "motion graphic", "chữ chuyển động", "kinetic text", "số chạy", "counter", "biểu đồ", "con trỏ chuột", "thẻ giấy", "thu nhỏ người nói", "làm giống video mẫu", "hyperframes".
---

# HyperFrames graphics

Reply in the user's language. This plugin gives you hands, not a style: HyperFrames renders whatever HTML, CSS and
GSAP you write, deterministically, frame by frame. Design each graphic for this video, from what the speaker says and
how the reference or the channel looks (`bc:style-study` profile, reference frames), not from the examples' looks.
Whether a sentence needs a graphic, when it lands and how long it holds is `bc:motion-graphics`; this skill is how
to make it.

## 1. What you have

`P` is this plugin's folder: two levels above this SKILL.md (`<skill_dir>/../..`).

| Tool | What it does |
|---|---|
| `"$P/bin/hf" catalog [words] --json` | Search 392 ready blocks and components (transitions, typography, captions, overlays, lower thirds, data, mock UI, cursors, counters, shaders, 3D) |
| `"$P/bin/hf" add NAME --dir D` | Install one into composition folder D (`compositions/…/NAME.html`); mount it with `data-composition-src`. It also copies a snippet to the clipboard |
| `"$P/bin/hf" lint D` / `check D` | Validate; `check` also runs it in Chrome and measures contrast and overflow |
| `"$P/bin/hf" snapshot D --at 0.3,0.8,1.6 --no-end -o OUT` | PNG frames and a `contact-sheet.jpg` to look at; `--against ref.mp4` pairs each with a reference frame; `--zoom "#card"` crops one element sharp |
| `"$P/bin/hf" docs compositions\|data-attributes\|gsap` | The runtime's own rules |
| `"$P/bin/hf" --gsap` | Path of GSAP to copy next to `index.html` (render copies it when missing) |
| `bashcut plugins invoke graphics.render --params '{…}'` | Render for the timeline: alpha `.mov` (HEVC, or ProRes 4444 with `"codec":"prores"`), lint findings in the result |
| `$P/examples/` | Raw material, each lint-clean: `keyword-pop` (serif lead-in + bold keyword), `stat-counter` (number counts up, line draws), `cursor-click` (pointer lands and clicks), `paper-card` (full-frame card turns in like a page, lines build on words), `checklist-card` |

When `bin/hf` exits 3 or the render says `dependency_missing`, the user chooses **Install Dependencies…** for
HyperFrames Graphics in Plugins (you cannot); say so and fall back to native text.

## 2. The loop: design, build, look, render, place, check

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
4. **Render**: `bashcut plugins invoke graphics.render --params '{"composition":"/abs/<project>/graphics/<name>",
   "fps":30,"variables":{…},"name":"<name>"}'`, then `bashcut jobs wait <job>`. The result has `path`, `frames`,
   `bytes`, `renderSeconds` and `lint`; fix lint errors, they usually mean a frame is wrong. A 1080×1920 graphic of
   3 s renders in about 10 s and is about 0.2 MB.
5. **Place**: `bashcut library add --kind sticker --name "<Name>" --file <path>` (keeps the alpha), then
   `bashcut library place <id> --at-frame <W − entrance frames> --size 1 --position center --base-rev N` (the
   composition is the full canvas; its layout lives in the HTML). A full-frame card goes the same way and covers the
   picture while the voice continues underneath.
6. **Check in BashCut**: `bashcut ui frame W --phone` on the landing frame and `bashcut review window W --span 12`
   across the entrance (it also shows the words heard there);
   after re-cutting that range, re-read the words and move or re-render the graphic.

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

## 4. Moves that combine a graphic with BashCut

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
- **A pointer clicking something on screen**: `cursor-click` with the target's pixel position read from
  `bashcut ui frame` on that frame.
- **A screen or app page**: build it in HTML around the user's own screenshot or thumbnail; never draw a real
  brand's logo or interface from memory and present it as theirs.

## 5. The catalog

`hf catalog cursor --json`, `hf catalog --tag transition`, `--type component`. Blocks are whole scenes; components
are parts to mount. The registry lives in the HyperFrames repository (Apache-2.0). Leave out items built around a
real company or person (product ads, named creators) unless the user asks, and snapshot a block before relying on
it: WebGL and WebGPU blocks need the GPU and may render blank in software mode.

## Report

Per graphic: the words it serves and why, the design choices and where they came from (reference, style profile,
the video), example or block it started from, the frames you looked at and what you changed, render numbers, where
it sits (frame, layer), and what was left bare on purpose.
