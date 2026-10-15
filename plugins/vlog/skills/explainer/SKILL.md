---
name: explainer
description: Recipe for an explainer with little or no footage: a question-and-number hook, one data widget per section timed to the voice (table, chart, map, counter), every number sourced. Use after bashcut.vlog:plan picks explainer. Triggers: "video giải thích", "explainer", "video kiến thức", "infographic", "lịch sử", "luật", "bất động sản".
---

# Explainer

Reply in the user's language. An explainer carries its meaning in the words and the widgets, not in footage: plan the
script and the facts first, then one widget per section that builds while the voice says it. Ranges go into the plan
and the review profile with `bashcut.vlog:plan`; edit with `bc:edit-workflow`.

## Build it in four calls

The whole picture is one list, `plan.cut`: voiceover lines, one graphic per section (a growing diagram: one for all), captions, music, SFX. Never
place voice takes, graphics or captions one by one with `timeline apply`. `P` is the HyperFrames plugin folder
(`~/Library/Application Support/BashCut/Plugins/bashcut.hyperframes`).

1. **Facts and widgets.** Places: `"$P/bin/osm-map" --places "Hồ Tây, Hà Nội;…"` prints each one's area and
   perimeter from OpenStreetMap (no maths by hand). A map: copy `$P/examples/map-route` into
   `<project>/graphics/map`, then `osm-map --dir … --points "lat,lon,Name;…"` (route km and minutes; `--places` draws
   outlines to scale). `"$P/bin/graphic" examples` lists every widget's variables in one call; copy the ones you use
   and change only variables unless the design needs more (`locale` `vi-VN` writes 11,2 and 528,5).
2. **The list.** `project set-data plan --merge` with `{cut: {…}}`: `voiceover` (one line per sentence; `text`
   exactly as heard, numbers spelled out; `caption` what the captions show instead, with digits), `graphics` (one
   per section on Main with `track: "main"`, the picture of the video; overlays such as a counter over the map
   without `track`; `render.frame` the chrome every card shares, below), `captions`, `music`, `sfx` (`on` a graphic
   id), `review` (limits from the ranges below). Every field: `bashcut help plan check`. In `set`, `"@words"` becomes
   the seconds from the graphic's start to those words, so a row lands on its word. Captions sit above the output's
   caption bar from the first build (TikTok covers the bottom 24 %: `positionY` about 0.3 for one line).

   ```json
   {"sections": [{"id": "s1", "label": "1/4 Hồ Gươm"}],
    "cut": {"voiceover": [{"id": "l1", "text": "Hồ Gươm rộng mười một phẩy hai héc ta.", "caption": "Hồ Gươm rộng 11,2 ha.",
                           "section": "s1", "pause": 0.3}],
            "graphics": [{"id": "g1", "section": "s1", "track": "main",
                          "render": {"composition": "graphics/s1-count", "set": {"from": 0, "to": 11.2,
                                     "unit": " ha", "locale": "vi-VN", "label": "Hồ Gươm", "at": "@héc ta"}}}],
            "captions": {"from": "speech", "maxChars": 26, "style": {"positionY": 0.3}},
            "review": {"captionLineChars": 26, "maxStillSeconds": 2}}}
   ```
3. **The voice.** Hand the `voiceover` rows to the `bc:voice` sub-agent and keep only its summary (without
   sub-agents: `bc:voiceover`, `voice lines`). A line whose best take has `unmatched` words: respell it (a number in
   words, a name split) and voice only that line again.
4. **Render and build.** Hand the `graphics` rows to the `bc:graphics` sub-agent (without: `"$P/bin/graphic" plan`
   renders every graphic to its span and runs `plan apply`; 10–60 s per render, one at a time, so give it a long
   timeout; unchanged graphics are kept on a rerun).

Before rendering, `plan check --words` lists `problems` (text under a caption bar, a cut inside a word) and each
graphic's span with the words heard in it: fix those first. Then look (`timeline sheet --cuts --text --outputs
tiktok`, `ui frame F --phone` on landing words), `review run --measure`, export.

Sources: RC = the Reelcrew / AgentVid study (30 explainer and promo videos measured 2026-10-07: cuts, motion, still
frames, loudness, speech rate, structure); T-notes as in the other recipes.

## Ranges

Outputs: vertical → `tiktok`, `reels`, `shorts`; landscape → `youtube-1080` (a 2–5 min science or history piece is
usually landscape, RC).

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Cuts | 0–1.5 hard cuts a minute: scenes change by a card swinging away, a dissolve or a widget building (RC) | news and promos cut every 4–4.5 s (RC); a calm card piece does not cut at all | `review shots --summary` → `cutsPerMinute` |
| Long shot `maxShotSeconds`, `severities.shot-long` | `shot-long` at `info`: one card per section; judge pace by motion (RC) | a sequence of photos does cut: use the photo hold below | `review shots` → `motion.mean` |
| Frozen picture `maxStillSeconds`, `severities.still` | 1–2 s, `warning`: every picture drifts and every widget builds (RC: still frames 0–14 % in voiced pieces; 14–66 % in older music-only kits, which read as slides) | a quote or dense table held to be read | `review measure`, `review picture` |
| Jump cut `jumpCutChange`, `severities.jump` | `info` when one frame chrome runs through every section: two cards under it differ little on purpose (RC) | photos or footage cut between sections: keep `warning` | `review run` → `jump-…` |
| Photo or illustration hold | 2–4 s with a Ken Burns drift of 0.3–1.5 % a second (T08 §3); 3–6 s under a line | a photo with a widget holds while the widget builds | `timeline get` keyframes; `review picture` |
| Hook `hookSeconds` | 1–3 s: a question and one big concrete number on screen ("Lãi thật mỗi đơn 37.000đ?", "938 · Trận Bạch Đằng") (RC) | landscape long-form may say the question over a title for 3–5 s | `review layout --to F`, `transcript words --to F` |
| Speech rate | 165–236 syllables a minute in Vietnamese TTS explainers; silences 0–6 % (RC) | dense legal or science text sits low; size lines with the voice's measured rate | `speech rate`; `media speech-map` → `gaps` |
| Dead air `maxSilenceSeconds` | 0.5–1 s between sections; one held beat before the payoff (T07 §3) | music-only: `maxMusicGapSeconds` instead | `audio measure --timeline` |
| Captions `captionLineChars`, `captionMaxLines` | one line of 3–6 words, keyword highlighted, on a pill (RC); vertical 15–32 characters (T09 §3) | music-only: no captions, the cards carry the words | `review layout` → `longestLineChars` |
| `minSpeechCoverage` | 0.85–0.95 voiced (RC) | music-only: unset | `review run` |
| Music under the voice | the deep end of 5–18 dB (T11 §3): every word is information | music-only: music is the only layer | `audio mix-measure` |

## Structure (45–90 s vertical, 2–5 min landscape)

Sample lengths, not slots; the plan gives each section its range and reason.

| Part | Length | What |
|---|---|---|
| Hook | 1–3 s | the question + the big number, on a card or the most striking picture (`vlog-hook-question`) |
| Sections ×4–7 | 6–8 s each vertical (RC); 20–60 s landscape | chip "n/N" + header bar (`vlog-section-chip`), one widget that builds with the voice, one picture behind it |
| Recap | 4–6 s | the answer to the hook in one card: total, ranking, route, verdict |
| CTA | 2–3 s | save, follow, the next part (`vlog-cta`) |

Each voiceover line's `section` makes the section markers on apply (labels from `plan.sections`).

**A housing project (bất động sản)**, 35–60 s vertical, four sections:
- **1 The project**: its photo or render, 3–5 s with a drift. No AI or "minh hoạ" label on the video, and no
  `disclosure` line on `amenity-radius`; accept review's `ai-undisclosed` with `review accept --reason` and tell the
  user to turn on the platform's AI toggle when posting (`bashcut.vlog:publish`).
- **2 Routes to landmarks, 3 amenities**: one `amenity-radius` graphic, 8–10 s, from one `osm-map --legs star
  --amenities "school,hospital,mall,park" --radius 1000` call on its copy (`--style dark` for a dark map). Every minute, km, count and "nearest" on
  screen comes from its output, never counted by hand; landmarks within ~6 km (a farther one gets its own
  `map-route`). A kind in its `none` list is left off the legend: never say or show it as "0" (never set `showZero`).
- **4 Price and CTA**: `cost-table` or `stat-counter` with the price's source and date, then the CTA, 4–6 s.

Ranges: hook 1–3 s on the price or a count ("4 trường trong 1 km"); 0–2 cuts a minute.

## The widgets

One per section, chosen by what the words say; each row lands on its word (`"@words"`). `bc:motion-graphics` decides
what each graphic shows and how long it holds; read `bashcut.hyperframes:hyperframes` only for what the examples
cannot do.

| The section says | Example to start from |
|---|---|
| prices, costs, a budget (rows adding up to a total) | `cost-table` |
| a comparison, a trend, a ranking | `bar-chart` |
| a day plan, a history, the steps of a process | `timeline` |
| a system or flow that grows with the voice across sections | one `growing-diagram` for all of them (`render.scene`) |
| a place, a route, distances, travel times | `map-route` after `osm-map` |
| what is around a place | `amenity-radius` after `osm-map --amenities` |
| conditions, rules, what to bring or check | `checklist-card` |
| one number that matters | `stat-counter` |
| a quote, a law article, a definition | `paper-card` |
| anything else | a catalog block (`hf catalog`) or your own composition |

Two sections in a row with the same widget need a reason. Graphic density sits at the top of the 3–8 a minute band
(T13 §3): the widgets are the picture.

## Pictures and frame chrome

- **Where pictures come from**, in order: the user's own; stock (`bc:stock-images`); public-domain or open archives
  (Wikimedia, NASA); screenshots of a real source, cropped; generated illustrations (`bashcut.vlog:scene-prompt`).
  Never present a generated picture as a photo of a real place, person or event.
- **One illustration style for the whole video** (RC: crayon, engraving, paper-cut collage, isometric — one per
  channel): in `decisions` with the prompt fragment that keeps it, reused for every generated picture.
- **Frame chrome stays across scenes** (RC): section chip and header bar, the user's avatar or mascot in a corner if
  any; only the content swaps. No credit, source or licence line on the picture unless the user asks for one (then
  `render.frame` › `credit`). Inside the safe zone. Give every row the same `render.frame` instead of editing HTML,
  e.g. `{"backdrop": "texture"|"paper", "float": true, "chip": "2/4", "callout": {"text": "≈ *47 lần*", "at": "@bốn
  mươi bảy"}, "scale": 1.2}` (`float` keeps held cards moving for the frozen-picture check; hook and recap leave out
  the chip; `map-route` lands each pin with `arriveAt` `["@…"]`). Keys: `bashcut.hyperframes:hyperframes`.
- **A mascot or character** only from the user's own image or a style they approved; never invented and presented as
  theirs.
- **Scene changes**: widgets exit by swinging away in 3D; the next card enters as one leaves (0.3–0.45 s overlap).
  Between full-frame cards on Main, the `swing` transition does it natively (about 9 frames at 30 fps, RC). Between
  photos, a `dissolve` of 0.3–0.5 s, the title fading out first, then the picture, then the new title in (RC). No
  other transition is needed.

## Facts and honesty

- Every number, date, price, distance and legal claim has a source in the script beats (`bashcut.vlog:hook-script`):
  the user, an official page, an open dataset. A number without a source is said to be an example ("số liệu minh
  hoạ") on the card or in the words, or left out.
- All numbers: one `fetch_facts.py` call (`bc:motion-graphics`) before any web search; search by hand only its `none`
  rows; widget data comes from its rows {value, unit, credit}.
- Maps: real coordinates from the user or a named source, the route from `osm-map`; its minutes and km go on screen
  rounded ("≈ 16 phút · 7,5 km"). No map credit on screen unless the user asks (`credit` variable).
- Law, health and money: name the law, article and date of the rule; say "check with a professional" when advice
  depends on the viewer's case.

## Two versions: voice or music only

The references ship both (RC). A music-only version makes the cards carry every word (holds about letters ÷ 15 +
1–1.5 s, T09 §3), has no captions and its own profile (no `minSpeechCoverage`, `maxMusicGapSeconds` set). Make it a
sibling project (`project derive`) or a second output, never a mix.

## Sound and look

Voice first at the measured rate (`bc:voiceover`), music deep under it, a soft whoosh on card swings and a tick on
checklist items when they help (`bc:audio-mix`). The older music-only kits shipped 17 dB too quiet (RC): normalize
(plan §4). One palette and one font family from the brand or a reference (`bc:style-study`); a paper, kraft or dark
textured background behind the cards; photos graded to the palette's warmth (`bc:color-grade`); generated
illustrations left as made.

## Review notes

- Blockers a viewer notices: a number said but not on screen, a card before or long after its word, a widget that
  never moves, two sections built the same way, text too small at phone width, captions
  over a widget.
- Deliberate: one card for a whole section (`shot-long` at `info`), no hard cuts, the same chrome on every scene.
- `needs_user`: the facts and sources, voice or music only, the illustration style, the user's mascot, avatar and
  palette, whether generated pictures may be used.

## Plan data

What this recipe adds to the plan (`bashcut.vlog:plan` §3).

- `stages`: `{"voiceover": {"required": true, "why": "the voice carries the explanation; the widgets are timed to its words"}, "effects": {"required": true, "skill": "bc:motion-graphics", "why": "one widget per section, built with bashcut.hyperframes:hyperframes"}, "visuals": {"skill": "bc:visual-plan", "after": "voiceover", "required": true, "why": "every line gets a widget, a picture or the chrome alone, on purpose"}}`
  (music-only: `voiceover` `{"required": false, "why": "music-only version; cards carry the words"}`).
- `checks` (source: explainer recipe): `number-shown` every number said is on screen; `number-sourced` every number
  has a source or is marked as an example; `widget-on-word` each widget row lands on its word;
  `one-widget-per-section` each section has its widget and neighbours differ; `nothing-frozen` nothing stands still
  beyond its reading time; `one-style`
  generated pictures share the plan's illustration style.
- `askAtIntake`: `["voiceOrMusicOnly", "factSources", "brandKit"]`.
