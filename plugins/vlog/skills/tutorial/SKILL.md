---
name: tutorial
description: Recipe for a tutorial or tool demo: the result first, numbered steps with step cards, zooms onto what is clicked, waiting sped up, limits and next steps; landscape plus a vertical cut. Use after bashcut.vlog:plan picks tutorial. Triggers: "video hướng dẫn", "tutorial", "demo phần mềm", "cách làm", "từng bước", "quay màn hình".
---

# Tutorial and tool demo

Reply in the user's language. Survey the footage, choose ranges and values from the tables below, write them into the
edit plan and the review profile with `bashcut.vlog:plan`, then edit with `bc:edit-workflow` (its "Screen recording
with a presenter" section has the layout).

## Ranges

Outputs: landscape → `youtube-1080`, plus `shorts` for a vertical cut; vertical-first (a 30–60 s tip) → `shorts`,
`tiktok`, `reels`. Ranges follow `bashcut.vlog:plan` (a measured reference replaces them).

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Longest shot `maxShotSeconds` | long-form sources put the next visual change at most 15 s apart, others at 30–45 s (T07 §3, a contradiction) | a zoom or a click inside one screen shot is a change even without a cut; vertical tips cut much faster | `bashcut review shots --summary`; `bashcut review picture` (change inside a shot) |
| Long static shot `stillMotion`, `severities.shot-long` | stillMotion just under the change of a screen while the cursor works; `info` when screens hold on purpose | a code editor changes little per second; a design app a lot | `review shots` → `motion.mean` after `bashcut review measure` |
| Frozen screen `maxStillSeconds` | at least the reading time of what is on it: about letters ÷ 15 + 1–1.5 s; key text held ≥5 s (T09 §3, §7) | a dialog to read holds; a loading spinner does not | `review measure`, then `review picture`; `bashcut review layout` → `holdSeconds` |
| Speechless stretch | look again at any lift over 10–20 s with no speech: silence is not empty picture in a screen demo (T06 §3) | a silent demonstration may be the step itself | `bashcut media speech-map --media <id>` → `gaps`; `bashcut narration windows --min-seconds <n>` |
| Shortest shot `minShotSeconds` | long enough to see the click and its result | a vertical tip cuts tighter | `review shots --summary` min |
| Zoom onto the screen | 1.5–2.5× as a start, eased, up to the clip's headroom; one framing per narration line, aimed at the panel it names | a Retina recording in a 1080 project has room to zoom without upscaling; a 1080 recording does not; a small panel needs more | `bashcut timeline get` → `scale.maxZoomNative`, `pixelRatio`; `bashcut clip motion --focus`; `bashcut ui frame <frame> --phone` per line |
| Live speech beside the voiceover | each camera clip within about 2 LU of the voiceover | camera mics differ by 15–20 dB; one presenter sat at −31 LUFS against a −17.5 LUFS voiceover | `bashcut audio mix-measure` → `speechWindows` |
| Hook `hookSeconds` | 5–7 s landscape (structure below); a vertical tip 1.5–3 s | the result must play with its own sound before the explanation | `bashcut review layout --to F`, `transcript words --to F` |
| Captions `captionLineChars`, `captionMaxLines` | landscape subtitles 6–8 words or 32–42 characters × 2 lines; vertical 15–32 characters (T09 §3, §7) | landscape takes a sidecar caption file, vertical burns them in (T09 §7) | `bashcut review layout` → `longestLineChars` |
| Music under the voice | 15–20 dB under the quieter voice (the deep end of T11 §3's 5–18), or none | dense instruction needs every word; a bed set for the voiceover sat only 0–4 LU under the presenter | `bashcut audio mix-measure` → `musicUnderSpeech` per window |

## Structure (1–3 min landscape, 30–60 s vertical)

Sample lengths from earlier vlog practice, not slots: the plan gives each section its own range from the footage
and says why (`bashcut.vlog:plan` §3); review compares it with the section marker.

| Part | Length | What |
|---|---|---|
| Hook | 5–7 s | the **result** (the finished output, with its own sound) + one line on what the viewer will be able to do |
| Intro | 3–5 s | the presenter: who and why, one sentence |
| Steps ×3–6 | 15–40 s each (5–10 s vertical) | `vlog-step` ("BƯỚC 1") or `vlog-section-chip`; show the action, zoom onto it, say why |
| Result | 5–10 s | the output again, now understood |
| Limits | 3–5 s | what it does not do, a `vlog-warning` sticker |
| CTA | 2–3 s | link, next video, "comment nếu bị lỗi" |

## Cuts and motion

- Zoom onto the part of the screen each line talks about: one framing per narration line, aimed at the panel the
  line names, a new one where the screen changes (a contact sheet of the recording and its scene cuts), checked with
  `ui frame --phone` at the line's key word (`bc:effects` §5). Build with `clip motion --focus`, or plan.cut
  `focus` / `focusKeys` once BashCut ships them (branch `feat/focus-visible-band`). Never one framing reused across
  the screen shots: one edit kept pan 0, tilt −480, zoom 1.9 on every screen and missed each line's panel. Back out
  between steps.
- Speed up typing, loading and waiting at the speed below, or cut it; a frozen screen holds only as long as there is
  something to read.
- Presenter on an overlay layer at the bottom centre (landscape: a corner), captions between screen and face, never
  over the part of the screen being clicked.

## Presence, rhythm, transitions and graphics

| What | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Presenter presence | 25–60 % of the runtime in tutorials and explainers (T19 §3; one kit about 40 %, T13 §3). Audit it, do not cap it | a dense screen needs the room; the intro, the result and the limits are the presenter's | `bashcut timeline get` → time the presenter layer is visible ÷ length |
| Presenter size (picture in picture) | 0.25–0.6 of the frame width (T19 §3, a contradiction between sources) | smaller when the screen text is dense; larger when the face carries the story | `bashcut ui frame <frame> --phone` |
| Demo speed | 1.5–2× when narrated over; 4–20× for silent waiting (T19 §3) | how much of the action must still read | `bashcut timeline get` → item speed |
| Pattern interrupt | a zoom, a new step or a result every 10–30 s in a vertical tip; long-form sources say at most 15 s against 30–45 s (T07 §3, a contradiction) | a zoom inside one screen counts as a change | `bashcut review shots --summary`; `bashcut review picture` |
| Transitions | hard cuts inside a step; `vlog-soft-cut` between steps; 0–1 special transitions per minute (T08 §3) | — | `bashcut review shots` → count `cut.kind` |
| Step card | `vlog-step` 2–4 s at the step start (T13 §7); key text on screen held 5 s or more (T09 §3) | the label's length | `bashcut review layout` → `holdSeconds` |
| Shortcut, menu path, value | on screen while said, held for reading: about letters ÷ 15 + 1–1.5 s (T09 §3) | how long the path is | `review layout` → `holdSeconds` |
| Graphic density | high for a tutorial: 3–8 per minute (T13 §3, §7) | a quick tip has fewer | `review layout` → text items per minute |

## Text, sound, look

- Captions from the presenter; every shortcut, menu path and value on screen as text ("⌘K → Export").
- Sound: the presenter's voice; mute the screen recording unless its sound is the result; quiet music bed or none;
  click sounds only if they help. With a voiceover beside the presenter, level each camera clip to the voiceover
  (about 2 LU) after reading its source peak, set the bed 15–20 LU under the quieter voice, and re-check true peak
  (`bc:audio-mix`, "Real speech vs voiceover").
- Words: cut restarts the transcript hides (a word over about 1 s or under about 0.4 confidence: re-transcribe that
  window, `bc:footage-survey`); a voiceover line never repeats the presenter's next or previous line
  (`bc:voiceover`).
- Look: leave the screen recording ungraded; grade only the presenter camera to natural skin (`bc:color-grade`).

For the Shorts output, make a vertical cut of the hook and one step (`bashcut.vlog:publish`).

## Review notes

- A viewer notices: screen text too small to read at phone width, a frozen spinner, a zoom that misses the click
  or the panel the line names, the presenter covering the part of the screen in use, a presenter much quieter than
  the voiceover, the same intro said twice. Treat these as blockers.
- Review does not pass while `effects` or `sound` is still `pending` (`run checklist`; BashCut answers
  `stage_pending`): do the stage or log it skipped with the reason.
- Deliberate in a tutorial: screen shots held while there is something to read (`shot-long` at `info`), the repeated
  framing of one screen recording.
- `needs_user`: private details on screen to blur or cut (emails, keys, names), the app version shown, the link and
  the next video for the CTA.

## Plan data

What this recipe adds to the plan (`bashcut.vlog:plan` §3); `bc:edit-workflow` and the critic read it.

- `stages`: `{"effects": {"required": true, "why": "one zoom per narration line onto the panel it names, fast-forward waiting"}, "sound": {"required": true, "why": "camera speech levelled to the voiceover, music 15-20 LU under both"}, "colour": {"rules": ["leave the screen recording ungraded; grade only the presenter"]}, "visuals": {"skill": "bc:visual-plan", "after": "voiceover", "required": true, "why": "the narration carries it; each step gets the screen, a zoom or a step card"}}`
- `checks` (source: tutorial recipe): `result-first` the hook shows the output; `screen-readable` screen text reads
  at phone width; `zoom-on-click` each narration line's zoom lands on the panel or click it names, one framing per
  line, checked with `ui frame`; `presenter-clear` the presenter never covers the part in use; `private-hidden` no
  email, key or name left on screen; `shortcuts-shown` every shortcut and menu path is on screen as text;
  `voice-match` every live-speech window within about 2 LU of the voiceover, music 15–20 LU under, no true peak over
  the ceiling (`audio mix-measure`); `no-restart` no restart or phrase said twice, and no voiceover line repeating
  the live line beside it.
- `askAtIntake`: `["privateOnScreen", "ctaLink"]`.
