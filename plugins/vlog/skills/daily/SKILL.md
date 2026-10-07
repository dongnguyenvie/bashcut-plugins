---
name: daily
description: Recipe for a daily-life vlog in BashCut ("a day in my life", routines, study or work with me) — time-stamped moments in order, a calm pace with room to breathe, voiceover or captions as a diary, a soft look; the review profile that lets slower shots pass. Use after bashcut.vlog:plan picked daily, or when the footage is one day or routine of one person. Triggers: "a day in my life", "một ngày của tôi", "vlog đời thường", "daily vlog", "routine", "morning routine", "study with me", "work with me", "cuối tuần của tôi".
---

# Daily vlog

Reply in the user's language. Apply the profile with `bashcut.vlog:plan` step 2, then edit with `bc:edit-workflow`.

## Profile

```json
{"outputs": ["tiktok", "reels", "shorts"],
 "review": {"minShotSeconds": 1, "maxShotSeconds": 6, "maxStillSeconds": 4, "hookSeconds": 3,
            "severities": {"shot-long": "info"}}}
```

Long-form (YouTube, 4–10 min): `["youtube-1080"]`, `maxShotSeconds` 10, `maxStillSeconds` 6.

## Structure (30–90 s vertical)

| Part | Length | What |
|---|---|---|
| Hook | 2–3 s | the most interesting moment of the day, or a question/number ("5H SÁNG THỨC DẬY ĐỂ LÀM GÌ?") |
| Moments ×5–10 | 4–10 s each | in time order; `vlog-time-stamp` ("07:30 · SÁNG") at each new part of the day |
| Close | 3–5 s | the end of the day, a thought in one line |
| CTA | 2 s | soft: "theo dõi để xem ngày mai" |

## Cuts and motion

- 8–12 cuts a minute; let a shot breathe 3–6 s when something happens in it (pouring coffee, a view).
- Short sequences of 3–4 quick shots (1 s) for repeated actions (getting ready, cooking), then a longer shot.
- Transitions: hard cuts and `vlog-soft-cut` between parts of the day; `vlog-blink` for a time jump.
- Speed ramp or 2–4× for commutes and long tasks.

## Shots

Wake-up, window light, hands doing things, the person in the room, outside, food, the work or study desk, a time
cue (clock, phone, sky). Missing time cues: put the time stamps on screen.

## Text, sound, look

- A diary voice: short sentences, first person, present tense; captions small and low, 3–6 words.
- Sound: one calm music bed for the whole video, ducked under speech; keep room tone and small sounds (cup, door).
- Look intent: soft and bright, gentle contrast, a little warmth; consistent between indoor and outdoor. Measure first
  (`bc:color-grade`).

## Review notes

Slow shots are part of the style: long static-shot warnings are notes here. A frozen picture stays a warning and
black frames an error.
