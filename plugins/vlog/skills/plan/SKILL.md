---
name: plan
description: Start a vlog in BashCut from one prompt — pick the topic recipe (travel, food, daily life, product review, talking head, tutorial), set the project's platform outputs and review profile from it, plan the hook, sections and shot list, then hand the edit to bc:edit-workflow with that recipe. Use first whenever the user asks for a vlog or a short video about a trip, a meal, a day, a product, a talk or a how-to, before cutting anything, and when footage is still to be shot or generated. Triggers: "làm vlog", "dựng vlog", "vlog du lịch", "vlog ăn uống", "review món", "review sản phẩm", "a day in my life", "video hướng dẫn", "video nói chuyện", "lên kịch bản vlog", "shot list", "cần quay những gì", "một prompt ra video".
---

# Plan a vlog

Reply in the user's language. This plugin's skills are **recipes**: each topic skill holds the decisions a kind of
vlog makes the same way every time (structure, pacing, hook, text, sound and look intent) and the **review profile**
it sets on the project, so one prompt gives a consistent result. The editing itself is the agent kit's job
(`bc:edit-workflow` and the skills it names); a recipe tells those skills *which values* to use.

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
one the *whole* video is about and borrow single moves from the other. None fits: use the nearest and say so; do not
invent a profile.

## 2. Set the project up from the recipe

Ask only what changes the result and cannot be seen in the footage: **where it will be posted** (the platform sets
the frame, length and safe zones) and **how long**. Defaults: vertical → TikTok, Reels and Shorts; landscape →
YouTube.

1. Canvas: `bashcut project create … --canvas portrait|landscape` for a new project, or `project format --canvas`.
2. Read the current review object: `bashcut project get` → `review` (may be absent). Keep the user's own keys
   (`disabledChecks`, anything you do not recognise); replace only the recipe keys `minShotSeconds`, `maxShotSeconds`,
   `maxStillSeconds`, `hookSeconds` and `severities` with the recipe's values.
3. One undoable edit that records the recipe, its review profile and the outputs (first output = primary platform):

```json
[{"op": "setProjectProperties", "patch": {
  "recipe": {"skill": "bashcut.vlog:travel", "outputs": ["reels", "tiktok", "shorts"]},
  "output": {"presets": ["reels", "tiktok", "shorts"]},
  "review": {"minShotSeconds": 0.8, "maxShotSeconds": 4.5, "maxStillSeconds": 3, "hookSeconds": 3,
             "severities": {"still": "error"}, "disabledChecks": ["…kept from the project…"]}
}}]
```

```sh
bashcut timeline apply recipe.json --base-rev N --label "Vlog recipe: travel"
```

Use the exact numbers of the recipe's **Profile** block. Output presets are `tiktok`, `reels`, `shorts`,
`youtube-1080`, `youtube-4k` (newer BashCut also takes `project format --outputs reels,tiktok`). The review then
checks the first output's platform: its safe zones and smallest text, a cut longer than the platform takes, a frame of
the wrong shape. Never set `audio.targetLUFS` from a recipe: the platform's loudness target stays (-14 LUFS), and
normalization measures the real mix to reach it.

## 3. Plan before cutting

Write the plan in a few lines and show it to the user before the rough cut:

- **Hook** (first 1–3 s): the line or on-screen text, with a number or a question (`bashcut.vlog:hook-script`).
- **Sections** from the recipe's structure, each with what it shows and says, and a length.
- **Coverage**: after `bc:footage-survey`, list which planned shots exist and which are missing. Say plainly what is
  missing; offer a cutaway from the footage, a stock picture (`bc:stock-images`) or a generated shot.
- **Not shot yet**: give the recipe's shot list as a checklist (what to film, how long, which angle).
- **Generated shots**: when the user wants a scene made with an AI video model instead of filming it, write the prompt
  with `bashcut.vlog:scene-prompt`, and add the recipe's disclosure label to the edit when the clip is placed.

## 4. Edit, review, publish

Run `bc:edit-workflow` from its step 1 with the recipe at hand. Where a kit skill asks for a value (cut rate, caption
preset, look, music level), use the recipe's. In the review loop, the recipe's `severities` already turn deliberate
choices into notes; anything still an **error** must be fixed before export. Finish with
`bashcut.vlog:publish` (caption, hashtags, cover frame, one export per output).

Report at the end: the recipe used, the outputs, what the review fixed and what was left on purpose.
