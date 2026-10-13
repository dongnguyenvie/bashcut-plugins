---
name: tutorial
description: Recipe for a tutorial or tool demo in BashCut — the result first, then the presenter, numbered steps with step cards, zooms onto what is clicked, waiting sped up, limits and next steps; landscape for YouTube with a vertical cut for Shorts, and the review profile that lets screen shots hold longer. Use after bashcut.vlog:plan picked tutorial, or when the footage is a screen recording, an app demo or a how-to. Triggers: "video hướng dẫn", "tutorial", "demo phần mềm", "giới thiệu tool", "cách làm", "từng bước", "how to", "quay màn hình", "hướng dẫn sử dụng".
---

# Tutorial and tool demo

Reply in the user's language. Survey the footage, choose ranges and values from the tables below, write them into the
edit plan and the review profile with `bashcut.vlog:plan`, then edit with `bc:edit-workflow` (its "Screen recording
with a presenter" section has the layout).

## Ranges

Outputs: landscape → `youtube-1080`, plus `shorts` for a vertical cut; vertical-first (a 30–60 s tip) → `shorts`,
`tiktok`, `reels`. The ranges are starting points: a measured reference profile (`bc:style-study`) replaces every
range it measures, and the recipe only fills what it does not measure (T07 §7, T15 §7). Write each chosen range, its
source and its reason in the plan.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Longest shot `maxShotSeconds` | long-form sources put the next visual change at most 15 s apart, others at 30–45 s (T07 §3, a contradiction) | a zoom or a click inside one screen shot is a change even without a cut; vertical tips cut much faster | `bashcut review shots --summary`; `bashcut review picture` (change inside a shot) |
| Long static shot `stillMotion`, `severities.shot-long` | stillMotion just under the change of a screen while the cursor works; `info` when screens hold on purpose | a code editor changes little per second; a design app a lot | `review shots` → `motion.mean` after `bashcut review measure` |
| Frozen screen `maxStillSeconds` | at least the reading time of what is on it: about letters ÷ 15 + 1–1.5 s; key text held ≥5 s (T09 §3, §7) | a dialog to read holds; a loading spinner does not | `review measure`, then `review picture`; `bashcut review layout` → `holdSeconds` |
| Speechless stretch | look again at any lift over 10–20 s with no speech: silence is not empty picture in a screen demo (T06 §3) | a silent demonstration may be the step itself | `bashcut media speech-map --media <id>` → `gaps`; `bashcut narration windows --min-seconds <n>` |
| Shortest shot `minShotSeconds` | long enough to see the click and its result | a vertical tip cuts tighter | `review shots --summary` min |
| Zoom onto the screen | 1.5–2.5× as a start, eased, up to the clip's headroom | a Retina recording in a 1080 project has room to zoom without upscaling; a 1080 recording does not | `bashcut timeline get` → `scale.maxZoomNative`, `pixelRatio`; `bashcut clip motion --focus` |
| Hook `hookSeconds` | 5–7 s landscape (structure below); a vertical tip 1.5–3 s | the result must play with its own sound before the explanation | `bashcut review layout --to F`, `transcript words --to F` |
| Captions `captionLineChars`, `captionMaxLines` | landscape subtitles 6–8 words or 32–42 characters × 2 lines; vertical 15–32 characters (T09 §3, §7) | landscape takes a sidecar caption file, vertical burns them in (T09 §7) | `bashcut review layout` → `longestLineChars` |
| Music under the voice | the deep end of 5–18 dB (T11 §3), or none | dense instruction needs every word | `bashcut audio mix-measure` → `musicUnderSpeech` |

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

- Zoom onto the part of the screen being talked about (keyframed transform zoom at the factor you chose, eased;
  `bc:effects`), back out between steps.
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
  click sounds only if they help. Loudness is each output's own target (`bashcut platforms get`).
- Look: leave the screen recording ungraded; grade only the presenter camera to natural skin (`bc:color-grade`).

For the Shorts output, make a vertical cut of the hook and one step (`bashcut.vlog:publish`).

## Review notes

- A viewer notices: screen text too small to read at phone width, a frozen spinner, a zoom that misses the click,
  the presenter covering the part of the screen in use. Treat these as blockers.
- Deliberate in a tutorial: screen shots held while there is something to read (`shot-long` at `info`), the repeated
  framing of one screen recording.
- `needs_user`: private details on screen to blur or cut (emails, keys, names), the app version shown, the link and
  the next video for the CTA.

## Plan data

What this recipe adds to the plan (`bashcut.vlog:plan` §3); `bc:edit-workflow` and the critic read it.

- `stages`: `{"effects": {"required": true, "why": "zoom onto the panel in use, fast-forward waiting"}, "colour": {"rules": ["leave the screen recording ungraded; grade only the presenter"]}, "visuals": {"skill": "bc:visual-plan", "after": "voiceover", "required": true, "why": "the narration carries it; each step gets the screen, a zoom or a step card"}}`
- `checks` (source: tutorial recipe): `result-first` the hook shows the output; `screen-readable` screen text reads
  at phone width; `zoom-on-click` each zoom lands on the click; `presenter-clear` the presenter never covers the part
  in use; `private-hidden` no email, key or name left on screen; `shortcuts-shown` every shortcut and menu path is
  on screen as text.
- `askAtIntake`: `["privateOnScreen", "ctaLink"]`.
