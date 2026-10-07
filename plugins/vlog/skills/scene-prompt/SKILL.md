---
name: scene-prompt
description: Turn a plot summary, novel excerpt, character relationship or scene idea into a cinematic 6-30 s prompt for AI video models (Seedance, Kling, Veo, Sora, Runway, Jimeng, Hailuo, Wan) — diagnose the story first, then write action, camera, performance, dialogue, light and sound; plan reference images, continue a series and repair failed generations. Use before shooting or generating footage, when the user wants a video prompt or a scene written for an AI video model, or brings back a generated clip that went wrong. Triggers: "viết prompt video", "prompt video AI", "prompt Kling", "prompt Seedance", "prompt Veo", "prompt Sora", "kịch bản cảnh quay", "cảnh điện ảnh", "biến cốt truyện thành video", "viết tiếp đoạn sau", "sửa prompt video", "cinematic video prompt".
---

# Scene prompt

> Based on [cinematic-video-prompt-engineer](https://github.com/CyberJ0605/cinematic-video-prompt-engineer-skill)
> v1.8.0 by CyberJ0605 (MIT, see `LICENSE-upstream`). This copy adds the BashCut notes below and moves
> "Cinematic Translation Rules" into `references/cinematic_translation_rules.md` to fit BashCut's skill size limit;
> the rest is upstream's text, translated from Chinese to English.

## In BashCut

This skill writes text for an AI video or image model; it does not edit the timeline. BashCut gives it to agents
while the `bashcut.vlog` plugin is trusted and turned on. In a vlog it makes the shots the footage lacks (an intro
scene, a b-roll moment, an illustration): `bashcut.vlog:plan` sends you here, and the clip, once generated and placed,
gets the `vlog-disclosure` label ("Ảnh/Video minh hoạ tạo bằng AI").

- **Language.** Talk to the user in their language. The section labels below are English (【Story diagnosis】…); write them
  in the user's language when it is not English (for Vietnamese: 【Chẩn đoán cốt truyện】, 【Chiến lược chuyển thể điện ảnh】,
  【Prompt video cuối cùng】…). Write the final video prompt in the language the user asks for; otherwise in the
  language the target model reads best (Chinese or English for Seedance, Kling, Jimeng, Hailuo, Wan; English for
  Veo, Sora, Runway) and say which one you chose.
- **No generation by default.** Delivering the prompt is the job. Call a video or image generator only when the user
  asks and a tool for it is available; never spend their credits on your own initiative.
- **Bringing the clips in.** When the user has generated clips and wants to edit them, import them with
  `bashcut media import <path> --base-rev <rev>` (rev from `bashcut timeline get`; `--place` also puts them on the
  timeline), check with `bashcut ui frame`, then continue with `bc:edit-workflow` (and `bc:color-grade`,
  `bc:audio-mix`, `bc:captions-text` as needed).
- **Not this skill:** effects, transitions or grading on footage already in BashCut — use `bc:effects` and
  `bc:color-grade`.
- **Series.** For continuation work across sessions, offer to save the character, scene and prop anchors in the
  project memo (`bashcut knowledge memo`) so the next segment can reuse them.

## About this skill

# Cinematic Video Prompt Engineer

This skill turns a user's plot summary, novel excerpt, or scene idea into a cinematic AI video prompt. It does not only decorate text with film words; it first identifies what can be shown in a short video, then translates abstract story into visible action, camera language, performance details, light, sound, and timing.

It can also continue a previous generated segment. When the user asks to continue, extend the story from the prior segment's ending, preserve character/scene/prop continuity, and create new reference-image prompts only for newly introduced characters, locations, products, or key props.

## Execution Decisions and Agent Capabilities

Apply these rules before mode/path-specific checkpoints. They work through ordinary conversation and available attachments; no named agent, special question API, persistent memory, or media-generation tool is required.

1. Read the requested deliverable/stage and explicit constraints, then reuse relevant decisions from the available conversation or supplied handoff. Do not claim to remember unavailable context. Ask only for the missing state needed to continue; "unrelated to the earlier story" (in any language) starts a new story state.
2. Honor an explicit request to discuss, approve, or stop at a stage. Otherwise, reuse an already selected direction, route, ratio, scope, or asset when its controlling conditions have not changed. Resolve `1`, "as suggested", and "continue" (in any language) against the most recent unambiguous pending choice; ask which choice only if more than one remains plausible.
3. Check required evidence and material availability. Missing assets block only dependent work; finish useful independent work already requested. A plain-language question is sufficient when clarification is necessary.
4. Ask only if an unresolved fact cannot be reasonably inferred or supplied through authorized creative discretion, and would change core story facts, a hard constraint, delivery scope, or costly production assets. Genre labels, length alone, multiple valid treatments, and missing ordinary cinematography details are not independent reasons to pause. Select camera, light, performance, and pacing within the brief. Preserve a vague-input question when even the intended event/emotional transformation is unknown and creative control has not been delegated.
5. Approval is object-specific: a direction choice permits that direction, not image approval; a reference-first route permits the asset plan/image prompts, not a generation-service call; selected actual images permit reference-driven writing, not redesign of approved facts; full adaptation requests preserve full coverage, not a highlight-only substitute. Requests to generate/edit actual media authorize only the requested media work within the host's permissions. Never infer publication or unrelated external actions.

### Capability and Completion Boundaries

- The baseline deliverable is text. Distinguish the agent writing the prompt from the video model receiving it; video-model assumptions below do not grant the agent tools or permissions.
- Read supporting files relative to this skill through the host's available resource mechanism. If a needed reference is unavailable, name the missing resource/rule and its effect; do not invent its contents. Continue only portions that do not depend on it.
- Inspect actual images when the host can access and view them. A filename, earlier image prompt, or user description is not a visual inspection. If the host cannot view a required image, identify the specific missing visual facts; offer a provisional description-based draft only if useful, clearly marked as not image-verified. Do not claim a production reference has been inspected or approved by the agent.
- Generate or edit media only when requested/authorized and supported by available tools and host permissions. Otherwise deliver the requested text that can be completed and identify any unfulfilled media action. Do not turn a prompt-only request into a media-generation step. An agent's image inspection does not replace user approval when the user explicitly reserved it.
- Stage-only requests end after that stage. For a complete deliverable, continue through authorized stages once required decisions/assets are available; do not introduce a fresh approval merely because a stage ended. If the host's output/continuation limit forces batching, preserve completed segment numbers, remaining scope, continuity anchors, and the next step; resume when the host permits and never label a partial batch as the whole deliverable.
- Report only the verification actually performed: text self-check, actual image inspection, or actual video-result review. Text quality or a successful tool call alone does not prove generated-image/video quality. No generation tool is required to finish a prompt-only task.

## Continuity and Director Delivery Gate

For continuation, multi-shot reference-driven work, or cut/geometry repairs, read `references/continuity_director_contract.md` before drafting. This contract governs six controls: tail-frame versus first-frame authority and cut auditing; visible-only model instructions; shot-to-reference coverage; visible diagnosis/strategy sections; purposeful camera geometry/lens/depth; motivated camera variety. It overrides older examples that imply copying a tail frame. Run its final delivery gate before responding.

Default workshop and continuation outputs retain concise 【Story diagnosis】 and 【Cinematic adaptation strategy】; repeated revisions do not imply prompt-only mode. Missing new-angle evidence triggers reference prompts before final image-grounded video compilation. Explicit user scope and approval boundaries still apply.

## Default Workflow

Choose an output mode from the user's intent. Default to full workshop mode.

After choosing the output mode, choose one production path: `Direct video path` or `Reference-first path`. Do not merge both into one universal prompt. Use the direct path for a self-contained video prompt; use the reference-first path as a staged workflow whose later video prompt assumes approved/generated reference images. Read `references/reference_first_video_workflow.md` only when references are requested, supplied, or materially useful.

If the user asks to continue, use the continuation workflow instead of the standard first-segment workflow.

If the user provides or describes a generated video result and asks to fix it, use `Generated-Result Surgical Repair` in `references/style_patterns.md`: diagnose the result-to-intent gap, lock successful elements, and change only the failed control unless the underlying shot structure is unsound.

For generated-video attribution, or an emotional true one-take involving near/far attention, approaching characters or shared-object contact, also read `references/one_take_emotional_coverage.md`. Audit readable emotional coverage, world-space facing/gaze, contact ownership and camera travel time; distinguish framing, zoom and focus transfer. Do not impose elaborate movement on simple or deliberately locked shots.

If the user provides or describes a generated reference image and asks to fix it, use `Reference Image Result Repair` in `references/reference_first_video_workflow.md`: preserve approved visual facts, change only the failed field and its physical dependents, and do not redesign the asset from scratch unless the failure is foundational.

When camera movement materially affects storytelling, the user requests a specific move, or the shot needs more precise start/path/speed/end control, read `references/camera_movement_prompt_library.md`. Select by dramatic function and adapt only the needed module; do not load all 46 movements into the output.

When a named emotion, emotional transition, close performance, dialogue barrier, concealment, or reaction beat needs more observable acting detail, read `references/emotion_performance_prompt_library.md`. Select one nearest base emotion, keep only 2-4 useful signals, and adapt them to the character rather than copying a complete stock expression.

Resolve aspect ratio without adding routine friction. Follow an explicit ratio, inherit the actual first-frame/approved continuation ratio, and preserve a confirmed series ratio. If nothing indicates otherwise, default ordinary low-risk work to `16:9 landscape` without asking. Ask once only when the ratio cannot be inferred and would materially change production references, two-person/group blocking, full-body action, fight/dance/chase, architecture/landscape/vehicle scale, or a multi-platform master; merge the question with any existing direction or production-path checkpoint. When vertical/portrait/`9:16` is selected, read `references/vertical_9x16_adaptation.md` and recompose for the narrow frame rather than cropping horizontal grammar.

Output modes:

- `Concise mode`: final video prompt only; use only when the user explicitly says "just give me the prompt", "no analysis", "only the finished prompt", "output only the final prompt", or "concise mode" (in any language).
- `Workshop mode`: diagnosis, strategy, and the deliverable for the current production path/stage; default for ordinary creation and revision. Do not force reference prompts and a final video prompt into the same response.
- `Direction-confirmation mode`: diagnosis, strategy, and the specific unresolved decision only; use when the execution rules above require clarification or the user explicitly reserved approval.
- `Continuous short-film mode`: continuity summary, character bible, scene continuity sheet, references, segmented/continued prompts, and clip-bridging instructions; use for multi-part stories or repeated continuation.

Use `Direction-confirmation mode` only when:

- The user explicitly asks to discuss/confirm direction or strategy before the deliverable. A request for diagnosis as part of the finished answer does not alone reserve a separate approval turn.
- Core story foundations cannot be inferred within the brief and creative invention has not been delegated.
- A proposed change would contradict a specified identity, relationship, ending, key line, hard duration, or delivery scope, and the conflict cannot be resolved within the current authorization.

**🔴 CHECKPOINT · Direction selection:** In `Direction-confirmation mode`, stop after the following sections and wait for the user's choice or explicit delegation:

```text
【Story diagnosis】
...

【Cinematic adaptation strategy】
...

【Directions to confirm】
1. ...
2. ...
3. ...
```

While this direction decision is unresolved, do not output reference prompts or the final video prompt. Once the user selects or delegates that decision, continue with the deliverable for the chosen production path and actual asset state. Do not ask the same question again or treat direction approval as image approval.

### Production Path Routing

- If the user explicitly asks to generate reference images first or use supplied images, choose `Reference-first path` without another route question.
- If the user explicitly asks for a direct/final video prompt or says to skip reference images, choose `Direct video path` without another route question.
- For a simple single-character, single-location, low-drift scene, default to `Direct video path`; do not add a route checkpoint merely because a reference image could help.
- If the task has high visual-drift or reuse cost—period identity/costume, several principal characters, several recurring or topology-critical locations, strict prop ownership, relationship blocking, product structure, or multi-clip continuity—and the user has not chosen a route, ask once: `For this kind of scene I suggest building reference images first. Do you want to go reference-first, or generate the complete video prompt directly?`
- Combine this choice with an existing direction-selection checkpoint when both apply. Do not create two consecutive confirmation rounds.
- If the user delegates the decision, choose `Reference-first path` for the high-drift cases above and `Direct video path` for simple low-drift scenes.

In `Reference-first path`, wait only when required actual images are unavailable/unreadable or the user reserved an image-approval step. If images are already supplied, selected, and readable, inspect them and proceed without repeating Stage 1. If actual generation and continuation are authorized, use available tools, inspect results, and continue unless user approval was reserved. If the user requests a complete text package before images exist, label the later video draft as provisional and not compiled from actual images; never invent image verification.

1. **Story diagnosis**
   - Identify the emotional core, visual core, conflict relationship, and the strongest filmable moment.
   - When the user explicitly wants a breakout short drama, strong hook, suspense reversal, cliffhanger, serial episode, or plot-driven high-concept scene, run the `Short-Drama Hook and Narrative Drive Diagnostic` in `references/style_patterns.md`. Check anomaly, immediate goal, rule/cost, active obstacle, information reversal, and unresolved question as optional functions, not mandatory ingredients. Do not apply this formula by default to emotional close-ups, atmosphere pieces, product films, action demonstrations, or already complete plots.
   - For mystery, reunion, time displacement, hidden identity, delayed recognition, or any scene where a character learns the truth gradually, track character knowledge separately from audience knowledge. Use the `Character Knowledge and Evidence Control` system in `references/style_patterns.md`: preserve what the character already knows, what new evidence they observe, what they may reasonably infer, and what must remain unknown. Do not let a character react to information the screenplay has not yet made available to them.
   - For subjective memory, hallucination, deceptive montage, false perception, or an ending designed to reinterpret earlier images or sounds, use the `Retrospective Reversal and Dual-Meaning Montage System` in `references/style_patterns.md`. Track objective truth, character perception, and audience belief separately; pair earlier and later beats through action, composition, motion direction, contact, or sound; and reveal enough final evidence to change the earlier meaning without explanatory narration. Do not force this system onto ordinary emotional scenes or add an unsupported twist merely to use it.
   - If the input is a novel excerpt, treat it as source material rather than translating it sentence by sentence: identify the filmable main event, character relationship, visible emotional turn, and the parts that are internal narration, exposition, memory, metaphor, or authorial description.
   - Decide the duration needed for the prompt. Do not default to 30 seconds.
   - Decide the best structure using the structure selection table in `references/style_patterns.md`: single take, multi-shot sequence, jump cuts, montage, continuous action editing, dialogue cross-cutting, close-up micro-expression, product/person texture film, large-scene compression, or another fitting form.
   - Note what abstract material must be translated into visible behavior, sound, objects, or environmental motion.
   - If the source is too long for one video, state what this prompt will cover and what should be split into later clips.

2. **Cinematic adaptation strategy**
   - Briefly explain the chosen duration, structure, and cinematic treatment.
   - For novel excerpts, state what is preserved, compressed, omitted, or externalized. Preserve the dramatic intention, not the original sentence order.
   - If human performance realism is central, add a compact `Lifelike performance handling` note: name the character's psychological motive and how eye line, expression, pause, voice, incidental body language, contact, environment response, and camera conditions should stay consistent.
   - If the scene depends on long dialogue, accusation, confession, breakup, interrogation, rebuttal, apology, or a line-triggered emotional turn, add a compact `Dialogue performance control` note: state the character's purpose, emotion barrier, trigger words, pauses, breath, facial/body changes, and what reaction must not happen too early.
   - If the short-drama diagnostic finds a missing narrative function, name the gap and propose one minimal optional repair. Do not silently invent a deadly rule, identity reversal, hidden villain, or cliffhanger unless the user asked for stronger short-drama writing or delegated creative control. Preserve a complete supplied plot instead of rewriting it toward a formula.
   - Mention any creative additions if the user gave permission or the missing details are technical rather than foundational.

3. **Reference images to generate first**
   - In `Direct video path`, omit this section by default. A brief optional recommendation is enough when references would improve control; do not also dump full image prompts unless the user asks.
   - In `Reference-first path`, provide only missing asset planning/image prompts for the requested stage. Apply the availability and approval conditions in `Production Path Routing`; skip asset creation for usable, selected images already supplied.
   - Usually include only the needed anchors: character, scene, key prop, product, costume, or atmosphere. Do not force all categories.
   - Keep reference-image prompts consistent with the final video prompt: same era, color palette, lighting, environment, character age, clothing, and emotional state.
   - When outputting reference-image prompts, write them at a complete production-control level: enough to directly generate usable character/scene/prop reference images. Match clothing, appearance, damage, makeup, emotional baseline, environment, and lighting to the current segment's story state rather than using a generic template.
   - For a single-character reference, describe only that one character. Do not include other characters, relationship interactions, another person's body parts, or phrases that may cause extra people to appear. Use a separate relationship/two-shot reference only when a combined blocking reference is truly needed.

4. **Final video prompt**
   - Output one directly usable prompt.
   - In `Direct video path`, make it self-contained: include the minimum character, setting, costume, prop, light, and start-state anchors needed to work without images.
   - In `Reference-first path`, compile it from the actual approved/generated images. The pixels in the selected images outrank their earlier image prompts: do not treat a planned prop, costume detail, pose, or layout as present unless it is visibly confirmed. Do not repeat full static descriptions. State a compact reference-authority mapping, then prioritize story structure, duration, action order, performance change, shot-size/angle development, camera movement, dialogue/lip-sync, sound, transitions, and ending state. Describe any intended change from a reference as an explicit timed delta with cause and final state.
   - If the user asks for both forms, label and output two distinct prompts: `Reference-driven version` and `No-reference direct version`. Do not make one ambiguous prompt serve both purposes.
   - Keep only the final prompt within the duration-based ceiling when possible: 2000 Chinese characters (about 1200 English words) for 1-15s prompts, 3200 (about 1900 words) for 16-24s prompts, and 4000 (about 2400 words) for 25-30s prompts. This limit does not include the user's original plot, `Story diagnosis`, `Cinematic adaptation strategy`, or optional reference-image prompts. Do not treat the ceiling as a target length.
   - Default final-prompt target: 800-1300 Chinese characters (about 500-800 English words) for most 8-15s prompts. Use 500-800 characters (300-500 words) for simple one-person or one-action scenes and 1300-2000 characters (800-1200 words) for complex 10-15s scenes. For longer scenes, target 1600-2600 characters (1000-1600 words) for 16-24s and 2200-3400 characters (1300-2000 words) for 25-30s. Use the upper end only when longer dialogue, multi-shot progression, a complete emotional arc, action geography, or continuity control genuinely needs it.
   - If the draft is too long, apply the automatic compression ladder in `references/style_patterns.md` before recommending a split.
   - Write the final prompt in the language chosen under "In BashCut" › Language (Chinese or English for Seedance, Kling, Jimeng, Hailuo and Wan; English for Veo, Sora and Runway). Standardized cinematography abbreviations and professional camera/lens/focus terms stay in English in either language when they improve precision, such as `ECU`, `CU`, `MS`, `MLS`, `Dolly In/Out`, `Pan Right/Left`, `Tilt Up/Down`, `Track Right/Left`, `Rack Focus`, `35mm`, or `Handheld`. Write action, emotion, performance, lighting effect, sound, causality, and story instructions in the chosen language, adapted to the scene; do not paste the reference libraries' sentences verbatim into the final prompt.
   - Give every final prompt a compact, motivated light baseline and a concrete sound bed. Most scenes need one scene-level light sentence and 2-4 sound anchors; expand only when light or sound carries the dramatic turn. For multi-shot, dialogue-led, suspense, action, or continuation prompts, add a compact `Overall sound and light` block when it improves continuity. Follow the placement hierarchy in `references/style_patterns.md`.
   - Before responding, run the quality self-check in `references/style_patterns.md`. Do not print the checklist unless the user asks for critique or debugging.

When the user does not specify a model, assume a high-capability Seedance 2.5 / Kling 3.0 class video model that can support longer coherent prompts, but still choose duration from the story rather than defaulting to 30s. Do not add a separate generic model field. This skill does not maintain separate model-adaptation branches for now.

## Execution Gates and Failure Recovery

Resolve the following conditions before writing the final prompt:

| Trigger | First response | If it still cannot fit or stabilize |
|---|---|---|
| A story foundation is unresolved and cannot be inferred or chosen within delegated creative control | Ask one concise question covering only that missing foundation | Once resolved or delegated, choose one coherent interpretation and proceed; do not restart other confirmed choices |
| The requested events cannot play within one 30-second clip | Preserve the requested coverage: select a highlight only for highlight scope; use numbered clips for full coverage | If full coverage and a hard single-clip limit conflict, explain the concrete conflict and ask which constraint may change; do not silently omit events |
| Dialogue timing is dense or uncertain | Run a dialogue playability audit: judge local speaking pace, interruption, overlap, pauses, failed starts, listener reactions, and ending residue; word count and average speech rate are risk signals, not automatic deletion rules | If the intended performance still cannot complete naturally, preserve key lines and first simplify shots, camera, blocking, and decorative detail; then explain the conflict and offer a split or user-approved line edit instead of silently deleting dialogue or forcing an unnatural delivery |
| The final prompt exceeds the duration-based ceiling | Apply the compression ladder in `references/style_patterns.md` | Simplify decorative shots/actions; split only within authorized coverage and clip constraints, otherwise ask about that conflict. Preserve causality, key dialogue, continuity anchors, and the final reaction |
| Spatial, prop, costume, or emotional continuity is uncertain | Reconstruct the last confirmed state and list the minimum continuity anchors | Use a neutral re-establishing shot or a new clip boundary; do not invent an invisible reset |
| The user requests conflicting camera instructions | Preserve the requested dramatic function and choose one physically plausible camera path | State the single conflict that was resolved; do not stack incompatible moves |
| A requested reference image would introduce unwanted people or visual drift | Separate identity, relationship, scene, and prop references by production purpose | Omit the unnecessary reference and restate the stable visual anchors inside the video prompt |
| Actual reference images differ from their original prompts or contain unclear story-critical details | Treat the visible image as the source of truth; inventory confirmed, absent/unclear, conflicting, and contaminated fields | Repair/regenerate the asset, add a compatible dedicated reference, or redesign the action around what is visibly present; do not silently inherit the plan |
| A supplied reference contains a watermark, logo, garbled text, malformed anatomy, crop, or obstruction likely to propagate | Flag the issue before compiling the production prompt and recommend a clean, repaired, or cropped asset | Do not rely on a negative prompt to erase content already embedded in the reference |
| A reference-driven action may conflict with the visible hand position, furniture, reach, clearance, weight, friction, or exit path | Run the physical-feasibility audit in `references/reference_first_video_workflow.md` and rewrite the contact/action chain | If the motion cannot be made credible from the selected image, repair the keyframe, change the blocking, or split the action |
| Aspect ratio is unspecified and would materially change expensive reference generation or complex blocking | Combine one `16:9 landscape or 9:16 vertical?` question with any existing checkpoint | If the user delegates, default to 16:9 unless an actual vertical production asset or explicit vertical delivery context controls the choice |
| Vertical/9:16 output is explicit, inherited, or confirmed | Read `references/vertical_9x16_adaptation.md`; redesign composition, coverage, movement, and reference frames for a narrow canvas | Simplify/group shots, add a vertical keyframe, or make a separate vertical adaptation if essential width cannot survive |

**🔴 CHECKPOINT · Adaptation scope conflict:** "full adaptation" / "full coverage" / "continuous short film" already select full coverage; "pick the strongest segment" selects highlights. Do not re-ask that choice. Build the appropriate structure before detailed prompts, then continue the requested deliverable unless the user requested structure-only/approval-first or required assets are missing. Pause only for an unresolved material scope conflict, such as full coverage plus an unworkable hard single-clip limit. Input length alone is not a checkpoint.

## Duration Rules

- Choose the duration from the story content. Maximum single prompt duration is 30 seconds.
- Evaluate duration by playable screen content, not by text length alone. Count the number of plot beats, dialogue lines, physical actions, emotional turns, reaction pauses, scene/location changes, camera moves, and ending breath. A short user description may still require multiple segments if the full action or emotional progression cannot play naturally in one clip.
- If the scene can be fully shown in less than 15 seconds, use the actual duration, such as 6s, 8s, or 12s.
- Use 16-30 seconds only when the content benefits from the extra duration: longer dialogue, multi-person reactions, a complete emotional curve, ordinary drama one-take blocking, montage progression, or a scene that would feel rushed in 15 seconds. Do not stretch a simple beat to 30 seconds.
- If the story exceeds what 30 seconds can carry, preserve the requested scope using the adaptation rules above: one selected scene for a highlight, a causal clip sequence for full coverage, or a concrete question when hard constraints conflict.
- For novel excerpts, use the workload tiers in `references/style_patterns.md`, subordinate to requested coverage. A short passage may need multiple clips; a long passage does not by itself require an approval round. Establish the selected scene or continuous structure first, then deliver the requested prompts while preserving cause and effect.
- If a complete treatment would require more than the duration-based character ceiling, recommend splitting into multiple prompts; each prompt should stay under its own ceiling.
- If a final prompt exceeds 1300 characters for <=15s, 2400 characters for 16-24s, or 3000 characters for 25-30s, every extra detail should improve generation stability, emotional clarity, spatial continuity, sound/performance timing, or model failure prevention. Treat 3000 characters as a soft threshold for 25-30s prompts and 4000 as the absolute ceiling; remove decorative detail that does not help the video render.
- Leave enough time for reaction and ending breath. Do not place a critical line or action at the final instant and then cut immediately unless the user specifically asks for an abrupt ending. Prefer ending key dialogue or peak action at least 1-2 seconds before the end, then use the remaining time for facial reaction, sound decay, stillness, movement continuation, or a visual afterimage.
- Allocate shot duration by dramatic weight. Give setup, turn, reaction, and aftertaste enough space; do not divide time mechanically. In short prompts, reduce event count before stealing time from the emotional reaction.
- Do not enforce a fixed dialogue word-count ceiling. High-density dialogue can remain intact when rapid speech, interruption, overlap, or emotional urgency is the intended performance and the full line order, lip-sync, breaths, reactions, and ending can still play. Estimate delivery by local pace and simultaneous speech, not one global words-per-minute number. If dialogue is important but dense, simplify camera and secondary action before proposing cuts; if a real timing conflict remains, state it and recommend splitting or ask before changing key lines.

## When to Ask Questions

Apply `Execution Decisions and Agent Capabilities`. Ask one concise question only when a necessary story foundation remains unresolved after checking the brief and delegated creative control, for example:

- Who is the main character?
- Where does the scene happen?
- What emotion or transformation should the scene express?

Do not ask for missing technical details such as lens, lighting, camera movement, sound, micro-expression, or pacing. Fill those in cinematically. If the user says to freely create, do not ask.

## Continuation Workflow

Use this when the user says (in any language) "continue", "keep writing", "carry on from the last one", "next segment", "next shot", "continue from the last one's last frame", "the first one is good, write the second", or gives a follow-up after approving the previous prompt.

Continuation is not a new unrelated prompt. It must preserve continuity and move the story forward.

Default continuation format; include the reference-assets block only when the chosen path or a new/updated visual anchor needs it:

```text
【Story diagnosis】
Visible change in this segment and duration risk:

【Cinematic adaptation strategy】
Performance, cut points and camera choices:

【Continuation check】
End state of the previous segment:
Emotional progression in the next segment:
Continuity notes:

【Reference asset status】
Reused character/scene/prop references from the previous segment:
How this segment bridges:
New character reference images:
New scene reference images:
New key prop reference images:

【Final video prompt for the next segment】
Overview:
...
```

Rules:

- Continue from the previous segment's story state, not necessarily from the exact previous tail frame. Preserve continuity, but choose a natural bridge: different shot size/angle for continuous drama, match-on-action for unfinished movement, or a complete new 15s shot group when the previous segment already has a finished mini-arc.
- Preserve identity: same character age, face, hairstyle, clothing, injury/makeup state, emotional residue, and body position when relevant.
- Preserve setting: same location layout, lighting direction, weather, time of day, color palette, important furniture/vehicles/objects, and sound bed.
- Preserve key props: phone, letter, cup, car, music box, sword, old sweater, ring, document, weapon, etc.
- For continuous novel adaptation, avoid repeating full character and scene descriptions in every segment when they are unchanged. Instead, state the previous story state and chosen bridge, then only restate the identity, costume, setting, and prop anchors needed for stability. If a new character appears, the scene changes, the character changes clothing/makeup/injury state, or a new key prop becomes narratively important, give a fresh concise description and, when useful, a new reference-image prompt.
- Emotion should progress, not restart. If the previous segment ended in shock, the next can move into denial, action, numbness, anger, or collapse; it should not replay the same discovery.
- Each new 15s continuation should add only one main event or emotional turn.
- If the next segment introduces a new character, location, product, costume state, or key prop, add a corresponding new reference-image prompt. If no new visual anchor appears, say to reuse existing character/scene/prop references; use the previous tail frame only when exact body position or action continuity is genuinely needed.
- In continuous-short-film mode, maintain an internal character bible and scene continuity sheet with an anchor budget: keep 4-6 stable identity anchors for the main character, 3-5 for an important supporting character, 4-6 spatial/light anchors for each recurring scene, and 1-2 group-level anchors for background people. Track temporary story state separately, including held/placed props, missing accessories, wetness/injury, body position, travel direction, voice condition, and emotional residue. Causally necessary state overrides the numeric budget. Repeat only the anchors visible or relevant in the current shot; when the prompt becomes crowded, remove decorative identity detail before action causality, spatial direction, prop state, key dialogue, or the ending reaction. Print compact bible/sheet versions only when they help the user generate multiple segments consistently.
- If the user provides a new direction for the continuation, follow it. If the user only says "continue", infer the most natural emotional consequence and proceed.
- Keep the next final prompt under the normal length targets and 30s maximum.

## Output Format

Default format is workshop mode. Keep diagnosis and strategy visible so the user can correct the interpretation before reusing the production deliverable. Keep these sections concise. The chosen production path determines what follows: a direct-video prompt, or the current reference-first stage. Do not show empty sections.

For detailed mode selection and templates, use `Output Modes` in `references/style_patterns.md`.

Direct-video workshop format:

```text
【Story diagnosis】
Emotional core:
Visual core:
Structure:
Duration:
Trade-offs and additions:

【Cinematic adaptation strategy】
...

【Final video prompt】
Overview:
...
```

Reference-first Stage 1 format:

```text
【Story diagnosis】
...

【Cinematic adaptation strategy】
...

【Reference image plan】
Needed at this stage:
Not generated separately:

【Reference image prompts】
Reference image 1 | Type and purpose:
Prompt:
```

After the actual images are generated, selected, or supplied, use the reference-driven prompt shape in `references/reference_first_video_workflow.md`.

For the final prompt, include the sections that matter for the scene. Do not force every label if it makes the prompt bloated. Use negative constraints selectively: choose only the scene-specific risks that are likely to harm generation, instead of repeating a long generic list.

Useful final-prompt components:

- Length and structure
- Overview
- Related context
- Shot number / timeline
- Shot size and focal length
- Camera angle and movement
- Subject and composition
- Light and atmosphere
- Character performance
- Micro-reactions / physiological reactions
- Dialogue lines / inner monologue / voice-over
- Sound design
- Ending
- Negative constraints, only when needed

Do not include a separate `Video model` line by default. If the user specifies a model, adapt the prompt to it naturally. Put duration and structure into `Overview`, for example: `Overview: this is an 18-second continuous emotional dialogue...`.

## Cinematic Translation Rules

Before drafting any diagnosis, strategy or prompt, read `references/cinematic_translation_rules.md`: structure choice, shot ledger, novel excerpts, dialogue, performance, camera, light, sound and prompt-length rules. They apply to every output mode.

## Visual Reference Image Prompts

Offer optional reference-image prompts when they help control identity, setting, costume, product, props, or atmosphere. These are for generating still images first, then using them as references with the video prompt.

For route selection, staged delivery, reference authority, static-information deduplication, and image-to-video compilation, read `references/reference_first_video_workflow.md`. The rules below define reference content; that file defines how references and video text divide control.

- Make it clear the user can either generate reference images first or skip directly to video generation.
- Do not output a complete reference set and a complete self-contained video prompt together by default. Keep the current turn scoped to the chosen production path and stage.
- Character references should stabilize identity, not look like fashion posters. Treat identity/role, age range, era, facial impression, body type/posture, hair, clothing/costume state, dirt/wetness/injury/makeup, emotional baseline, framing, light/background, and non-stylization as a candidate field menu, not a completeness checklist. Select 4-6 recurring identity/costume anchors plus one emotional baseline; add a field only when the current production state genuinely depends on it. A single-character reference must contain only that character; do not mention a child, parent, lover, enemy, partner, crowd, hand holding, hugging, protecting another person, or any other visible person.
- Scene references should define usable video space with 4-6 topology/light anchors: select only the location relationships, foreground/midground/background, entrances/exits, action path, obstacles, source light, materials, era, palette, atmosphere, or action area that affect later blocking and continuity. These are candidate fields, not a checklist. Use `no people` if the scene reference should be clean.
- Key prop references should be used only when the object drives the story: old sweater, music box, letter, phone, car, sword, cup, ring.
- Do not create too many references. Most scenes need 1-2. Complex historical, product, or large-scene prompts may need 2-3.
- Keep all references consistent with the final video prompt.
- Select reference type by production need: identity reference, relationship/two-shot reference, clean scene plate, key prop/product reference, or first/tail-frame reference. Do not output every type by default. If two characters must appear together to control height, distance, blocking, or chemistry, use `relationship/two-shot reference`; do not hide that relationship inside a single-character reference.
- For continuation or split clips, update references only when the visible state changes: new costume, wet/dusty/bloody-but-non-gory state, injury, hairstyle change, new prop, new location, or a meaningfully different emotional baseline. Otherwise reuse existing references and restate only the minimum current-state anchor.

Recommended counts:

- Emotional close-up: character reference only.
- Dialogue or intimacy scene: character references plus scene reference if identity and space matter.
- Product/person texture film: product/person reference plus environment reference.
- Period drama: character/costume reference plus scene reference.
- Large scene: main character reference plus scene/crowd environment reference.
- Object-led memory scene: key prop reference plus scene reference.

## Anti-Patterns and Red Flags

Do not:

- turn prose into a sentence-by-sentence storyboard or preserve exposition that has no visible screen equivalent
- cram several dramatic turns into one 30-second prompt or place the key line at the final instant without reaction time
- use vague substitutions such as “the other person delivers the bad news” when the spoken fact changes the plot
- stack camera moves, lens changes, lighting jargon, slow motion, and cuts without assigning each one a dramatic function
- reset a character's face, costume, injury, held object, screen direction, location layout, lighting state, or emotional residue between clips
- create every possible reference-image type by default, or put a second person inside a single-character identity reference
- repeat full face, costume, setting, palette, and lighting descriptions inside a reference-driven video prompt; retain only compact reference bindings and story-required timed changes
- treat the first-frame reference as a command to preserve one shot size, one angle, and one composition for the entire clip when the story needs motivated coverage or camera development
- import a planned object or state from the earlier image prompt after the actual selected reference failed to show it clearly
- squeeze a horizontal two-shot, group tableau, wide action, or landscape into 9:16 without re-blocking, shot separation, or a deliberate vertical composition
- treat a reference-driven prompt and a no-reference prompt as interchangeable when one omits static visual information
- use generic labels such as `cinematic feel`, `premium look`, `epic feel`, or `maxed-out atmosphere` in place of concrete action, light source, sound, composition, and timing
- hide an overloaded scene inside dense fragments merely to stay under the character limit; reduce events or split the scene instead

## Safety and Taste Boundaries

- Strong emotion, intimacy, suspense, crime atmosphere, psychological pressure, and implied danger are allowed when handled cinematically.
- Do not generate explicit sexual content, sexualized minors, or non-consensual sexual material.
- If a user asks for unsafe sexual content, rewrite toward psychological tension, implication, distance, aftermath, or non-explicit emotional conflict.
- Avoid fetishized violence. For violent scenes, focus on suspense, consequence, staging, and emotional impact rather than gore.

## Style Reference

When more guidance is needed, read `references/style_patterns.md`. It contains the evolving house style extracted from user-provided cinematic prompt examples. Update that reference when the user shares better prompt examples and asks to improve the skill.

When testing, reviewing, or revising this skill, read `references/evaluation_cases.md` and run the relevant cases. Do not load the evaluation set during ordinary prompt generation.
