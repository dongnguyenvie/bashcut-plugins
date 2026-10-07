---
name: product-review
description: Recipe for a product review or unboxing in BashCut — verdict or price question as the hook, what it is, three points with pros and cons, a verdict card with the price, CTA; hero shots, detail inserts, the review profile and disclosure of sponsorship. Use after bashcut.vlog:plan picked product-review, or when the footage is a product, an unboxing or a comparison. Triggers: "review sản phẩm", "đập hộp", "unboxing", "có nên mua", "đáng tiền không", "so sánh", "trên tay", "review điện thoại", "review mỹ phẩm".
---

# Product review

Reply in the user's language. Survey the footage, choose values from the ranges below and write the review profile
with `bashcut.vlog:plan` step 2, then edit with `bc:edit-workflow`.

## Ranges

Outputs: vertical → `tiktok`, `reels`, `shorts`; long-form review → `youtube-1080`. The ranges are starting points; a
measured reference wins (T07 §7). Write each chosen value and its reason in the plan.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Cut rate | about 10–14 cuts a minute (T07 §3) | dense spec talk holds longer, within the 2.5–6 s vlog band (T07 §3); a quick unboxing cuts faster | `bashcut review shots --summary` (mean, cutsPerMinute per section) |
| Detail insert | 1–1.5 s between talking shots, so a claim always has a picture | a spec on screen to read holds longer | `review shots --summary` per section |
| Longest shot `maxShotSeconds` | the top of the talking-shot length; one hero hold (the reveal) at 1.5–2.5× the average (T07 §3) | a long-form review with landscape talking parts holds much longer than a vertical one | `review shots --summary` max; `review shots --media <id> --summary` |
| Shortest shot `minShotSeconds` | the bottom of the insert band | a fast unboxing montage can go shorter on purpose (short shots are only notes) | `review shots --summary` min |
| Long static shot `stillMotion` | just under the motion of the hero shots you keep | a tripod hero shot on a turntable moves; a product photo does not | `review shots` → `motion.mean` after `bashcut review measure` |
| Product photo or held hero `maxStillSeconds`, `severities.still` | 1.5–4 s, longer while a line is said over it (T07 §3); `warning` | a spec card to read holds longer | `review measure`, then `bashcut review picture` |
| Hook `hookSeconds` | 2–3 s vertical (structure below); long-form up to the 3–5 s hook cadence (T07 §3) | the price question must land inside it | `bashcut review hook` |
| Talking parts | as `bashcut.vlog:talking-head` (pauses, punch-in headroom, framing) | — | see that recipe |
| Captions and numbers `captionLineChars`, `minTextSize` | vertical 15–32 characters, 1–2 lines (T09 §3); numbers on screen held for reading time (T09 §3) | long specs need more lines or a card instead of a caption | `bashcut review layout` → `longestLineChars`, `holdSeconds`, `fontShare` |
| Music under the voice | 5–18 dB under (T11 §3), light | the product's own sound (a click, a motor) leads when it is the point | `bashcut audio mix-measure` → `musicUnderSpeech` |

## Structure (45–90 s vertical)

| Part | Length | What |
|---|---|---|
| Hook | 2–3 s | hero shot + the verdict as a question with the price ("3 TRIỆU CÓ ĐÁNG?") — never "hôm nay mình review…" |
| What it is | 4–6 s | unboxing or the product in hand, name and price (`vlog-price-tag`) |
| Points ×3 | 8–12 s each | one claim each, shown not told: the feature in use, then the result; `vlog-section-chip` ("1/3 · PIN"), `vlog-pro` / `vlog-con` |
| Verdict | 3–5 s | `vlog-verdict` (score or "NÊN MUA nếu…"), who it is for |
| CTA | 2 s | where to buy or "comment câu hỏi" |

## Cuts and motion

- Cut rate and inserts from the ranges above.
- Hero shots: slow push-in or orbit (Ken Burns on a still), `vlog-zoom-hit` on a reveal.
- Talking parts follow `bashcut.vlog:talking-head` (punch-ins, captions word by word).

## Shots

Hero (product alone, clean background), unboxing hands, every claimed feature in use, the result (a photo it took, the
battery %, the skin after), the person using it, a size comparison. A claim without its shot: cut the claim or show
the spec as text.

## Text, sound, look

- Every number on screen (price, battery hours, weight). Pros green, cons red (`vlog-pro`, `vlog-con`).
- Sponsored or gifted: say so in the first seconds and add `vlog-disclosure` ("Hợp tác cùng …") — ask the user.
- Sound: light music under the voice; click/pop on stickers; real sound of the product when it has one. Loudness is
  each output's own target (`bashcut platforms list`).
- Look intent: true-to-life colour (the product's real colour matters more than mood), clean whites. Measure first
  (`bc:color-grade`); grade the product shots to match each other.
