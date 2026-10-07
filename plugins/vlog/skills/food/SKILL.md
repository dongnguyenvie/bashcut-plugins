---
name: food
description: Recipe for a food vlog or food review in BashCut, vertical by default — the bite or pour as the hook with the price, place and price card, quick process inserts, tasting with reactions, verdict and address, CTA; pacing, close-up and slow-motion moves, sound and look intent and the review profile. Use after bashcut.vlog:plan picked food, or when the footage is eating, cooking, a restaurant or a street food stall. Triggers: "review món", "review quán", "vlog ăn uống", "food review", "món ngon", "ăn gì", "mukbang", "nấu ăn", "street food".
---

# Food vlog

Reply in the user's language. Apply the profile with `bashcut.vlog:plan` step 2, then edit with `bc:edit-workflow`.

## Profile

```json
{"outputs": ["tiktok", "reels", "shorts"],
 "review": {"minShotSeconds": 0.5, "maxShotSeconds": 4, "maxStillSeconds": 3, "hookSeconds": 2,
            "severities": {"still": "error"}}}
```

## Structure (25–45 s)

| Part | Length | What |
|---|---|---|
| Hook | 1.5–2 s | the best bite, pull or pour in close-up, slow motion, with `vlog-price-tag` or a question ("45K CÓ ĐÁNG?") |
| Place | 3–4 s | sign or front of the shop + `place-card` (name · district), the price tag if not in the hook |
| Process | 4–8 s | 3–5 quick inserts (0.5–1.5 s): cooking, plating, sauce, steam |
| Tasting | 8–15 s | 2–3 bites, each: close-up of the food → the bite → the face; `vlog-pro`/`vlog-con` stickers for what is said |
| Verdict | 3–4 s | score or one-line verdict (`vlog-verdict`), price and address |
| CTA | 2 s | `vlog-cta` ("LƯU LẠI ĐỂ ĂN THỬ") |

## Cuts and motion

- The fastest recipe: 0.5–1.5 s inserts, 2–3 s for bites and reactions.
- Slow motion (0.5×) on pours, cheese pulls, steam and the first bite; punch-in (`zoom-punch-in`) on the reaction.
- `vlog-zoom-hit` into the dish at a section start; no transitions inside the tasting.

## Shots to look for and to shoot

Macro of the dish (top-down and 45°), the pour or pull, steam, the bite from the side, the face right after, the shop
front, the menu or price board, the cook's hands. No close-up of the food is the most common gap: say so before
editing; a punch-in on a wider shot is the fallback.

## Text, sound, look

- Text: price always on screen; one keyword sticker per bite at most.
- Sound: keep the real sizzle, crunch and slurp up front (ASMR moments: music dips under them); short pop/ding on
  price tags (`bc:audio-mix` for finding SFX).
- Look intent: warm, rich colour, appetising; never green-tinted or grey; highlights on sauce kept. Measure first
  (`bc:color-grade`); no fixed numbers.

## Review notes

Very short shots are notes, not problems, in this recipe (minShotSeconds 0.5). A frozen picture over 3 s is an error in this
recipe: a held plate shot needs a slow push-in.
