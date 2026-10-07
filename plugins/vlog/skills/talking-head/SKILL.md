---
name: talking-head
description: Recipe for a talking-head video in BashCut (one person to camera — opinion, story time, tips, a podcast clip) — the strongest line first, tight cuts on speech, a punch-in every 4–6 s, word-by-word captions and keyword pops, B-roll on claims; the review profile that accepts the repeated framing of one camera. Use after bashcut.vlog:plan picked talking-head, or when the footage is mostly one person speaking. Triggers: "video nói chuyện", "nói trước camera", "talking head", "chia sẻ quan điểm", "story time", "podcast", "cắt podcast", "tips", "kể chuyện".
---

# Talking head

Reply in the user's language. Apply the profile with `bashcut.vlog:plan` step 2, then edit with `bc:edit-workflow`.

## Profile

```json
{"outputs": ["shorts", "tiktok", "reels"],
 "review": {"minShotSeconds": 1, "maxShotSeconds": 6, "maxStillSeconds": 6, "hookSeconds": 2,
            "severities": {"framing": "info"}}}
```

One camera means the same framing again and again: "Repeated framing" is a note here; jump cuts still warn and are
fixed with punch-ins. Landscape podcast: `["youtube-1080"]`, `maxShotSeconds` 10.

## Structure (30–60 s)

| Part | Length | What |
|---|---|---|
| Hook | 1.5–3 s | the strongest sentence of the take, moved to the start (a claim, a number, a question) |
| Points ×2–4 | 8–15 s each | one idea each; a `vlog-keyword` pop on its key word |
| Payoff | 3–6 s | the conclusion or the twist |
| CTA | 1–2 s | one short line, said or on screen |

## Cuts and motion

- Cut every pause over 0.3 s, ums, false starts and repeats (`captions generate` → read the lines → cut on sentence
  boundaries, `bc:beat-cut`).
- Alternate framing every 4–6 s: normal → punch-in 1.2–1.3× (`zoom-punch-in` or a transform zoom) → normal; a hard
  punch on the strongest words.
- B-roll or a screenshot over any claim that can be shown (`bc:stock-images`), 1.5–3 s, voice continues under it.
- `vlog-blink` only to hide a cut that still jumps.

## Text, sound, look

- Captions word by word (highlight), bold-outline, 2–4 words, mid-low in the frame; keywords in `vlog-keyword`.
- Sound: the voice is everything — clean and even; music very low or none; a subtle whoosh on punch-ins.
- Look intent: natural skin, eyes bright, background a little darker than the face. Measure first (`bc:color-grade`).
