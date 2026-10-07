---
name: food
description: Recipe for a food vlog or food review in BashCut, vertical by default — the bite or pour as the hook with the price, place and price card, quick process inserts, tasting with reactions, verdict and address, CTA; pacing, close-up and slow-motion moves, sound and look intent and the review profile. Use after bashcut.vlog:plan picked food, or when the footage is eating, cooking, a restaurant or a street food stall. Triggers: "review món", "review quán", "vlog ăn uống", "food review", "món ngon", "ăn gì", "mukbang", "nấu ăn", "street food".
---

# Food vlog

Reply in the user's language. Survey the footage, choose ranges and values from the tables below, write them into the
edit plan and the review profile with `bashcut.vlog:plan`, then edit with `bc:edit-workflow`.

## Ranges

Outputs: vertical → `tiktok`, `reels`, `shorts`. The ranges are starting points: a measured reference profile
(`bc:style-study`) replaces every range it measures, and the recipe only fills what it does not measure
(T07 §7, T15 §7). Write each chosen range, its source and its reason in the plan.

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

Sample lengths from earlier vlog practice, not slots: the plan gives each section its own range from the footage
and says why (`bashcut.vlog:plan` §3); review compares it with the section marker.

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
- A held plate shot gets a slow push-in rather than sitting still.

## Rhythm, transitions and graphics

| What | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Tone bands | process inserts 0.5–1.5 s; the tasting slower, 2–4 s a bite (T07 §3, §7) | a calm cooking video holds longer everywhere | `bashcut review shots --summary` per section |
| Pattern interrupt | a new step, bite or verdict every 10–30 s (T07 §3) | a 30 s short changes almost every section | `review shots --summary` per section |
| Breath before the bite | one moment of near-silence, 0.5–2 s, before the first bite's sound; once (T07 §3; real sound leads in food, T11 §7) | an ASMR-style edit uses more | `bashcut review window <frame>`; `bashcut audio measure --timeline` |
| Transitions | `vlog-zoom-hit` into the dish at a section start; `vlog-whip-fast` between shops in a multi-shop video; none inside the tasting (T08 §3) | one shop needs almost none | `bashcut review cuts` → counts per kind, runs |
| Transition budget | special transitions 1–3 per minute of short form (T08 §3) | a declared motif (a whip every new dish) may go over; say so | `review cuts` counts ÷ minutes |
| Price tag | lands on the word the price is said (entrance 0.15–0.6 s ending on the word) and stays while it is said and read (T13 §3) | price read from a board needs longer | `bashcut transcript words`; `bashcut review layout` → `holdSeconds` |
| Stickers | at most one keyword sticker per bite (`vlog-pro`, `vlog-con`, `vlog-drool`), 0.5–2 s as an accent (T13 §3) | a review-style food video uses pro/con labels on the claim word | `review layout` → text items per minute |

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

## Review notes

- A viewer notices: food that looks grey or green, a price never shown, a bite whose crunch is buried under music,
  slow motion that stutters (a 30 fps source slowed). Treat these as blockers.
- Deliberate in food: inserts under 0.6 s (short-shot notes stay info), a held plating reveal as the hero hold.
- `needs_user`: the price, shop name and address to confirm, whether the meal was free or sponsored (disclosure), the
  music.
