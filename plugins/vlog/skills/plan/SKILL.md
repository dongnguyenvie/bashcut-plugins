---
name: plan
description: Start a vlog in BashCut from one prompt — pick the topic recipe (travel, food, daily life, product review, talking head, tutorial), set the project's platform outputs and review profile from it, plan the hook, sections and shot list, then hand the edit to bc:edit-workflow with that recipe. Use first whenever the user asks for a vlog or a short video about a trip, a meal, a day, a product, a talk or a how-to, before cutting anything, and when footage is still to be shot or generated. Triggers: "làm vlog", "dựng vlog", "vlog du lịch", "vlog ăn uống", "review món", "review sản phẩm", "a day in my life", "video hướng dẫn", "video nói chuyện", "lên kịch bản vlog", "shot list", "cần quay những gì", "một prompt ra video".
---

# Plan a vlog

Reply in the user's language. This plugin's skills are **recipes**: each topic skill holds what a kind of vlog keeps
(structure, hook, text, sound and look intent) and a **Ranges** table: per check, a sample range from published
practice, why it varies and how to measure it. The numbers are starting points, not settings: you survey the footage,
choose a value inside each range, write the project's `review` profile yourself and say why in the plan. Two folders
of the same genre can and should get different profiles. The editing itself is the agent kit's job
(`bc:edit-workflow` and the skills it names).

## 1. Pick the recipe

| The user's footage or ask | Recipe skill |
|---|---|
| a trip, a city, places, a route, "đi đâu", "ở đâu" | `bashcut.vlog:travel` |
| eating, cooking, a restaurant, a street food stall, "quán", "món" | `bashcut.vlog:food` |
| a day, a routine, "a day in my life", "một ngày của tôi", study/work with me | `bashcut.vlog:daily` |
| a product, an unboxing, a comparison, "có nên mua", "đáng tiền không" | `bashcut.vlog:product-review` |
| one person talking to camera, an opinion, a story time, a podcast clip | `bashcut.vlog:talking-head` |
| a screen recording, an app or tool demo, "cách làm", a step-by-step | `bashcut.vlog:tutorial` |

Read the chosen skill in full (`bashcut skills get bashcut.vlog:<name>`). Two fit (a food stop inside a trip): take the
one the *whole* video is about and borrow single moves from the other. None fits: use the nearest and say so.

## 2. Survey, choose, then set the project up

Ask only what changes the result and cannot be seen in the footage: **where it will be posted** (the platform sets
the frame, length, safe zones and loudness) and **how long**. Defaults: vertical → TikTok, Reels and Shorts;
landscape → YouTube.

1. Canvas: `bashcut project create … --canvas portrait|landscape` for a new project, or `project format --canvas`.
2. **Survey before choosing any number** (`bc:footage-survey`). Read the facts the recipe's "Measure with" column
   names, at least:
   - `bashcut media list --analysis` — shape, `fps` per media, what is measured and transcribed;
   - `bashcut review shots --media <id> --summary` — how long the source shots are and how much they move;
   - `bashcut media speech-map --media <id>` and `bashcut speech rate` — gaps and speaking rate, for speech;
   - `bashcut timeline get` after placing — `scale` per item: `maxZoomNative` (punch-in headroom before upscaling);
   - `bashcut platforms list` — each output's shape, `maxSeconds`, safe zones and loudness target;
   - a reference video the user shared: `review shots --media <ref> --summary` (its rhythm wins over the recipe's
     range, T07 §7).
3. **Choose** a value inside each range of the recipe. Go outside a range only for a measured reason (a reference, a
   platform fact) and say so. Leave a key unset when you have no reason to check it: core has no defaults, and an
   unset key means the check does not run or reports info with no verdict.
4. **Write the reasons into the plan**, one line per key, e.g. "maxShotSeconds 3.5 — 41 short handheld clips, median
   source shot 2.8 s; maxStillSeconds 2.5 — 12 photos with no voice over them".
5. Read the current review object: `bashcut project get` → `review` (may be absent). Keep the user's own keys
   (`disabledChecks`, values the user set, anything you do not recognise); replace only the keys you chose.
6. One undoable edit that records the recipe, the profile and the outputs (first output = primary platform):

```json
[{"op": "setProjectProperties", "patch": {
  "recipe": {"skill": "bashcut.vlog:<recipe>", "outputs": ["<output>", "…"]},
  "output": {"presets": ["<output>", "…"]},
  "review": {"minShotSeconds": <chosen>, "maxShotSeconds": <chosen>, "maxStillSeconds": <chosen>,
             "hookSeconds": <chosen>, "severities": {"<check>": "<chosen>"},
             "disabledChecks": ["…kept from the project…"]}
}}]
```

```sh
bashcut timeline apply recipe.json --base-rev N --label "Vlog recipe: <recipe>"
```

Output presets are `tiktok`, `reels`, `shorts`, `youtube-1080`, `youtube-4k` (`project format --outputs reels,tiktok`
does the same). Review checks the outputs' platform: safe zones, smallest text, longest length, frame shape.

### Review profile keys

| Key | What it checks |
|---|---|
| `minShotSeconds`, `maxShotSeconds` | shots on Main shorter / longer (short ones are always notes) |
| `stillMotion` | with `maxShotSeconds`: a long shot warns only when its mean picture change is under this (0–1, `review shots` motion) |
| `maxStillSeconds` | frozen picture longer than this |
| `hookSeconds` | speech or text inside the opening window (`review hook`) |
| `maxSilenceSeconds`, `maxMusicGapSeconds` | stretches with no audible layer; gaps inside the music bed |
| `voiceoverMarginSeconds`, `minSpeechCoverage` | voiceover too close to real speech; share of the edit with tagged speech or voiceover (0–1) |
| `captionLineChars`, `captionMaxLines`, `minTextSize` | caption line length and lines; smallest text (share of the short side) |
| `jumpCutChange`, `blackMinSeconds` | hard cuts that change less than this (0–1, `review picture`); black runs longer than this |
| `loudnessToleranceLU` | export loudness this far off its output's target |
| `severities` | check ID or prefix (`still`, `shot-long`, `framing`, `jump`) or `provider:` → `error`, `warning`, `info`, `off` |
| `platform` | `{safeArea, maxSeconds}` overrides, only when an app changed its interface (cite the source) |

### Checks every recipe shares

| Check | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Monotony | a run of 6+ shots with length variation (CV) under ~0.15 reads flat (T07 §3) | a calm run on purpose is fine; say so | `bashcut review shots --summary --run-length 6 --max-cv 0.15` |
| Pattern interrupt | a new beat every 10–30 s short-form, 30–90 s long-form (T07 §3) | sources contradict; depends on whether "change" means a cut or a new idea | `review shots --summary` per section |
| Payoff / CTA hold | ≥1 s, up to 4–6 s for a CTA (T07 §3) | platform and CTA | `bashcut review hook` → close |
| Dead air `maxSilenceSeconds` | sources cut dead air over about 1.5 s (T11 §3) | one held silence of about 2 s before a payoff is a choice, used once (T07 §3) | `bashcut audio measure --timeline` → `silences` |
| Music under the voice | 5–18 dB under during speech (T11 §3) | less when music carries the piece; more for dense information, a soft voice, music with vocals | `bashcut audio mix-measure` → `musicUnderSpeech` |
| `loudnessToleranceLU` | 1–2 LU (T11 §3) | tighter when outputs are compared side by side | export receipt, `review run` |
| Length | the platform's `maxSeconds` is a hard limit; "sweet spots" contradict between sources (T17 §3) | the moment sets the length; never trim to a sweet spot | `bashcut platforms list` |

**Loudness is per output, never one number**: each export normalizes to its own preset's target (`platforms list` →
`targets`; T11 §3, T17 §3). Never set `audio.targetLUFS` from a recipe; export each output with `--normalize-audio`.

## 3. Plan before cutting

Write the plan in a few lines and show it to the user before the rough cut:

- **Hook** (first 1–3 s): the line or on-screen text, with a number or a question (`bashcut.vlog:hook-script`).
- **Sections** from the recipe's structure, each with what it shows and says, and a length.
- **Profile**: each chosen value and its reason (step 2.4).
- **Coverage**: after `bc:footage-survey`, list which planned shots exist and which are missing. Say plainly what is
  missing; offer a cutaway from the footage, a stock picture (`bc:stock-images`) or a generated shot.
- **Not shot yet**: give the recipe's shot list as a checklist (what to film, how long, which angle).
- **Generated shots**: when the user wants a scene made with an AI video model instead of filming it, write the prompt
  with `bashcut.vlog:scene-prompt`, and add the recipe's disclosure label to the edit when the clip is placed.

## 4. Edit, review, publish

Run `bc:edit-workflow` from its step 1 with the recipe at hand. Where a kit skill asks for a value (cut rate, caption
grouping, punch-in, music level), choose inside the recipe's range from what you measured, and say why. In the review
loop, the severities you set turn deliberate choices into notes; anything still an **error** must be fixed before
export. If the cut shows a chosen value was wrong (the footage cannot hold it), change the profile with a reason
instead of forcing the edit. Finish with `bashcut.vlog:publish` (caption, hashtags, cover frame, one export per output).

Report at the end: the recipe used, the outputs, the profile with its reasons, what the review fixed and what was left
on purpose.
