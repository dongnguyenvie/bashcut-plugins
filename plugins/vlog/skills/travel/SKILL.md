---
name: travel
description: Recipe for a travel vlog or travel guide in BashCut, vertical by default — hook with a cost or time number, numbered place sections with place cards, a cost recap and a save/follow CTA; pacing, text, sound and look intent and the review profile to set. Use after bashcut.vlog:plan picked travel, or when the user edits footage of a trip, a city, places or a route. Triggers: "vlog du lịch", "review chuyến đi", "đi Đà Lạt", "48h ở", "lịch trình", "travel vlog", "travel guide", "ăn chơi ở", "check-in".
---

# Travel vlog

Reply in the user's language. Survey the footage, choose values from the ranges below and write the review profile
with `bashcut.vlog:plan` step 2, then edit with `bc:edit-workflow`.

## Ranges

Outputs: vertical → `reels`, `tiktok`, `shorts`; landscape for YouTube → `youtube-1080`. The ranges are starting
points; a measured reference wins (T07 §7). Write each chosen value and its reason in the plan.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Average shot | 3–4.5 s; 1–2 s in the hook and when listing things (T07 §7) | longer with dense voiceover, landscape or a calm place, within the 2.5–6 s vlog band (T07 §3) | `bashcut review shots --summary` (mean, median, cutsPerMinute per section) |
| Longest shot `maxShotSeconds` | the top of your average band; one hero hold (the view at its best) at 1.5–2.5× the average (T07 §3) | a long walking or drone take can hold if it moves; locked-off views cannot | `review shots --summary` max; `review shots --media <id> --summary` for the source takes |
| Long static shot `stillMotion` | just under the motion of the moving takes you keep | handheld walking moves more than tripod views | `review shots` → `motion.mean` after `bashcut review measure` |
| Shortest shot `minShotSeconds` | near the 0.6 s under which `bc:beat-cut` merges pieces (T07 §5) | a beat-cut list can go shorter on purpose (short shots are only notes) | `review shots --summary` min |
| Photo or locked-off hold `maxStillSeconds` | 1.5–4 s, longer while a line is said over it (T07 §3: change every 1.5–3 s in short-form, calm holds 2–4 s) | photos with voiceover or text to read hold longer; a silent photo montage cannot | `review measure`, then `bashcut review picture` (frozen stretches) |
| Frozen picture `severities.still` | `error` or `warning` | error when every still should move in this edit; warning when some holds are deliberate (a sign, a map) | `bashcut review run` |
| Repeated framing `severities.framing` | `warning` | two clips of one place with the same framing read as a jump: fix with a punch-in, not a note | `bashcut review cuts` → `sameFraming` |
| Hook `hookSeconds` | 2–3 s (structure below) | later only when the number is said late and cannot move | `bashcut review hook` |
| Captions `captionLineChars`, `captionMaxLines` | vertical 15–32 characters, 1–2 lines; landscape 32–42 (T09 §3) | font width and size, speech rate | `bashcut review layout` → `longestLineChars`, `wordsPerSecond` |
| Music under the voice | toward the small end of 5–18 dB (T11 §3) in montage parts, deeper under dense voiceover | music carries a travel montage; vocals or a soft voice need more room | `bashcut audio mix-measure` → `musicUnderSpeech` |

## Structure (45–75 s vertical)

| Part | Length | What |
|---|---|---|
| Hook | 2–3 s | the most striking shot plus `vlog-hook-question`: a number the viewer wants (cost, hours, days) and a question — "48H Ở ĐÀ LẠT HẾT BAO NHIÊU?" |
| Sections ×4–6 | 6–8 s each | one place or one step of the route; `vlog-section-chip` ("2/5 · CHỢ ĐÊM") as it starts, `place-card` with the name, `vlog-price-tag` when money is said |
| Recap | 4–6 s | the total (cost table as stacked lines, or the route in one map shot) |
| CTA | 2–3 s | `vlog-cta` ("LƯU LẠI ĐỂ ĐI NHÉ!") over the nicest wide shot |

Mark each section with `upsertSection` (label = place name) so review and the user see the structure.

## Cuts and motion

- Cut rate from the range above: about 13–16 cuts a minute at 3–4.5 s a shot; faster in the hook and in lists.
- Every still or locked-off shot moves: Ken Burns (`ken-burns-in`/`-out`, `bc:effects`); hold a photo 1.5–4 s, longer
  while a line is said over it.
- Between sections: `vlog-whip-fast` or a hard cut on a beat (`bc:beat-cut`); inside a section, hard cuts only.
- Walking, driving and food shots: speed ramp through the boring middle (`speed-ramp`).
- Punch-in on a repeated framing: as far as the clip's headroom allows (`bashcut timeline get` → `scale.maxZoomNative`;
  beyond it the picture is upscaled) and as far as the framing still shows the place.

## Shots to look for (survey) and to shoot

Establishing wide of each place, a detail (sign, food, ticket), the person in the place (selfie or from behind),
movement between places (feet, vehicle, window), the view at the best moment (sunset, night lights). Missing an
establishing shot: use the widest shot of the place, or a stock picture labelled `vlog-disclosure` when it is not
the user's own (`bc:stock-images`).

## Text and voice

- Captions from the voice (`bc:captions-text`), bold-outline, 3–6 words a line; keep them above the platform's
  caption bar (the review checks it).
- Voiceover when the footage has none: 165–235 Vietnamese syllables a minute, one fact per section
  (`bashcut.vlog:hook-script`, `bc:voiceover`).
- Numbers are always on screen when said (price, time, distance).

## Sound

Upbeat music bed under the voice (ducked, level from the range above); natural sound of each place for the first
second of its section; a whoosh on the whips. Loudness is each output's own target (`bashcut platforms list`); do not
set it here (`bc:audio-mix`).

## Look

Intent: bright, warm and clean, skies not blown out, skin natural. Measure the footage first and grade to that intent
(`bc:color-grade`); never apply fixed numbers. One look for the whole video; night shots may stay cooler.
