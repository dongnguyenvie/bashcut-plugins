---
name: talking-head
description: Recipe for a talking-head video in BashCut (one person to camera — opinion, story time, tips, a podcast clip) — the strongest line first, tight cuts on speech, a punch-in every 4–6 s, word-by-word captions and keyword pops, B-roll on claims; the review profile for one camera (jump cuts measured, fixed with punch-ins). Use after bashcut.vlog:plan picked talking-head, or when the footage is mostly one person speaking. Triggers: "video nói chuyện", "nói trước camera", "talking head", "chia sẻ quan điểm", "story time", "podcast", "tips", "kể chuyện".
---

# Talking head

Reply in the user's language. Survey the footage, choose ranges and values from the tables below, write them into the
edit plan and the review profile with `bashcut.vlog:plan`, then edit with `bc:edit-workflow`.

## Ranges

Outputs: vertical → `shorts`, `tiktok`, `reels`; landscape → `youtube-1080`. The ranges are starting points: a
measured reference profile (`bc:style-study`) replaces every range it measures, and the recipe only fills what it does
not measure (T07 §7, T15 §7). Write each chosen range, its source and its reason in the plan.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Pauses to cut | tighten pauses of 0.3–0.8 s and keep breaths (T06 §7); a kept pause is 0.15–0.5 s, scaled to the speaker's own median gap (T11 §3) | high energy and a fast talker cut to the low end; emotion, a joke's beat or a thoughtful line keep the pause | `bashcut media speech-map --media <id>` → `gaps`, `gapStats`; `bashcut speech rate` |
| Cut padding | in 50–150 ms before the word, out 80–300 ms after (T06 §3); gaps ≥400 ms are clean cut points, 150–400 ms need a look (T06 §3) | tighter for energy, looser for trailing reactions and TTS; never past the next word's start | `bashcut transcript words`, `bashcut review sync` (cut inside a word) |
| Framing change | every 4–6 s (T07 §7) | a dense argument changes more often; a story told slowly less | `bashcut review shots` → `cut.framingBefore/After`, `cut.sameFraming` |
| Punch-in zoom | three families (T08 §3): a slow drift 1.03–1.07× over a shot; a snap punch 1.1–1.15× on one word, about 4–6 in a 60 s reel; a reframe cut 1.15–1.3×; all up to the clip's headroom | a 4K source in a 1080 project has room to 2×; a 1080 webcam has none, so the punch upscales; tight framing (a face filling the frame) leaves less to crop | `bashcut timeline get` → `scale.maxZoomNative`, `pixelRatio`; `bashcut ui frame` to check the crop |
| Longest shot `maxShotSeconds` | the top of your framing-change band (each punch-in is a new shot) | a podcast in landscape holds longer than a vertical tip | `bashcut review shots --summary` |
| Shortest shot `minShotSeconds` | about the shortest clean sentence fragment you keep | a hard punch on one strong word is short on purpose (short shots are only notes) | `review shots --summary` min |
| Jump cut `jumpCutChange` | just above the picture change of the cuts you fixed with a punch-in | a still speaker changes less across a cut than a moving one | `bashcut review picture` → cut `difference` after `bashcut review measure` |
| Hook `hookSeconds` | 1.5–3 s: the strongest complete sentence (T06 §7) | a long sentence needs the top of the band | `bashcut review layout --to F`, `transcript words --to F` |
| Captions `captionLineChars`, `captionMaxLines` | 2–4 words a group, highlight (T09 §7); vertical 15–32 characters, 1–2 lines (T09 §3); break groups on pauses of 0.15–0.6 s (T09 §3) | fast talkers need the low end; landscape subtitles 32–42 characters | `bashcut review layout` → `wordsPerSecond`, `speech.onsetOffsetFrames` |
| Music under the voice | the deep end of 5–18 dB (T11 §3), or none | the voice is everything; music with vocals masks words | `bashcut audio mix-measure` → `musicUnderSpeech` |

## Structure (30–60 s)

Sample lengths from earlier vlog practice, not slots: the plan gives each section its own range from the footage
and says why (`bashcut.vlog:plan` §3); review compares it with the section marker.

| Part | Length | What |
|---|---|---|
| Hook | 1.5–3 s | the strongest sentence of the take, moved to the start (a claim, a number, a question) |
| Points ×2–4 | 8–15 s each | one idea each; a `vlog-keyword` pop on its key word |
| Payoff | 3–6 s | the conclusion or the twist |
| CTA | 1–2 s | one short line, said or on screen |

## Cuts and motion

- Cut ums, false starts and repeats, and the pauses the range above says to tighten (`captions generate` → read the
  lines → cut on sentence boundaries, `bc:beat-cut`). Keep the last complete take (T06 §3).
- Alternate framing: normal → punch-in → normal (`zoom-punch-in` or a transform zoom) at the zoom you chose; a snap
  punch on the strongest words.
- B-roll or a screenshot over any claim that can be shown (`bc:stock-images`), 1.5–3 s, voice continues under it.
- Shorts cut from a long recording: `bashcut.vlog:podcast-clips` picks them; each is then edited with this recipe.

## Rhythm, presence, transitions and graphics

| What | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Pattern interrupt | a B-roll, a graphic, a framing change or a new point every 10–30 s short-form; 30–90 s long-form (T07 §3) | framing changes every 4–6 s are the small resets; this is the bigger one | `bashcut review shots --summary` per section |
| Speaker presence | B-roll and cards cover about 30–50 % of edited reels; one explainer kit keeps the speaker on screen about 40 % (T13 §3); 25–60 % across tutorials and explainers (T19 §3). Audit it, do not cap it | an opinion or a story keeps the face (the face carries the emotion); tips with things to show cover more | `bashcut timeline get` → time covered by B-roll and full-screen cards ÷ length |
| Transitions | hard cuts and punch-ins; 0–1 special transitions per video (T08 §7); `vlog-blink` only to hide a cut that still jumps | — | `bashcut review shots` → count `cut.kind` |
| Keyword pops | `vlog-keyword` on the key word: entrance 0.15–0.6 s ending on the word, 0.5–2 s as an accent (T13 §3) | the word's weight | `bashcut transcript words`; `bashcut review layout` |
| Graphic density | 3–8 graphics per minute of talking footage; leave some sentences bare so the next one lands (T13 §3, §4) | dense information high; a personal story low | `review layout` → text items per minute |
| Caption landing | captions start within 0.1–0.3 s of the word (T16 §3) | — | `bashcut review layout` → `speech.onsetOffsetFrames` |

## Text, sound, look

- Captions word by word (highlight), bold-outline, mid-low in the frame; keywords in `vlog-keyword`.
- Sound: the voice is everything — clean and even; music very low or none; a subtle whoosh on punch-ins. Loudness is
  each output's own target (`bashcut platforms get`).
- Look intent: natural skin, eyes bright, background a little darker than the face. Measure first (`bc:color-grade`).

## Review notes

- One camera repeats its framing by nature: `framing` at `info`. Jump cuts still warn and are fixed with punch-ins.
- A viewer notices: a cut inside a word, captions that come late, a pause cut so tight the breath is gone, music with
  vocals under speech. Treat these as blockers; a slightly long pause is not.
- `needs_user`: the speaker's name and title for a label, which take to keep when two are equally clean, sources for
  claims made on camera, music or none.
