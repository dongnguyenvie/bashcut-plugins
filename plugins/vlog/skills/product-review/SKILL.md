---
name: product-review
description: Recipe for a product review or unboxing in BashCut — verdict or price question as the hook, what it is, three points with pros and cons, a verdict card with the price, CTA; hero shots, detail inserts, the review profile and disclosure of sponsorship. Use after bashcut.vlog:plan picked product-review, or when the footage is a product, an unboxing or a comparison. Triggers: "review sản phẩm", "đập hộp", "unboxing", "có nên mua", "đáng tiền không", "so sánh", "trên tay", "review điện thoại", "review mỹ phẩm".
---

# Product review

Reply in the user's language. Survey the footage, choose ranges and values from the tables below, write them into the
edit plan and the review profile with `bashcut.vlog:plan`, then edit with `bc:edit-workflow`.

## Ranges

Outputs: vertical → `tiktok`, `reels`, `shorts`; long-form review → `youtube-1080`. The ranges are starting points: a
measured reference profile (`bc:style-study`) replaces every range it measures, and the recipe only fills what it does
not measure (T07 §7, T15 §7). Write each chosen range, its source and its reason in the plan.

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

Sample lengths from earlier vlog practice, not slots: the plan gives each section its own range from the footage
and says why (`bashcut.vlog:plan` §3); review compares it with the section marker.

| Part | Length | What |
|---|---|---|
| Hook | 2–3 s | hero shot + the verdict as a question with the price ("3 TRIỆU CÓ ĐÁNG?") — never "hôm nay mình review…" |
| What it is | 4–6 s | unboxing or the product in hand, name and price (`vlog-price-tag`) |
| Points ×2–4 | 8–12 s each | one claim each, shown not told: the feature in use, then the result; `vlog-section-chip` ("1/3 · PIN"), `vlog-pro` / `vlog-con` |
| Verdict | 3–5 s | `vlog-verdict` (score or "NÊN MUA nếu…"), who it is for |
| CTA | 2–4 s (T14 §3) | where to buy or "comment câu hỏi" |

## Cuts and motion

- Cut rate and inserts from the ranges above.
- Hero shots: slow push-in or orbit (Ken Burns on a still).
- Talking parts follow `bashcut.vlog:talking-head` (punch-ins, captions word by word).
- An ad that sells the product rather than judging it: `bashcut.vlog:product-ad`.

## Rhythm, transitions and graphics

| What | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Pattern interrupt | each point is a new beat; 8–12 s points sit inside the 10–30 s short-form band, long-form 30–90 s (T07 §3) | a long-form review needs inserts inside each point | `bashcut review shots --summary` per section |
| Hook and verdict | the verdict answers the hook's question; the hook promises only what the points pay off (T14 §4) | — | `bashcut review hook` → `opening` and `close` |
| Transitions | hard cuts between talking and inserts; `vlog-zoom-hit` on the reveal; `vlog-soft-cut` between points (T08 §7) | an unboxing montage may whip; say so | `bashcut review cuts` → counts per kind, runs |
| Transition budget | special transitions 1–3 per minute of short form (T08 §3) | long-form landscape reviews use fewer | `review cuts` counts ÷ minutes |
| Section chip | `vlog-section-chip` 2–3 s at the point's start (T13 §7) | longer labels need longer | `bashcut review layout` → `holdSeconds` |
| Pro / con labels | land on the claim word: entrance 0.15–0.6 s ending on the word (T13 §3, §7) | energy | `bashcut transcript words` |
| Spec card | one idea 3–8 s, held through the line it illustrates; a comparison table 8–14 s (T13 §3) | words on the card; narration length | `review layout` → `holdSeconds` |
| Graphic density | 3–8 per minute of talking footage (T13 §3) | dense specs high; a feel-based review low | `review layout` → text items per minute |

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

## Review notes

- A viewer notices: a claim with no picture behind it, a number said but not on screen, the product's colour wrong,
  a sponsored video that does not say so early. Treat these as blockers.
- Deliberate in a review: repeated framing in the talking parts (no `jumpCutChange` there), held spec cards.
- `needs_user`: whether the product was sponsored or gifted and the disclosure wording, the price and where to buy,
  the user's own verdict when they have one.
