# Reference-First Video Workflow

Read this file only when the user requests reference images, supplies reference images, or the production-path router identifies a high-drift task where references materially improve control.

## Purpose

Separate static visual design from temporal video direction. A reference-first workflow should reduce ambiguity in the video prompt, not append image prompts to an already complete direct-video prompt.

Use two distinct compiled outputs:

- `No-reference direct version`: self-contained text-to-video prompt with the necessary static and dynamic information.
- `Reference-driven version`: image-to-video prompt bound to actual selected images; static descriptions are minimized and temporal instructions carry the detail.

Do not try to make one prompt optimal for both modes.

## Stage 1: Reference Asset Plan

Resolve the target aspect ratio before creating composition-controlling production assets. Follow an explicit ratio, inherit an approved first frame/previous clip, and preserve a confirmed series ratio. If ratio is unspecified and would materially change costly relationship, scene, first/tail-frame, group, full-body action, or large-scale assets, combine one aspect-ratio question with any existing direction/production-path checkpoint. For vertical production, read `vertical_9x16_adaptation.md`.

First classify every supplied or planned image by source and authority:

- `Inspiration reference image`: an external still, photograph, painting, mood board, or user-provided style example used to abstract one or a few declared dimensions such as composition method, color logic, material mood, or subject direction. It is not automatically authoritative for identity, exact blocking, scene topology, or story action. Do not copy a recognizable shot, cast arrangement, prop combination, or complete visual design.
- `Production asset reference image`: an approved/generated character, wardrobe, location, prop, product, or vehicle asset intended to lock the named static facts across generation.
- `State/first-frame reference image`: an approved image intended to lock the current pose, screen positions, contact, prop state, or opening composition for one clip. It does not control later movement, performance change, or camera development unless explicitly assigned.

If the user's intent is ambiguous, treat external inspiration as inspiration rather than a production lock. A production image may serve several compatible fields only when they do not conflict, but still state its authority explicitly.

All instructions below to generate, regenerate, repair, or add a reference mean execute only when actual media work is authorized and supported; otherwise provide the appropriate image prompt/repair recommendation and identify the unresolved asset dependency.

Before writing image prompts, identify the visual facts that are expensive to let drift:

- recurring principal identity and costume state
- recurring or topology-critical location
- relationship geometry that affects blocking, height, distance, or contact
- exact product, vehicle, or story-critical prop structure
- exact first frame only when the opening composition must be tightly controlled

Choose the smallest asset set that solves those risks. Do not create one reference per named person, room, or object mechanically.

- Give recurring principal characters individual identity references.
- Keep one-off supporting characters inside a relationship/keyframe image or the video prompt unless their identity must recur.
- Use a clean scene plate for recurring locations or spaces whose entrances, exits, depth, or action path matter.
- Use a relationship/two-shot reference only when shared blocking or chemistry is generation-critical.
- Use a prop/product reference only when its design, ownership, readable marking, or state carries the story.
- Most generation stages should use 1-3 active references. If more assets are genuinely needed for a series, output an asset plan and generate them in batches rather than dumping every prompt at once.

Stage 1 output:

```text
【Reference image plan】
Needed at this stage: ...
Not generated separately: ... (reason)

【Reference image prompts】
Reference image 1 | Type and purpose: ...
Prompt: ...
```

Follow `Execution Decisions and Agent Capabilities` and `Production Path Routing` in `../SKILL.md`. Stage 1 is complete when the requested asset plan/prompts are delivered, but it is not completion of a requested reference-driven video prompt. Wait only for missing/unreadable required images or an explicitly reserved image approval. Selected, readable images skip this wait and proceed to inspection. Authorized tool-based generation may continue after inspection unless user approval was reserved. Without image-viewing capability, identify the needed visual facts and any provisional text work; never claim to have inspected pixels. Image prompts are design intent, not evidence of the generated result.

For `9:16 vertical`, create composition-controlling assets—blocking scene plates, relationship/two-shots, first/tail frames, and ordered keyframes—in the target ratio. Identity or isolated prop references may use another practical ratio only when they are attribute references and crop-safe; any literal first/last frame must match 9:16, and first/last frames must match each other. Do not treat a side-cropped horizontal frame as a valid vertical keyframe until people, hands, props, exits, light source, and action path have been inspected and deliberately recomposed.

## Reference Image Prompt Compiler

Compile each image prompt in this order, omitting fields that do not serve that asset:

1. image type and single production purpose
2. only the stable anchors controlled by that image
3. neutral baseline or one current visible state/action
4. physically possible camera witness position, height, distance, and subject scale when composition matters
5. visual center and decisive foreground/midground/background relationships when space or blocking matters
6. one motivated primary light source and only necessary practical fill/reflection; tie color to real sources
7. material behavior that affects continuity, such as layer, weight, wear, wetness, reflectivity, or contact
8. a short scene-specific exclusion list

Prefer specific nouns, physical relationships, and source-based light over generic labels such as `cinematic`, `premium look`, `epic`, `masterpiece`, `8K`, or `highly detailed`. The image should remain specific after generic quality words are removed. Unless the user explicitly requests a turnaround, contact sheet, collage, or storyboard, request one standalone frame and one composition; do not ask the image model to place several views or several reference types on one canvas. Do not impose a universal aspect ratio or English-only prompt format.

Use type-specific information budgets as selection gates rather than one template for every image. The listed fields are maxima and candidate categories, not a requirement to fill every slot. Keep the exclusion list to the few likely failures for that asset—normally 3-6 failure classes—and remove generic negatives that do not protect production use.

- `Character look reference`: keep 4-6 stable identity/costume anchors plus one readable emotional baseline. Use a neutral, current-state posture; no story interaction, second person, relationship action, or elaborate narrative background. If costume construction is critical, describe visible layers, fasteners, material, fit, and current wear state, but remove decorative details that will not recur.
- `Empty scene plate`: keep 4-6 topology/light anchors, one main source-light rule, and 2-3 causal environmental traces that reveal age, use, weather, or a recent event. Clarify entrances, exits, depth, action path, and obstacles; use `no people` when a clean plate is required. Do not clutter the room with objects that do not affect later blocking or story.
- `Two-person relationship image`: lock one relationship axis, screen-left/right positions, height/distance, eye lines, and one contact or no-contact state. Choose one visual center and one composition decision produced by the relationship pressure; do not turn it into two independent fashion portraits.
- `First-frame/keyframe image`: use one main action state, one secondary story clue, one principal composition decision, one motivated primary light source, and 2-3 decisive environment facts. A keyframe may imply what just happened and what may happen next, but should not try to depict several time beats at once.
- `Key prop/product image`: lock identity, scale, material, orientation, readable marking when essential, wear/state, owner or placement when relevant, and one clear viewing angle. Do not add a decorative story scene unless context is required to judge scale or use.

For relationship and keyframe composition, decide internally:

- who looks at whom and who knows more
- which person, object, boundary, or empty space carries the pressure
- where the viewer is physically placed
- where the eye enters, what slows or occludes it, and where it lands

Use these questions to choose camera position and layering; do not print the analysis unless it helps the user review the asset plan.

## Stage 2: Inspect and Bind Actual Images

Compile the video prompt from the images that will actually be used, not only from their original image prompts. If images are available, inspect visible identity, costume state, layout, screen position, prop state, light direction, and any accidental discrepancy that may affect motion.

### Actual-Reference Supremacy Gate

Before binding, make a compact internal inventory for each selected image:

- `visibly confirmed`: facts the pixels clearly support
- `absent or unclear`: planned facts that cannot be verified in the image
- `conflicting`: visible facts that disagree with another active reference or the intended action
- `contaminated`: watermark/logo, garbled text, malformed anatomy, accidental extra object/person, damaging crop, or another artifact likely to propagate into video

The actual selected image is authoritative for its visible state. Its original image prompt records design intent but is not evidence that the result contains every requested fact. Do not name, lock, move, or transfer an absent/unclear prop merely because it appeared in the earlier prompt. If an absent detail is essential to the opening action, repair/regenerate the frame or bind a compatible dedicated reference first. If it can enter later, give it a visible source, entrance/contact action, and final state instead of making it appear.

Do not send a contaminated production reference forward without warning. A negative clause such as `no watermark` is not a reliable way to remove a watermark or malformed detail already embedded in the input. Recommend cleaning, cropping, repairing, or regenerating the asset when the flaw is likely to persist or animate.

### Reference-to-Motion Physical Feasibility Audit

Before writing the timeline, reconstruct the visible starting geometry and test the intended motion:

- current hand/foot placement, body support, facing direction, and balance
- reach distance and unobstructed path to the target
- chair arms, table edges, doors, clothing layers, and other clearance limits
- which surface or body part supplies force; grip, pressure, weight, friction, resistance, and release
- prop orientation, support point, ownership, and final resting place
- room to stand, turn, cross, or exit without intersecting furniture or another person
- whether the chosen shot size can actually show the important contact and its consequence

Write contact as `approach -> contact -> pressure/weight response -> release or transfer -> visible endpoint`. Replace brittle numeric precision such as `stops 2 cm away` with a visually judgeable event such as `stops just before the fingertips touch`, unless measurement itself matters to the story. If the selected frame cannot support the motion, change the blocking, repair the keyframe, add a compatible view, or split the action; do not ask the model to solve impossible geometry.

Assign each reference one narrow authority:

```text
Reference image 1: locks the heroine's identity, face, hair bun and current costume state.
Reference image 2: locks the hall's spatial layout, the positions of the doors and windows, and the direction of the candlelight.
Reference image 3: locks the two people's initial left/right positions, distance and eyeline relationship.
```

This mapping is required when several references could compete. Do not ask two references to control the same fact differently. If they conflict, choose the authoritative image for that fact, repair/regenerate the conflicting asset, or explicitly describe the intended on-screen change.

## Reference Image Result Repair

Use this when the user likes most of a generated reference image and asks to correct a limited failure. Inspect the actual result when available; do not diagnose only from the original prompt.

1. Name at most 1-3 dominant failed fields.
2. List the approved visual facts under `Keep unchanged`.
3. Put the requested correction under `Change only`.
4. Include only unavoidable physical dependents of that correction, such as sleeve fold after changing a cuff, shadow/contact after moving a hand, or reflections after changing a prop material.
5. Put likely collateral drift under `No side changes`.

Repair shape:

```text
【Keep unchanged】
Keep the character's identity, the confirmed main costume, the composition, the camera position, the background and the light sources unchanged.

【Change only】
Change the right cuff to the narrow-cuffed, cross-collar robe construction; correct the fabric folds directly connected to the cuff and the way it covers the wrist to match.

【No side changes】
Do not change the face shape, apparent age, hair bun, costume colors, body proportions, camera position, scene layout or light direction.
```

If the failed field is foundational—wrong person, wrong era, unusable topology, or a composition that cannot support the intended video—recommend regenerating that asset instead of accumulating contradictory repair clauses. Do not claim repair success until the revised image has been generated and inspected.

## Static Information Deduplication

In a `Reference-driven version` video prompt:

Keep only:

- reference identifier and authority mapping
- role/identity binding needed to tell people apart
- initial screen position, contact, or prop ownership when motion depends on it
- temporary state not reliably visible or easy to misread
- explicit changes that must occur during the clip

Do not restate:

- full facial and body descriptions
- full costume inventories
- full room, architecture, material, palette, or lighting descriptions
- alternate adjectives or synonyms that may pull the render away from the image
- a new initial pose or composition that contradicts a first-frame reference

Minimal binding is not redundant description. It tells the model which image controls which fact.

## Dynamic-Difference Contract

The images control assigned static visible facts. The video text controls time:

- duration and beat order
- body action, biomechanics, object contact, and recovery
- gaze, breath, voice, micro-expression, and emotional transition
- camera path, focus change, cuts, and transitions
- dialogue order, speaker identity, lip-sync, overlap, and pauses
- environmental motion and diegetic sound
- final visible state

When a static fact must change, write it as a timed delta with cause and endpoint:

```text
At 12s, she turns too quickly; the red outer robe from reference image 1 slips off her right shoulder, revealing the white mourning garment she was wearing underneath; the outer robe ends up hanging on her left elbow and does not return to its place.
```

Avoid bare contradictions such as describing the character as wearing white at the start while the identity reference shows a red outer robe.

## First-Frame and Camera-Development Contract

Before applying this section, distinguish a previous tail-frame state reference from an explicitly bound opening frame. A supplied previous ending does not automatically authorize matching its composition. Follow `continuity_director_contract.md` for cross-clip cuts and shot-to-reference coverage. Only a user-selected actual first-frame binding uses the opening-composition contract below.

A `State/first-frame reference image` controls the opening state, not the whole film grammar. Unless the user explicitly requests `static shot`, `one-take`, or the model/workflow requires a locked view, its shot size, angle, framing, and focus authority ends after the opening beat is established. Identity, costume state, scene topology, relationship axis, light direction, handedness, and prop continuity remain locked across later views.

Choose the structure from the dramatic content before writing the timeline:

- Use a one-take only when continuous space, uninterrupted performance, or real-time tension is the dramatic advantage. Let the camera develop inside the take through one coherent path, motivated reframing, or focus change; do not keep the first-frame composition static by habit.
- Use a multi-shot sequence when the story needs distinct evidence, object contact, a listener reaction, a power shift, or an aftermath that one view cannot read clearly. When the image is explicitly bound as the first frame, begin there; otherwise use it as state evidence and open on the planned new angle. Cut only to views supported by the same identity and inspected spatial references.
- Build a motivated shot progression rather than equal time slices. A common relationship-drama progression is `relationship geography -> decisive hand/object action -> affected face/reaction -> release or aftermath`, but omit or reorder stages to fit the actual story.
- Each new shot must change what the audience knows, feels, or can physically verify. Vary shot size, horizontal angle, focus, or camera distance enough to create a real edit; preserve the 180-degree axis, eyelines, screen direction, light, body/prop state, and match-on-action continuity.
- If a required new view depends on unseen room geometry, an unverified reverse side, or a face/prop angle the active references cannot hold reliably, generate a compatible additional keyframe/scene view or split the clip instead of inventing uncontrolled space.

Reference stability and cinematic coverage are separate goals: references keep the world consistent; the shot design tells the story.

## Reference-Driven Prompt Shape

```text
【Reference binding】
Reference image 1 locks ...; reference image 2 locks .... Static information not explicitly changed stays the same.

【Generation priority】
First ensure ..., then ...; play down unnecessary decorative changes.

【Motion video prompt】
Duration and structure: ... (state one-take or multi-shot; whether the first frame locks only the opening or, at the user's request, the whole clip)
0-...s: action, performance, camera, sound...
...s: explicit changes and cause and effect...
Ending state: ...
```

Do not force every label when a compact paragraph is clearer. The essential invariant is `binding + temporal direction + explicit deltas`, not a fixed template.

## Direct-Video Prompt Shape

When the user skips references, restore the static anchors needed for independent use:

- who and where
- identity/costume distinctions that prevent character confusion
- usable scene geography
- key prop ownership and start state
- motivated light baseline and sound bed
- first-frame reconstruction, temporal action, performance, camera, and ending

Do not refer to nonexistent images. If the user wants both versions, compile this separately from the reference-driven version.

## Continuation and Multiple Scenes

- Reuse approved assets across clips. Create or update a reference only when identity, costume/injury/weather state, location, or a story-critical prop visibly changes.
- For several locations, do not front-load every scene prompt. Prepare the current clip's active assets first; maintain the rest as a concise asset plan.
- For several principal characters, keep identity references separate when stable faces matter, but activate only the references supported by the current generation tool and shot.
- If the next clip changes a visible fact, preserve the previous final state and generate an updated-state reference only when that state will recur or is difficult to hold through text alone.

## Final Conflict Check

Before delivery, verify:

- every supplied image is classified as inspiration, production asset, or state/first-frame control
- every active reference has one stated purpose
- each image prompt follows its type-specific information budget and asks for one frame/composition unless the user requested a sheet or storyboard
- no static fact has two conflicting authorities
- the final prompt uses only facts visibly confirmed in the selected images; absent/unclear planned details are repaired, separately bound, visibly introduced, or omitted
- the selected images are checked for watermarks/logos, garbled text, malformed anatomy, accidental objects/people, harmful crops, and other contaminants before production use
- the video prompt does not redescribe static appearance in competing language
- every intended change from a reference has time, cause, and final state
- every key action is reachable and mechanically credible from the visible starting pose, furniture, clearance, prop support, weight, and friction
- a first-frame image locks only the opening unless a locked shot or one-take was explicitly chosen; later shot sizes, angles, focus, cuts, and camera movement follow the dramatic structure
- each cut or camera move has a story function and preserves axis, eyeline, screen direction, light, identity, and prop/body continuity
- the chosen ratio is explicit, inherited, or safely defaulted; a costly composition-sensitive reference stage did not proceed with an unresolved ratio
- for vertical output, composition-controlling references use the target ratio and the narrow frame preserves faces, hands, props, entry/exit paths, full-body clearance, and the intended relationship blocking
- character identity, scene geography, prop ownership, light direction, and starting contact are sufficient to interpret the motion
- the prompt is clearly labeled as reference-driven or no-reference when both are supplied
