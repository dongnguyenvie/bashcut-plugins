---
name: explainer
description: Recipe for an explainer in BashCut, vertical by default, made without footage or with little of it — a question and a number as the hook, numbered sections each built around one data widget that builds with the voice (cost table, bar chart, timeline, map route, checklist, counter), a recap and a CTA, one illustration style and frame chrome for the whole video, every number with its source; the review profile for cards that move instead of cutting. Use after bashcut.vlog:plan picked explainer, or when the user wants a topic, place, law, history, science or business idea explained with cards, numbers and a voice. Triggers: "video giải thích", "explainer", "giải thích bằng hình", "video kiến thức", "video infographic", "video thẻ", "lịch sử", "luật", "khoa học", "tin tức", "bất động sản", "tuyến đường".
---

# Explainer

Reply in the user's language. An explainer carries its meaning in the words and the widgets, not in footage: plan the
script and the facts first, then design one widget per section that builds while the voice says it. Choose ranges
and values from the tables below, write them into the edit plan and the review profile with `bashcut.vlog:plan`,
then edit with `bc:edit-workflow`.

Sources: RC = the Reelcrew / AgentVid study (30 explainer and promo videos measured on 2026-10-07: cuts, motion,
still frames, loudness, speech rate, structure); T-notes as in the other recipes.

## Ranges

Outputs: vertical → `tiktok`, `reels`, `shorts`; landscape for YouTube → `youtube-1080` (a science or history piece
of 2–5 min is usually landscape, RC). The ranges are starting points: a measured reference profile
(`bc:style-study`) replaces every range it measures (T07 §7, T15 §7). Write each chosen range, its source and its
reason in the plan.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Cuts | 0–1.5 hard cuts a minute: scenes change by a card swinging away, a dissolve or a widget building, not by cutting (RC) | a news or promo explainer cuts every 4–4.5 s (12–13 a minute, RC); a calm card piece does not cut at all | `bashcut review shots --summary` → `cutsPerMinute` |
| Long shot `maxShotSeconds`, `severities.shot-long` | `shot-long` at `info`: one card stays on screen for a whole section; judge pace by motion, not by shot length (RC) | a sequence of photos does cut; then use the photo hold below | `review shots --summary`; `review shots` → `motion.mean` |
| Frozen picture `maxStillSeconds`, `severities.still` | 1–2 s, `warning`: nothing is ever still in the references, every picture drifts and every widget builds (RC: still frames 0–14 % in voiced pieces; 14–66 % in the older music-only kits, which read as slides) | a quote or a dense table held to be read may stay still for its reading time | `bashcut review measure`, then `bashcut review picture` (frozen stretches) |
| Photo or illustration hold | 2–4 s with a Ken Burns drift of 0.3–1.5 % a second (T08 §3); 3–6 s while a line is said over it | a photo with a widget on it holds as long as the widget builds | `bashcut timeline get` → keyframes; `review picture` |
| Hook `hookSeconds` | 1–3 s: a question and one big concrete number on screen ("Lãi thật mỗi đơn 37.000đ?", "938 · Trận Bạch Đằng") (RC) | a landscape long-form piece may open with the question said over a title for 3–5 s | `bashcut review layout --to F`, `transcript words --to F` |
| Speech rate | 165–236 syllables a minute in Vietnamese TTS explainers; silences 0–6 % of the runtime (RC) | dense legal or science text sits low; travel and news high. Size lines with the voice's measured rate, not this band | `bashcut speech rate`; `bashcut media speech-map` → `gaps` |
| Dead air `maxSilenceSeconds` | 0.5–1 s between sections; one held beat before the payoff (T07 §3) | a music-only version has no speech: use `maxMusicGapSeconds` instead | `bashcut audio measure --timeline` → `silences` |
| Captions `captionLineChars`, `captionMaxLines` | one line of 3–6 words with the keyword highlighted, on a pill (RC); vertical 15–32 characters (T09 §3) | a music-only version has no captions; its cards carry all the words | `bashcut review layout` → `longestLineChars`, `wordsPerSecond` |
| Speech coverage `minSpeechCoverage` | 0.85–0.95 for a voiced explainer (RC: silence 0–6 %) | music-only versions: leave unset | `bashcut review run` |
| Music under the voice | the deep end of 5–18 dB (T11 §3): every word is information | a music-only version has the music as the only layer | `bashcut audio mix-measure` → `musicUnderSpeech` |

## Structure (45–90 s vertical, 2–5 min landscape)

Sample lengths from the references, not slots: the plan gives each section its own range from the script and says
why (`bashcut.vlog:plan` §3).

| Part | Length | What |
|---|---|---|
| Hook | 1–3 s | the question + the big number, on a card or over the most striking picture (`vlog-hook-question`) |
| Sections ×4–7 | 6–8 s each vertical (RC); 20–60 s landscape | chip "n/N" + a header bar as it starts (`vlog-section-chip`), one widget that builds with the voice, one picture behind it |
| Recap | 4–6 s | the answer to the hook in one card: the total, the ranking, the route, the verdict |
| CTA | 2–3 s | save, follow, the next part (`vlog-cta`) |

Mark each section with `upsertSection` (label = the section's header) so review and the user see the structure.

## The widgets

One widget per section, chosen by what the words say. Build each with `bashcut.hyperframes:hyperframes` from its
examples, timed so each row lands on its word (`bashcut transcript words` → `at` per row); `bc:motion-graphics`
decides the timing and the hold.

| The section says | Widget | Example to start from |
|---|---|---|
| prices, costs, a budget, a receipt | rows that add up to a total | `cost-table` |
| a comparison, a trend, a ranking | bars that rise with their values | `bar-chart` |
| a day plan, a history, the steps of a process | stops that light up in order | `timeline` |
| a place, a route, distances, travel times | a map with the route drawn and the minutes and km | `map-route` after `bin/osm-map` |
| conditions, rules, what to bring, what to check | items that tick one by one | `checklist-card` |
| one number that matters | the number counting up | `stat-counter` |
| a quote, a law article, a definition | a full-frame card with lines that build | `paper-card` |
| anything else | a catalog block (`hf catalog`) or a composition you design | — |

Vary the widget from section to section: two sections in a row with the same widget need a reason. Graphic density
sits at the top of the 3–8 a minute band (T13 §3) because the widgets are the picture.

## Pictures and frame chrome

- **Where pictures come from**, in this order: the user's own footage or photos; stock (`bc:stock-images`, credit
  line when the licence asks); public-domain or open-licence archives with the credit on screen (Wikimedia, NASA);
  screenshots of a real source, cropped to the part that matters, with the source named; generated illustrations
  (`bashcut.vlog:scene-prompt`). Never present a generated picture as a photo of a real place, person or event.
- **One illustration style for the whole video** (RC: crayon, engraving, paper-cut collage, isometric — one per
  channel): write it in the plan's `decisions` with the prompt fragment that keeps it, and reuse it for every
  generated picture.
- **Frame chrome stays across scenes** (RC): the section chip and header bar, a small channel avatar or mascot in a
  corner when the user has one, a credit line while sourced data or archive pictures are on screen. Only the content
  swaps; the chrome is what makes the channel recognisable. Keep it in the platform's safe zone (`bashcut platforms
  get <id>`).
- **A mascot or character** only from the user's own image or a style they approved; no character is invented and
  presented as theirs.
- **Scene changes**: the widget examples exit by swinging away in 3D; let the next card enter as one leaves
  (0.3–0.45 s overlap). Between photos, a cross-dissolve of 0.3–0.5 s, the title fading out first, then the picture,
  then the new title in (RC). No other transition is needed.

## Facts and honesty

- Every number, date, price, distance and legal claim has a source in the plan's script beats
  (`bashcut.vlog:hook-script`): the user, an official page, an open dataset (OpenStreetMap, Wikipedia, arXiv). A
  number without a source is said to be an example ("số liệu minh hoạ") on the card or in the words, or left out.
- Maps: real coordinates from the user or a named source, a route from `bin/osm-map`; its minutes and km are what
  goes on screen, rounded ("≈ 16 phút · 7,5 km"); "© OpenStreetMap contributors" stays visible.
- Law, health and money: name the law, article and date of the rule; say "check with a professional" when advice
  depends on the viewer's case.

## Two versions: voice or music only

The references ship a voiced version and a music-only version of the same piece (RC). A music-only version needs the
cards to carry every word (longer holds: about letters ÷ 15 + 1–1.5 s, T09 §3), no captions, and its own review
profile (no `minSpeechCoverage`, `maxMusicGapSeconds` set). Make it a sibling project (`bashcut project derive`) or a
second output, not a mix of both.

## Sound

Voice first: a TTS or recorded voice at the measured rate (`bc:voiceover`), music deep under it, a soft whoosh on
card swings and a tick on checklist items when they help (`bc:audio-mix`). Loudness is each output's own target
(`bashcut platforms get`); the older music-only kits shipped 17 dB too quiet (RC), so export with
`--normalize-audio`.

## Look

One palette and one font family for the whole video, taken from the user's brand or a reference
(`bc:style-study`); a paper, kraft or dark textured background behind the cards. Vietnamese text needs a font with
every tone mark (`bc:captions-text`). Photos and footage are graded to match the palette's warmth
(`bc:color-grade`); generated illustrations are left as made.

## Review notes

- A viewer notices: a number said but not on screen, a card that appears before or long after its word, a widget
  that never moves, a map without its credit, two sections built the same way, text too small at phone width,
  captions over a widget. Treat these as blockers.
- Deliberate in an explainer: one card on screen for a whole section (`shot-long` at `info`), no hard cuts, the
  same chrome on every scene.
- `needs_user`: the facts and sources to confirm, the voice (or music only), the illustration style, the user's
  own mascot or avatar and palette if any, whether generated pictures may be used.

## Plan data

What this recipe adds to the plan (`bashcut.vlog:plan` §3); `bc:edit-workflow` and the critic read it.

- `stages`: `{"voiceover": {"required": true, "why": "the voice carries the explanation; the widgets are timed to its words"}, "effects": {"required": true, "skill": "bc:motion-graphics", "why": "one widget per section, built with bashcut.hyperframes:hyperframes"}, "visuals": {"skill": "bc:visual-plan", "after": "voiceover", "required": true, "why": "every line gets a widget, a picture or the chrome alone, on purpose"}}`
  (music-only version: `voiceover` `{"required": false, "why": "music-only version; cards carry the words"}`).
- `checks` (source: explainer recipe): `number-shown` every number said is on screen; `number-sourced` every number
  has a source in the plan or is marked as an example; `widget-on-word` each widget row lands on its word;
  `one-widget-per-section` each section has its widget and neighbours differ; `nothing-frozen` no picture or card
  stands still beyond its reading time; `credit-visible` maps, archive pictures and sourced data keep their credit;
  `one-style` generated pictures share the plan's illustration style.
- `askAtIntake`: `["voiceOrMusicOnly", "factSources", "brandKit"]` (voice or music only; where the facts come from;
  the user's own mascot, avatar, palette and fonts, if any).
