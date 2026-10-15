---
name: plan
description: Start any vlog or short video in BashCut: pick the topic recipe, survey footage, write the edit plan and review profile, hand over to bc:edit-workflow. Use first, before cutting, even when footage is still to be shot. Triggers: "làm vlog", "dựng vlog", "một prompt ra video", "lên kịch bản vlog", "shot list", "cần quay những gì".
---

# Plan a vlog

Reply in the user's language. This plugin's topic skills are **recipes**: what a kind of vlog keeps (structure, hook,
text, sound and look intent) and **sample ranges** from published practice, each with its source, why it varies and
how to measure it. The numbers are starting points, not settings: survey the footage, choose a range and a value per
key, write them into the **edit plan** with a reason. Two folders of the same genre can and should get different
plans. A recipe's structure is one shape, not the only one: compare it with a shape the footage suggests
(`plan.options`). Going outside a range is allowed when the footage or idea earns it: write the value, the reason and
`"deliberate": true`; review keeps it as info. The editing itself is `bc:edit-workflow` and the skills it names.

**Priority of numbers** (T15 §7): the user's instruction → what our footage can hold → a measured **reference
profile** (a creator or video the user pointed to, measured with `bc:style-study` or `review shots --media <ref>
--summary`) → the recipe's sample ranges. A reference profile replaces the recipe's range for every key it measures
(T07 §7); the recipe fills only the rest. Name the reference in the plan. Every recipe's ranges follow this rule; they
do not repeat it.

## 0. Read what already exists

- `project data brief` — goal, audience, outputs, angle, length, each stated, inferred or confirmed. No brief and no
  clear angle in the prompt: run `bashcut.vlog:ideate` first.
- `project data plan` — resume from its `stage`; in `revision` mode change only the sections the user named and
  leave `frozen` ones alone.
- `workflow gates` — which gates ask the user (G1 brief, G2 strategy, G3 rough cut, G4 script, G5 draft). Never
  decide a gate is approved yourself.
- `knowledge prefs`, `knowledge facts` — the creator's preferences and a reference profile, if any.

## 1. Pick the recipe

The brief's angle chooses the recipe, not the other way round (T01 §7).

| The user's footage or ask | Recipe |
|---|---|
| a trip, a city, places, a route, "đi đâu", "ở đâu" | `bashcut.vlog:travel` |
| eating, cooking, a restaurant, a street food stall, "quán", "món" | `bashcut.vlog:food` |
| a day, a routine, "a day in my life", study/work with me | `bashcut.vlog:daily` |
| a product, an unboxing, a comparison, "có nên mua", "đáng tiền không" | `bashcut.vlog:product-review` |
| an ad, a video that sells one thing, "quảng cáo", "video bán hàng", "TVC" | `bashcut.vlog:product-ad` |
| one person talking to camera, an opinion, a story time | `bashcut.vlog:talking-head` |
| shorts cut from a long podcast, interview or livestream | `bashcut.vlog:podcast-clips` |
| a screen recording, an app or tool demo, "cách làm", step by step | `bashcut.vlog:tutorial` |
| a topic explained with cards, numbers and a voice, little or no footage | `bashcut.vlog:explainer` |
| news or a documentary from photos, archive and source screenshots, "tin nóng", "phóng sự" | `bashcut.vlog:news` |
| energy and identity, not one product's sale: brand hype, showreel, motion comic | `bashcut.vlog:promo` |

Read the chosen skill in full (`bashcut skills get bashcut.vlog:<name>`); its **Plan data** goes into the plan (§3).
Two fit (a food stop inside a trip): take the one the *whole* video is about and borrow single moves from the other.
None fits: the nearest, and say so.

## 2. Survey before choosing any number

Intake (`bc:edit-workflow`): one round of at most 4 questions on what the prompt and brief do not say among **where it
is posted**, **how long**, for a new project **the language** of speech and captions (no default; offer the user's
writing language first), and the recipe's `askAtIntake`. No answer: decide, write the field `inferred` with its
reason; the strategy audit checks it. Never ask again later. Defaults when the user does not care: vertical → TikTok,
Reels, Shorts; landscape → YouTube.

1. Canvas: `project create … --canvas` or `project format --canvas`.
2. Survey (`bc:footage-survey`). Read at least: `media inventory` (what the footage holds), `media list --analysis`
   (shape, fps), `review shots --media <id> --summary` (source shot lengths, motion), `media describe` /
   `media description` (shot size, move, subjects in the closed vocabulary: plan rows are matched against these),
   `media speech-map` and `speech rate` for speech, `platforms get <id>` per output (shape, `maxSeconds`, safe
   zones, loudness target, with sources), and a reference's `review shots --summary` (its rhythm replaces the
   recipe's band).
3. After placing clips: `timeline get` › `scale.maxZoomNative` per item (punch-in headroom before upscaling).

## 3. Write the edit plan

The plan is project data (`project set-data plan`); `context get` summarises it, so work resumes from `project data
plan` alone. Write it before the rough cut and keep it current.

**Recipe data**, only what differs from the kit's defaults:
- `recipe`: `{"skill": "bashcut.vlog:<name>", "version": "<plugin version>"}`.
- `promise`: `{hook, payoff}`, the question the opening raises and the line that closes it (words by
  `bashcut.vlog:hook-script`; a first version here from the angle).
- `stages`: the recipe's deviations per stage id (`required` with `why`, `skill`, `rules`); a stage the footage makes
  pointless gets `{"required": false, "why": …}`. An added stage names its place with `after` (speech-led recipes add
  `visuals` after `voiceover`, read by `bc:visual-plan`); a music-only cut sets it `{"required": false, "why": "no
  words carry it"}`.
- `checks`: the recipe's checks that apply, at most 8, each `{id, text, source}`. The engine adds the kit's generic
  checks; never copy them.
- `askAtIntake`: the recipe's list, as asked in §2.

**Sections**: one per part of the structure, each with a length *range* from the recipe and the footage and a reason
("3 places with good footage, 1 with two clips → 4 sections of 6–9 s"), and the `id` or `label` of its section marker
(`upsertSection`): review compares each planned range with its marker, as info.

**Establish or hook** (T03 §3), recorded in `decisions` with why:
- *Hook first*: the strongest moment, line or number in the first 1–3 s; short-form and anything scrollable.
- *Establish first*: the widest placing shot (an arrival, a room, a city); narrative scenes, travel arrivals,
  long-form the viewer chose.
The first shot row carries it: a hook row with the hero subject in `mustShow`, or an establishing row of size `WS` or
`EWS`. After the rough cut, read what really opens the edit: `transcript words --to F`, `review layout --to F`,
`review shots --to F`.

**Shot rows** (T03 §4): one per shot the viewer must see, not per clip: `{id, section, purpose, size, move, mustShow,
targetSeconds, source}`.
- `purpose`: what the viewer must notice first ("the price board, readable").
- `size` (ECU, CU, MCU, MS, MWS, WS, EWS, insert) and `move` (static, pan, tilt, push, pull, track, orbit, handheld,
  zoom, crane), chosen by the information that must be seen.
- `mustShow`: subject names as written in `media describe`, to match the clips' `described` subjects.
- `targetSeconds` from the recipe's shot band; `source`: `footage`, `stock` or `generated`.
- Neighbours change size, angle or subject; two alike in a row need a reason, three usually mean merge (T03 §3).
- About runtime ÷ average shot length rows (45–60 s holds about 10–14 shots, T03 §3); key rows only.

**Ranges**: per review key you will set, the range, its source and the reason, under `ranges` ("T07 §7", or
"style-study: @creator, n=12, median 2.9 s").

```json
{"mode": "create", "stage": "story",
 "recipe": {"skill": "bashcut.vlog:food", "version": "0.0.7"},
 "promise": {"hook": "45K for this bowl — worth it?", "payoff": "Yes, if you come before 7 — save it"},
 "stages": {"colour": {"required": true, "why": "food must look appetising"}},
 "checks": [{"id": "price-shown", "text": "The price is on screen", "source": "bashcut.vlog:food"}],
 "askAtIntake": ["sponsored", "shopAddress"],
 "sections": [{"id": "hook", "label": "Hook", "lengthSeconds": {"min": 1.5, "max": 2.5},
               "reason": "the pour is 1.8 s at 120 fps; the price is said at 1.2 s"}],
 "shots": [{"id": "s1", "section": "hook", "purpose": "the noodle pull, steam visible", "size": "CU",
            "move": "static", "mustShow": ["noodles"], "targetSeconds": 1.8, "source": "footage"}],
 "decisions": [{"text": "Hook first: the pull, not the shop front — vertical feed, the bite is the promise"}],
 "ranges": {"maxShotSeconds": {"min": 2, "max": 3, "source": "food recipe (T07 §3)",
                               "reason": "bites and reactions; one 4 s cheese pull kept as the hero hold"}}}
```

Write it whole once (`project set-data plan plan.json`), later changes with `--merge` and only the changed fields.

## 4. Set the outputs and the review profile

Review reads the project's `review` object, not the plan's ranges: one value per key, inside the range you wrote,
with the same reason. Leave a key unset when you have no reason to check it (core has no defaults). Keys and what
each checks: `bc:review` ("Before round 1") and `bashcut schema get`.

1. Read the current `review` (`project get`). Keep the user's own keys (`disabledChecks`, `accepted`, values the user
   set, anything unknown); replace only the keys you chose.
2. One undoable edit records the recipe, the outputs (first = primary platform) and the profile:

```json
[{"op": "setProjectProperties", "patch": {
  "recipe": {"skill": "bashcut.vlog:<recipe>", "outputs": ["<output>"]},
  "output": {"presets": ["<output>"]},
  "review": {"maxShotSeconds": <chosen>, "hookSeconds": <chosen>, "severities": {"<check>": "<chosen>"},
             "disabledChecks": ["…kept from the project…"]}}}]
```

`setProjectProperties` replaces the whole `review` object: always write back the kept keys. Output presets: `tiktok`,
`reels`, `shorts`, `youtube-1080`, `youtube-4k`, `feed-4x5`, `square`, `portrait-3x4`. Review checks every output's
platform (safe zones, smallest text, longest length, frame shape).

### Checks every recipe shares

| Check | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Monotony | a run of 6+ shots with length variation (CV) under ~0.15 reads flat (T07 §3) | a calm run on purpose is fine; say so | `review shots --summary` → cv of 6 consecutive `seconds` |
| Pattern interrupt | a new beat every 10–30 s short-form, 30–90 s long-form (T07 §3) | sources contradict; "change" may mean a cut or a new idea | `review shots --summary` per section |
| Payoff / CTA hold | ≥1 s, up to 4–6 s for a CTA (T07 §3) | platform and CTA | `review layout --from F` → last title's `holdSeconds` |
| Dead air `maxSilenceSeconds` | sources cut dead air over about 1.5 s (T11 §3) | one held silence of about 2 s before a payoff, used once (T07 §3) | `audio measure --timeline` → `silences` |
| Music under the voice | 5–18 dB under during speech (T11 §3) | less when music carries the piece; more for dense information, a soft voice, music with vocals | `audio mix-measure` → `musicUnderSpeech` |
| `loudnessToleranceLU` | 1–2 LU (T11 §3) | tighter when outputs are compared side by side | export receipt, `review run` |
| Length | the platform's `maxSeconds` is the hard limit; "sweet spots" contradict (T17 §3) | the moment sets the length; never trim to a sweet spot | `platforms get <id>` |
| Section length | the plan's own range per section | — | `review run` (section off plan, info) |

**Loudness is per output, never one number**: each export normalizes to its preset's target (`platforms get` ›
`targets`; T11 §3, T17 §3). Never set `audio.targetLUFS` from a recipe; export every output with `--normalize-audio`.
This holds for every recipe.

**Shared by every recipe** (the recipes do not repeat these): Vietnamese text needs a font with every tone mark
(`bc:captions-text`); the brand (`project get` › `brand`: palette, fonts, logo, mascot) sets the look when there is
one; nothing generated, stock or AI is labelled on the video unless the recipe says so (news; an explainer's
illustrative housing project); sponsorship
is said early with `vlog-disclosure` in the user's wording; transition kinds and their sizes are `bc:effects`.

## 5. Strategy audit and gate, then coverage

1. Strategy audit (`bc:edit-workflow`: `review packet --point strategy`, a fresh critic, `run append audit`); fix
   the plan when it finds two messages or a payoff that misses the hook. Show the plan in 4–8 sentences plus the
   section table (T00 §3): hook and the establish-or-hook choice, sections and ranges, shot rows, each chosen value
   with its reason, what is missing. Request G2 with a contact sheet attached and wait for the answer; `changes`:
   update the plan and ask again.
2. **Coverage**: `review coverage` says which described shot each clip plays (and its `planShot`); match each row as
   placed, found (`media description` has a fitting shot), missing, or undescribed (describe the media first).
   Missing: say so and offer, in this order, a cutaway from the footage, a punch-in on a wider shot (within its
   headroom), a stock picture (`bc:stock-images`, `source: stock`) or a generated shot (`source: generated`).
3. **Generated shots**: write the prompt with `bashcut.vlog:scene-prompt`, giving it the row and its neighbours (size,
   move, subjects, what the placed clips look like) so the shot cuts in. Never label it on the video (no "AI" or
   "minh hoạ"); AI disclosure is the platform's upload toggle (`bashcut.vlog:publish`). Exception: in
   `bashcut.vlog:news` an illustration carries its label, because a news viewer takes pictures as evidence.
4. **Not shot yet**: give the missing rows as a checklist to film (what, how long, which angle).

## 6. Edit, review, publish

Record survey and story (`run append stage --stage story --status done --evidence "plan;strategy audit"`), then hand
over to `bc:edit-workflow` from the rough cut on; `context get` › `workflow.next` names the skill per stage. Where a
kit skill asks for a value (cut rate, caption grouping, punch-in, music level), choose inside the plan's range and say
why. Words come from `bashcut.vlog:hook-script`. In review, your severities turn deliberate choices into notes;
anything still an **error** is fixed before export. If the cut shows a range was wrong (the footage cannot hold it),
change the plan and profile with a reason instead of forcing the edit. Finish with `bashcut.vlog:publish`.

Report: the recipe, the outputs, the sections and ranges with reasons and sources, what review fixed, what was left on
purpose and why, and what the user still has to decide.
