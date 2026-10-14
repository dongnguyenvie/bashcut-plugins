---
name: explainer
description: Recipe for an explainer in BashCut, vertical by default, made without footage or with little of it — a question and a number as the hook, numbered sections each built around one data widget that builds with the voice (cost table, bar chart, timeline, map route, checklist, counter), a recap and a CTA, one illustration style and frame chrome for the whole video, every number with its source; the review profile for cards that move instead of cutting. Use after bashcut.vlog:plan picked explainer, or when the user wants a topic, place, law, history, science or business idea explained with cards, numbers and a voice. Triggers: "video giải thích", "explainer", "giải thích bằng hình", "video kiến thức", "video infographic", "video thẻ", "lịch sử", "luật", "khoa học", "bất động sản", "tuyến đường".
---

# Explainer

Reply in the user's language. An explainer carries its meaning in the words and the widgets, not in footage: plan the
script and the facts first, then design one widget per section that builds while the voice says it. Choose ranges
and values from the tables below, write them into the edit plan and the review profile with `bashcut.vlog:plan`,
then edit with `bc:edit-workflow`.

## Build it in four calls

The whole picture is one list, `plan.cut`: voiceover lines, one graphic per section, captions, music, SFX. Never place
voice takes, graphics or captions one by one with `timeline apply`. `P` is the HyperFrames plugin folder
(`~/Library/Application Support/BashCut/Plugins/bashcut.hyperframes`).

1. **Facts and widgets.** Places: `"$P/bin/osm-map" --places "Hồ Tây, Hà Nội;Hồ Hoàn Kiếm, Hà Nội"` prints each one's
   areaHa, areaKm2 and perimeterKm from OpenStreetMap (no Overpass, no maths by hand). A map:
   `cp -R "$P/examples/map-route" <project>/graphics/map`, then `"$P/bin/osm-map" --dir <project>/graphics/map
   --points "lat,lon,Name;…" [--places "…"]` (route km and minutes; `--places` also draws the outlines to scale).
   `"$P/bin/graphic" examples` lists every widget's variables and defaults in one call: copy the examples you use into
   `<project>/graphics/<name>/` and change only variables unless the design needs more: `stat-counter`, `bar-chart`
   and `cost-table` take `locale` (`vi-VN` writes 11,2 and 528,5), `decimals` and a unit; `stat-counter` `at` and a
   bar's `at` land on a word; `bar-chart` and `stat-counter` take `top`. `bin/osm-map --help` lists its options.
2. **The list.** `bashcut project set-data plan plan.json --merge --base-rev last` with `{cut: {…}}`:
   `voiceover` [{id, text, caption, section, pause}] (one line per sentence; `text` exactly as it should be heard,
   numbers spelled out; `caption` what the captions show instead, with digits),
   `graphics` [{id, section, track: "main", render: {composition: "graphics/<name>", set: {…}, frame: {…}}}] (one
   per section on Main, the picture of the video; overlays such as a counter over the map without `track`;
   `frame` is the chrome every card shares, below), `captions`
   {from: "speech", preset, maxChars (the caption line length from the ranges below), style {positionY}}, `music`
   {media, volumeDb, duckDb}, `sfx` [{media, on: "<graphic id>", offset}], `review` {limits from the ranges below}. In `set`, a value `"@words"` becomes the seconds from the graphic's
   start to where the voice says those words: a row `{"label": "Hồ Tây", "value": 528, "at": "@năm trăm hai mươi
   tám"}` lands on its word. Captions sit above the output's caption bar from the first build (TikTok covers the
   bottom 24 %, `bashcut platforms get tiktok`): `positionY` about 0.3 for one line. The shape, in short (every
   field: `bashcut help plan check`):

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
3. **The voice.** Hand the `voiceover` rows to the `bc:voice` sub-agent and keep only its summary. Without
   sub-agents: `bashcut voice lines --takes 2 --min-similarity 0.9` voices and checks every line in one job
   (`bashcut jobs wait <job> --done --timeout 110` returns `{job: {state, result}, timedOut}` after at most 110 s:
   repeat it in the same shell call until `.job.state` is `completed`; `.job.result.lines` holds each line). A line whose best take lists `unmatched` words: rewrite how it is spelled (a
   number in words, a name split) in plan.cut and run `voice lines --only <id>`.
4. **Render and build.** Hand the `graphics` rows to the `bc:graphics` sub-agent and keep only its summary. Without
   sub-agents: `"$P/bin/graphic" plan` renders every graphic to its span (an exit lands on the span's end)
   and runs `plan apply`: it prints what it rendered and the apply's problems and review. Renders take 10–60 s each
   and run one at a time: give the call a long timeout. After a change, run it again: unchanged graphics are kept.

Before rendering, `bashcut plan check --words` lists what the build would get wrong in `problems`
(`review-errors`: text under a caption bar, a cut inside a word): fix those in the list first. Then look
(`bashcut timeline sheet --cuts --text --outputs tiktok`, `bashcut ui frame F --phone` on landing words), `bashcut review
run --measure`, and export. `bashcut plan check --words` shows each graphic's span and the words heard in it.

Sources: RC = the Reelcrew / AgentVid study (30 explainer and promo videos measured on 2026-10-07: cuts, motion,
still frames, loudness, speech rate, structure); T-notes as in the other recipes.

## Ranges

Outputs: vertical → `tiktok`, `reels`, `shorts`; landscape for YouTube → `youtube-1080` (a science or history piece
of 2–5 min is usually landscape, RC). The ranges are starting points: a measured reference profile
(`bc:style-study`) replaces every range it measures (T07 §7, T15 §7). Write each chosen range, its source and its
reason in the plan.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Cuts | 0–1.5 hard cuts a minute: scenes change by a card swinging away, a dissolve or a widget building, not by cutting (RC) | news and promos cut every 4–4.5 s (12–13 a minute, RC; `bashcut.vlog:news`, `bashcut.vlog:promo`); a calm card piece does not cut at all | `bashcut review shots --summary` → `cutsPerMinute` |
| Long shot `maxShotSeconds`, `severities.shot-long` | `shot-long` at `info`: one card stays on screen for a whole section; judge pace by motion, not by shot length (RC) | a sequence of photos does cut; then use the photo hold below | `review shots --summary`; `review shots` → `motion.mean` |
| Frozen picture `maxStillSeconds`, `severities.still` | 1–2 s, `warning`: nothing is ever still in the references, every picture drifts and every widget builds (RC: still frames 0–14 % in voiced pieces; 14–66 % in the older music-only kits, which read as slides) | a quote or a dense table held to be read may stay still for its reading time | `bashcut review measure`, then `bashcut review picture` (frozen stretches) |
| Jump cut `jumpCutChange`, `severities.jump` | `jump` at `info` when one frame chrome (backdrop, chip, credit) runs through every section: two section cards under it differ little at the swap on purpose (RC: same chrome every scene) | photos or footage cut between sections: keep `warning`, a near-identical swap there is a mistake | `bashcut review run` → `jump-…` issues |
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

Each voiceover line's `section` makes the section markers on apply (labels from `plan.sections`), so review and the
user see the structure.

**A housing project (bất động sản)**, 35–60 s vertical, in four sections:
- **1 The project**: its photo or render, 3–5 s with a drift. A generated or illustrative picture says so on screen
  ("Ảnh tạo bằng AI · dự án minh hoạ"): `bashcut image disclose` labels every `generated` picture (review warns
  `ai-undisclosed` until it does), and `amenity-radius` keeps its `disclosure` line up for an illustrative project.
- **2 Routes to the landmarks, 3 amenities**: one `amenity-radius` graphic, 8–10 s, from one call on its copy:
  `"$P/bin/osm-map" --dir <project>/graphics/area --points "project;landmark;…" --legs star --amenities
  "school,hospital,mall,park" --radius 1000 [--places "…"]`. Every minute, km, count and "nearest" on screen is
  from its output, never counted or measured by hand; landmarks within ~6 km (a farther one gets its own `map-route`).
  A kind in its `none` list is left off the legend; never say or show it as "0".
- **4 Price and CTA**: `cost-table` or `stat-counter` with the price's source and date, then the CTA, 4–6 s.

Ranges: hook 1–3 s on the price or a count ("4 trường trong 1 km"); 0–2 cuts a minute; `maxStillSeconds` as above.

## The widgets

One widget per section, chosen by what the words say, built from the HyperFrames examples (step 1 above); each row
lands on its word with an `"@words"` value. `bc:motion-graphics` decides what each graphic shows and how long it
holds; read `bashcut.hyperframes:hyperframes` only to design something the examples cannot do.

| The section says | Widget | Example to start from |
|---|---|---|
| prices, costs, a budget, a receipt | rows that add up to a total | `cost-table` |
| a comparison, a trend, a ranking | bars that rise with their values | `bar-chart` |
| a day plan, a history, the steps of a process | stops that light up in order | `timeline` |
| a place, a route, distances, travel times | a map with the route drawn and the minutes and km | `map-route` after `bin/osm-map` |
| what is around a place (schools, hospitals, malls, parks) | routes, a radius circle and counts per kind | `amenity-radius` after `bin/osm-map --amenities` |
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
  get <id>`). Give every row the same `render.frame` instead of editing the widgets' HTML: `{"backdrop": "texture"` (or
  `"paper"` for a kraft or notebook look), `"float": true` (held cards keep moving for the frozen-picture check), `"chip": "2/4", "credit": "© OpenStreetMap contributors", "callout": {"text": "≈ *47 lần*", "at":
  "@bốn mươi bảy"}, "scale": 1.2}` — the hook and recap leave out the chip; `map-route` lands each pin on its name
  with `arriveAt` `["@…", "@…"]`.
- **A mascot or character** only from the user's own image or a style they approved; no character is invented and
  presented as theirs.
- **Scene changes**: the widget examples exit by swinging away in 3D; let the next card enter as one leaves
  (0.3–0.45 s overlap). Between full-frame cards on Main, BashCut's `swing` transition does the same swap natively
  (about 0.3 s, 9 frames at 30 fps, RC). Between photos, a cross-dissolve of 0.3–0.5 s, the title fading out first,
  then the picture, then the new title in (RC). No other transition is needed.

## Facts and honesty

- Every number, date, price, distance and legal claim has a source in the plan's script beats
  (`bashcut.vlog:hook-script`): the user, an official page, an open dataset (OpenStreetMap, Wikipedia, arXiv). A
  number without a source is said to be an example ("số liệu minh hoạ") on the card or in the words, or left out.
- Every number: one `fetch_facts.py` call (`bc:motion-graphics`) for all of them before any web search; search by
  hand only for its `none` rows; widget data comes from its `--json` rows {value, unit, credit}.
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
