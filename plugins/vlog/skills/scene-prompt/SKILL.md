---
name: scene-prompt
description: Turn a plot, novel excerpt or scene idea into a cinematic 6–30 s prompt for AI video models (Seedance, Kling, Veo, Sora…), plan reference images, continue a series, fix a failed generation. Use when a shot must be generated. Triggers: "viết prompt video", "prompt video AI", "prompt Kling", "cảnh điện ảnh", "viết tiếp đoạn sau", "sửa prompt video".
---

# Scene prompt

> Based on [cinematic-video-prompt-engineer](https://github.com/CyberJ0605/cinematic-video-prompt-engineer-skill)
> v1.8.0 by CyberJ0605 (MIT, see `LICENSE-upstream`), translated from Chinese. This copy adds the BashCut notes,
> keeps the long rules in `references/` and condenses `SKILL.md` to point at them.

## In BashCut

This skill writes text for an AI video or image model; it does not edit the timeline. In a vlog it makes the shots
the footage lacks (an intro scene, a b-roll moment, an illustration); `bashcut.vlog:plan` sends you here. The placed
clip carries no on-video label; AI disclosure is the platform's upload toggle (`bashcut.vlog:publish`).

- **Language.** Talk in the user's language and write the section labels in it (Vietnamese: 【Chẩn đoán cốt truyện】,
  【Chiến lược chuyển thể điện ảnh】, 【Prompt video cuối cùng】…). The final prompt goes in the language the user asks
  for, else the one the model reads best (Chinese or English for Seedance, Kling, Jimeng, Hailuo, Wan; English for
  Veo, Sora, Runway); say which. Camera terms stay in English when more precise (`ECU`, `MS`, `Dolly In`, `Rack
  Focus`, `35mm`, `Handheld`); never paste the reference libraries' sentences verbatim.
- **Read the neighbours first (a shot for an edit plan).** Read the row in `project data plan` › `shots` (purpose,
  size, move, mustShow, targetSeconds) and the rows before and after it in its section, and what their clips really
  show (`review coverage`, `media description`, the last frame of the shot before and the first of the shot after).
  Write the new shot to cut in: a size step from the shot before, screen direction carried from its exit, the same
  subjects with the same look sentence (light, colour, time of day), a length inside `targetSeconds` (T03 §7). Say
  which neighbours you read.
- **No generation by default.** The prompt is the job. Generate only when the user asks and a tool exists; never
  spend their credits on your own initiative.
- **Dry run before generating**: `bashcut library generate … --kind clip --dry-run` returns the provider request,
  whether it is paid and its estimate. Check it against the provider's limits (durations, prompt length, reference
  count) and the row's `targetSeconds`, show the priced request and wait for a yes; the real run carries a
  `--request-id` so a retry never pays twice. No provider: deliver the prompt and say generation is theirs.
- **Compare takes, then keep one.** Takes are candidates. Import them and look side by side (`media frames --media
  a,b,c --sheet`; for a row, `--reference <neighbour>`). Measure what the model did, not what was asked: real
  duration, cuts inside the clip, motion (`media strip`, `media description`). Cull on hard invariants first
  (identity, wardrobe, props, screen direction, text that must not appear, length), then judge. Record each verdict
  on the media (`setMediaData` patch `{take, verdict: keep|cull, reason}`) so the next session sees the ledger. The
  same failure in most takes is the prompt (rewrite it); one bad take among good ones is chance (run again).
- **Chaining.** The next clip starts from the kept take's real last frame (`media frame --edge last`), never an
  imagined one.
- **Bringing clips in**: `media import`, check with `ui frame`, `media describe` and set `planShot` to the row id,
  then `bc:edit-workflow`. Effects, transitions or grading on footage already in BashCut: `bc:effects`,
  `bc:color-grade`, not this skill.
- **Series.** Offer to save character, scene and prop anchors in the project memo (`bashcut knowledge memo`) with the
  media each comes from (kept take and frame).

## What it does

Turns a plot summary, novel excerpt or scene idea into a cinematic prompt: first find what a short video can show,
then translate abstract story into visible action, camera, performance, light, sound and timing. It also continues a
previous segment (from its ending, keeping character, scene and prop continuity; new reference prompts only for new
characters, places, products or key props).

## Execution Decisions and Agent Capabilities

Apply before any mode or path checkpoint; ordinary conversation is enough, no special tool or memory is needed.

1. Read the requested deliverable, stage and constraints; reuse decisions from the visible conversation or a handoff.
   Never claim to remember unavailable context. "Unrelated to the earlier story" starts a new story state.
2. Honour an explicit request to discuss, approve or stop at a stage. Otherwise reuse a chosen direction, route,
   ratio, scope or asset while its conditions hold. Resolve "1", "as suggested", "continue" against the most recent
   unambiguous pending choice; ask only if several remain plausible.
3. Missing assets block only the work that depends on them; finish the independent work requested.
4. Ask only when a fact cannot be inferred or chosen within delegated creative control **and** would change core
   story facts, a hard constraint, delivery scope or costly assets. Genre, length, several valid treatments and
   missing cinematography details are never reasons to pause: choose camera, light, performance and pacing yourself.
   Keep a vague-input question when even the event or emotional change is unknown and control was not delegated.
5. Approval is object-specific: a direction choice is not image approval; a reference-first route permits the asset
   plan and image prompts, not a generation call; selected images permit reference-driven writing, not redesign of
   approved facts; a full-adaptation request keeps full coverage, not highlights. Never infer publication or
   unrelated external actions.

**Boundaries.** The baseline deliverable is text; the video model's abilities grant the agent nothing. Read
references through the host; if one is missing, name it and its effect, never invent its contents. Inspect actual
images when you can view them: a filename, an earlier prompt or a description is not an inspection; without vision,
name the missing visual facts and mark any draft "not image-verified". Generate or edit media only when asked and
permitted. Stage-only requests end after that stage; a complete deliverable continues through authorized stages
without a fresh approval per stage. When output limits force batches, keep segment numbers, remaining scope,
continuity anchors and the next step, and never call a partial batch the whole. Report only the verification really
done (text self-check, image inspection, video review).

## Continuity and Director Delivery Gate

For continuation, multi-shot reference-driven work or cut and geometry repairs, read
`references/continuity_director_contract.md` before drafting and run its final delivery gate before answering (tail
frame vs first frame, visible-only instructions, shot-to-reference coverage, visible diagnosis and strategy,
purposeful camera geometry, motivated camera variety; it overrides older examples that copy a tail frame). Workshop
and continuation outputs keep a short 【Story diagnosis】 and 【Cinematic adaptation strategy】; missing new-angle evidence
calls for reference prompts before the image-grounded video prompt.

## Default Workflow

Pick an output mode (default: workshop), then one production path: **Direct video path** (a self-contained prompt)
or **Reference-first path** (staged; the later video prompt assumes approved images). Never merge them into one
universal prompt. Then read only what the case needs:

| Case | Read |
|---|---|
| references requested, supplied or clearly useful; a generated reference image to fix | `references/reference_first_video_workflow.md` (Reference Image Result Repair: keep approved facts, change only the failed field and its dependents) |
| a generated video to fix | `Generated-Result Surgical Repair` in `references/style_patterns.md`: lock what worked, change only the failed control unless the shot structure is unsound |
| generated-video attribution, or an emotional true one-take with near/far attention, approaching characters or shared-object contact | `references/one_take_emotional_coverage.md` (never impose movement on simple or locked shots) |
| camera movement carries the story, a named move, precise start/path/speed/end | `references/camera_movement_prompt_library.md`: one module by dramatic function, not all 46 |
| a named emotion, close performance, dialogue barrier, concealment or reaction | `references/emotion_performance_prompt_library.md`: one base emotion, 2–4 signals adapted to the character |
| vertical / 9:16 | `references/vertical_9x16_adaptation.md`: recompose, never crop horizontal grammar |
| always, before drafting | `references/cinematic_translation_rules.md` |
| mode templates, structures, compression, self-check | `references/style_patterns.md` |

**Aspect ratio.** Follow an explicit ratio, inherit an actual first frame or a confirmed series ratio, else 16:9
without asking. Ask once only when it cannot be inferred and would change references, two-person or group blocking,
full-body action, fight, dance or chase, architecture, landscape or vehicle scale, or a multi-platform master; merge
the question with any other checkpoint.

**Output modes** (templates: `Output Modes` in `references/style_patterns.md`):
- `Concise`: only the final prompt, when the user says so ("just the prompt", "no analysis"); checks still run inside.
- `Workshop` (default): diagnosis, strategy and the deliverable of the current path and stage; never reference
  prompts and a final video prompt together by force.
- `Direction-confirmation`: diagnosis, strategy and the open decision only, when the user asked to confirm direction
  first (a diagnosis inside the finished answer is not that), when core story foundations cannot be inferred and
  invention was not delegated, or when a change would contradict a given identity, relationship, ending, key line,
  hard duration or scope.
- `Continuous short-film`: continuity summary, character bible, scene sheet, references, segmented prompts and
  bridges, for multi-part stories.

**🔴 CHECKPOINT · Direction selection** (direction-confirmation mode only): stop after these and wait for a choice or
delegation; no reference or final prompts meanwhile; never ask again or treat it as image approval.

```text
【Story diagnosis】
...
【Cinematic adaptation strategy】
...
【Directions to confirm】
1. ...
2. ...
```

### Production Path Routing

- Asked for reference images first, or images supplied → Reference-first. Asked for a direct prompt or to skip
  references → Direct. No route question either way.
- Simple single-character, single-location, low-drift scene → Direct by default.
- High drift or reuse cost (period identity or costume, several principals, recurring or topology-critical places,
  strict prop ownership, relationship blocking, product structure, multi-clip continuity) and no route chosen → ask
  once: "For this kind of scene I suggest building reference images first. Reference-first, or the complete video
  prompt directly?" Merge it with a direction checkpoint; never two confirmation rounds. Delegated → Reference-first
  for high drift, Direct for simple scenes.
- Reference-first waits only for unavailable or unreadable required images or a reserved approval. Supplied readable
  images: inspect and proceed. Authorized generation: generate, inspect, continue. A text package asked before images
  exist labels its video draft provisional, never image-verified.

### Steps

1. **Story diagnosis.** The emotional core, visual core, conflict and the strongest filmable moment; the duration
   (never 30 s by default); the structure (`Structure Selection` in `style_patterns.md`); what abstract material
   becomes behaviour, sound, objects or environment; for a source too long for one clip, what this prompt covers and
   what goes to later clips. Optional systems in `style_patterns.md`, only when they fit:
   - `Short-Drama Hook and Narrative Drive Diagnostic` when the user wants a breakout short drama, hook, reversal,
     cliffhanger or serial episode (anomaly, goal, rule or cost, obstacle, reversal, open question as optional
     functions); never for close-ups, atmosphere, product films, action demos or complete plots.
   - `Character Knowledge and Evidence Control` for mystery, reunion, hidden identity or gradual recognition: track
     what the character knows apart from what the audience knows; no reaction to information not yet given.
   - `Retrospective Reversal and Dual-Meaning Montage System` for subjective memory, false perception or an ending
     that reinterprets earlier images: objective truth, perception and audience belief tracked apart; earlier and
     later beats paired; no twist added just to use it.
   - Novel excerpts are source material: find the filmable event, relationship and visible turn; separate inner
     narration, exposition, memory and metaphor.
2. **Adaptation strategy.** Duration, structure and treatment in brief; for novels what is kept, compressed, omitted
   or externalized (the dramatic intention, not the sentence order). Add a short `Lifelike performance handling` note
   when realism is central (motive; eye line, expression, pause, voice, incidental body language, contact,
   environment, camera kept consistent) and a `Dialogue performance control` note for long dialogue, accusation,
   confession, interrogation or a line-triggered turn (purpose, emotion barrier, trigger words, pauses, breath, what
   must not react too early). A missing short-drama function gets one minimal optional repair; never invent a deadly
   rule, reversal, villain or cliffhanger unless asked or delegated. Name creative additions.
3. **Reference images.** Direct path: omit, or one line recommending them. Reference-first: only the missing assets
   of the current stage, consistent with the video prompt (era, palette, light, age, clothing, emotional state, the
   segment's story state). Rules: `Visual Reference Image Prompts` below.
4. **Final video prompt.** One usable prompt. Direct: self-contained with the minimum character, setting, costume,
   prop, light and start-state anchors. Reference-first: compiled from the actual images (their pixels outrank the
   earlier image prompts; a planned detail not visibly confirmed is absent), a compact reference-authority mapping,
   no repeated static description; spend the words on structure, timing, action order, performance change, shot
   development, camera, dialogue and lip-sync, sound, transitions and the ending; a change from a reference is a
   timed delta with cause and end state. Both asked: two labelled prompts, `Reference-driven version` and
   `No-reference direct version`.
   - **Length**, final prompt only (not the plot, diagnosis, strategy or image prompts): ceiling 2000 Chinese
     characters (about 1200 English words) for 1–15 s, 3200 (1900) for 16–24 s, 4000 (2400) for 25–30 s; a ceiling,
     not a target. Usual targets: 800–1300 characters (500–800 words) for 8–15 s; 500–800 (300–500) for one person or
     one action; 1300–2000 (800–1200) for complex 10–15 s; 1600–2600 (1000–1600) for 16–24 s; 2200–3400 (1300–2000)
     for 25–30 s, the upper end only when dialogue, multi-shot progression, a full arc, action geography or
     continuity needs it. Too long: the compression ladder in `style_patterns.md` before proposing a split.
   - Every prompt gets one motivated light sentence and 2–4 concrete sound anchors; more only when light or sound
     carries the turn. Multi-shot, dialogue, suspense, action or continuation prompts may add a compact `Overall sound
     and light` block (placement: `Global Sound and Lighting Baseline` in `style_patterns.md`).
   - Run the `Quality Self-Check` in `style_patterns.md`; print it only for critique or debugging.

No model named: assume a Seedance 2.5 / Kling 3.0 class model that holds long coherent prompts, still choosing the
duration from the story. No separate model line; adapt naturally to a model the user names.

## Execution Gates and Failure Recovery

| Trigger | First response | If it still cannot fit or stabilize |
|---|---|---|
| Story foundation unresolved, not inferable or delegated | One short question on that foundation only | Once answered, choose one interpretation; do not reopen confirmed choices |
| Events cannot play in one 30 s clip | Highlight scope: pick the highlight; full coverage: numbered clips | Full coverage vs a hard single-clip limit: explain and ask which may change; never drop events silently |
| Dialogue dense or timing uncertain | Dialogue playability audit (`style_patterns.md`): local pace, interruption, overlap, pauses, failed starts, listener reactions, ending residue; word counts are risk signals, not deletion rules | Keep key lines; simplify shots, camera, blocking and decoration first; then offer a split or a user-approved line edit |
| Prompt over its ceiling | Compression ladder (`style_patterns.md`) | Simplify decoration; split only within authorized coverage, else ask; keep causality, key dialogue, anchors, final reaction |
| Spatial, prop, costume or emotional continuity uncertain | Reconstruct the last confirmed state; list the minimum anchors | Neutral re-establishing shot or a new clip boundary; never an invisible reset |
| Conflicting camera instructions | Keep the dramatic function; one physically plausible path | Name the one conflict resolved; never stack incompatible moves |
| A reference would add unwanted people or drift | Separate identity, relationship, scene and prop references by purpose | Drop it and restate the anchors in the video prompt |
| Actual images differ from their prompts or are unclear where it matters | The visible image is the truth: list confirmed, absent or unclear, conflicting and contaminated fields | Repair or regenerate, add a dedicated reference, or redesign the action around what is visible |
| A reference has a watermark, logo, garbled text, bad anatomy, crop or obstruction | Flag it before compiling; recommend a clean or cropped asset | A negative prompt does not erase what the reference contains |
| An action may conflict with visible hand position, furniture, reach, clearance, weight, friction or exit | Physical-feasibility audit (`reference_first_video_workflow.md`); rewrite the contact chain | Repair the keyframe, change the blocking or split the action |
| Ratio unspecified and it changes costly references or blocking | One "16:9 or 9:16?" question merged with any checkpoint | Delegated: 16:9 unless a vertical asset or vertical delivery decides |
| 9:16 explicit, inherited or confirmed | Read `vertical_9x16_adaptation.md`; redesign composition, coverage, movement and frames | Group shots, add a vertical keyframe, or a separate vertical adaptation |

**🔴 CHECKPOINT · Adaptation scope conflict:** "full adaptation", "full coverage" or "continuous short film" already
choose full coverage; "pick the strongest segment" chooses highlights; never re-ask. Build the structure, then
deliver unless the user asked for structure or approval first or assets are missing. Pause only for a real scope
conflict (full coverage plus an unworkable single-clip limit); input length alone is never a checkpoint.

## Duration Rules

- Choose by playable content, not text length: count beats, lines, actions, emotional turns, reaction pauses,
  location changes, camera moves and the ending breath. 30 s is the maximum per prompt.
- Under 15 s when it fits (6, 8, 12 s). 16–30 s only for longer dialogue, several people reacting, a complete
  emotional curve, one-take drama blocking, montage progression or a scene that would feel rushed; never stretch a
  simple beat.
- Longer stories keep the requested scope (highlight, causal clip sequence, or a question when hard limits clash).
  Novel excerpts: the workload tiers in `style_patterns.md`, below the requested coverage; a long passage alone needs
  no approval round.
- Past 1300 characters (≤15 s), 2400 (16–24 s) or 3000 (25–30 s, soft; 4000 absolute), every extra detail must
  improve stability, emotional clarity, space, sound or performance timing, or prevent a model failure.
- Leave the reaction and ending breath: key lines or peak action end 1–2 s before the end unless an abrupt end is
  asked for. Time follows dramatic weight; in short prompts cut events before cutting the reaction.
- No fixed dialogue word ceiling: dense, overlapping or urgent dialogue can stay when line order, lip-sync, breaths,
  reactions and the ending still play. Estimate by local pace; simplify camera and secondary action before cutting
  lines; a real conflict is stated, with a split or a question before changing key lines.

## When to Ask Questions

Per the execution decisions: one short question only for an unresolved foundation (who, where, which emotion or
change). Never ask about lens, light, camera, sound, micro-expression or pacing; fill them in. "Create freely" means
no questions.

## Continuation Workflow

When the user says continue, next segment, next shot, "the first is good, write the second", or follows up after
approving a prompt. Rules: `Continuation and Clip-Bridging Workflow`, `Character Consistency Bible` and `Scene Spatial
Continuity Bible` in `references/style_patterns.md`, after `continuity_director_contract.md`. In short:

- Continue from the previous **story state**, not by habit from its tail frame; choose the bridge (new size and
  angle, match on action, or a new shot group for a finished mini-arc). The tail frame only when exact posture,
  blocking, damage or object position matters.
- Keep identity (age, face, hair, clothing, injury or makeup, emotional residue, body position), setting (layout,
  light direction, weather, time, palette, key objects, sound bed) and key props.
- Emotion progresses, never replays (shock → denial, action, numbness, anger or collapse); one main event or turn per
  15 s.
- Restate only the anchors needed; give fresh descriptions and reference prompts only for a new character, place,
  costume or injury state, or key prop; otherwise say to reuse the existing references.
- Continuous short-film mode keeps a character bible and scene sheet with an anchor budget: 4–6 identity anchors for
  the lead, 3–5 for an important supporting character, 4–6 space and light anchors per recurring scene, 1–2 for
  background groups; temporary state (held or placed props, missing accessories, wet or injured, position, travel
  direction, voice, emotional residue) is tracked apart and causally needed state overrides the budget. Trim
  decorative identity before causality, direction, prop state, key dialogue or the ending reaction. Print the bible
  only when it helps.
- A new direction from the user is followed; a bare "continue" takes the most natural consequence.

```text
【Story diagnosis】
Visible change in this segment and duration risk:
【Cinematic adaptation strategy】
Performance, cut points and camera choices:
【Continuation check】
End state of the previous segment:
Emotional progression in the next segment:
Continuity notes:
【Reference asset status】   (only when the path or a new anchor needs it)
Reused / bridge / new character, scene, prop references:
【Final video prompt for the next segment】
Overview:
```

## Output Format

Workshop by default: diagnosis and strategy short and correctable, then the current path's deliverable; no empty
sections.

```text
【Story diagnosis】
Emotional core:
Visual core:
Structure:
Duration:
Trade-offs and additions:
【Cinematic adaptation strategy】
【Final video prompt】
Overview:
```

Reference-first stage 1 replaces the final prompt with 【Reference image plan】 (needed now, not generated separately)
and 【Reference image prompts】 (type and purpose, prompt); after the images exist, use the reference-driven shape in
`reference_first_video_workflow.md`.

Final-prompt components, only those the scene needs: length and structure (in `Overview`, e.g. "an 18-second
continuous emotional dialogue"), related context, shot number or timeline, shot size and focal length, angle and
movement, subject and composition, light and atmosphere, performance, micro-reactions, dialogue / inner monologue /
voice-over, sound design, ending, and negative constraints only for scene-specific risks.

## Cinematic Translation Rules

Before any diagnosis, strategy or prompt, read `references/cinematic_translation_rules.md` (structure choice, shot
ledger, novel excerpts, dialogue, performance, camera, light, sound, length). It applies to every mode.

## Visual Reference Image Prompts

Optional stills that anchor identity, setting, costume, product, props or atmosphere before video; the user may skip
them. How references and video text divide control: `reference_first_video_workflow.md`; field standards, types and
counts: `Visual Reference Image Prompt Patterns` in `style_patterns.md`. Never a full reference set and a full
self-contained video prompt together by default.

- Character references fix identity, not fashion: 4–6 recurring identity or costume anchors plus one emotional
  baseline from the field menu, more only when the current state depends on it. A **single-character reference shows
  only that person**: no other person, hands, hugging, holding, protecting or looking at someone named.
- Scene references: 4–6 topology and light anchors that affect blocking (layout, depth layers, exits, action path,
  obstacles, source light, materials, era, palette); `no people` for a clean plate.
- Key props only when the object drives the story. Most scenes need 1–2 references, complex period, product or large
  scenes 2–3. A relationship / two-shot reference only when height, distance, blocking or chemistry must be
  controlled.
- Continuation or split clips update a reference only when the visible state changes (costume, wet, dusty or injured,
  hair, new prop or place, a clearly different emotional baseline).
- Typical sets: emotional close-up → character; dialogue or intimacy → characters plus scene when space matters;
  product or person texture film → subject plus environment; period drama → costume plus scene; large scene → lead
  plus crowd environment; object-led memory → prop plus scene.

## Anti-Patterns and Red Flags

Do not:
- storyboard prose sentence by sentence or keep exposition with no screen equivalent;
- cram several turns into 30 s or put the key line at the last instant without reaction time;
- replace a plot-changing spoken fact with "the other person delivers the news";
- stack camera moves, lens changes, light jargon, slow motion and cuts without a dramatic job each;
- reset face, costume, injury, held object, screen direction, layout, light or emotional residue between clips;
- produce every reference type by default, or a second person inside a single-character reference;
- repeat full static descriptions in a reference-driven prompt, or treat the first frame as one fixed size, angle and
  composition for the whole clip;
- import a planned object or state the selected image does not clearly show;
- squeeze a horizontal two-shot, group, wide action or landscape into 9:16 without re-blocking;
- treat reference-driven and no-reference prompts as interchangeable;
- use labels like "cinematic feel", "premium look", "epic" instead of concrete action, light source, sound,
  composition and timing;
- hide an overloaded scene in dense fragments to meet the limit: cut events or split.

## Safety and Taste Boundaries

Strong emotion, intimacy, suspense, crime atmosphere and implied danger are fine when handled cinematically. No
explicit sexual content, no sexualized minors, no non-consensual sexual material: rewrite toward tension,
implication, distance or aftermath. No fetishized violence: suspense, consequence, staging and impact, not gore.

## Style Reference

`references/style_patterns.md` holds the house style from user-shared examples; update it when the user shares better
examples and asks to improve the skill. When testing or revising this skill, run the relevant cases in
`references/evaluation_cases.md`; never load it during ordinary prompt writing.
