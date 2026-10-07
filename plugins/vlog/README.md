# Vlog

Agent skills and a library pack for making vlogs in BashCut. Each **topic skill is a recipe**: what one kind of vlog
keeps — structure, hook, text, sound and look intent — and tables of **sample ranges** from published practice (shot
lengths, rhythm and interrupt bands, transition vocabulary and budget, graphic holds and density, presenter presence,
hook window, captions, severities), each with its source, why it varies and how to measure it. The agent surveys the
footage, chooses a range and a value for each key and writes them, with the reason, into the project's **edit plan**
(`bashcut project set-data plan`: sections with length ranges, shot rows, decisions) and **review profile**, so two folders of the
same genre can get different, justified plans. A measured reference profile (`bc:style-study`) replaces a recipe's
ranges wherever it has a measurement. Each recipe ends with review notes in viewer terms and a `needs_user` list. The
plugin runs no program; BashCut gives the skills to Claude, Codex and its other agents while it is trusted and turned
on, as `bashcut.vlog:<name>`, and lists the pack's items in the library. How to cut, mix, grade and caption stays in
the agent kit (`bc:`); a recipe says what to measure and which range to choose from.

| Skill | Use it for |
|---|---|
| `ideate` | No angle yet: angles from the footage with a source each, a 3-hook screen, a decision table, the project brief (`project set-data brief`) |
| `plan` | Start here: read the brief, pick the recipe, survey, write the edit plan (sections with ranges, shot rows, establish or hook first, chosen ranges with reasons) and the review profile and outputs |
| `hook-script` | Story options, hook options checked against real shots, the script as beats (job, ON SCREEN, source per line) sized with the measured speaking rate, a counterfactual review, on-screen text, CTA |
| `publish` | Platform facts from data (`platforms get`), one export per output, cover candidates checked at phone size (`export cover`), YouTube chapters (`export chapters`), title, caption and hashtags |
| `travel` | Travel vlog / guide: cost or time hook, numbered place sections, cost recap |
| `food` | Food vlog / review: the bite as the hook, price, process inserts, tasting, verdict |
| `daily` | A day in my life, routines: time stamps, calm pace |
| `product-review` | Review or unboxing: verdict question, points with pros and cons, verdict card |
| `product-ad` | An ad or selling video: ad brief with a truth source, hook and CTA as a pair, arcs, truth rules, variants that change one thing |
| `talking-head` | One person to camera: tight speech cuts, punch-ins, word-by-word captions, presence |
| `podcast-clips` | Shorts from a long podcast or interview: selects by quote, standalone test, blind second pass, one project per clip (`project derive`) |
| `tutorial` | Screen recording or tool demo: result first, step cards, zooms, waiting sped up, presenter presence |
| `scene-prompt` | A scene idea → a cinematic prompt for AI video models (Seedance, Kling, Veo, Sora…) for shots the footage lacks; reads the neighbouring plan rows so the shot cuts in |

The `library/vlog` pack adds text styles (hook question, section chip, time stamp, price tag, pro/con, step, keyword,
verdict, CTA, disclosure label), emoji stickers by topic and four transitions, all tagged by topic
(`bashcut library list --pack Vlog --tag food`). It ships no music or sound files; the skills say where to find
licensed ones (`bc:audio-mix`).

## Recipes and numbers

A recipe ships ranges, not settings: no recipe has a profile block to copy. Each range cites where it comes from (the
analysis notes T00–T19, e.g. "(T07 §3)") and says what makes it move. The agent picks a range and a value and says why
in the plan; contradictions between sources are shown, not hidden. It never fixes colour values
or loudness: a look is an intent the agent grades to after measuring the footage (`bc:color-grade`), and each export
is normalized to its own output's target (`bashcut platforms get`), never one number for every platform.

## Adding a recipe

Copy a topic skill to `skills/<topic>/SKILL.md` (front matter `name` = folder name, `description` with "Use when …"
and `Triggers:`), keep its sections (Ranges, Structure, Cuts and motion, Rhythm, transitions and graphics, Shots,
Text, sound, look, Review notes), add a row to the table in `plan` and above, and list it in `plugin.json` ›
`contributes.skills` (at most 16). Ranges rows are check → sample range (with its source) → why it varies → what to
measure, using only commands in BashCut's command reference. Review keys are listed in `plan` (core has no defaults:
an unset key means no check, or info only); `severities` maps a check ID or prefix, or `provider:`, to `error`,
`warning`, `info` or `off`; outputs are export preset names.

## Sources and licenses

- `scene-prompt` is based on
  [cinematic-video-prompt-engineer](https://github.com/CyberJ0605/cinematic-video-prompt-engineer-skill) v1.8.0
  (commit `53bdce3`) by CyberJ0605, MIT License — the license is in
  [`skills/scene-prompt/LICENSE-upstream`](skills/scene-prompt/LICENSE-upstream). Changes: translated from
  Chinese to English (`SKILL.md` and every reference), renamed to `scene-prompt`, a BashCut section and description added (moved from the withdrawn Pre-production plugin), "Cinematic Translation Rules" moved to
  `references/cinematic_translation_rules.md` so `SKILL.md` stays under BashCut's 64 KB limit, and the upstream
  `agents/openai.yaml`, evaluation videos and README left out. To update, translate the upstream changes to
  `SKILL.md` and `references/` into English (keeping the section labels of
  this copy) and repeat the other changes.
