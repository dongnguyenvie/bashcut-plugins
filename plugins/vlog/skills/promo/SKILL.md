---
name: promo
description: Recipe for a fast promo, hype or showreel in BashCut — a brand or product hype, a personal profile or portfolio showreel, a motion-comic teaser — cut every 4–4.5 s on the beat with something moving in every frame, kinetic type with RGB-split glitch, rolling counters, screenshots sliding in, full-frame colour wipes, a giant ghost word behind, flash frames and halftone dissolves; truth rules for every number and claim, only the person's own work in a showreel; the review profile for pictures that never rest. Use after bashcut.vlog:plan picked promo, or when the user wants energy and identity rather than selling one product. Triggers: "video hype", "promo", "teaser", "giới thiệu thương hiệu", "video giới thiệu bản thân", "profile", "showreel", "portfolio", "intro kênh", "motion comic", "truyện tranh động", "video năng lượng", "brand video", "sizzle reel".
---

# Promo, hype and showreel

Reply in the user's language. A promo says who someone is and makes the viewer feel it: energy and identity, often
with music only. It is not an ad: an ad sells one product to one audience with a truth source and variants
(`bashcut.vlog:product-ad`); a promo has no offer to read and may never show a price. Choose ranges and values from
the tables below, write them into the edit plan and the review profile with `bashcut.vlog:plan`, then edit with
`bc:edit-workflow`.

Sources: RC = the Reelcrew / AgentVid study (measured 2026-10-07; here its fast promos: a 36 s vertical motion-comic
hype and a 38 s landscape profile showreel, with filmstrips at 0.1 s a frame); T-notes as in the other recipes.

## Three shapes

| Shape | What it shows | Output |
|---|---|---|
| Brand or product hype | the brand's name, what it does in 3–4 powers, a reveal | vertical `tiktok`, `reels`, `shorts`; `youtube-1080` for a launch page |
| Profile or portfolio showreel | a person's journey, numbers, real work and events, then their name card (RC: 16:9) | `youtube-1080`; a vertical cut-down as a sibling project (`bashcut project derive`) |
| Motion-comic hype | a comic "issue": cover, numbered powers, "to be continued" (RC: 9:16) | `tiktok`, `reels`, `shorts` |

## Ranges

The ranges are starting points: a measured reference profile (`bc:style-study`) replaces every range it measures
(T07 §7, T15 §7). Write each chosen range, its source and its reason in the plan.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Cuts | 12–13.3 hard cuts a minute, 4.0–4.5 s a shot (RC: comic 13.3 / 4.0 s, showreel 12.6 / 4.2 s); inside a shot something changes about every 2.7 s (RC comic) | slower builds where a counter or a timeline must be read | `bashcut review shots --summary` → `cutsPerMinute`, mean |
| Cuts on the beat | every cut and every wipe on a beat or a bar (`bc:beat-cut`, `bashcut beats detect`) | a voiced hype cuts on the phrase first, the beat second | `bashcut review sync` |
| Long shot `maxShotSeconds`, `stillMotion` | 5–6 s, `shot-long` at `warning`; `stillMotion` high: mean picture change 10–18 in the references against 1.4–4.2 for card explainers (RC) | a name card at the end holds longer | `review shots --summary` max; `review shots` → `motion.mean` |
| Frozen picture `maxStillSeconds`, `severities.still` | 0.5–1 s, `error`: still frames 0–2 % (RC) | a manifesto line on black may hold for its reading time | `bashcut review measure`, then `bashcut review picture` |
| Hook `hookSeconds` | vertical: 1–2 s, the logo or the first big word already moving (RC comic: first cut at 0.1 s); a landscape showreel may build for up to 8 s under a ghost word (RC: first cut 8.0 s) | the platform: a feed is scrolled past, a portfolio page is chosen | `bashcut review layout --to F`, `review shots --to F` |
| Kinetic word hold | 1–3 words a card, held about letters ÷ 15 + 1–1.5 s (T09 §3) inside the 4 s shot | a counter's final value holds; a ghost word never needs reading | `bashcut review layout` → `holdSeconds` |
| Captions `captionLineChars`, `captionMaxLines` | voiced: one line in a caption box, 3–6 words, keyword highlighted (RC comic); music-only: none, the type carries the words | — | `bashcut review layout` → `longestLineChars` |
| Speech coverage `minSpeechCoverage` | voiced: 0.85–0.95 (RC: silence 3.0–3.5 %); music-only: unset, `maxMusicGapSeconds` set | — | `bashcut review run` |
| Music under the voice | the small end of 5–18 dB (T11 §3): the music drives a promo | a soft voice needs more room | `bashcut audio mix-measure` → `musicUnderSpeech` |
| Transition budget | a declared motif, far over the 1–3 a minute of other short form (T08 §3): RC comic about one every 2.7 s | the motif is the identity; write it in the plan | `bashcut review shots` → `cut.kind` counts ÷ minutes |

## Structure

Sample lengths from the references, not slots: the plan gives each section its own range and says why
(`bashcut.vlog:plan` §3). Mark each with `upsertSection`.

| Shape | Parts (RC timings) |
|---|---|
| Motion-comic hype, 30–40 s | cover: logo burst, "issue #01" (0–6 s) → powers ×3–4, each a "POWER #0n" title, a counter "n/04" and one proof card (a checklist, a chat bubble, a flow) (about 6 s each) → reveal: logo, "coming soon / to be continued" (6–8 s) |
| Profile showreel, 30–45 s | ghost word and a one-line belief (0–10 s) → the journey: years rolling (2005 → 2021) with places and roles → impact counters (100+, 10,500+) → proof: real events, press, a grid of photos → the manifesto in two big words → name card: photo, name, role, URL (last 3–5 s) |
| Brand or product hype, 15–45 s | the name or the promise in the first 1–2 s → 3–4 powers or facts, one per shot → the logo and one line to remember (no RC reference of its own: built from the two above) |

## Type, counters and pictures

- **Kinetic type is the picture**: one to three words per card in a heavy face (`vlog-kinetic-word`), entering on the
  beat; a giant ghost word scrolling slowly behind at low opacity (RC "COMPLEXITY"); a two-colour word for the
  manifesto ("BUILD / CAPACITY."). `bashcut.hyperframes:hyperframes` (`keyword-pop`) when the type must animate
  beyond native text; `bc:motion-graphics` sets the timing.
- **Counters roll fast**: 10 → 24 → 29+ in about 0.3 s (RC), then hold the final number with its label
  (`stat-counter`); a journey of years with `timeline`.
- **Screenshots slide in** from the edge, tilted, over the number they prove (RC): the user's real product, site or
  press page.
- **Frame chrome**: a thin viewfinder frame with small labels (section "01 / SIMPLIFY", a timecode) for a showreel;
  the logo and an issue counter "n/04" for the comic (RC). It stays put; only the content swaps.
- **Where pictures come from**: the person's or the brand's own work, photos, events and press only; stock
  (`bc:stock-images`) only for textures and abstract backgrounds; generated art in one style for a comic
  (`bashcut.vlog:scene-prompt`), never presented as real work.

## Transitions

Use BashCut's kinds, sized from the RC filmstrips (0.1 s a frame), at 30 fps:

| Moment | Kind | Duration |
|---|---|---|
| kinetic word to word, showreel | `glitch` (RGB split + jitter) | 3–6 frames (0.1–0.2 s) |
| comic panel to panel | `halftone` (print dots dissolve), often through a black flash | 12–15 frames (0.4–0.5 s) |
| comic power to power | colour-stripe wipe: a custom kind, `{"op":"upsertTransition", …, "motion": {"incoming": {"reveal": [0, 1], "exposure": [1, 0]}}}` | 6–9 frames (0.2–0.3 s) |
| section to section, showreel | a full-frame colour wipe in the accent (`wipe`, or a colour card of 2–4 frames) | 3–6 frames |
| a hit on the drop | flash frame (`blink`), white or black | 2–4 frames |
| card to card, when the promo uses cards | `swing` | about 9 frames (0.3 s, RC card swing) |

A custom kind can mix `rgbSplit` (0–0.2), `halftone` (0–0.1), `swing`, `reveal`, `exposure` and the transform
properties; save one that works with `bc:library`. Pick two or three kinds for the whole promo and repeat them: the
repeated set is the identity.

## Truth rules (not taste)

- Every number on a counter is real and sourced (the user, a dashboard, a press page) and written in the plan; no
  rounding up past the source ("10,500+" only when 10,500 is true). No source: no counter.
- A showreel uses only the person's own work, roles and events; a client logo or a TV appearance only when the user
  confirms it happened and may be shown.
- No invented testimonials, awards or "as seen on". Sponsorship: said early and `vlog-disclosure` on screen.

## Sound

Music first: one track with a clear beat, cut to it (`bc:beat-cut`); a riser into the drop, whooshes on wipes, a
glitch hit on `glitch`, a paper or print sound on `halftone` (`bc:audio-mix`, licensed or CC0). A voice, when there
is one, sits on top at its measured rate (`bc:voiceover`). Loudness is each output's own target (`bashcut platforms
get`); export with `--normalize-audio` (the references sit at the platform target, RC).

## Look

One palette, one heavy display face and one text face for the whole promo, from the brand when there is one
(`bashcut project get` → `brand`: palette, fonts, logo, mascot; `bashcut library apply <brand-id>`). Intent per shape:
a showreel dark and restrained with one accent; a comic saturated and loud (RC: saturation 63 against the
showreel's 48) with halftone, sunburst and paper textures. Footage is graded toward the palette (`bc:color-grade`).
Vietnamese text needs a font with every tone mark (`bc:captions-text`).

## Review notes

- A viewer notices: a cut off the beat, a word gone before it is read, a still frame in a promo, a counter that
  ends on a number nobody can source, three different transition looks fighting, the logo missing at the end. Treat
  these as blockers.
- Deliberate here: many transitions (the declared motif), shots of 4 s with constant motion, music-only versions.
- `needs_user`: the shape, the numbers and their sources, which work, clients and events may be shown, the music, the
  brand.

## Plan data

What this recipe adds to the plan (`bashcut.vlog:plan` §3); `bc:edit-workflow` and the critic read it.

- `stages`: `{"voiceover": {"required": false, "why": "music-led; a voice only when the user wants one"}, "rhythm": {"required": true, "skill": "bc:beat-cut", "why": "cuts and wipes land on the beat"}, "effects": {"required": true, "skill": "bc:motion-graphics", "why": "kinetic type, counters and screenshots are the picture"}}`
  (voiced version: `voiceover` `{"required": true, "why": "the voice carries the powers"}` and `visuals`
  `{"skill": "bc:visual-plan", "after": "voiceover", "required": true, "why": "each line gets a word, a counter or a proof"}`).
- `checks` (source: promo recipe): `on-beat` every cut and wipe sits on a beat; `numbers-sourced` every counter's
  number has a source in the plan; `own-work` a showreel shows only the person's own work and confirmed clients;
  `word-readable` every kinetic word holds for its reading time; `nothing-still` no still frame beyond 1 s;
  `motif` the transitions come from the plan's declared set; `logo-close` the name or logo is on screen at the end.
- `askAtIntake`: `["shape", "truthSource", "brandKit"]` (hype, showreel or comic; where the numbers and the work
  come from; the user's palette, fonts, logo and mascot, if any).
