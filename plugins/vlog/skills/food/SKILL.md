---
name: food
description: Recipe for a food vlog or food review in BashCut, vertical by default — the bite or pour as the hook with the price, place and price card, quick process inserts, tasting with reactions, verdict and address, CTA; pacing, close-up and slow-motion moves, sound and look intent and the review profile. Use after bashcut.vlog:plan picked food, or when the footage is eating, cooking, a restaurant or a street food stall. Triggers: "review món", "review quán", "vlog ăn uống", "food review", "món ngon", "ăn gì", "mukbang", "nấu ăn", "street food".
---

# Food vlog

Reply in the user's language. Survey the footage, choose values from the ranges below and write the review profile
with `bashcut.vlog:plan` step 2, then edit with `bc:edit-workflow`.

## Ranges

Outputs: vertical → `tiktok`, `reels`, `shorts`. The ranges are starting points; a measured reference wins (T07 §7).
Write each chosen value and its reason in the plan.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Insert length | 0.5–1.5 s (T07 §7); fast short-form averages 0.6–2 s (T07 §3) | shorter for high-motion, low-information shots (steam, sauce); longer when the viewer must read a price | `bashcut review shots --summary` (mean, median, cutsPerMinute per section) |
| Longest shot `maxShotSeconds` | 2–4 s for bites and reactions; one hero hold (a plating reveal, a cheese pull) at 1.5–2.5× the average (T07 §3) | a talking verdict to camera holds longer than a bite | `review shots --summary` max; `review shots --media <id> --summary` for the source takes |
| Shortest shot `minShotSeconds` | the bottom of the insert band, about 0.5 s (T07 §7) | quick inserts are the style here: short shots are only notes | `review shots --summary` min |
| Long static shot `stillMotion` | just under the motion of the macro shots you keep | a tripod top-down plate barely moves; handheld street food moves a lot | `review shots` → `motion.mean` after `bashcut review measure` |
| Held plate or photo `maxStillSeconds` | 1.5–4 s, longer while a line is said over it (T07 §3: change every 1.5–3 s in short-form, calm holds 2–4 s) | a menu board to read holds longer; a silent plate does not | `review measure`, then `bashcut review picture` |
| Frozen picture `severities.still` | `error` or `warning` | error when every held plate gets a push-in in this edit; warning when the footage is mostly photos and some holds are deliberate | `bashcut review run` |
| Hook `hookSeconds` | 1.5–2 s (structure below) | longer only when the price or question is spoken and cannot be cut | `bashcut review hook` |
| Slow motion | as slow as the source has real frames: project fps ÷ source fps (60 fps in a 30 fps project → 0.5×, 120 fps → 0.25×) | a 30 fps source at 0.5× repeats frames and stutters; use a speed ramp or full speed instead | `bashcut media list` → `fps` per media; project fps from `bashcut timeline get` |
| Punch-in on a reaction | up to the clip's headroom, and only while the face and food stay framed | a 4K source in a 1080 project has room; a phone 1080 clip has none | `bashcut timeline get` → `scale.maxZoomNative` (beyond it, upscaled) |
| Captions `captionLineChars`, `captionMaxLines` | vertical 15–32 characters, 1–2 lines (T09 §3) | energetic talk takes 2–4 words a group, calm talk 3–6 (T09 §3) | `bashcut review layout` → `longestLineChars`, `wordsPerSecond` |
| Music under the voice | 5–18 dB under (T11 §3); dip further under ASMR moments | the real sizzle and crunch lead here (T11 §7: room-tone first for food ASMR) | `bashcut audio mix-measure` → `musicUnderSpeech`, `musicInGaps` |

## Structure (25–45 s)

| Part | Length | What |
|---|---|---|
| Hook | 1.5–2 s | the best bite, pull or pour in close-up, slowed if the source allows, with `vlog-price-tag` or a question ("45K CÓ ĐÁNG?") |
| Place | 3–4 s | sign or front of the shop + `place-card` (name · district), the price tag if not in the hook |
| Process | 4–8 s | 3–5 quick inserts (0.5–1.5 s): cooking, plating, sauce, steam |
| Tasting | 8–15 s | 2–3 bites, each: close-up of the food → the bite → the face; `vlog-pro`/`vlog-con` stickers for what is said |
| Verdict | 3–4 s | score or one-line verdict (`vlog-verdict`), price and address |
| CTA | 2 s | `vlog-cta` ("LƯU LẠI ĐỂ ĂN THỬ") |

## Cuts and motion

- The fastest recipe: inserts and bites from the ranges above.
- Slow motion on pours, cheese pulls, steam and the first bite, at the speed the source frame rate allows (above);
  punch-in (`zoom-punch-in`) on the reaction within the clip's headroom.
- `vlog-zoom-hit` into the dish at a section start; no transitions inside the tasting.
- A held plate shot gets a slow push-in rather than sitting still.

## Shots to look for and to shoot

Macro of the dish (top-down and 45°), the pour or pull, steam, the bite from the side, the face right after, the shop
front, the menu or price board, the cook's hands. Shoot the pour and the pull at 60 fps or more if slow motion is
planned. No close-up of the food is the most common gap: say so before editing; a punch-in on a wider shot is the
fallback when the headroom allows it.

## Text, sound, look

- Text: price always on screen; one keyword sticker per bite at most.
- Sound: keep the real sizzle, crunch and slurp up front (ASMR moments: music dips under them); short pop/ding on
  price tags (`bc:audio-mix` for finding SFX). Loudness is each output's own target (`bashcut platforms list`).
- Look intent: warm, rich colour, appetising; never green-tinted or grey; highlights on sauce kept. Measure first
  (`bc:color-grade`); no fixed numbers.
