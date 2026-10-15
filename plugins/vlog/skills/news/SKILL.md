---
name: news
description: Recipe for news and documentary from photos, archive and source screenshots: a vertical news short with fixed chrome, or a landscape documentary with date cards; honesty rules for every claim, picture, date and quote. Use after bashcut.vlog:plan picks news. Triggers: "tin tức", "bản tin", "tin nóng", "thời sự", "phóng sự", "phim tài liệu", "news".
---

# News and documentary

Reply in the user's language. News carries facts the viewer will repeat: plan the facts and their sources first, then
the pictures that prove them. Ranges go into the plan and review profile with `bashcut.vlog:plan`; edit with
`bc:edit-workflow`.

Sources: RC = the Reelcrew / AgentVid study (measured 2026-10-07; here its 45 s vertical news piece and three
landscape documentaries of 105–292 s); T-notes as in the other recipes.

## Two shapes

| Shape | When | Output |
|---|---|---|
| Vertical news | one recent story, 30–60 s (RC: 45 s) | `tiktok`, `reels`, `shorts` |
| Landscape documentary | an event or a history, 1.5–5 min (RC: 105–292 s) | `youtube-1080` |

Write the shape and its reason in `decisions`; a vertical cut-down of a documentary is a sibling project (`project
derive`), not the same timeline reframed.

## Ranges

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Cuts | vertical: about 12 hard cuts a minute, 4–4.5 s a picture (RC: 12.0, mean 4.49 s); documentary: 0.2–13 a minute (RC) | a documentary of photos cuts like news (RC: 13.1, 4.4 s); one of illustrations and cards morphs instead (RC: 0.2–0.8) | `review shots --summary` → `cutsPerMinute`, mean |
| Long shot `maxShotSeconds`, `stillMotion` | vertical: 5–6 s, `shot-long` at `warning`; documentary of morphing cards: `shot-long` at `info`, judge by motion (RC motion 6.4–7.5) | a quote card holds for its reading time | `review shots --summary`; `motion.mean` |
| Frozen picture `maxStillSeconds`, `severities.still` | 1.5–3 s, `warning`: every photo drifts (Ken Burns 0.3–1.5 % a second, T08 §3); still frames 22 % in the news piece, 1–57 % in documentaries (RC) | a screenshot, quote or date card held to be read | `review measure`, `review picture` |
| Hook `hookSeconds` | vertical: 2–3.5 s, the most striking picture and one teasing line (RC: first line ends 3.0 s, first cut 3.4 s); documentary: 3–5 s for the first line over the first picture, the question inside the cold open (RC) | the first picture must be the story's own, not a stock mood shot | `review layout --to F`, `transcript words --to F` |
| Speech rate | about 200 syllables a minute in Vietnamese TTS news (RC: 201); silences 1–6 % | a documentary breathes on its date cards; size lines with the measured rate | `speech rate`; `media speech-map` |
| Dead air `maxSilenceSeconds` | 0.5–1 s; one held beat on a date card or before the quote (T07 §3) | — | `audio measure --timeline` |
| Captions `captionLineChars`, `captionMaxLines` | vertical: one keyword caption of 2–4 words over the photo, keyword in the accent (RC); documentary: full-sentence subtitles, 1–2 lines, 32–42 characters (T09 §3; RC) | the headline band already says the story | `review layout` → `longestLineChars` |
| `minTextSize` | the credit line is the smallest text: set the key to its size once it reads at phone width (`ui frame F --phone`) | longer outlet names; landscape has more room | `review layout` → `fontShare` |
| `minSpeechCoverage` | 0.9–0.97 (RC) | lower with music-only title sequences | `review run` |
| Music under the voice | the deep end of 5–18 dB (T11 §3): a neutral bed or none | up on a documentary's titles and date cards | `audio mix-measure` |

## Structure

Sample lengths, not slots; the plan gives each section its range and reason; mark each with `upsertSection`.

**Vertical news (30–60 s)**

| Part | Length | What |
|---|---|---|
| Hook | 2–3.5 s | the most striking picture and one teasing line (RC: "Tên lửa bay ngang mặt trời…", 3.0 s) |
| What happened | 10–12 s | who, what, when, where: the date said and on screen (RC: two sentences) |
| The latest, in numbers | 12–16 s | 2–3 numbers, each on its picture or a `stat-counter` (RC: three sentences) |
| The quote | 4–6 s | a quote card: the words verbatim, speaker, role and date; "(lời dịch)" when translated |
| What's next | 5–7 s | the next date or step (RC: "Đầu năm 2027"); a follow CTA only if the user wants one |

About one picture per sentence of 4.5–6 s, cut in the pause after it (RC: eight sentences, nine cuts).

**Landscape documentary (1.5–5 min)**

| Part | Length | What |
|---|---|---|
| Cold open | 10–30 s | a present-day headline screenshot, then the question |
| Chapters ×3–6 | 20–60 s each | a date card, then the archive pictures, screenshots and charts of that moment |
| Return | 10–20 s | back to today: what changed, a chart of the numbers over the years |
| Close | 5–10 s | the question again, now answerable, on a card (RC: "Tri thức, hay cạm bẫy?") |

## Pictures and frame chrome

- **Where pictures come from**, in order: the user's own; public-domain or open archives (NASA, Wikimedia Commons);
  screenshots of the real source (article, document, log), cropped, the key line highlighted, outlet and date named
  (RC); stock (`bc:stock-images`) only for generic places and objects, never as the event; charts and maps from data.
  Off-aspect photos fill with a blurred copy.
- **Generated pictures**: never of a real person, place or event as if photographed. An illustration (a
  reconstruction, an engraving of an ancient scene, a diagram) is allowed in one style for the whole film
  (`bashcut.vlog:scene-prompt`; RC: engraving, paper-cut collage) and, unlike the other recipes, carries a label on
  screen ("ảnh tạo bằng AI", RC): a news viewer takes pictures as evidence.
- **Vertical chrome stays on** (RC): breaking tag (`vlog-breaking-tag`, "TIN NÓNG") and credit line
  (`vlog-credit-line`) top-left, the photo in the top half with the keyword caption at its foot, the headline band
  mid-frame (`vlog-headline-band`: topic chip, then 2–3 lines), the blurred photo below. Only the photo and caption
  change; the chrome never moves. Inside the safe zone.
- **Documentary chrome**: a date card per chapter (`vlog-date-card`, "30.04.1993"), the source under each screenshot,
  subtitles at the bottom; the brand's logo small in a corner when there is one.
- **Graphics** (`bashcut.hyperframes:hyperframes`; timing by `bc:motion-graphics`): `stat-counter`, `bar-chart` for
  numbers over years, `timeline` for dates, `map-route` for where, `paper-card` for the quote, `calendar`.

## Transitions

- Vertical news: plain hard cuts on the sentence pauses; no transitions, no whips (RC).
- Documentary: `dissolve` of 0.3–0.5 s (9–15 frames at 30 fps) between pictures, staggered: the title fades out,
  then the picture dissolves, then the new title fades in (RC). A date card into its archive picture: `dip-black`
  (the picture comes up out of black) over 0.5–1 s.
- Paper looks (RC: torn-paper edges, paper sliding in): a `paper-card` graphic, or the `slide` kind (a custom kind
  saved with `bc:library` only for an extra tilt). One motif per film.

## Facts and honesty (not taste)

- Every claim, number, date and name has a source in the script beats (`bashcut.vlog:hook-script`): the outlet, the
  official page, the document. No source, or sources that disagree: say so or leave it out.
- Background figures (population, GDP, dates, places): one `fetch_facts.py` call (`bc:motion-graphics`) first; its
  source URL is the on-screen credit. The news itself comes from the outlet, never from it.
- The date of the news is said or shown; a story older than a few days says when it happened ("ngày 30/8").
- Quotes verbatim, the speaker named with role and date; a translated quote says "(lời dịch)"; never shorten a quote
  so it says something else.
- Every picture keeps its credit on screen while it shows; a screenshot names its outlet and date. This is the one
  recipe with a credit by default, because a news viewer takes pictures as evidence: the credit names where the
  picture comes from (outlet, agency, archive). Licence notices stay off screen unless the user asks: no
  "© OpenStreetMap contributors" on a map, no stock or CC licence line.
- No defamation: an accusation is attributed ("theo …", "cáo buộc"), never stated as fact; no private person's face,
  name or address without a public reason.

## Sound and look

A clear voice at the measured rate (`bc:voiceover`), a neutral bed deep under it or none, a soft hit on date cards
when the film uses them (`bc:audio-mix`). Intent: news calm and serious, one accent for the tag and the caption
keyword; a documentary paper or dark archive. Archive photos keep their own colour (`bc:color-grade` only to match
exposure).

## Review notes

- Blockers a viewer notices: a picture without its credit, a date said but not shown, a quote with no speaker, a stock
  shot posing as the event, a caption over the headline band, chrome that jumps, a photo that stands still.
- Deliberate: identical chrome in every shot, plain hard cuts in vertical news, long morphing shots and `shot-long`
  at `info` in a documentary of cards.
- `needs_user`: the facts and sources, the shape, the voice, unclear licences, generated illustrations, the brand.

## Plan data

What this recipe adds to the plan (`bashcut.vlog:plan` §3).

- `stages`: `{"voiceover": {"required": true, "why": "the voice carries the facts; pictures are cut to its phrases"}, "captions": {"rules": ["the chrome (tag, credit, headline band or date card) is placed once and never moves", "every date and number said is on screen"]}, "colour": {"rules": ["archive pictures keep their own colour; match exposure only"]}, "visuals": {"skill": "bc:visual-plan", "after": "voiceover", "required": true, "why": "every line gets a sourced picture, a screenshot, a chart or a card"}}`
- `checks` (source: news recipe): `fact-sourced` every claim, number and date has a source in the plan;
  `credit-visible` every picture keeps its credit while on screen; `date-shown` the date of the news (or each
  chapter) is on screen; `quote-verbatim` quotes match their source word for word, speaker named;
  `generated-labelled` no generated picture shows a real event, and every illustration carries its label;
  `chrome-fixed` the chrome stays put across cuts; `nothing-frozen` no photo stands still beyond its reading time;
  `attributed` accusations and disputed claims are attributed.
- `askAtIntake`: `["factSources", "shape", "brandKit"]`.
