# Vlog

Agent skills and a library pack for making vlogs in BashCut. Each **topic skill is a recipe**: the decisions one kind
of vlog makes the same way every time — structure, pacing, hook, text, sound and look intent — and the **review
profile** it sets on the project (`review` thresholds and severities, `output.presets`), so one prompt gives a
consistent result. The plugin runs no program; BashCut gives the skills to Claude, Codex and its other agents while it
is trusted and turned on, as `bashcut.vlog:<name>`, and lists the pack's items in the library. How to cut, mix, grade
and caption stays in the agent kit (`bc:`); a recipe says which values those skills use.

| Skill | Use it for |
|---|---|
| `plan` | Start here: pick the recipe from the prompt, set the project's outputs and review profile, plan hook, sections and shot list |
| `hook-script` | Hook line and title (a number or a question), voiceover or talking script at a speakable pace, on-screen text, CTA |
| `publish` | One export per output platform, a separate cut for another shape, cover frame, post caption and hashtags |
| `travel` | Travel vlog / guide: cost or time hook, numbered place sections, cost recap |
| `food` | Food vlog / review: the bite as the hook, price, process inserts, tasting, verdict |
| `daily` | A day in my life, routines: time stamps, calm pace |
| `product-review` | Review or unboxing: verdict question, three points with pros and cons, verdict card |
| `talking-head` | One person to camera: tight speech cuts, punch-ins, word-by-word captions |
| `tutorial` | Screen recording or tool demo: result first, step cards, zooms, waiting sped up |
| `scene-prompt` | A scene idea → a cinematic prompt for AI video models (Seedance, Kling, Veo, Sora…) for shots the footage lacks |

The `library/vlog` pack adds text styles (hook question, section chip, time stamp, price tag, pro/con, step, keyword,
verdict, CTA, disclosure label), emoji stickers by topic and four transitions, all tagged by topic
(`bashcut library list --pack Vlog --tag food`). It ships no music or sound files; the skills say where to find
licensed ones (`bc:audio-mix`).

## Recipes and numbers

A recipe's numbers are the ones a review can check: shot lengths, hook window, severities, output platforms. It never
fixes colour values or loudness: a look is an intent the agent grades to after measuring the footage
(`bc:color-grade`), and loudness is the platform's target (-14 LUFS) that normalization reaches from the real mix.

## Adding a recipe

Copy a topic skill to `skills/<topic>/SKILL.md` (front matter `name` = folder name, `description` with "Use when …"
and `Triggers:`), keep its sections (Profile, Structure, Cuts and motion, Shots, Text, sound, look, Review notes),
add a row to the table in `plan` and above, and list it in `plugin.json` › `contributes.skills` (at most 16). Profile
keys are `minShotSeconds`, `maxShotSeconds`, `maxStillSeconds`, `hookSeconds` and `severities` (review check ID or
prefix → `error`, `warning`, `info` or `off`); outputs are export preset names.

## Sources and licenses

- `scene-prompt` is based on
  [cinematic-video-prompt-engineer](https://github.com/CyberJ0605/cinematic-video-prompt-engineer-skill) v1.8.0
  (commit `53bdce3`) by CyberJ0605, MIT License — the license is in
  [`skills/scene-prompt/LICENSE-upstream`](skills/scene-prompt/LICENSE-upstream). Changes: renamed to
  `scene-prompt`, a BashCut section and description added (moved from the withdrawn Pre-production plugin), "Cinematic Translation Rules" moved to
  `references/cinematic_translation_rules.md` so `SKILL.md` stays under BashCut's 64 KB limit, and the upstream
  `agents/openai.yaml`, evaluation videos and README left out. To update, copy the upstream `SKILL.md` and
  `references/` again and repeat these changes.
