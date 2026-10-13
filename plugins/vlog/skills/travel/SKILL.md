---
name: travel
description: Recipe for a travel vlog or travel guide in BashCut, vertical by default — hook with a cost or time number, numbered place sections with place cards, a cost recap and a save/follow CTA; pacing, text, sound and look intent and the review profile to set. Use after bashcut.vlog:plan picked travel, or when the user edits footage of a trip, a city, places or a route. Triggers: "vlog du lịch", "review chuyến đi", "đi Đà Lạt", "48h ở", "lịch trình", "travel vlog", "travel guide", "ăn chơi ở", "check-in".
---

# Travel vlog

Reply in the user's language. Survey the footage, choose ranges and values from the tables below, write them into the
edit plan and the review profile with `bashcut.vlog:plan`, then edit with `bc:edit-workflow`.

## Ranges

Outputs: vertical → `reels`, `tiktok`, `shorts`; landscape for YouTube → `youtube-1080`. The ranges are starting
points: a measured reference profile (`bc:style-study`) replaces every range it measures, and the recipe only fills
what it does not measure (T07 §7, T15 §7). Write each chosen range, its source and its reason in the plan.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Average shot | 3–4.5 s; 1–2 s in the hook and when listing things (T07 §7) | longer with dense voiceover, landscape or a calm place, within the 2.5–6 s vlog band (T07 §3) | `bashcut review shots --summary` (mean, median, cutsPerMinute per section) |
| Longest shot `maxShotSeconds` | the top of your average band; one hero hold (the view at its best) at 1.5–2.5× the average (T07 §3) | a long walking or drone take can hold if it moves; locked-off views cannot | `review shots --summary` max; `review shots --media <id> --summary` for the source takes |
| Long static shot `stillMotion` | just under the motion of the moving takes you keep | handheld walking moves more than tripod views | `review shots` → `motion.mean` after `bashcut review measure` |
| Shortest shot `minShotSeconds` | near the 0.6 s under which `bc:beat-cut` merges pieces (T07 §5) | a beat-cut list can go shorter on purpose (short shots are only notes) | `review shots --summary` min |
| Photo or locked-off hold `maxStillSeconds` | 1.5–4 s, longer while a line is said over it (T07 §3: change every 1.5–3 s in short-form, calm holds 2–4 s) | photos with voiceover or text to read hold longer; a silent photo montage cannot | `review measure`, then `bashcut review picture` (frozen stretches) |
| Frozen picture `severities.still` | `error` or `warning` | error when every still should move in this edit; warning when some holds are deliberate (a sign, a map) | `bashcut review run` |
| Jump cut `jumpCutChange` | just above the picture change of cuts that read as a jump (same place, same framing included) | fix with a punch-in, not a note | `bashcut review shots` → `cut.sameFraming`; `review picture` cut `difference` |
| Hook `hookSeconds` | 2–3 s (structure below) | later only when the number is said late and cannot move | `bashcut review layout --to F`, `transcript words --to F` |
| Captions `captionLineChars`, `captionMaxLines` | vertical 15–32 characters, 1–2 lines; landscape 32–42 (T09 §3) | font width and size, speech rate | `bashcut review layout` → `longestLineChars`, `wordsPerSecond` |
| Music under the voice | toward the small end of 5–18 dB (T11 §3) in montage parts, deeper under dense voiceover | music carries a travel montage; vocals or a soft voice need more room | `bashcut audio mix-measure` → `musicUnderSpeech` |

## Structure (45–75 s vertical)

Sample lengths from earlier vlog practice, not slots: the plan gives each section its own range from the footage
and says why (`bashcut.vlog:plan` §3); review compares it with the section marker.

| Part | Length | What |
|---|---|---|
| Hook | 2–3 s | the most striking shot plus `vlog-hook-question`: a number the viewer wants (cost, hours, days) and a question — "48H IN DA LAT / HOW MUCH?" |
| Sections ×4–6 | 6–8 s each | one place or one step of the route; `vlog-section-chip` ("2/5 · CHỢ ĐÊM") as it starts, `place-card` with the name, `vlog-price-tag` when money is said |
| Recap | 4–6 s | the total (cost table as stacked lines, or the route in one map shot) |
| CTA | 2–3 s | `vlog-cta` ("LƯU LẠI ĐỂ ĐI NHÉ!") over the nicest wide shot |

Mark each section with `upsertSection` (label = place name) so review and the user see the structure.

## Cuts and motion

- Cut rate from the ranges above: about 13–16 cuts a minute at 3–4.5 s a shot; faster in the hook and in lists.
- Every still or locked-off shot moves: Ken Burns (`ken-burns-in`/`-out`, `bc:effects`) at the drift rate below; hold
  a photo 1.5–4 s, longer while a line is said over it.
- Walking, driving and food shots: speed ramp through the boring middle (`speed-ramp`).
- Punch-in on a repeated framing: as far as the clip's headroom allows (`bashcut timeline get` → `scale.maxZoomNative`;
  beyond it the picture is upscaled) and as far as the framing still shows the place.

## Rhythm, transitions and graphics

| What | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Tone bands | calm stretches 2–4 s a shot; urgent stretches (a rush, a list) 0.4–1 s (T07 §3) | arrival and views are calm; lists and transfers are quick | `bashcut review shots --summary` per section |
| Pattern interrupt | a new place, number or change of pace every 10–30 s short-form; 30–90 s long-form (T07 §3) | each place section is one; a long walk needs one inside it | `review shots --summary` per section |
| Breath before the payoff | one held moment of 0.5–2 s before the best view, once or twice a video (T07 §3, §7) | a montage to music breathes on the drop | `bashcut review window <frame>` |
| Transitions | between places: `vlog-whip-fast` (0.2–0.4 s, same direction on both sides) or a hard cut on a beat; inside a place: hard cuts only (T08 §3, §7) | a calm landscape edit uses `vlog-soft-cut` for time passing | `bashcut review shots` → count `cut.kind` and its runs |
| Transition budget | special transitions 1–3 per minute of short form; whips 1–2 per short (T08 §3) | a fast many-place montage may use more as a declared motif; say so in the plan | `review shots` `cut.kind` counts ÷ minutes |
| Ken Burns drift | 0.3–1.5 % a second, alternating direction (T08 §3) | bigger for short photos in a fast edit | `bashcut timeline get` → keyframes |
| Place card, section chip | at the section start, held for reading: about letters ÷ 15 + 1–1.5 s (T09 §3) | longer names, busier backgrounds | `bashcut review layout` → `holdSeconds` |
| Price tag | lands on the word the price is said: its entrance (0.15–0.6 s) ends on the word, held while it is said (T13 §3) | energy of the edit | `bashcut transcript words`; `review layout` |
| Graphic density | about one card per section plus price tags; travel sits at the low end next to explainers' 3–8 per minute (T13 §3, §7) | a cost guide has more numbers than a mood film | `review layout` → text items per minute |

## Shots to look for (survey) and to shoot

Establishing wide of each place, a detail (sign, food, ticket), the person in the place (selfie or from behind),
movement between places (feet, vehicle, window), the view at the best moment (sunset, night lights). Missing an
establishing shot: use the widest shot of the place, or a stock picture (`bc:stock-images`), unlabelled on the video
and never named as the real place.

## Text and voice

- Captions from the voice (`bc:captions-text`), bold-outline, 3–6 words a line; keep them above the platform's
  caption bar (the review checks it).
- Voiceover when the footage has none: one fact per section, sized with the measured rate of the voice
  (`bashcut.vlog:hook-script`, `bc:voiceover`).
- Numbers are always on screen when said (price, time, distance).

## Sound

Upbeat music bed under the voice (ducked, level from the range above); natural sound of each place for the first
second of its section; a whoosh on the whips. Loudness is each output's own target (`bashcut platforms get`); do not
set it here (`bc:audio-mix`).

## Look

Intent: bright, warm and clean, skies not blown out, skin natural. Measure the footage first and grade to that intent
(`bc:color-grade`); never apply fixed numbers. One look for the whole video; night shots may stay cooler.

## Review notes

- A viewer notices: a place named but never labelled, a price said but not shown, a photo frozen with nothing said
  over it, two clips of one place with the same framing back to back. Treat these as blockers.
- Deliberate in travel: a long walking or drone take that keeps moving (`shot-long` stays a note when it is over
  `stillMotion`), the one hero hold of the best view, quick cuts in lists.
- `needs_user`: prices and place names to confirm, the route order when capture times are missing, whether stock or
  generated shots may fill a missing place, the music.

## Plan data

What this recipe adds to the plan (`bashcut.vlog:plan` §3); `bc:edit-workflow` and the critic read it.

- `stages`: `{"captions": {"rules": ["place card at each location change; a number said is on screen"]}}`
- `checks` (source: travel recipe): `place-labelled` every place named is labelled on screen; `price-shown` every
  price said is on screen; `no-silent-still` no photo held with nothing said or heard over it; `route-order` places
  follow the route or the capture time, or the plan says why; `place-framing` no two clips of one place back to back
  with the same framing.
- `askAtIntake`: `["stockAllowed"]` (may stock or generated shots fill a missing place).
