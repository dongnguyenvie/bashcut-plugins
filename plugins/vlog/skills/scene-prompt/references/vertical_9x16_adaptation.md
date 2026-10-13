# Vertical 9:16 Adaptation System

Read this file only when the user explicitly requests vertical/portrait/`9:16`, an existing production reference or approved continuation is vertical, or the aspect-ratio router resolves the delivery to vertical. Do not apply it to ordinary horizontal work.

## Aspect-Ratio Routing Without Extra Friction

Resolve aspect ratio before composition-sensitive writing:

1. Follow an explicit `landscape`, `vertical`, `16:9`, `9:16`, or other ratio without asking.
2. Inherit the actual ratio of a production first frame, keyframe, or approved previous clip unless the user requests reformatting.
3. Preserve the last confirmed ratio across a continued series without asking again.
4. Follow a platform format only when the user states the format; do not assume one universal ratio from a platform name that supports several formats.
5. If ratio is unspecified and the scene is low-risk—a single subject, close performance, simple object action, or no production references—default to `16:9 landscape` and continue.
6. Ask once only when ratio cannot be inferred and would materially change expensive work: production references, two-person/table blocking, three or more people, full-body movement, dance/fight/chase, architecture/landscape/vehicle scale, or a multi-platform master. Merge this with any existing direction or production-path checkpoint.

Use one concise question:

```text
The aspect ratio will noticeably affect these reference images/this blocking. Please confirm whether the final output should be 16:9 landscape or 9:16 vertical.
```

Do not ask again after the ratio is confirmed or inherited. If the user delegates, default to `16:9 landscape` unless an actual vertical production asset or explicit vertical delivery context controls the choice.

## Vertical Composition Principles

Vertical is not a horizontal frame with both sides removed. Recompose around a narrow central action corridor and stronger near/far or upper/middle/lower relationships.

- Keep one principal visual target per shot and normally no more than one secondary target.
- Protect faces, eyes, hands, story-critical props, and action endpoints from extreme edges. Reserve overlay space only when the user states a platform, subtitle, title, or interface requirement; do not add universal blank bands.
- Use depth staging, `OTS` foreground, doorway/column masking, mirror/reflection, diagonal blocking, seated/standing height contrast, or upper/lower layers instead of forcing two people into opposite side edges.
- Give empty space a function—distance, absence, threat, destination, or waiting. Do not leave unused sky/floor merely because the canvas is tall.
- Establish vertical geography concretely: foreground floor/object, middle character/action, and upper or deep doorway/window/stair destination.
- When location width is essential, use a detail sequence, controlled move, or separate horizontal master rather than shrinking the subject until the room fits.

## Shot-Size Adaptation

### Single person

- `CU/MCU` are strong in 9:16. Preserve gaze room and include the relevant hand/prop when it carries the beat.
- Keep eyes around the upper-middle visual area rather than crowding the top edge; use lower frame for breath, hands, costume, or objects only when relevant.
- Do not fill the frame with a face when the next action needs shoulders, hands, standing, or turning.

### Two people

- Avoid a small symmetrical side-by-side two-shot by default. Prefer staggered depth, `OTS`, profile layers, reflection, doorway separation, or alternating singles while preserving the 180-degree axis and eyelines.
- Use a relationship-establishing `MS/MLS` only when bodies and the separating object must be read together; then move to meaningful reactions or object/hand inserts.
- If both faces remain visible, differentiate them by depth, height, focus, and gaze rather than pushing them against side edges.

### Full-body movement

- Before standing, turning, embracing, falling, drawing a weapon, dancing, or fighting, create head/foot room with `KS/FLS`, a pull-back, a tilt, or a cut to a wider vertical composition.
- Keep destination and travel corridor visible. Do not let the body leave frame when the action mechanics matter.
- Use depth for movement toward/away from camera. For lateral motion, shorten the path and settle the subject back into a readable position.

### Groups and large scenes

- Choose one visual anchor and organize others in depth or reveal them over time. Do not demand several equally large full faces in one narrow frame.
- Use reaction singles, partial bodies, hands, status height, doorway layers, or progressive reveal to show group relationships.
- Decide whether ceremony, architecture, crowd, vehicle, battlefield, or landscape depends on height/depth or width. If width is indispensable, simplify, use several shots, or recommend a horizontal master plus a separate vertical adaptation.

## Camera Movement in 9:16

Select by story function first, then adapt the path to the narrow frame. Read `camera_movement_prompt_library.md` for the base module when needed.

- Often effective: `Dolly In/Out`, `Tilt Up/Down`, `Pedestal Up/Down`, `Crane Up/Down`, `Follow Shot / OTS`, `Reverse Tracking`, `Push Past`, `Rack Focus`, and controlled forward/backward depth movement.
- `Pan`, `Truck`, `Slider`, and `Side Tracking` remain valid, but use shorter travel, name the visible target, and finish with the subject safely re-established. Do not sweep across empty lateral space.
- Use `Whip Pan` or `Crash Zoom` only for a real attention break; the landing target must survive the narrow frame.
- Prefer a shallow `Arc` to a large/full `Orbit` in confined interiors. A wide orbit may expose unseen space or push faces out of frame.
- `Crane`, `Tilt`, and `Pedestal` are not automatically better because the frame is tall; use them only when height, stairs, standing/kneeling power, falling/rising, architecture, or scale changes.
- In a vertical one-take, state how framing evolves as the body changes height/depth. Do not keep a tight face composition while demanding a full-body exit.

## Vertical Story Coverage Patterns

Use as decision patterns, not fixed templates:

- Restrained single-person emotion: `MCU/CU protective layer -> very slow Dolly In or Static -> CU/BCU after the trigger -> breath and lingering aftertaste`.
- Two-person relationship: `MS/MLS establishes depth/separation -> OTS/CU on the speaker -> CU/BCU on the listener -> necessary hand/prop insert -> wider ending confirms the distance or the exit`.
- Discovery/suspense: `subject near the central axis -> eyeline/sound trigger -> Rack Focus, a short Pan or a cut reveals a clue in depth/above/below -> facial reaction -> keep the unknown space`.
- Stand/turn/exit: `readable starting point -> widen or cut to KS/FLS before the action -> head, feet and exit visible -> Follow/short Track exit -> end on the empty spot or the remaining character`.
- Group/scale: `single anchor -> foreground and background revealed layer by layer -> height, doors and windows, stairs or Crane/Tilt establish scale -> return to the consequences for the character`.

## Reference-First Vertical Workflow

- Create composition-controlling assets—blocking scene plates, relationship/two-shots, first/tail frames, and ordered keyframes—in the target `9:16` ratio.
- Identity and isolated prop references may use another practical ratio only when they act as attribute references and remain crop-safe.
- Any literal first or last frame must match the target ratio, and first/last frames must match each other.
- A horizontal production frame cannot become a reliable vertical first frame merely by adding `9:16` to the video prompt. Inspect whether people, hands, props, entrances/exits, light source, and action path survive; otherwise regenerate/recompose a vertical keyframe while preserving approved facts.
- A vertical scene plate should reveal height/depth and a central action corridor, not a narrow crop of a horizontal room. A vertical relationship frame should use depth or layers rather than edge-to-edge symmetry.
- Keep composition-controlling references for one clip consistent in orientation and ratio; resolve mismatches before Stage 2 binding.

## Vertical Failure Checks

- Is `9:16 vertical` stated when vertical output is selected and the prompt/tool needs it?
- Do central action, face, hands, key prop, entry/exit, and final state fit the narrow frame?
- Are multiple people layered or covered through motivated shots rather than squeezed side by side?
- Does full-body action have head/foot room and a visible destination?
- Does horizontal movement have limited travel and a readable landing target?
- Is vertical movement story-motivated rather than added because the canvas is tall?
- Do multi-shot axis, eyelines, direction, identity, light, and prop/body state remain stable?
- Do production first/tail frames match the target ratio, without a broken silent crop from horizontal?
- Is platform overlay or subtitle space reserved only when the delivery requirement is known?
