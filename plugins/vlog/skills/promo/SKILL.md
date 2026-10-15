---
name: promo
description: Recipe for a promo, hype or showreel (brand hype, portfolio, motion comic): beat cuts, kinetic type, rolling counters, a declared transition motif, sourced numbers, only the person's own work. Use after bashcut.vlog:plan picks promo (identity, not a sale). Triggers: "promo", "teaser", "showreel", "portfolio", "video hype", "motion comic".
---

# Promo, hype and showreel

Reply in the user's language. A promo says who someone is and makes the viewer feel it: energy and identity, often
music only. It is not an ad: an ad sells one product to one audience with a truth source and variants
(`bashcut.vlog:product-ad`); a promo has no offer and may never show a price. Ranges go into the plan and review
profile with `bashcut.vlog:plan`; edit with `bc:edit-workflow`.

Sources: RC = the Reelcrew / AgentVid study (measured 2026-10-07; here a 36 s vertical motion-comic hype and a 38 s
landscape profile showreel, filmstrips at 0.1 s a frame); T-notes as in the other recipes.

## Three shapes

| Shape | What it shows | Output |
|---|---|---|
| Brand or product hype | the name, what it does in 3–4 powers, a reveal | `tiktok`, `reels`, `shorts`; `youtube-1080` for a launch page |
| Profile or portfolio showreel | a person's journey, numbers, real work and events, then their name card (RC: 16:9) | `youtube-1080`; a vertical cut-down as a sibling project (`project derive`) |
| Motion-comic hype | a comic "issue": cover, numbered powers, "to be continued" (RC: 9:16) | `tiktok`, `reels`, `shorts` |

## Ranges

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Cuts | 12–13.3 hard cuts a minute, 4.0–4.5 s a shot (RC: comic 13.3 / 4.0 s, showreel 12.6 / 4.2 s); inside a shot something changes about every 2.7 s (RC comic) | slower where a counter or timeline must be read | `review shots --summary` → `cutsPerMinute`, mean |
| Cuts on the beat | every cut and wipe on a beat or bar (`bc:beat-cut`) | a voiced hype cuts on the phrase first, the beat second | `review sync` |
| Long shot `maxShotSeconds`, `stillMotion` | 5–6 s, `shot-long` at `warning`; `stillMotion` high: mean picture change 10–18 against 1.4–4.2 for card explainers (RC) | a name card at the end holds longer | `review shots` → `motion.mean` |
| Frozen picture `maxStillSeconds`, `severities.still` | 0.5–1 s, `error`: still frames 0–2 % (RC) | a manifesto line on black may hold for its reading time | `review measure`, `review picture` |
| Hook `hookSeconds` | vertical: 1–2 s, the logo or first big word already moving (RC comic: first cut 0.1 s); a landscape showreel may build up to 8 s under a ghost word (RC: first cut 8.0 s) | a feed is scrolled past, a portfolio page is chosen | `review layout --to F`, `review shots --to F` |
| Kinetic word hold | 1–3 words a card, held about letters ÷ 15 + 1–1.5 s (T09 §3) inside the 4 s shot | a counter's final value holds; a ghost word never needs reading | `review layout` → `holdSeconds` |
| Captions `captionLineChars`, `captionMaxLines` | voiced: one line in a caption box, 3–6 words, keyword highlighted (RC comic); music-only: none | — | `review layout` |
| `minSpeechCoverage` | voiced: 0.85–0.95 (RC: silence 3.0–3.5 %); music-only: unset, `maxMusicGapSeconds` set | — | `review run` |
| Music under the voice | the small end of 5–18 dB (T11 §3): the music drives a promo | a soft voice needs more room | `audio mix-measure` |
| Transition budget | a declared motif, far over the 1–3 a minute of other short form (T08 §3): RC comic about one every 2.7 s | the motif is the identity; write it in the plan | `review shots` → `cut.kind` counts ÷ minutes |

## Structure

Sample lengths, not slots; the plan gives each section its range and reason; mark each with `upsertSection`.

| Shape | Parts (RC timings) |
|---|---|
| Motion-comic hype, 30–40 s | cover: logo burst, "issue #01" (0–6 s) → powers ×3–4, each a "POWER #0n" title, a counter "n/04" and one proof card (a checklist, a chat bubble, a flow) (about 6 s each) → reveal: logo, "coming soon / to be continued" (6–8 s) |
| Profile showreel, 30–45 s | ghost word and a one-line belief (0–10 s) → the journey: years rolling (2005 → 2021) with places and roles → impact counters (100+, 10,500+) → proof: real events, press, a photo grid → the manifesto in two big words → name card: photo, name, role, URL (last 3–5 s) |
| Brand or product hype, 15–45 s | the name or promise in the first 1–2 s → 3–4 powers or facts, one per shot → the logo and one line to remember (no RC reference of its own) |

## Type, counters and pictures

- **Kinetic type is the picture**: one to three words per card in a heavy face (`vlog-kinetic-word`), entering on the
  beat; a giant ghost word scrolling slowly behind at low opacity (RC "COMPLEXITY"); a two-colour word for the
  manifesto ("BUILD / CAPACITY."). `bashcut.hyperframes:hyperframes` (`keyword-pop`) when native text cannot do it;
  `bc:motion-graphics` sets the timing.
- **Counters roll fast**: 10 → 24 → 29+ in about 0.3 s (RC), then hold the final number with its label
  (`stat-counter`); a journey of years with `timeline`.
- **Screenshots slide in** from the edge, tilted, over the number they prove (RC): the user's real product, site or
  press page.
- **Frame chrome**: a thin viewfinder frame with small labels ("01 / SIMPLIFY", a timecode) for a showreel; the logo
  and an issue counter "n/04" for the comic (RC). It stays put; only the content swaps.
- **Pictures**: the person's or brand's own work, photos, events and press only; stock only for textures and
  abstract backgrounds; generated art in one style for a comic (`bashcut.vlog:scene-prompt`), never presented as real
  work.

## Transitions

BashCut's kinds, sized from the RC filmstrips (0.1 s a frame), at 30 fps; the full list and custom kinds are
`bc:effects`. Kinetic words and cards can also take a kind as their own In and Out (`clip transition --side in|out`).

| Moment | Kind | Duration |
|---|---|---|
| kinetic word to word, showreel | `glitch` (RGB split + jitter) | 3–6 frames (0.1–0.2 s) |
| comic panel to panel | `halftone`, often through a `flash` | 12–15 frames (0.4–0.5 s) |
| comic power to power | colour-stripe wipe: `wipe-right` or `slide` (a custom kind only for the stripe colour) | 6–9 frames (0.2–0.3 s) |
| section to section, showreel | `wipe` or `barn-door` in the accent | 3–6 frames |
| a hit on the drop | `flash` (white) or `dip-black` | 2–4 frames |
| card to card | `swing` | about 9 frames (0.3 s, RC card swing) |

Pick two or three kinds for the whole promo and repeat them: the repeated set is the identity. Save a custom kind
that works with `bc:library`.

## Truth rules (not taste)

- Every number on a counter is real and sourced (the user, a dashboard, a press page) and written in the plan; no
  rounding up past the source ("10,500+" only when 10,500 is true). No source: no counter.
- A showreel uses only the person's own work, roles and events; a client logo or a TV appearance only when the user
  confirms it happened and may be shown.
- No invented testimonials, awards or "as seen on".

## Sound and look

Music first: one track with a clear beat, cut to it (`bc:beat-cut`); a riser into the drop, whooshes on wipes, a
glitch hit on `glitch`, a paper or print sound on `halftone` (`bc:audio-mix`, licensed or CC0). A voice, if any, sits
on top at its measured rate (`bc:voiceover`). The references sit at the platform target (RC). One palette, one heavy
display face and one text face. Intent: a showreel dark and restrained with one accent; a comic saturated and loud
(RC: saturation 63 against the showreel's 48) with halftone, sunburst and paper textures. Footage graded toward the
palette (`bc:color-grade`).

## Review notes

- Blockers a viewer notices: a cut off the beat, a word gone before it is read, a still frame, a counter that ends on
  an unsourced number, three different transition looks fighting, the logo missing at the end.
- Deliberate: many transitions (the declared motif), 4 s shots with constant motion, music-only versions.
- `needs_user`: the shape, the numbers and their sources, which work, clients and events may be shown, the music, the
  brand.

## Plan data

What this recipe adds to the plan (`bashcut.vlog:plan` §3).

- `stages`: `{"voiceover": {"required": false, "why": "music-led; a voice only when the user wants one"}, "rhythm": {"required": true, "skill": "bc:beat-cut", "why": "cuts and wipes land on the beat"}, "effects": {"required": true, "skill": "bc:motion-graphics", "why": "kinetic type, counters and screenshots are the picture"}}`
  (voiced: `voiceover` `{"required": true, "why": "the voice carries the powers"}` and `visuals` `{"skill":
  "bc:visual-plan", "after": "voiceover", "required": true, "why": "each line gets a word, a counter or a proof"}`).
- `checks` (source: promo recipe): `on-beat` every cut and wipe sits on a beat; `numbers-sourced` every counter's
  number has a source in the plan; `own-work` a showreel shows only the person's own work and confirmed clients;
  `word-readable` every kinetic word holds for its reading time; `nothing-still` no still frame beyond 1 s; `motif`
  the transitions come from the plan's declared set; `logo-close` the name or logo is on screen at the end.
- `askAtIntake`: `["shape", "truthSource", "brandKit"]`.
