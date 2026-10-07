---
name: tutorial
description: Recipe for a tutorial or tool demo in BashCut — the result first, then the presenter, numbered steps with step cards, zooms onto what is clicked, waiting sped up, limits and next steps; landscape for YouTube with a vertical cut for Shorts, and the review profile that lets screen shots hold longer. Use after bashcut.vlog:plan picked tutorial, or when the footage is a screen recording, an app demo or a how-to. Triggers: "video hướng dẫn", "tutorial", "demo phần mềm", "giới thiệu tool", "cách làm", "từng bước", "how to", "quay màn hình", "hướng dẫn sử dụng".
---

# Tutorial and tool demo

Reply in the user's language. Apply the profile with `bashcut.vlog:plan` step 2, then edit with `bc:edit-workflow`
(its "Screen recording with a presenter" section has the layout).

## Profile

```json
{"outputs": ["youtube-1080", "shorts"],
 "review": {"minShotSeconds": 1.5, "maxShotSeconds": 15, "maxStillSeconds": 8, "hookSeconds": 5,
            "severities": {"shot-long": "info", "framing": "info"}}}
```

Vertical-first (a 30–60 s tip): `["shorts", "tiktok", "reels"]`, `maxShotSeconds` 8, `maxStillSeconds` 5,
`hookSeconds` 3.

## Structure (1–3 min landscape, 30–60 s vertical)

| Part | Length | What |
|---|---|---|
| Hook | 5–7 s | the **result** (the finished output, with its own sound) + one line on what the viewer will be able to do |
| Intro | 3–5 s | the presenter: who and why, one sentence |
| Steps ×3–6 | 15–40 s each (5–10 s vertical) | `vlog-step` ("BƯỚC 1") or `vlog-section-chip`; show the action, zoom onto it, say why |
| Result | 5–10 s | the output again, now understood |
| Limits | 3–5 s | what it does not do, a `vlog-warning` sticker |
| CTA | 2–3 s | link, next video, "comment nếu bị lỗi" |

## Cuts and motion

- Zoom onto the part of the screen being talked about (keyframed transform zoom 1.5–2.5×, eased; `bc:effects`), back
  out between steps.
- Speed up typing, loading and waiting (4–8×) or cut it; never leave a frozen screen over 8 s.
- Presenter on an overlay layer at the bottom centre (landscape: a corner), captions between screen and face.
- Transitions: hard cuts inside a step, `vlog-soft-cut` between steps.

## Text, sound, look

- Captions from the presenter; every shortcut, menu path and value on screen as text ("⌘K → Export").
- Sound: the presenter's voice; mute the screen recording unless its sound is the result; quiet music bed or none;
  click sounds only if they help.
- Look: leave the screen recording ungraded; grade only the presenter camera to natural skin (`bc:color-grade`).

## Review notes

Screens hold longer than footage: long static shots are notes. A frozen picture over 8 s is still a warning — speed
it up. For the Shorts output, make a vertical cut of the hook and one step (`bashcut.vlog:publish`).
