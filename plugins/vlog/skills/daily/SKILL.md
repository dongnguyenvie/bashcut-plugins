---
name: daily
description: Recipe for a daily-life vlog in BashCut ("a day in my life", routines, study or work with me) — time-stamped moments in order, a calm pace with room to breathe, voiceover or captions as a diary, a soft look; the review profile that lets slower shots pass. Use after bashcut.vlog:plan picked daily, or when the footage is one day or routine of one person. Triggers: "a day in my life", "một ngày của tôi", "vlog đời thường", "daily vlog", "routine", "morning routine", "study with me", "work with me", "cuối tuần của tôi".
---

# Daily vlog

Reply in the user's language. Survey the footage, choose values from the ranges below and write the review profile
with `bashcut.vlog:plan` step 2, then edit with `bc:edit-workflow`.

## Ranges

Outputs: vertical → `tiktok`, `reels`, `shorts`; long-form (YouTube, 4–10 min) → `youtube-1080`. The ranges are
starting points; a measured reference wins (T07 §7). Write each chosen value and its reason in the plan.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Hold when something happens | 3–6 s (T07 §7); calm tone 2–4 s (T07 §3); about 8–12 cuts a minute (T07 §3) | pouring coffee or a view holds; landscape long-form and a calm voice hold longer, within the 2.5–6 s vlog band (T07 §3) | `bashcut review shots --summary` (mean, median, cutsPerMinute per section) |
| Longest shot `maxShotSeconds` | the top of your hold band; one hero hold at 1.5–2.5× the average (T07 §3) | a study-with-me or long-form edit holds much longer than a 45 s short | `review shots --summary` max; `review shots --media <id> --summary` for the source takes |
| Long static shot `stillMotion`, `severities.shot-long` | stillMotion just under the motion of the calm shots you keep; `info` when slow shots are the style | slow shots are part of this genre; a tripod desk shot may barely move | `review shots` → `motion.mean` after `bashcut review measure` |
| Quick sequence | about 1 s a shot for 3–4 repeated actions (getting ready, cooking), then a longer shot | how many repeated actions were filmed | `review shots --summary` per section |
| Shortest shot `minShotSeconds` | the bottom of the quick sequence, about 1 s | a beat-cut sequence can go shorter on purpose (short shots are only notes) | `review shots --summary` min |
| Frozen picture `maxStillSeconds`, `severities.still` | 1.5–4 s, longer while a line is said over it (T07 §3); `warning` | a window-light photo under the diary voice holds longer; a frozen screen with nothing said does not | `review measure`, then `bashcut review picture` |
| Hook `hookSeconds` | 2–3 s (structure below) | a quiet opening needs the time-stamp text or a question early | `bashcut review hook` |
| Captions `captionLineChars`, `captionMaxLines` | 3–6 words, small and low (T09 §7); vertical 15–32 characters, 1–2 lines; landscape 32–42 (T09 §3) | speech rate and frame shape | `bashcut review layout`, `bashcut speech rate` |
| Pauses in the diary voice | keep 0.15–0.5 s breaths, scaled to the speaker's own median gap (T11 §3) | a slow, thoughtful voice keeps longer pauses than a fast one | `bashcut media speech-map --media <id>` → `gapStats` |
| Music under the voice | 5–18 dB under (T11 §3), one calm bed | music carries the wordless parts; dense diary talk needs more room | `bashcut audio mix-measure` → `musicUnderSpeech`, `musicInGaps` |

## Structure (30–90 s vertical)

| Part | Length | What |
|---|---|---|
| Hook | 2–3 s | the most interesting moment of the day, or a question/number ("5H SÁNG THỨC DẬY ĐỂ LÀM GÌ?") |
| Moments ×5–10 | 4–10 s each | in time order; `vlog-time-stamp` ("07:30 · SÁNG") at each new part of the day |
| Close | 3–5 s | the end of the day, a thought in one line |
| CTA | 2 s | soft: "theo dõi để xem ngày mai" |

## Cuts and motion

- Pace from the ranges above: let a shot breathe when something happens in it.
- Short sequences of quick shots for repeated actions, then a longer shot.
- Transitions: hard cuts and `vlog-soft-cut` between parts of the day; `vlog-blink` for a time jump.
- Speed ramp or 2–4× for commutes and long tasks.

## Shots

Wake-up, window light, hands doing things, the person in the room, outside, food, the work or study desk, a time
cue (clock, phone, sky). Missing time cues: put the time stamps on screen.

## Text, sound, look

- A diary voice: short sentences, first person, present tense; captions small and low.
- Sound: one calm music bed for the whole video, ducked under speech; keep room tone and small sounds (cup, door).
  Loudness is each output's own target (`bashcut platforms list`).
- Look intent: soft and bright, gentle contrast, a little warmth; consistent between indoor and outdoor. Measure first
  (`bc:color-grade`).
