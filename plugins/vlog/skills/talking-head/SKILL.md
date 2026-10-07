---
name: talking-head
description: Recipe for a talking-head video in BashCut (one person to camera — opinion, story time, tips, a podcast clip) — the strongest line first, tight cuts on speech, a punch-in every 4–6 s, word-by-word captions and keyword pops, B-roll on claims; the review profile that accepts the repeated framing of one camera. Use after bashcut.vlog:plan picked talking-head, or when the footage is mostly one person speaking. Triggers: "video nói chuyện", "nói trước camera", "talking head", "chia sẻ quan điểm", "story time", "podcast", "cắt podcast", "tips", "kể chuyện".
---

# Talking head

Reply in the user's language. Survey the footage, choose values from the ranges below and write the review profile
with `bashcut.vlog:plan` step 2, then edit with `bc:edit-workflow`.

## Ranges

Outputs: vertical → `shorts`, `tiktok`, `reels`; landscape podcast → `youtube-1080`. The ranges are starting points;
a measured reference wins (T07 §7). Write each chosen value and its reason in the plan.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Pauses to cut | tighten pauses of 0.3–0.8 s and keep breaths (T06 §7); a kept pause is 0.15–0.5 s, scaled to the speaker's own median gap (T11 §3) | high energy and a fast talker cut to the low end; emotion, a joke's beat or a thoughtful line keep the pause | `bashcut media speech-map --media <id>` → `gaps`, `gapStats`; `bashcut speech rate` |
| Cut padding | in 50–150 ms before the word, out 80–300 ms after (T06 §3); gaps ≥400 ms are clean cut points, 150–400 ms need a look (T06 §3) | tighter for energy, looser for trailing reactions and TTS; never past the next word's start | `bashcut transcript words`, `bashcut review sync` (cut inside a word) |
| Framing change | every 4–6 s (T07 §7) | a dense argument changes more often; a story told slowly less | `bashcut review cuts` → `framingBefore/After`, `sameFraming` |
| Punch-in zoom | 1.2–1.3× as a start, up to the clip's headroom | a 4K source in a 1080 project has room to 2×; a 1080 webcam has none, so the punch upscales; tight framing (a face filling the frame) leaves less to crop | `bashcut timeline get` → `scale.maxZoomNative`, `pixelRatio`; `bashcut ui frame` to check the crop |
| Longest shot `maxShotSeconds` | the top of your framing-change band (each punch-in is a new shot) | a podcast in landscape holds longer than a vertical tip | `bashcut review shots --summary` |
| Shortest shot `minShotSeconds` | about the shortest clean sentence fragment you keep | a hard punch on one strong word is short on purpose (short shots are only notes) | `review shots --summary` min |
| Repeated framing `severities.framing` | `info` | one camera repeats its framing by nature; jump cuts still warn and are fixed with punch-ins | `review cuts` |
| Jump cut `jumpCutChange` | just above the picture change of the cuts you fixed with a punch-in | a still speaker changes less across a cut than a moving one | `bashcut review picture` → cut `difference` after `bashcut review measure` |
| Hook `hookSeconds` | 1.5–3 s: the strongest complete sentence (T06 §7) | a long sentence needs the top of the band | `bashcut review hook` |
| Captions `captionLineChars`, `captionMaxLines` | 2–4 words a group, highlight (T09 §7); vertical 15–32 characters, 1–2 lines (T09 §3); break groups on pauses of 0.15–0.6 s (T09 §3) | fast talkers need the low end; landscape subtitles 32–42 characters | `bashcut review layout` → `wordsPerSecond`, `speech.onsetOffsetFrames` |
| Music under the voice | the deep end of 5–18 dB (T11 §3), or none | the voice is everything; music with vocals masks words | `bashcut audio mix-measure` → `musicUnderSpeech` |

## Structure (30–60 s)

| Part | Length | What |
|---|---|---|
| Hook | 1.5–3 s | the strongest sentence of the take, moved to the start (a claim, a number, a question) |
| Points ×2–4 | 8–15 s each | one idea each; a `vlog-keyword` pop on its key word |
| Payoff | 3–6 s | the conclusion or the twist |
| CTA | 1–2 s | one short line, said or on screen |

## Cuts and motion

- Cut ums, false starts and repeats, and the pauses the range above says to tighten (`captions generate` → read the
  lines → cut on sentence boundaries, `bc:beat-cut`). Keep the last complete take (T06 §3).
- Alternate framing: normal → punch-in → normal (`zoom-punch-in` or a transform zoom) at the zoom you chose; a hard
  punch on the strongest words.
- B-roll or a screenshot over any claim that can be shown (`bc:stock-images`), 1.5–3 s, voice continues under it.
- `vlog-blink` only to hide a cut that still jumps.

## Text, sound, look

- Captions word by word (highlight), bold-outline, mid-low in the frame; keywords in `vlog-keyword`.
- Sound: the voice is everything — clean and even; music very low or none; a subtle whoosh on punch-ins. Loudness is
  each output's own target (`bashcut platforms list`).
- Look intent: natural skin, eyes bright, background a little darker than the face. Measure first (`bc:color-grade`).
