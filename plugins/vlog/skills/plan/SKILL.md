---
name: plan
description: Start a vlog in BashCut from one prompt — read the brief, pick the topic recipe (travel, food, daily life, product review, product ad, talking head, podcast clips, tutorial), survey the footage, write the edit plan with `project set-data plan` (the recipe's data — recipe, promise, stages, checks, askAtIntake — sections with length ranges and reasons, shot rows, the establish-or-hook choice, the chosen review ranges), set the project's outputs and review profile from it, then hand the edit to bc:edit-workflow. Use first whenever the user asks for a vlog or a short video about a trip, a meal, a day, a product, a talk or a how-to, before cutting anything, and when footage is still to be shot or generated. Triggers: "làm vlog", "dựng vlog", "vlog du lịch", "vlog ăn uống", "review món", "review sản phẩm", "a day in my life", "video hướng dẫn", "video nói chuyện", "lên kịch bản vlog", "shot list", "cần quay những gì", "một prompt ra video".
---

# Plan a vlog

Reply in the user's language. This plugin's topic skills are **recipes**: each holds what a kind of vlog keeps
(structure, hook, text, sound and look intent) and tables of **sample ranges** from published practice, each with its
source, why it varies and how to measure it. The numbers are starting points, not settings. You survey the footage,
choose a range and a value for each key, write them into the **edit plan** with a reason, and say why. Two folders of
the same genre can and should get different plans. A recipe's structure table is one shape, not the only
one: compare it with a shape the footage suggests (`plan.options`). Going outside a range is allowed when the footage
or the idea earns it: write the value, the reason and `"deliberate": true` in the plan, and review keeps it as info. The editing itself is the agent kit's job (`bc:edit-workflow` and
the skills it names).

**Priority of numbers** (T15 §7): the user's instruction → what our footage can hold → a measured **reference
profile** (a creator or video the user pointed to, measured with `bc:style-study` or `bashcut review shots --media
<ref> --summary`) → the recipe's sample ranges. When a reference profile exists it replaces the recipe's ranges for
every key it measures; the recipe only fills the keys it does not measure. Name the reference in the plan.

## 0. Read what already exists

- `bashcut project data brief` — goal, audience, outputs, angle, length, each with a status (stated, inferred, confirmed).
  No brief and no clear angle in the prompt: run `bashcut.vlog:ideate` first; it writes the brief.
- `bashcut project data plan` — a plan already exists: resume from its `stage`. In `revision` mode, change only the sections
  the user named and leave `frozen` ones alone.
- `bashcut workflow gates` — which gates ask the user (G1 brief, G2 strategy, G3 rough cut, G4 script, G5 draft).
  Request each with `bashcut checkpoint request`; never decide a gate is approved yourself.
- `bashcut knowledge prefs` and `bashcut knowledge facts` — the creator's own preferences and a reference profile, if
  any.

## 1. Pick the recipe

The brief's angle chooses the recipe; the recipe is a suggestion from the brief, not the starting point (T01 §7).

| The user's footage or ask | Recipe skill |
|---|---|
| a trip, a city, places, a route, "đi đâu", "ở đâu" | `bashcut.vlog:travel` |
| eating, cooking, a restaurant, a street food stall, "quán", "món" | `bashcut.vlog:food` |
| a day, a routine, "a day in my life", "một ngày của tôi", study/work with me | `bashcut.vlog:daily` |
| a product, an unboxing, a comparison, "có nên mua", "đáng tiền không" | `bashcut.vlog:product-review` |
| an ad, a product video that sells, "quảng cáo", "video bán hàng", "TVC" | `bashcut.vlog:product-ad` |
| one person talking to camera, an opinion, a story time | `bashcut.vlog:talking-head` |
| shorts cut from a long podcast, interview or livestream | `bashcut.vlog:podcast-clips` |
| a screen recording, an app or tool demo, "cách làm", a step-by-step | `bashcut.vlog:tutorial` |

Read the chosen skill in full (`bashcut skills get bashcut.vlog:<name>`); its **Plan data** section is what you write
into the plan (§3). Two fit (a food stop inside a trip): take the one the *whole* video is about and borrow single
moves from the other. None fits: use the nearest and say so.

## 2. Survey before choosing any number

Ask once (`bc:edit-workflow`, intake): in one round of at most 4 questions, what the prompt and the brief do not say
among **where it will be posted**, **how long**, for a new project **the language** of speech and captions (no
default: `project create --language <tag>`; offer the language the user writes in first), and the recipe's
`askAtIntake` fields. No answer: decide, write the field `inferred` with its reason; the strategy audit checks it.
Never ask again later. Defaults when the user does not care: vertical → TikTok, Reels and Shorts; landscape → YouTube.

1. Canvas: `bashcut project create … --canvas portrait|landscape` for a new project, or `bashcut project format
   --canvas <canvas> --base-rev N`.
2. Survey (`bc:footage-survey`). Read at least:
   - `bashcut media inventory` — what the footage holds: capture time, place, orientation, speech, what is measured,
     transcribed and described;
   - `bashcut media list --analysis` — shape and `fps` per media;
   - `bashcut review shots --media <id> --summary` — source shot lengths and motion;
   - `bashcut media describe` (write) and `bashcut media description` (read) — shot size, move and subjects in the
     closed vocabulary; you match plan rows against these (`bashcut review coverage` shows what each clip plays);
   - `bashcut media speech-map --media <id>` and `bashcut speech rate` — gaps and speaking rate, for speech;
   - `bashcut platforms get <id>` per output — shape, `maxSeconds`, safe zones, loudness target, with sources;
   - a reference video: `bashcut review shots --media <ref> --summary` (its rhythm replaces the recipe's band).
3. After placing clips: `bashcut timeline get` → `scale.maxZoomNative` per item (punch-in headroom before upscaling).

## 3. Write the edit plan

The plan is project data (`project set-data plan`); `context get` summarises it, so work can resume after a break from `project data plan`
alone. Write it before the rough cut and keep it current.

**Recipe data.** From the recipe's Plan data section, only what differs from the kit's defaults:
- `recipe`: `{"skill": "bashcut.vlog:<name>", "version": "<the plugin version, plugins list>"}`.
- `promise`: `{hook, payoff}`, the question the opening raises and the line that closes it (`bashcut.vlog:hook-script`
  writes the words; set a first version here from the angle).
- `stages`: the recipe's deviations per stage id (`required` with `why`, `skill`, `rules`); a stage the footage makes
  pointless gets `{"required": false, "why": …}`.
- `checks`: the recipe's checks that apply to this video, at most 8, each `{id, text, source: "bashcut.vlog:<name>"}`.
  The kit's generic checks are added by the engine; never copy them.
- `askAtIntake`: the recipe's list, as asked in §2.

**Sections.** One per part of the recipe's structure, each with a length *range* chosen from the recipe and the
footage, and a reason ("3 places with good footage, 1 with only two clips → 4 sections of 6–9 s"). Give each section
the `id` or `label` you will use for its section marker (`upsertSection`): review compares each section's planned range
with its marker's length, as info.

**Establish or hook** (T03 §3). Decide how the video opens and record it in `decisions`:
- *Hook first*: the strongest moment, line or number in the first 1–3 s. Fits short-form and anything the viewer can
  scroll past.
- *Establish first*: the widest shot that places the viewer (an arrival, a room, a city). Fits narrative scenes,
  travel arrivals and long-form where the viewer chose to watch.
Say why ("vertical TikTok, the price is the promise → hook first with the bite"). The first shot row carries the
choice: a hook row with the hero subject in `mustShow`, or an establishing row with size `WS` or `EWS`. After the rough
cut, read what really opens the edit over the first seconds: `bashcut transcript words --to F` (first words),
`review layout --to F` (first text), `review shots --to F` (described subjects of the first shots).

**Shot rows** (T03 §4). One row per shot the viewer must see, not per clip: `{id, section, purpose, size, move,
mustShow, targetSeconds, source}`.
- `purpose`: what the viewer must notice first ("the price board, readable").
- `size` from the closed vocabulary (ECU, CU, MCU, MS, MWS, WS, EWS, insert) and `move` (static, pan, tilt, push,
  pull, track, orbit, handheld, zoom, crane), chosen by the information that must be seen.
- `mustShow`: subject names as you wrote them in `media describe`, so you can match them with the clips' `described` subjects.
- `targetSeconds` from the recipe's shot-length band; `source`: `footage`, `stock` or `generated`.
- Neighbouring rows change size, angle or subject. Two rows in a row with the same size and move need a reason; three
  or more usually mean "merge them" (T03 §3).
- How many rows: about runtime ÷ the chosen average shot length (45–60 s holds about 10–14 shots, T03 §3); key rows
  only, not every insert.

**Ranges.** For each review key you will set, the range you chose, its source and the reason, under `ranges`. Cite
the recipe's source ("T07 §7") or the reference ("style-study: @creator, n=12, median 2.9 s").

```json
{
  "mode": "create",
  "stage": "story",
  "recipe": {"skill": "bashcut.vlog:food", "version": "0.0.2"},
  "promise": {"hook": "45K for this bowl — worth it?", "payoff": "Yes, if you come before 7 — save it for later"},
  "stages": {"colour": {"required": true, "why": "food must look appetising"}},
  "checks": [{"id": "price-shown", "text": "The price is on screen", "source": "bashcut.vlog:food"}],
  "askAtIntake": ["sponsored", "shopAddress"],
  "sections": [
    {"id": "hook", "label": "Hook", "lengthSeconds": {"min": 1.5, "max": 2.5},
     "reason": "the pour is 1.8 s at 120 fps; the price is said at 1.2 s"},
    {"id": "place", "label": "Place", "lengthSeconds": {"min": 3, "max": 4}, "reason": "one sign shot, one front shot"}
  ],
  "shots": [
    {"id": "s1", "section": "hook", "purpose": "the noodle pull, steam visible", "size": "CU", "move": "static",
     "mustShow": ["noodles"], "targetSeconds": 1.8, "source": "footage"},
    {"id": "s2", "section": "place", "purpose": "shop name readable", "size": "WS", "move": "handheld",
     "mustShow": ["shop sign"], "targetSeconds": 2, "source": "footage"}
  ],
  "decisions": [
    {"text": "Recipe bashcut.vlog:food; outputs tiktok, reels"},
    {"text": "Hook first: the pull, not the shop front — vertical feed, the bite is the promise"}
  ],
  "ranges": {
    "maxShotSeconds": {"min": 2, "max": 3, "source": "food recipe (T07 §3, §7)",
                       "reason": "bites and reactions; one 4 s cheese pull kept as the hero hold"},
    "hookSeconds": {"min": 1.5, "max": 2, "source": "food recipe", "reason": "the price question is on screen at 0.4 s"}
  }
}
```

```sh
bashcut project set-data plan plan.json --base-rev N          # whole plan; later changes: --merge with only the changed fields
```

## 4. Set the outputs and the review profile

Review checks the project's `review` object, not the plan's ranges: put one value per key, picked inside the range you
wrote, and give the same reason. Leave a key unset when you have no reason to check it: core has no defaults, and an
unset key means no check or info only.

1. Read the current review object: `bashcut project get` → `review` (may be absent). Keep the user's own keys
   (`disabledChecks`, `accepted`, values the user set, anything you do not recognise); replace only the keys you chose.
2. One undoable edit that records the recipe, the outputs (first = primary platform) and the profile:

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

Output presets: `tiktok`, `reels`, `shorts`, `youtube-1080`, `youtube-4k`, and the feed shapes `feed-4x5`, `square`,
`portrait-3x4` (`project format --outputs reels,tiktok` sets the list too). Review checks every output's platform: safe
zones, smallest text, longest length, frame shape.

### Review profile keys

| Key | What it checks |
|---|---|
| `minShotSeconds`, `maxShotSeconds` | shots on Main shorter / longer (short ones are always notes) |
| `stillMotion` | with `maxShotSeconds`: a long shot warns only when its mean picture change is under this (0–1, `review shots` motion) |
| `maxStillSeconds` | frozen picture longer than this |
| `hookSeconds` | speech or text inside the opening window (`review layout --to F`, `transcript words --to F`) |
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
| Monotony | a run of 6+ shots with length variation (CV) under ~0.15 reads flat (T07 §3) | a calm run on purpose is fine; say so | `bashcut review shots --summary` → compute the cv of 6 consecutive `seconds` |
| Pattern interrupt | a new beat every 10–30 s short-form, 30–90 s long-form (T07 §3) | sources contradict; depends on whether "change" means a cut or a new idea | `review shots --summary` per section |
| Payoff / CTA hold | ≥1 s, up to 4–6 s for a CTA (T07 §3) | platform and CTA | `bashcut review layout --from F` → the last title's `holdSeconds` |
| Dead air `maxSilenceSeconds` | sources cut dead air over about 1.5 s (T11 §3) | one held silence of about 2 s before a payoff is a choice, used once (T07 §3) | `bashcut audio measure --timeline` → `silences` |
| Music under the voice | 5–18 dB under during speech (T11 §3) | less when music carries the piece; more for dense information, a soft voice, music with vocals | `bashcut audio mix-measure` → `musicUnderSpeech` |
| `loudnessToleranceLU` | 1–2 LU (T11 §3) | tighter when outputs are compared side by side | export receipt, `review run` |
| Length | the platform's `maxSeconds` is a hard limit; "sweet spots" contradict between sources (T17 §3) | the moment sets the length; never trim to a sweet spot | `bashcut platforms get <id>` |
| Section length | the plan's own range per section | — | `bashcut review run` (section off plan, info) |

**Loudness is per output, never one number**: each export normalizes to its own preset's target (`platforms get` →
`targets`; T11 §3, T17 §3). Never set `audio.targetLUFS` from a recipe; export each output with `--normalize-audio`.

## 5. Strategy audit and gate, then coverage

1. Run the strategy audit (`bc:edit-workflow`: `review packet --point strategy`, a fresh critic, `run append audit`);
   fix the plan when it says two messages or a payoff that misses the hook. Show the plan in 4–8 sentences plus the
   section table (T00 §3): hook and the establish-or-hook choice, sections with
   their ranges, the shot rows, each chosen value with its reason, and what is missing. Request G2:
   `bashcut checkpoint request G2 --summary "<the plan in short>" --attach <contact sheet>` and poll `bashcut
   checkpoint status` until it is not `awaiting_user`. `changes`: update the plan and ask again.
2. **Coverage**: `bashcut review coverage` says which described shot each clip plays (and its `planShot`); match
   each shot row yourself as placed (a clip plays it), found (`media description` has a fitting shot), missing or
   undescribed (`described` null: describe the media first). Missing: say it plainly and offer, in this order, a cutaway from the footage, a punch-in
   on a wider shot (within its headroom), a stock picture (`bc:stock-images`, row `source: stock`) or a generated shot
   (row `source: generated`).
3. **Generated shots**: write the prompt with `bashcut.vlog:scene-prompt`, giving it the row and its neighbours (the
   rows before and after in the plan, with their size, move and subjects, and what the clips placed there look like),
   so the new shot cuts in. Never label it on the video (no "AI" or "minh hoạ" text); AI disclosure is the
   platform's upload toggle (`bashcut.vlog:publish`).
4. **Not shot yet**: give the missing rows as a checklist to film (what, how long, which angle).

## 6. Edit, review, publish

Survey and story are done here: record them (`bashcut run append stage --stage story --status done --evidence
"plan;strategy audit"`), then hand over to `bc:edit-workflow` from the rough cut on. It runs the stages, the checklist
and the audits from this plan, and `context get` › `workflow.next` names the one skill to read per stage. Where a kit skill asks
for a value (cut rate, caption grouping, punch-in, music level), choose inside the plan's range and say why. The words
(hook, script, voiceover) come from `bashcut.vlog:hook-script`. In the review loop, the severities you set turn
deliberate choices into notes; anything still an **error** must be fixed before export. If the cut shows a chosen
range was wrong (the footage cannot hold it), change the plan and the profile with a reason instead of forcing the
edit. Finish with `bashcut.vlog:publish`.

Report at the end: the recipe used, the outputs, the plan's sections and ranges with their reasons and sources, what
review fixed, what was left on purpose and why, and what the user still has to decide.
