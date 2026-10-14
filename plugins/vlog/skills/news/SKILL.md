---
name: news
description: Recipe for news and documentary in BashCut from photos, archive pictures and source screenshots with little or no footage — a vertical news short (breaking tag and credit always on, photo with a keyword caption, headline band, quote card, hard cuts about every 4 s) or a landscape documentary (date cards, archive images, named source screenshots, charts, staggered dissolves); honesty rules for every claim, picture, date and quote; the review profile for each shape. Use after bashcut.vlog:plan picked news, or when the user wants a news story, a bulletin, a report or the history of an event told with pictures and a voice. Triggers: "tin tức", "bản tin", "tin nóng", "thời sự", "điểm tin", "phóng sự", "tài liệu", "phim tài liệu", "lịch sử một sự kiện", "chuyện gì đã xảy ra", "news", "breaking news", "news recap", "documentary", "mini documentary".
---

# News and documentary

Reply in the user's language. News carries facts the viewer will repeat: plan the facts and their sources first,
then the pictures that prove them. Choose ranges and values from the tables below, write them into
the edit plan and the review profile with `bashcut.vlog:plan`, then edit with `bc:edit-workflow`.

Sources: RC = the Reelcrew / AgentVid study (measured 2026-10-07; here its 45 s vertical news piece and three
landscape documentaries of 105–292 s); T-notes as in the other recipes.

## Two shapes

| Shape | When | Output |
|---|---|---|
| Vertical news | one recent story, 30–60 s (RC: 45 s) | `tiktok`, `reels`, `shorts` |
| Landscape documentary | an event or a history, 1.5–5 min (RC: 105–292 s) | `youtube-1080` |

Write the shape and its reason in the plan's `decisions`; a vertical cut-down of a documentary is a sibling project
(`bashcut project derive`), not the same timeline reframed.

## Ranges

The ranges are starting points: a measured reference profile (`bc:style-study`) replaces every range it measures
(T07 §7, T15 §7). Write each chosen range, its source and its reason in the plan.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Cuts | vertical: about 12 hard cuts a minute, 4–4.5 s a picture (RC: 12.0, mean 4.49 s); documentary: 0.2–13 a minute (RC) | a documentary of photos cuts like news (RC rosetta: 13.1, 4.4 s); one of illustrations and cards morphs instead (RC: 0.2–0.8) | `bashcut review shots --summary` → `cutsPerMinute`, mean |
| Long shot `maxShotSeconds`, `stillMotion` | vertical: 5–6 s, `shot-long` at `warning`; documentary of morphing cards: `shot-long` at `info`, judge by motion (RC motion 6.4–7.5) | a quote card holds for its reading time | `review shots --summary` max; `review shots` → `motion.mean` |
| Frozen picture `maxStillSeconds`, `severities.still` | 1.5–3 s, `warning`: every photo drifts (Ken Burns 0.3–1.5 % a second, T08 §3); still frames 22 % in the news piece, 1–57 % in documentaries (RC) | a screenshot, a quote or a date card held to be read | `bashcut review measure`, then `bashcut review picture` |
| Hook `hookSeconds` | vertical: 2–3.5 s, the most striking picture and one line that teases the story (RC: first line ends at 3.0 s, first cut 3.4 s); documentary: 3–5 s for the first line over the first picture (explainer recipe), the question inside the cold open (RC) | the first picture must be the story's own, not a stock mood shot | `bashcut review layout --to F`, `transcript words --to F` |
| Speech rate | about 200 syllables a minute in Vietnamese TTS news (RC: 201); silences 1–6 % (RC) | a documentary breathes on its date cards; size lines with the voice's measured rate | `bashcut speech rate`; `bashcut media speech-map` → `gaps` |
| Dead air `maxSilenceSeconds` | 0.5–1 s; one held beat on a date card or before the quote (T07 §3) | — | `bashcut audio measure --timeline` → `silences` |
| Captions `captionLineChars`, `captionMaxLines` | vertical: one keyword caption of 2–4 words over the photo, keyword in the accent colour (RC); documentary: full-sentence subtitles, 1–2 lines, 32–42 characters (T09 §3; RC) | the headline band already says the story; the caption follows the voice | `bashcut review layout` → `longestLineChars`, `wordsPerSecond` |
| Smallest text `minTextSize` | the credit line is the smallest text: set the key to its size once it reads at phone width (`bashcut ui frame <frame> --phone`) | longer outlet names; landscape has more room | `bashcut review layout` → `fontShare` |
| Speech coverage `minSpeechCoverage` | 0.9–0.97 (RC: silence 1–6 %) | lower with music-only title sequences | `bashcut review run` |
| Music under the voice | the deep end of 5–18 dB (T11 §3): a neutral bed or none | up on a documentary's titles and date cards | `bashcut audio mix-measure` → `musicUnderSpeech` |

## Structure

Sample lengths from the references, not slots: the plan gives each section its own range from the facts and says
why (`bashcut.vlog:plan` §3). Mark each with `upsertSection`.

**Vertical news (30–60 s)**

| Part | Length | What |
|---|---|---|
| Hook | 2–3.5 s | the most striking picture of the story and one teasing line (RC: "Tên lửa bay ngang mặt trời…", 3.0 s) |
| What happened | 10–12 s | who, what, when, where: the date said and on screen (RC: 3.4–15 s, two sentences) |
| The latest, in numbers | 12–16 s | 2–3 numbers, each on its picture or a `stat-counter` (RC: 15.5–31 s, three sentences) |
| The quote | 4–6 s | a quote card: the words verbatim, the speaker, role and date; "(lời dịch)" when translated (RC: 5 s) |
| What's next | 5–7 s | the next date or step (RC: "Đầu năm 2027", 6 s); a follow CTA only if the user wants one |

About one picture per sentence of 4.5–6 s, cut in the pause after it (RC: eight sentences, nine cuts; the first cut
at 3.4 s sits in the pause after the first sentence).

**Landscape documentary (1.5–5 min)**

| Part | Length | What |
|---|---|---|
| Cold open | 10–30 s | a present-day headline screenshot, then the question (RC: a 2026 news article, then "…đang nối chúng ta với điều gì?") |
| Chapters ×3–6 | 20–60 s each (explainer recipe, landscape) | a date card, then the archive pictures, screenshots and charts of that moment |
| Return | 10–20 s | back to today: what changed, a chart of the numbers over the years (RC: users 2002–2004, a 2026 ranking) |
| Close | 5–10 s | the question again, now answerable, on a card (RC: "Tri thức, hay cạm bẫy?") |

## Pictures and frame chrome

- **Where pictures come from**, in this order: the user's own; public-domain or open-licence archives (NASA,
  Wikimedia Commons); screenshots of the real source (an article, a document, a log), cropped, the key line
  highlighted, the outlet and date named (RC); stock (`bc:stock-images`) only for generic places and objects, never
  as the event; charts and maps drawn from data. Off-aspect photos fill with a blurred copy (`bc:stock-images`).
- **Generated pictures**: never of a real person, place or event as if photographed. An illustration (a
  reconstruction, an engraving of an ancient scene, a diagram) is allowed in one style for the whole film
  (`bashcut.vlog:scene-prompt`; RC: engraving, paper-cut collage) and, unlike the other recipes, carries a label
  on screen ("ảnh tạo bằng AI", RC): a news viewer takes pictures as evidence.
- **Vertical frame chrome stays on** (RC): a breaking tag (`vlog-breaking-tag`, "TIN NÓNG") and the credit line
  (`vlog-credit-line`) top-left, the photo in the top half with the keyword caption at its foot, the headline band
  mid-frame (`vlog-headline-band`: a topic chip, then 2–3 lines), the blurred photo below. Only the photo and the
  caption change; the chrome never moves. Keep it in the safe zone (`bashcut platforms get <id>`).
- **Documentary chrome**: a date card per chapter (`vlog-date-card`, "30.04.1993"), the source named under each
  screenshot, subtitles at the bottom; the brand's logo small in a corner when there is one.
- **Graphics** (`bashcut.hyperframes:hyperframes`; timing by `bc:motion-graphics`): `stat-counter`, `bar-chart`
  for numbers over years, `timeline` for dates, `map-route` for where, `paper-card` for the quote, `calendar`.

## Transitions

- Vertical news: plain hard cuts on the sentence pauses; no transitions, no whips (RC).
- Documentary: a cross-dissolve of 0.3–0.5 s (9–15 frames at 30 fps) between pictures, staggered: the title fades
  out, then the picture dissolves, then the new title fades in (RC). A date card into its archive picture: the
  picture comes up out of black with a brightness ramp (an `exposure` keyframe, about −2 → 0 EV over 0.5–1 s).
- Paper looks (RC: torn-paper edges, paper sliding in): a `paper-card` graphic, or a custom kind
  (`upsertTransition` with `motion`, e.g. incoming `panX` 1 → 0 and `rotation` 3 → 0) saved with `bc:library`.
  One motif per film.

## Facts and honesty (not taste)

- Every claim, number, date and name has a source in the script beats (`bashcut.vlog:hook-script`): the outlet, the
  official page, the document. No source, or sources that disagree: say so or leave it out.
- Background figures (population, GDP, dates, places): one `fetch_facts.py` call (`bc:motion-graphics`) first; its
  source URL is the on-screen credit. The news itself comes from the outlet, never from it.
- The date of the news is said or shown; a story older than a few days says when it happened ("ngày 30/8").
- Quotes verbatim, the speaker named with role and date; a translated quote says "(lời dịch)"; never shorten a quote
  so it says something else.
- Every picture keeps its credit on screen while it shows; a screenshot names its outlet and date.
- No defamation: an accusation is attributed ("theo …", "cáo buộc"), never stated as fact; no private person's face,
  name or address without a public reason.

## Sound

A clear voice at the measured rate (`bc:voiceover`), a neutral bed deep under it or none, a soft hit on the date
cards when the film uses them (`bc:audio-mix`). Loudness is each output's own target (`bashcut platforms get`);
export with `--normalize-audio`.

## Look

One palette and one type family, from the brand when there is one (`bashcut project get` → `brand`: palette, fonts,
logo; `bashcut library apply <brand-id>`). Intent: news calm and serious, one accent for the tag and the caption
keyword; a documentary paper or dark archive. Archive photos keep their own colour (`bc:color-grade` only to match
exposure). Vietnamese text needs a font with every tone mark (`bc:captions-text`).

## Review notes

- A viewer notices: a picture without its credit, a date said but not shown, a quote with no speaker, a stock shot
  posing as the event, a caption over the headline band, chrome that jumps, a photo that stands still. Blockers.
- Deliberate here: the chrome identical in every shot, plain hard cuts in vertical news, long morphing shots and
  `shot-long` at `info` in a documentary of cards.
- `needs_user`: the facts and sources, the shape, the voice, unclear licences, generated illustrations, the brand.

## Plan data

What this recipe adds to the plan (`bashcut.vlog:plan` §3); `bc:edit-workflow` and the critic read it.

- `stages`: `{"voiceover": {"required": true, "why": "the voice carries the facts; pictures are cut to its phrases"}, "captions": {"rules": ["the chrome (tag, credit, headline band or date card) is placed once and never moves", "every date and number said is on screen"]}, "colour": {"rules": ["archive pictures keep their own colour; match exposure only"]}, "visuals": {"skill": "bc:visual-plan", "after": "voiceover", "required": true, "why": "every line gets a sourced picture, a screenshot, a chart or a card"}}`
- `checks` (source: news recipe): `fact-sourced` every claim, number and date has a source in the plan;
  `credit-visible` every picture keeps its credit while on screen; `date-shown` the date of the news (or of each
  chapter) is on screen; `quote-verbatim` quotes match their source word for word, with the speaker named;
  `generated-labelled` no generated picture shows a real event, and every illustration carries its label;
  `chrome-fixed` the frame chrome stays put across cuts; `nothing-frozen` no photo stands still beyond its reading
  time; `attributed` accusations and disputed claims are attributed.
- `askAtIntake`: `["factSources", "shape", "brandKit"]` (where the facts and pictures come from; vertical news or a
  landscape documentary; the user's palette, fonts and logo, if any).
