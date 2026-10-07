---
name: product-review
description: Recipe for a product review or unboxing in BashCut — verdict or price question as the hook, what it is, three points with pros and cons, a verdict card with the price, CTA; hero shots, detail inserts, the review profile and disclosure of sponsorship. Use after bashcut.vlog:plan picked product-review, or when the footage is a product, an unboxing or a comparison. Triggers: "review sản phẩm", "đập hộp", "unboxing", "có nên mua", "đáng tiền không", "so sánh", "trên tay", "review điện thoại", "review mỹ phẩm".
---

# Product review

Reply in the user's language. Apply the profile with `bashcut.vlog:plan` step 2, then edit with `bc:edit-workflow`.

## Profile

```json
{"outputs": ["tiktok", "reels", "shorts"],
 "review": {"minShotSeconds": 0.8, "maxShotSeconds": 6, "maxStillSeconds": 4, "hookSeconds": 3}}
```

Long-form review on YouTube: `["youtube-1080"]`, `maxShotSeconds` 10, `maxStillSeconds` 6, `hookSeconds` 5.

## Structure (45–90 s vertical)

| Part | Length | What |
|---|---|---|
| Hook | 2–3 s | hero shot + the verdict as a question with the price ("3 TRIỆU CÓ ĐÁNG?") — never "hôm nay mình review…" |
| What it is | 4–6 s | unboxing or the product in hand, name and price (`vlog-price-tag`) |
| Points ×3 | 8–12 s each | one claim each, shown not told: the feature in use, then the result; `vlog-section-chip` ("1/3 · PIN"), `vlog-pro` / `vlog-con` |
| Verdict | 3–5 s | `vlog-verdict` (score or "NÊN MUA nếu…"), who it is for |
| CTA | 2 s | where to buy or "comment câu hỏi" |

## Cuts and motion

- 10–14 cuts a minute; detail inserts (1–1.5 s) between talking shots so a claim always has a picture.
- Hero shots: slow push-in or orbit (Ken Burns on a still), `vlog-zoom-hit` on a reveal.
- Talking parts follow `bashcut.vlog:talking-head` (punch-ins, captions word by word).

## Shots

Hero (product alone, clean background), unboxing hands, every claimed feature in use, the result (a photo it took, the
battery %, the skin after), the person using it, a size comparison. A claim without its shot: cut the claim or show
the spec as text.

## Text, sound, look

- Every number on screen (price, battery hours, weight). Pros green, cons red (`vlog-pro`, `vlog-con`).
- Sponsored or gifted: say so in the first seconds and add `vlog-disclosure` ("Hợp tác cùng …") — ask the user.
- Sound: light music under the voice; click/pop on stickers; real sound of the product when it has one.
- Look intent: true-to-life colour (the product's real colour matters more than mood), clean whites. Measure first
  (`bc:color-grade`); grade the product shots to match each other.
