# Pre-production

Agent skills for the work before the edit: writing, planning and prompting, before there is footage on the timeline.
The plugin runs no program; BashCut gives its skills to Claude, Codex and its other agents while it is trusted and
turned on, as `bashcut.preproduction:<name>`. Editing skills stay in the agent kit (`bc:`).

| Skill | Use it for |
|---|---|
| `scene-prompt` | A plot summary, novel excerpt or scene idea → a cinematic 6–30 s prompt for AI video models (Seedance, Kling, Veo, Sora, Runway, Jimeng…): story diagnosis, camera, performance, dialogue, light and sound, reference-image planning, series continuation and repair of failed generations |

## Adding a skill

Put it in `skills/<name>/SKILL.md` (front matter `name` = folder name, `description` with "Use when …" and
`Triggers:`), list it in `plugin.json` › `contributes.skills` (at most 16) and add a row above. Keep it about work
before the edit; a skill that drives the timeline belongs in the agent kit. A skill taken from elsewhere says where
it came from below.

## Sources and licenses

- `scene-prompt` is based on
  [cinematic-video-prompt-engineer](https://github.com/CyberJ0605/cinematic-video-prompt-engineer-skill) v1.8.0
  (commit `53bdce3`) by CyberJ0605, MIT License — the license is in
  [`skills/scene-prompt/LICENSE-upstream`](skills/scene-prompt/LICENSE-upstream). Changes: renamed to
  `scene-prompt`, a BashCut section and description added, "Cinematic Translation Rules" moved to
  `references/cinematic_translation_rules.md` so `SKILL.md` stays under BashCut's 64 KB limit, and the upstream
  `agents/openai.yaml`, evaluation videos and README left out. To update, copy the upstream `SKILL.md` and
  `references/` again and repeat these changes.
