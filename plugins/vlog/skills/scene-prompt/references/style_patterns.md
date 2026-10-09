# Style Patterns

This reference captures the current house style for cinematic video prompts. Treat it as a living style library: add distilled rules and compact examples, not long pasted source prompts.

## Core Shape

The best prompts usually follow this order:

1. A short summary that includes duration, structure, emotional premise, and visual premise.
2. Optional model adaptation only if the user specifies a model.
3. Time-based shot design.
4. Camera, lens, framing, movement, and depth of field.
5. Physical action and composition.
6. Light, color, atmosphere, and environmental motion.
7. Character performance: inner logic, micro-reactions, physiological reactions.
8. Dialogue, voiceover, or inner monologue with timing.
9. Sound design and ending.

## Time Axis

Use time only when it improves generation clarity.

- Estimate duration by playable screen content, not by source text length. Before deciding one prompt vs split prompts, count:
  - plot beats or reversals
  - dialogue delivery time plus pauses and listener reactions
  - physical actions, travel, fights, embraces, falls, object handling, or reveals
  - emotional transitions and micro-expression settling time
  - scene/location/time changes
  - camera moves and reframing needed for large body action
  - final 1-2s breath, sound tail, or bridge hold
- A short synopsis can still exceed 30s if it contains multiple beats that need to be shown clearly.
- If the full content cannot breathe within 30s, split by emotional turning point, action phase, location change, or reveal/aftermath boundary. Do not compress by simply speeding up action or removing reaction time.
- For one continuous emotional beat: `0-3s / 3-8s / 8-12s`.
- For multi-shot prompts: `Shot 01`, `Shot 02`, etc.
- Each time block should contain a visible change: action, gaze, light, spatial relation, or sound.
- Avoid stuffing unrelated story events into a single 30s prompt.
- Do not end important dialogue or peak action exactly at the final second. Reserve 1-2 seconds for reaction, breath, silence, sound tail, or visual continuation.
- Time allocation should follow drama, not equal division. If a shot contains a line plus a complex action, give it more time or simplify it.
- If the ending feels rushed, remove a detail or split the prompt instead of making the final beat abrupt.

## Prompt Sampling Range Control Principles

Use these principles before writing the final prompt and again during compression. Their purpose is to narrow the model's guessing range into a smaller, cleaner set of possible videos.

1. **Specificity Principle / Observable Specificity**
   - Convert abstract intent into what the camera can see or hear: action, object, light source, texture, reflection, sound, body reaction, and timed transition.
   - Do not stop at labels such as `shattered memory flashback`, `premium feel`, `oppressive feel`, `sense of fate`, or `cinematic feel`; translate them into visible fragments. Example: `shattered memory flashback` can become rain on glass, a red umbrella in puddle reflection, a phone vibration, headlight flare, glass shards catching light, and a face losing focus.

2. **Non-Contradiction Principle / Non-Contradiction**
   - Remove instructions that cannot physically, spatially, emotionally, or temporally coexist.
   - Check object behavior, light source, camera path, costume/prop state, and action causality. Example: cloth can tear into fragments, but it should not also form a perfect blade-like arc unless it is an intentional visible VFX object.
   - If two instructions conflict, keep the one that serves the story function and rewrite the other as a compatible visual detail.

3. **Positive Description First / Positive Target Description**
   - Say the desired path first: `the ball rolls straight into the blue box`, `the car turns left at the intersection`, `the character runs toward the bright door at the end of the corridor`.
   - Use negative constraints only as a small fallback for likely model failures, especially subtitles, watermarks, background music, face/body distortion, unwanted genre drift, or unsafe escalation.
   - When the scene outcome matters, do not rely on `don't...` alone. Replace `don't go into the red box` with `go straight into the blue box`; replace `don't suddenly kiss` with `the two keep half a step apart, closing the distance only through their eyes and breathing`.

4. **Avoid Over-Specification / Avoid Over-Specification**
   - Details should reduce ambiguity, not try to control every pixel.
   - Limit one short clip to the necessary visible targets: the main action path, emotional turn, key props, space, light source, and sound anchors. If a prompt names too many small targets, remove decorative or redundant details before adding more.
   - When quality drops or action becomes unnatural, reduce goals: fewer fragments, fewer camera moves, fewer micro-actions, fewer props, or split into another clip.

## Camera Language

Resolve the aspect-ratio route before choosing composition-sensitive camera grammar. Ordinary low-risk work defaults to `16:9 landscape` when no ratio is given; vertical/portrait/`9:16` work must read `vertical_9x16_adaptation.md`. Do not ask routinely—ask once only when an unresolved ratio materially changes production references, complex blocking, full-body action, groups, scale, or multi-platform delivery.

Prefer specific but generation-friendly terms:

- Use standardized English abbreviations for shot size and camera movement in storyboard prompts. Chinese explanations can appear in diagnosis, but the final shot labels should use the abbreviations when professional terms are needed.
- Character shot sizes: `ECU` Detail Shot (only a facial detail), `VCU` Face Shot (forehead to chin), `BCU` Big Close-Up (full head including face), `CU` Close-Up (head and shoulders), `MCU` Chest Shot (head to below chest), `WS` Waist Shot (head to waist), `KS` Knee Shot (head to knees), `FLS` Full Length Shot (full body with head/foot room), `LS` Long Shot (person occupies about 3/4 of frame), `ELS` Extra Long Shot (person far away).
- Object/scenery shot sizes: `CU` Close-Up (local detail), `MCU` Medium Close-Up (about 1/4 of subject), `MS` Medium Shot (about 1/2 of subject), `MLS` Medium Long Shot (whole subject plus some surroundings), `LS` Long Shot (subject occupies about 3/4 to 1/3 of frame), `ELS` Extra Long Shot (farther than long shot).
- Camera movement and focus: `Dolly In/Out` or `Track In/Out` for camera physically moving forward/backward; `Pan Right/Left` for horizontal lens/head rotation; `Tilt Up/Down` for vertical lens/head rotation; `Track Right/Left`, `Truck Right/Left`, or `Crab Right/Left` for camera moving sideways; `Ped Up/Down` for vertical camera movement; `Crane Up/Down` or `Jib Up/Down` for vertical/diagonal camera movement with a crane/jib feel; `Arc/Orbit` for a curved path around the subject; `Zoom In/Out` for focal length change while camera stays physically still; `Dolly Zoom` / `Vertigo effect` for dollying one way while zooming the opposite way; `Whip Pan` or `Crash Zoom` for fast transition/emphasis; `Rack Focus` / `Focus Pull` for changing focus between foreground/background or person/object while the shot continues; `Handheld` for controlled human shake; `Static` for no camera movement.
- Focal length: `24mm`, `35mm`, `50mm`, `85mm`, `100mm macro`, `200mm`.
- Camera movement: prefer the standardized movement terms above; phrases such as `Slow Push in`, `Handheld Backward Tracking`, or `Snap Pull Back` are allowed when they describe the desired feel more clearly.
- Lens texture: shallow depth of field, anamorphic flare, bokeh, Chiaroscuro, hard side light, backlight, practical light.

Do not pile up terms. Use the terms that directly serve the scene's emotion.

When a term has possible ambiguity, disambiguate by context. For example, `MCU` in a character shot means Chest Shot, while `MCU` in an object/scenery shot means Medium Close-Up. If needed, write `MCU Chest Shot` or `MCU object detail` once, then use the abbreviation consistently.

### General Camera Movement Selection System

Use this system to choose the dramatic function first. If the selected move needs precise Chinese start/path/direction/speed/end wording, or a less common option such as `Snorricam`, `Pedestal`, `Slider`, aerial movement, or object pass-through, read `camera_movement_prompt_library.md`. Select only the relevant module; do not expand the final prompt into a catalogue.

Choose camera movement by narrative function, not as decoration. Most 6-15s prompts need only 1-3 principal moves; a simple emotional close-up may need none. If a move does not change emotional distance, reveal space, follow action, create disorientation, or mark a transition, use `Static` instead.

| Camera move | Best use | Writing rule |
|---|---|---|
| **Push-In / Dolly-In** | intimacy, tension, realization, a character being emotionally trapped | Move physically closer to the subject and end on the important face, hand, object, or decision. Keep it slow for emotion, faster only for shock or threat. |
| **Dolly-Out / Pull-Back** | reveal context, isolation, aftermath, closure, or a hidden spatial relationship | Start close enough to feel subjective, then reveal the larger room, crowd, landscape, or consequence. Do not pull back without new information. |
| **Pan Right/Left** | follow a gaze, track an entering subject, reveal adjacent space, build anticipation | Rotate from one readable subject/space to another; end on a clear target rather than vague scenery. |
| **Tilt Up/Down** | reveal height/depth, a body/object from detail to whole, power difference, vertical threat | Use when vertical information matters: tower, stairwell, falling object, kneeling/standing power change. |
| **Tracking / Truck / Crab** | walking, driving, pursuit, side-by-side dialogue, smooth movement through space | Keep camera parallel to the subject or movement path; show obstacles or destination so direction stays clear. |
| **Arc / Orbit** | show multiple sides of a character, reveal changing power, circle a confrontation, add dimension | Orbit around one stable subject or pair. Keep background readable and preserve axis logic through the visible move. |
| **Crane / Jib** | grand reveal, scale, environment, vertical transition, a subject becoming small or powerful | Rise/fall with story purpose: reveal the crowd, city, battlefield, cliff, lighthouse, or emotional isolation. |
| **Zoom In/Out** | focus attention, compress distance, isolate a face/object, observational or surveillance feel | Use when the camera should feel physically still; avoid replacing every emotional push-in with zoom. |
| **Dolly Zoom / Vertigo effect** | disorientation, panic realization, moral vertigo, world collapsing around a character | Reserve for rare turning points. State the emotion it expresses; avoid using it as a generic cool effect. |
| **Whip Pan / Crash Zoom** | sudden attention shift, energetic transition, surprise reveal, fast comedic or action beat | Use briefly. Start and end on readable subjects; preserve direction and avoid random blur. |
| **Handheld** | realism, urgency, documentary immediacy, panic, chase, unstable confrontation | Describe the intensity: subtle human shake, close handheld, or rough handheld. Do not use heavy shake when facial nuance or action readability matters. |
| **Static + angle family** | formal tension, observation, power, dread, comedy timing, precise performance | Use `Static Low Angle`, `Static High Angle`, `Static Dutch Angle`, `Bird's-Eye`, `Worm's-Eye`, or `Straight On` when perspective matters more than movement. Static is often strongest for micro-expression, interrogation, waiting, and moral pressure. |

#### Selection by Drama Beat

```text
Emotional closeness: Push-In / Dolly-In, or Static CU if the face already carries enough pressure
Loneliness and consequence: Dolly-Out / Pull-Back, Crane Up, ELS reveal
Discovery and anticipation: Pan, Tilt, Slow Push-In
Parallel movement: Tracking / Truck / Crab, Handheld following
Power shift: Low Angle Static, High Angle Static, Tilt Up/Down, Arc/Orbit
Psychological imbalance: Dolly Zoom, Dutch Angle Static, brief Handheld instability
Quick transition or surprise: Whip Pan / Crash Zoom, but end on a readable subject
Grand space: Crane/Jib, ELS, controlled Pull-Back
Micro-expression performance: Static ECU/CU or extremely slow Push-In; avoid restless camera
```

#### Combination Rules

- Tie camera movement to a visible cause: gaze, footsteps, vehicle motion, body approach/retreat, door opening, object reveal, emotional realization, or sound cue.
- Avoid stacking `Push-In + Orbit + Zoom + Handheld + Dutch Angle` in one beat. Choose one primary move and one supporting angle or lens choice.
- Prefer `Dolly-In` for emotional approach because the camera physically enters the character's space; prefer `Zoom-In` for observation, surveillance, shock compression, or a distant watcher feeling.
- Use `Static` deliberately. A fixed frame can make a confession, threat, micro-expression, or comedy pause more powerful than constant movement.
- When cutting between shots, maintain the 180-degree axis and camera-angle rules elsewhere in this reference.

## Cinematic Lighting as Dramatic Design

Do not use `cinematic lighting` as a vague magic phrase. Cinematic lighting should create dramatic tension, emotional direction, visual hierarchy, and story meaning. It is not only illumination.

Do not over-describe lighting by default. Lighting language should be proportional to the scene: it must support performance, action, and story, not replace them. If the scene is mainly about dialogue, suspense movement, a fight, or a micro-expression, keep lighting concise unless the light itself is the dramatic engine.

### Lighting Detail Budget

Choose one level before writing the final prompt:

1. **Minimal / one phrase**: use for ordinary rooms, fast action, phone calls, domestic suspense, short emotional beats. Example: `A dim small dark room; cold light from the door crack and the phone screen only traces the outline of the face, while the background keeps detail in the shadows.`
2. **Standard / one compact sentence**: use when light helps mood but is not the main subject. Mention source, direction, what is readable, and shadow mood in one sentence.
3. **Detailed / lighting design paragraph**: use only when lighting is the core test, the user asks to check lighting, or the scene is built around authority, ritual, judgment, noir pressure, product texture, stage-like composition, or a strong visual concept.

Do not repeat full Key/Fill/Rim/Volumetric descriptions in every shot. Put stable lighting once in the opening summary or first shot, then only mention changes: door opens, lamp switches off, phone screen lights a face, flashlight sweeps, neon flickers, etc.

### Motivated Light Source

Every strong light must have a believable source inside or just outside the scene: window, high window, door slit, bare bulb, table lamp, fluorescent tube, candle, TV, phone screen, police light, neon sign, car headlight, flashlight, skylight, firelight, or reflected light from table/floor/wall.

Match the light quality to the source:

- hard side-top light needs a plausible high, small, directional source and a story reason for harshness.
- soft front fill can come from weak bounce on a table, wall, floor, curtain, screen, or window diffusion.
- volumetric beams need dust, smoke, mist, rain, steam, or haze.
- rim light and strong edge highlights should not appear without a credible back/side source.

If the location does not support `Hard side-top Key Light` or `hard side-top light from upper right`, do not force it. In a small black room, domestic interior, cramped apartment, or ordinary office, prefer motivated practical light such as a door crack, exposed bulb, desk lamp, phone screen, TV spill, window slit, corridor light, or weak ambient bounce. Hard side-top light is a specialty pattern, not the default cinematic look.

### Realistic Night Exterior and Courtyard Light

Use this for ancient courtyards, gardens, alleys, patios, palace yards, manor entrances, rooftops, or other night exterior scenes. Keep the light cinematic but physically believable.

Core rule: moonlight can shape the overall cool ambience and edges, but it should not behave like a hard spotlight cutting a face unless the scene has a very specific high opening, mist, or stylized stage reason. Faces at night are usually made readable by nearby practical sources and bounce: lanterns, candles, corridor lamps, window spill, reflected light from stone floor/walls/table, or weak soft fill.

Good night-courtyard phrasing:

```text
A mansion courtyard at night. Cold moonlight falls as a soft ambient base on the eaves, stone ground and the edges of flowers and trees; lanterns under the veranda and candlelight by the table give the characters' faces a very faint warm reflection, keeping readable detail in the eyes and cheekbones, while shoulder lines, hair crowns and fabric edges carry natural cool rim highlights. The shadows overall have gradation; it is not hard-cut stage lighting.
```

Use artistic processing with restraint:

- Let moonlight outline hair, shoulders, headdress, roof edges, tree leaves, stone floor, and distant architecture.
- Let lantern/candle/window spill reveal eyes, cheekbone, mouth line, fingers, jewelry, sleeve texture, or the key prop.
- Use `soft edge highlight`, `weak practical fill`, `stone-floor bounce`, `lantern spill`, or `candle reflection` instead of hard face-cutting moonlight.
- If the face needs stronger contrast, explain the source: a nearby lantern, side corridor lamp, open doorway, window lattice, reflective stone table, or hand-held candle.
- For period courtyards, avoid modern studio terms unless the source is disguised as a motivated practical light.

Avoid:

- `cold moonlight cutting across one side of the face` if there is no believable angle or reflector.
- mixing every light type in one sentence: moonlight, Rembrandt, spotlight, blinds, candle, window, golden hour, and volumetric beams all at once.
- making night exteriors look like an indoor studio portrait unless the user asks for stylization.

For a restrained urban night exterior, a dark background can coexist with soft, readable midtones rather than mandatory high contrast. Let motivated street/bridge/window light retain facial modeling, clothing folds and natural skin color against a darker river or skyline; allow a small neutral-warm practical contrast within cool ambient light. Separate foreground, people and distant lights through occlusion, distance and subtle atmospheric falloff. Do not prescribe color-area percentages, a uniform cyan cast, lifted gray blacks or a complete glowing rim as universal requirements.

### Dynamic Light Interaction

Use this when the character, vehicle, train, curtain, door, window, flashlight, or weather is moving. The light should not sit still as decoration; it should interact with motion.

Good dynamic lighting links:

- repeated window light cuts across a running character's face and body
- a moving train/car causes sunlight and shadow to alternate rhythmically
- a door opening or closing changes both light level and sound bed
- a headlight, flashlight, phone screen, or TV flare reveals dust, smoke, rain, grass, fabric, or breath
- clouds, branches, curtains, rain, or passing streetlights make shadows move across walls, seats, floorboards, glass, or skin
- a character moves toward a fixed light source, making the light feel like a destination or temptation

Prompt phrases:

```text
Dynamic light and shadow: as the character moves toward the car door / window / end of the corridor, the practical light sources stay fixed and the body passes through alternating bands of light and dark; light patches sweep across the face, hands, fabric and floor, shadows stretch, compress and leap forward again, and the rhythm of light and shadow syncs with footsteps and breathing.
```

```text
Environmental particles: backlight only reveals dust, rain mist, grass bits, fabric fibers or exhaled white breath in the air, giving the space real depth; no unsourced bloom or decorative halos.
```

Use dynamic light sparingly. One strong interaction is usually enough for a 15s prompt.

### Light as Emotional Direction

Light can function as a story direction, not only a look. A fixed light source can represent exit, freedom, danger, judgment, exposure, temptation, memory, or an irreversible choice.

Common use:

- shadowed foreground frames a trapped character; distant light marks the only exit
- a child or adult runs toward a doorway/window/headlight, turning light into a physical destination
- warm exterior light contrasts with cold interior shadow to show escape from control
- a bright screen, document lamp, or phone glow exposes a secret
- a car door closing cuts off exterior light and wind, turning the scene inward and silent

Keep the description concrete: name the source, where it falls, what it hides, and what action changes it.

When lighting is truly important, describe the lighting system in this order:

1. **Key Light / key light**: direction, height, hardness/softness, color temperature, beam shape, and what it actually hits.
2. **Fill Light / fill light**: strength and purpose. Often very weak, only keeping minimum texture instead of flattening the face.
3. **Rim Light / rim light**: where it catches shoulders, ears, hair, objects, statues, weapons, or furniture edges to separate subject from darkness.
4. **Background / Volumetric Light / background light / volumetric light**: light hitting dust, smoke, mist, rain, curtains, windows, statues, walls, or architectural depth.
5. **Narrative meaning / lighting intent**: what the light/shadow relationship says about power, secrecy, guilt, judgment, hope, danger, intimacy, or ambiguity.

### Light Must Touch Concrete Surfaces

Avoid generic phrases like `dramatic lighting` or `cinematic lighting`. Write what the light does:

- hard side-back Key Light cuts across face, hand, table edge, and a statue
- left half of the room falls into near-black shadow
- weak ambient Fill Light keeps only a faint fabric outline
- Rim Light catches right shoulder, ear edge, hairline, and object contour
- Volumetric Light becomes visible through dust, smoke, rain mist, or thin fog
- practical light, window slit, doorway spill, police light, candle, TV, phone screen, neon, or car headlight creates motivated light

### High-Contrast Judgment / Courtroom Pattern

Use this for courtrooms, interrogations, offices of power, temples, throne rooms, police rooms, confession spaces, or any scene where authority and moral ambiguity matter.

```text
Lighting design: a strongly directional Key Light comes from the right rear of the frame, fairly hard, forming a clear beam that lights the character unevenly, catching only one side of the face, the hands, the tabletop and a background statue/symbol of power; the left side of the space sinks into large areas of shadow, forming a Chiaroscuro order of light and dark. The Fill Light is extremely weak, only preserving a little shadow gradation in the fabric and face without filling the shadows in. A Rim Light grazes the right shoulder, ear, hairline and statue edges, separating the character from the black background. The background has Volumetric Light through dust/thin haze, and the beam itself becomes part of the image. Lighting intent: the character stands at the boundary of light and dark, expressing that power, law, secrets or moral judgment are not pure—solemn, yet tinged with ambiguity and pressure.
```

### Lighting Prompt Template

Use a compact version inside final prompts:

```text
Light and shadow: the Key Light cuts in from {direction} as {hard/soft} light, hitting only {face/hands/tabletop/prop/background object}; the Fill Light is extremely weak, preserving {fabric/shadow contours} without filling in the shadows; a Rim Light traces {shoulders/ears/hairline/prop edges}; Volumetric Light in the background {smoke/dust/rain mist/curtains} forms visible beams. The overall light-dark relationship serves {judgment/secrecy/oppression/loneliness/ambiguity/hope}.
```

### Common Lighting Failures

- Only writing `cinematic lighting`, `premium light and shadow`, or `strong atmosphere` without direction, object, shadow, or meaning.
- Turning every shot into a full lighting lecture when the scene only needs a compact practical-light cue.
- Forcing `Hard side-top Key Light` or `hard side-top light from upper right` into environments where no believable high hard source exists.
- Lighting everything evenly so the image loses visual hierarchy.
- Adding too many light sources with no motivation.
- Using rim light, fog, lens flare, and glow everywhere without story reason.
- Describing light color but not what it hits or hides.
- Forgetting that shadow is part of the lighting design; decide what should fall into darkness.

### Off-Frame High Side-Back Light + Soft Front Fill

Use this for courtrooms, public hearings, institutional interiors, ceremonial halls, stage-like dialogue scenes, or character tableaux where the space needs scale and atmosphere but the face must remain readable.

Core pattern:

```text
Off-frame high side-back light slants into the frame from high behind the character, usually from an off-frame window, skylight, door crack or high practical light. The light passes through smoke, dust, rain mist or thin haze to form Volumetric Beams, layering the background crowd, spatial depth and foreground subject. The character's face is not carved by hard shadows; instead Soft Front Fill or weak ambient light bounced off a table, floor or wall gently lifts it, keeping the expression clear so the emotion does not turn horror-dark but can be more candid, absurd, restrained or self-mocking.
```

Use this distinction:

- `Rim Light`: deliberate, more defined contour light, often commercial or stylized, clearly separating the outline.
- `Soft edge highlight`: softer edge lift created by high side-back light catching hair top, ear, shoulder, cheek edge, or clothing folds. It is not a strong commercial rim light.

Prompt phrase:

```text
Light and shadow: an Off-frame high side-back light slants in from upper left/upper right, passing through thin haze to form large Volumetric Beams that separate the foreground character, the background crowd and the depth of the space; the character's face is gently lifted by Soft Front Fill or light bounced off the table, keeping the expression readable; the top of the hair, ears and shoulders carry only a Soft edge highlight, not a strong commercial Rim Light.
```

### Color Temperature as Story

Color temperature contrast should express story, not decorate the frame.

- Cold white light can suggest system, reason, distance, institution, loneliness, or emotional detachment.
- Warm white light can suggest humanity, memory, body temperature, fate, intimacy, or moral ambiguity.
- In symmetrical compositions, color contrast can make an apparently balanced frame emotionally unstable.

Prompt phrase:

```text
The centered symmetrical composition brings order and balance; the cold white light on the left stands for institution, reason and distance, the warm white light on the right for humanity, warmth and fate. The two color temperatures sit side by side around the character, giving the image both a sense of fairness and complex emotion.
```

### Low-key High Contrast Tonal Structure

`Low-key High Contrast` is a tonal structure, not a filter. Tonality is the planned distribution of dark values, midtones, highlights, black point, and shadow detail before the shot is generated. If the tonal base is wrong, post-filter words cannot reliably create the style.

Use `Low-key High Contrast` when the scene needs pressure, mystery, premium texture, crime atmosphere, interrogation, noir, restrained luxury, or dark psychological weight.

Characteristics:

- dark areas dominate the frame
- clean black point, not muddy gray
- concentrated local highlights
- wide range from deep black to controlled bright spots
- shadow detail remains visible
- subject is cut out by local light
- background is suppressed but not dead black
- light comes from motivated sources such as table lamp, flashlight, window slit, fluorescent tube, neon, candle, car headlight, phone screen, or product edge light

Prompt phrase for crime/interrogation:

```text
Tonality: Low-key High Contrast, with shadow as the base of the image; blacks are clean but keep shadow detail. A desk lamp on the interrogation table forms a small hard pool of light that lights only one side of the character's face, the hands and the documents on the table; the background is pressed into deep shadow but not crushed black, and the character is carved out of the darkness by local light.
```

Prompt phrase for product/luxury:

```text
Tonality: Low-key High Contrast with a high-end commercial texture; the dark minimalist background is pressed down but keeps gradation. The product edges have a refined narrow rim light, glass/metal surfaces show controlled specular highlights, the subject is carved out by local light, and the shadows are neither dirty nor crushed black.
```

Common tonal failures:

- calling it a filter instead of designing the light and tonal range
- making the whole image underexposed without highlight structure
- crushing shadows into dead black with no object separation
- using bright fill that destroys the low-key base
- adding random glow instead of concentrated motivated highlights

### Hard Side-Top Light for Rough Dangerous Characters

Use this for rough male characters, criminals, violent patriarchs, dirty antiheroes, exhausted interrogators, underground fighters, or any role that needs danger, anger, pressure, and tactile skin texture. Keep the subject adult when violence, intimidation, or criminal atmosphere is involved.

Use it only when the set can justify a high hard source: bare overhead bulb, high window, inspection lamp, ceiling practical, industrial fixture, interrogation lamp angled upward/sideward, doorway slit from above, car headlight from a raised angle, or similar motivated light. If the scene is a cramped domestic room, small black room, ordinary apartment, or soft emotional space, do not default to this pattern; use weaker motivated practical light instead.

Core logic:

- **Hard side-top Key Light**: usually from upper right or upper left, cutting downward across the face and fists. It creates hard highlights on forehead wrinkles, nose bridge, nose tip, cheekbone, knuckles, leather, sweat, grime, and worn fabric.
- **Deep shadow zones**: eye sockets, opposite cheek, beard depth, under brow, neck folds, and jacket gaps fall into dense shadow. This makes the character less predictable and more oppressive.
- **Weak front fill**: very low Soft Front Fill keeps minimal readable detail on the shadow side of face, fist, and clothing. It prevents dead black but must not erase the high-contrast shadow design.
- **Rough edge highlight**: high side/back light catches hair, shoulder, forearm, leather jacket edge, and hand outline. It should feel dirty, hard, and textured, not glossy commercial Rim Light.
- **Texture purpose**: the light is designed to reveal rough skin, pores, wrinkles, sweat, dust, stubble, scars, old leather, and dirty fabric. It should make the character feel coarse, angry, dangerous, or physically heavy.

Prompt phrase:

```text
Light and shadow: a hard side-top Key Light from the upper right slices across the character; strong highlights fall on the forehead wrinkles, bridge and tip of the nose, left cheek, fist and the edges of the old leather jacket; the eye sockets, right side of the face, the depths of the beard and the neck sink into heavy shadow, creating the oppressive feel of Low-key High Contrast. Soft Front Fill is extremely weak, keeping only the minimum detail in the right side of the face, the fist and the shadows of the clothing, avoiding crushed black without weakening the shadows. A high side-back light forms a rough Soft edge highlight on the hair, shoulders, arms and jacket edges, separating the character from the dim background and emphasizing a dirty, hard, rugged, dangerous texture.
```

Avoid:

- beauty lighting, smooth skin, clean fashion portrait texture
- bright front fill that makes the face friendly or flat
- pure black shadow with no beard, fist, or clothing detail
- over-polished commercial rim light if the character should feel dirty and dangerous

## Performance Writing

For a named emotion or a performance transition that needs more concrete observable cues, read `emotion_performance_prompt_library.md`. Use one nearest base emotion and adapt 2-4 signals to the character's motive, trigger, restraint, body condition, and scene distance. The library supplements the systems below; it does not override character knowledge, dialogue timing, FACS restraint, biomechanics, or emotional causality.

Strong performance prompts use this sequence:

```text
Inner logic: the character ... because of ...
Visible motive: on the surface he/she wants to ...
Micro-reactions: eyelids, jaw muscles, corners of the mouth, gaze, fingers...
Physiological reactions: breathing, swallowing, nostrils, sweat, trembling, body stiffening...
Action result: finally performs one clearly visible action.
```

Write emotions as body evidence:

- Repressed: jaw locked, lips pressed flat, shallow breath, hands clenching fabric, gaze avoiding contact.
- Collapse: breath breaks, fingers release, eyes wet but fixed, smile appearing against the character's will.
- Resolute: still gaze, no blinking, body leans forward before action, breath stops then releases.
- Freedom: posture opens, hair and clothes catch wind, eyes lock onto distant light, a small fearless smile.

## Character Knowledge and Evidence Control

Use this for delayed recognition, mystery, reunion, time displacement, hidden identity, supernatural ambiguity, investigation, betrayal, or any scene where the audience and characters do not know the same things at the same time.

### Knowledge-State Record

Track four states internally for each important character:

```text
Already knows -> newly observes/hears -> may reasonably infer -> must still remain unknown
```

Emotional performance must follow that order. A character cannot grieve a confirmed death while they only know someone is missing; cannot recognize a future relative before receiving identifying evidence; and cannot explain a time jump, culprit, relationship, or sacrifice merely because the writer knows it.

Useful progression:

```text
ordinary assumption -> anomaly noticed -> evidence checked -> tentative hypothesis -> emotionally costly recognition -> action based on partial knowledge
```

If the character never receives full proof, let the final behavior reflect a plausible partial understanding rather than false certainty.

### Audience and Character Information Ladder

Control two parallel questions:

- **Character question**: what is this person trying to understand right now?
- **Audience question**: what does the viewer suspect, know first, or still need confirmed?

A strong 20-30s scene may let the question evolve:

```text
Who/what is this? -> How can they know that? -> What happened between them? -> What choice or feeling does this truth create now?
```

Do not keep repeating the same mystery after it has been answered. Once identity or mechanism is clear enough, move to the more personal question.

### Character-Defining Question and Line Selection

What a character chooses to ask should reveal values, relationship, and worldview.

- A protective character may ask whether the other person survived before asking what happened to themselves.
- A grieving character may ask whether someone waited rather than demand an exposition dump.
- A lover facing the future may ask whether the life was worth living rather than how the mechanism works.

Test each key line: if any generic character could say it without changing the scene, rewrite it through this character's priorities. Avoid convenient questions whose only purpose is to explain the plot to the audience.

### Evidence Economy and Reaction-First Coverage

Use the fewest clear pieces of evidence needed to make the inference credible.

If physical mechanics matter, show the action. If realization matters more, keep the camera on the observer and prove the event through:

- a precise offscreen sound
- gaze shifting toward the unseen source
- object vibration, reflection, shadow, light, or environmental response
- a delayed breath, pupil, posture, or hand reaction
- one later confirmation rather than an immediate explanatory insert

Useful pattern:

```text
He first states exactly the habitual gesture she will make in the next second; the camera does not cut to her hands and stays on her face. Two small contact sounds come from off-screen; after the second, her gaze drops very briefly, her breath stops, and then she raises her eyes to him again. The audience completes the confirmation through sound and reaction.
```

Do not cut to a phone, handle, hand, key, footprint, or object merely to prove every noun. Use an insert only when the object's physical state, readable information, or later continuity depends on seeing it.

### Prediction -> Verification Beat

For suspense or high-concept hooks, a useful compact proof structure is:

```text
claim/prediction -> short waiting gap -> offscreen or visible verification -> observer reaction -> revised hypothesis
```

The verification must be specific enough to reduce coincidence but small enough to preserve mystery. Do not immediately explain the mechanism after the proof lands.

## Retrospective Reversal and Dual-Meaning Montage System

Use this system when the ending should make the audience reinterpret earlier images or sounds: subjective memory, hallucination, dissociation, deceptive montage, mistaken perception, unreliable experience, or a supplied twist whose strongest effect comes from retrospective meaning.

Do not activate it for ordinary emotional close-ups, product films, straightforward action, or complete scenes that do not need perceptual misdirection. Do not invent a hallucination, hidden reality, death, culprit, or world rule merely to create a twist. If the hidden truth changes a user-specified identity, relationship, motive, or ending, obtain direction approval unless the user already delegated that invention.

### Three-Track Belief Record

Track three different states internally:

```text
Objective truth: what is physically happening
Character perception: what the character currently experiences or can admit
Audience belief: what the available image and sound invite the viewer to believe
```

For every major beat, know:

```text
Visible/audible evidence -> intended surface interpretation -> hidden compatible truth -> later evidence that changes the interpretation
```

Character knowledge and audience belief are related but not interchangeable. A character may be hallucinating while the audience accepts the hallucination as a memory; a character may know the truth while the framing withholds it from the audience; or the audience may suspect more than the character. Performance must follow character perception, while editing, framing, and sound control audience belief.

### Dual-Meaning Beat Map

Before writing the copy-ready prompt, map only the paired beats needed to carry the reversal:

```text
Surface beat:
Hidden real event:
Shared physical carrier:
What must remain different:
Final proof:
```

Useful shared carriers:

- the same action phase: reaching, falling, turning, pulling, embracing, running
- the same subject position, silhouette, contact point, or foreground shape
- the same screen direction or entry path
- the same rhythmic sound family: breath, footsteps, pulse, scraping, beeps, cloth friction
- the same object geometry with a deliberately changed state or meaning

Use two or three strong correspondences rather than a long sentimental montage. Each earlier beat must make sense under the surface interpretation and remain physically compatible with the hidden truth. The ending should reveal a pattern, not introduce an unrelated fact.

### Matched Transition Across Perceptual States

When moving between reality and memory/perception, prefer a physical editorial carrier over decorative transformation:

```text
action begins in one state -> preserve composition/contact/motion direction -> hard cut at the action phase -> action resolves in the other state
```

Lock the elements that sell the match: frame position, action phase, motion direction, hand/contact point, camera height, and dominant sound rhythm. State intentional differences such as age, costume, location, light, weather, injury, or object condition clearly so the model does not treat the change as accidental continuity drift.

Particles, white flashes, morphing, dissolves, and transformation effects are not forbidden, but use them only when the story's perception genuinely requires them. A clean hard cut or sound bridge is usually stronger when the two images already share action and composition.

### Sound Recontextualization

Sound may carry the second reading rather than merely decorate the reveal. Design one compact motif whose cadence or texture can support both meanings:

```text
first hearing: benign or emotionally safe interpretation
return/reveal: the same rhythmic family exposes its actual source
```

Examples include playful beeps becoming an alarm pattern, excited breathing becoming oxygen-starved breathing, affectionate cloth movement becoming restrained physical struggle, or a household rhythm becoming failing machinery. Preserve enough acoustic similarity for recognition, while changing source position, room response, intensity, or accompanying image to reveal the truth.

Do not rely on graphic bodily sound, excessive volume, or a late unrelated effect. If the story works without a dual-use sound motif, use ordinary scene sound instead.

### Camera Stability as a Narrative Arc

Treat stabilization as a scene-level variable when consciousness, safety, or control changes:

```text
stable/ordered -> subtle human correction -> closer and less stable -> perceptual loss of control -> decisive final stabilization or collapse
```

This is a menu, not a compulsory sequence. A false memory may begin `Static` or gently stabilized, reality may intrude through increasingly close `Handheld`, and the final reveal may return to a locked wide shot that forces the audience to inspect the truth. Another story may reverse that pattern.

Do not shake every shot. Bind each stability change to a specific change in perception, physical danger, operator distance, or character control. Preserve face, prop, geography, and action readability.

### Timing and Reveal

For a 25-30s version, a useful proportional shape is:

```text
establish conflict and objective clues -> decision/contact threshold -> sustained surface interpretation with paired beats -> reveal and held evidence
```

Do not copy fixed timestamps mechanically. Give the deceptive middle enough time to feel emotionally real, but reserve enough ending time for two or three decisive pieces of visual or sonic evidence and a readable aftermath.

Prefer an inferable ending over explanatory dialogue or voiceover. The final shot should complete the immediate physical action, reveal the objective state, and hold long enough for the audience to connect the earlier correspondences. Ambiguity is allowed only when the remaining question is intentional; basic spatial facts should still be legible.

### Copy-Ready Prompt Rule

The belief record and beat map are planning tools. Do not print their abstract labels inside the final video prompt. Translate them into exact shots, actions, sound bridges, matched composition, performance state, and timed reveal evidence.

Avoid:

- random happy memories with no physical correspondence to the hidden event
- revealing the objective truth so early that the middle no longer carries a credible surface reading
- a final twist supported only by new exposition
- treating continuity changes as magic morphing when a deliberate hard cut is intended
- continuous heavy handheld movement with no stability progression
- explaining every correspondence through narration after the audience can already see it

## Live Performance Realism System / Lived-in Performance Realism System

Use this system when the scene depends on human presence rather than plot mechanics alone: close human drama, dialogue, everyday realism, intimacy, hesitation, concealment, explanation, lying, regret, memory, restrained grief, soft refusal, or any prompt where the viewer should feel the character is thinking in real time.

Do not print all six modules by default. Select only the modules that solve the scene's realism problem. For ordinary emotional dialogue, 2-4 concise live-performance cues are usually enough. For a long close-up or phone/live-action realism test, use more detail.

### 1. Psychological Motivation Drives Performance

Do not ask the character to "make a face." First decide what the character is doing internally: explaining, hiding, remembering, testing, lying, regretting, pretending to be relaxed, suppressing panic, or trying not to hurt someone.

Then align:

- eye direction and blink timing
- mouth corners, lips, brow, jaw, and throat
- voice texture, pace, hesitation, and pause placement
- breath and small recovery after key words
- whether the smile reaches the eyes

An expression need not finish. When new evidence or a competing task redirects attention, show the forming expression being interrupted and its residue changing gradually; do not reset to neutral at every line. Example: Before the smile has fully formed, a sound from behind the door pulls his gaze away first; his breathing shifts slightly, and the corners of his mouth then fall back. Use only when the interruption has a scene cause, not as a mandatory almost-smile or facial sequence.

Positive pattern:

```text
She does not show sadness directly; she is trying to stay calm. Before speaking she briefly lowers her head, as if organizing her words; when she looks up, her gaze does not fully meet the lens; at the key point she pauses half a beat and the corners of her mouth tighten slightly; at the end she gives a small smile, but it does not quite reach her eyes. Gaze, expression, tone and pauses all serve the mental state of "explaining, with restraint, something she cares about."
```

Avoid:

- fixed fake smile
- empty eyes
- sudden expression jumps
- exaggerated crying/laughing
- face emotion and dialogue meaning not matching
- voice tone detached from expression
- staring into camera without thought
- no pauses, like reading lines

### 2. State-Driven Incidental Body Language

Do not add actions to make the frame busy. Let small actions leak out of the character's current state, social relationship, and speaking purpose.

For serious explanation, hesitation, restraint, or concern, use low-amplitude movements near the body or table:

- small nod
- slight forward lean
- shoulders relaxing with breath
- fingers rubbing cup rim
- re-gripping a cup
- fingertip pause
- adjusting sleeve cuff
- tiny posture correction
- brushing a loose hair only if it fits the social state

Positive pattern:

```text
Action motivation: do not add obvious movement just to make the image busier. She is expressing, with restraint, something she cares about, so her body movement stays small, low-key and close to the table, mainly slight nods, brief pauses, small shifts of weight, subtle contact between fingers and cup, straightening a cuff or a stray strand of hair. The movements look like unconscious reactions that slip out naturally while she thinks and talks.
```

Avoid:

- sudden chin-on-hand pose
- big arm lift
- posed cute gestures
- exaggerated hand waving
- actions that show off movement rather than psychology
- actions that change the character's emotional state by accident

### 3. Biomechanical Linked Motion

Real bodies do not move as isolated parts. When one part moves, connected parts respond.

Useful linked-motion logic:

- Eyes usually react before the head.
- A head turn brings neck and shoulder compensation.
- A hand move involves forearm, wrist, fingers, sleeve, and small torso weight shift.
- Breathing affects chest, shoulders, voice, and pause rhythm.
- A nod is not only the head moving; eye focus, neck, shoulders, and breath all subtly participate.

Positive pattern:

```text
Before she looks up at the lens, her eyes first leave the tabletop, then her chin lifts slightly and her neck follows naturally. While she talks, her shoulders rise and fall slightly with her breath and her weight shifts a little forward and back. When her left hand steadies the cup, the wrist, forearm and cuff move together subtly; do not let the hand move like a separate object.
```

Avoid:

- isolated body-part motion
- head moving while shoulders and neck freeze
- stiff neck
- floating arms
- no breath movement
- missing muscle/cloth linkage
- robot keyframe motion

### 4. Physical Contact and Object Weight

When the character touches an object, write contact as a physical process: before contact, contact, pressure/resistance, and aftermath.

For example, gripping a cup:

```text
Her left fingertips first approach the rim of the cup, pause briefly, then her thumb and index finger steady the side of the cup. The cup stays stable, showing only an extremely slight change under pressure. When the fingers rub the side of the cup slightly, there is a sense of lingering and resistance. As the cuff nears the table it creases slightly; the arm does not pass through the cup or the paper bag.
```

Use contact cues for:

- cup, phone, letter, ring, sleeve, table edge, door handle, chair, bed sheet, sword hilt, bag, paper, glass
- weight, friction, pressure, inertia, cloth tension, shadow/reflection change

Avoid:

- hand-object penetration
- object moving before contact
- floating cups/phones/props
- no weight or resistance
- fingers not aligning to object surface
- clothes with no fold response
- unclear table/body spatial relationship

### 5. Environment Response to Human Action

The character should not feel pasted onto the background. Small human actions should create small environmental responses.

Use subtle feedback:

- loose hair lags half a beat after a head turn
- sleeve fold changes when the forearm moves
- cup reflection changes as a hand approaches
- paper bag edge compresses slightly under touch
- warm light and shadow shift slightly as the character leans forward
- room tone, cloth sound, cup sound, breath, chair creak, or phone vibration responds to action

Positive pattern:

```text
As she leans forward slightly to speak, the warm light and shadow on her face shift subtly, and the loose strands on her forehead sway a little with her head and then slowly settle. As her left hand nears the cup, the reflection on the cup changes subtly with the hand's position. The cuff creases slightly against the table, and the paper bag stays stable but has a real paper texture.
```

Avoid:

- character pasted onto background
- hair completely static
- clothing behaving like a flat texture
- light not responding to body angle
- objects with no reflection or shadow change
- unmotivated wind effects
- environment response becoming too large or stealing attention

### 6. Camera, Light, Focus, and Space Consistency

First decide the shooting condition: phone realism, handheld documentary, restrained film drama, period candlelight, low-key crime, commercial product, or another coherent visual mode. All camera distance, stabilization, focus, light, skin texture, background blur, grain/noise, and spatial scale should belong to that same condition.

Phone/live-action realism is one option, not the default for all cinematic prompts.

Phone realism pattern:

```text
The image looks like a phone shooting naturally indoors at night: a medium close-up, the lens slightly above the tabletop, a slight handheld sway that does not hurt viewing. A warm ceiling light is the main source, and the shadows on the face and hands fall in the same direction. The background is slightly blurred but still reads as a home; the image keeps slight noise, compression and real skin texture. Focus is stable, with a very slight natural breathing feel.
```

Avoid:

- commercial-ad look in a casual phone-realism scene
- perfect studio lighting when the scene claims natural home light
- plastic skin or heavy beauty smoothing
- overly stable camera in a handheld setting
- inconsistent light direction
- wrong scale between character and background
- severe focus drift
- over-clean image with no real texture

### When to Use Lightly vs Strongly

Use strongly for:

- face close-ups
- dialogue-driven scenes
- daily-life realism
- restrained emotion
- lying, explaining, remembering, hiding, testing
- intimate but non-explicit emotional beats
- phone/live-action realism

Use selectively for:

- fights: mainly biomechanics, contact, environment response
- large scenes: mainly camera/space consistency and one human anchor
- product films: mainly contact, light, reflection, material response
- period drama: mainly psychological motive, biomechanics, cloth/light response

## Species-Appropriate Non-Human Performance System

Use this when an animal, creature, robot, vehicle-like character, or other non-human subject carries emotion or narrative attention.

### Core Rule

Do not translate a human emotion label into a human face pasted onto a non-human body. Build performance from the subject's real or established expressive channels:

- sensory orientation: ears, eyes, head angle, antennae, sensors, sniffing, listening, scanning
- body tension and weight: freeze, crouch, lean, recoil, step, paw/foot placement, balance, tail/spine posture
- breathing or mechanical rhythm: panting, breath hold, whine, motor idle, fan speed, light pulse, servo hesitation
- approach and distance: avoidance, testing, circling, retreat, gradual commitment, contact seeking
- contact response: muscle release, head/limb leaning into touch, pressure change, sound, vibration, or power-down
- species/design-specific vocalization only when natural and restrained

### Recognition and Trust Ladder

A useful emotional sequence is:

```text
baseline habit/fatigue -> sensory cue -> orient without committing -> verify -> tentative movement -> second confirmation -> weight shifts forward -> approach -> contact -> tension release
```

Do not jump from first cue directly to maximal excitement unless the story and subject's condition justify it.

### Age, Injury, and Energy Limits

Preserve the body state throughout the emotional turn.

- An old animal may become more alert but should not suddenly move like a young one.
- An injured creature may commit emotionally while still protecting a limb or moving asymmetrically.
- A low-power robot may recognize someone while motors remain weak, delayed, or noisy.

Emotion can change intent faster than the body can change capability.

### Anthropomorphism Boundary

Avoid human-style crying, smiling, brow acting, hugging, nodding, or theatrical grief unless the established species/design supports it. Prefer observable behavior and contact state. A tear, whine, tail movement, light pulse, or head tilt should not be repeated as a generic emotion icon.

### Camera for Unequal Body Geometry

Preserve the relationship axis even when subjects are at different heights. Lower the camera toward the non-human subject's functional eyeline when needed. Replace a forced shoulder foreground with a hand, coat edge, waist, leg, ear, back, harness, or relevant body contour. Keep gaze direction and screen side stable without distorting anatomy to imitate a human over-shoulder composition.

Compact pattern:

```text
The dog is on the left of the frame looking up and right at the person; the person is on the right looking down and left at the dog. When shooting the dog, use the person's arm, waist or hem as a soft-focus foreground on the right; when shooting the person, use the dog's ear and back outline as a low foreground on the left. Keep the same axis, and do not force a shoulder into the low-angle frame.
```

## Intense Emotional Scene Director Chain

Use this for emotional confrontation, restraint breaking, confession, betrayal, reunion, intimacy, or any scene where an internal conflict becomes a decisive physical action.

### Performance Chain

Build the scene in this order:

```text
Inner conflict -> physiological reaction -> micro-expression -> through-line action anchor -> decisive act
```

Example logic:

```text
The character longs inwardly to get closer but outwardly guards the boundary; so the eyelids flutter, the jaw muscles tighten, the Adam's apple swallows dryly; the fingers keep twisting the fabric; when the defense collapses, the hand first lets go, hovers, and only then completes the approach or touch.
```

### Recurring Action Anchor

Choose one small action or prop to carry the emotional continuity:

- gripping and releasing a bedsheet, sleeve, cup, letter, ring, door handle, phone, sword hilt, or chair edge
- a hand reaching halfway, freezing, withdrawing, then finally completing the action
- breath repeatedly stopping and restarting
- gaze avoiding, returning, then locking onto the other person

The anchor must evolve with the emotion. Do not reset the hand, prop, or posture between time blocks.

### Physical Space Before Large Movement

If the scene moves from ECU/CU into a large body action, prepare the frame first:

```text
Before the big action -> camera widens or pulls back fast -> leaves room for body movement -> follows the action by changing camera position/composition
```

Use this before:

- standing, falling, turning over, embracing, pushing away
- full-body confrontation or physical struggle
- throws, tackles, large costume movement

Avoid asking an ECU shot to suddenly show a complex full-body action without a framing transition.

### Action-Motivated Camera

Camera movement should be caused by performance:

- gaze shift -> slight pan
- head lowering/raising -> tilt down/up
- emotional approach -> slow push-in
- sudden full-body movement -> snap pull-back or wider reframing
- fall or drop -> controlled tilt down
- retreat -> backward tracking

Do not add camera movement only to make the prompt sound cinematic.

### Action-Light-Sound Binding

Bind the same action to visual and sonic consequences:

- body crosses blinds -> light stripes break and move across skin
- hand releases fabric -> cloth tension and friction sound change
- turn or fall on bed/floor -> mattress, sheet, floor, dust, or furniture reacts
- object contact -> one clear impact sound and a visible environmental response

This creates one readable event instead of three unrelated descriptions.

### Internal Beats in a Single Take

A one-take scene still needs internal dramatic sections. Use 2-4 beats such as:

```text
Repression established -> relationship trigger -> defenses loosen -> decisive act -> afterglow
```

Keep camera continuity, but let framing, distance, gaze, action anchor, light, and sound evolve at each beat.

## Behavioral Setup-Payoff System

Use this when the ending should prove emotional change without an explanatory speech.

### Four-Step Loop

```text
Establish behavior -> repeat or strain it -> transform its meaning -> complete/stop/reverse/transfer it at the ending
```

Possible anchors:

- waiting posture or repeated gaze toward an entrance
- a hand that repeatedly reaches, stops, or returns to an object
- a cup, ring, door, photograph, coat, chair, or empty place
- a no-touch boundary or fixed physical distance
- a grooming, caretaking, protective, or avoidance habit
- a phrase that changes meaning when repeated

### Payoff Types

- **Completion**: an unfinished gesture finally reaches contact.
- **Stopping**: a repeated behavior ceases, proving release or acceptance.
- **Reversal**: the character performs the opposite of the opening habit.
- **Transfer**: one character begins a familiar gesture, stops, and the other completes it.
- **Recontextualization**: the same line or action returns with a different emotional meaning.

The payoff must remain physically continuous and readable. Do not introduce a new symbolic action only at the ending and call it resolution.

Useful pattern:

```text
At the start, every time she is nervous she grabs the door frame; in the middle her fingers gradually loosen; at the end, after hearing the truth, she does not grab the door frame again but steps over the threshold herself. The character's change of state is completed through behavior, with no extra explanatory dialogue.
```

### Ending State Reversal

Compare the final frame with the opening baseline:

- looking toward the entrance -> no longer looking there
- gripping an object -> releasing it
- avoiding touch -> allowing or initiating one restrained contact
- holding distance -> crossing one step of space
- trying to finish a sentence -> accepting that it need not be finished

Reserve enough time for the viewer to read the changed behavior and its sound. The action result, not the preceding dialogue alone, is the ending.

### Repeated Action Recovery

When an action recurs, show its visible completion, withdrawal or recovery before the next attempt. Give the restart a new stimulus or changed circumstance; vary timing or amplitude only when that change motivates it. Do not force a fixed cycle count, equal intervals, or a pause into deliberately continuous action. Recovery is physical continuity, not a reset of fatigue, emotion or prop state.

Example: She holds out the letter; the other person does not take it; her hand stops and then pulls back to her chest. Only when she hears the other person say her name does she reach out again, and this time she no longer avoids their eyes. Keep the path of the offer and the retreat; do not cover it with a cut or blur.

### Understated Comic Aftermath

Use only for requested or approved dry/black comedy. Let a heightened event resolve into a brief pause, an understated response, and a return to the character's established ordinary concern. Keep the physical aftermath credible; do not auto-add a quip, smile, triumph or gag to serious drama. Allocate actual dialogue and reaction time, and let action sound settle so the line reads; this does not change the default no-music policy.

### Ordinary Drama One-Take Blocking System

Use this for ordinary drama, suspense, romance, family conflict, intimate tension, waiting, investigation, or quiet confrontation when the scene can physically unfold in one continuous space. It is separate from action-fight long takes: the goal is readable blocking, emotional pressure, and spatial continuity rather than impact spectacle.

#### One-Take Arc

Design the shot as one continuous camera sentence:

```text
Opening frame (establishing start) -> moving/approaching (movement or emotional drift) -> relationship turn (turning beat) -> focus/foreground-background shift (focus or blocking shift) -> closing frame (held ending)
```

Each part must change something visible: distance, eyeline, body position, foreground/background relation, light crossing the face, object contact, sound, or emotional pressure.

#### Camera Path and Blocking

- Start with a clear spatial anchor: doorway, corridor, table, sofa, window, mirror, bed edge, kitchen island, hospital curtain, elevator door, or other fixed object.
- Keep one physically possible camera path. Avoid asking the camera to pass through walls, teleport, or circle a small room without enough space.
- Let the camera change shot size through distance, not cuts: `LS/MLS` to establish, `MCU/CU` for pressure, then `Pull-Back` or slight `Track` if a larger body action needs room.
- A true one-take does not imply fixed framing or fixed focal length. Read `one_take_emotional_coverage.md` when emotion, near/far attention or shared contact needs coverage: budget readable detail/reaction landing frames and the continuous route between them. A focus pull alone does not enlarge a distant face. Honor intentionally fixed shots and avoid compulsory close-up/orbit quotas.
- Use foreground objects to create depth: door frame, hanging cloth, glass reflection, table edge, chair back, curtain, hallway corner, bedpost, shelf, or mirror edge.
- If using a foreground occlusion as a hidden transition inside a one-take style shot, the next view must preserve screen direction, body position, lighting state, and emotional continuity.

- For requested observational handheld realism, a small framing or focus correction may follow a specific cause: an unexpected gesture, obstacle avoidance, subject acceleration or stopping. Let the operator notice and recover while preserving readable faces, key actions and the established path. Do not track every new speaker instantly by habit; keep the dramatic center until attention warrants moving. This is not random shake or scheduled error: do not require repeated delays, focus misses, exact subsecond offsets, or imperfections in locked/formal shots. If the user forbids hidden cuts, partial occlusion must preserve the real continuous path rather than conceal a transition.

#### Focus and Attention Shift

Use `Rack Focus` / `Focus Pull` when the drama shifts between:

- a face and a key object: phone, letter, cup, ring, weapon, medicine, door handle
- foreground listener and background speaker
- reflection and real body
- hand action and facial reaction
- outside threat and inside reaction

Focus changes should follow attention. Do not add focus pulls if the story has no competing visual priorities.

#### Multi-Person One-Take Blocking

For 2-4 people in one space:

- When opposing groups, a hostage/contact relation, or a physical boundary makes geography fragile, internally establish three linked facts: the fixed ordering/facing of people and landmarks; the camera's physically accessible route; and the background expected behind each viewed person. For example: river -> railing -> hostage and captor -> confrontation gap -> officers -> crowd. Moving attention to the officers must not move the crowd behind the captor. Characters leaving frame retain their world positions; left/right screen coordinates may change with a motivated camera move. Describe only the essential relationships in the final prompt, and scope any no-crossing restriction to the actual scene rather than banning axis crossings universally.

- Assign stable geography first: who begins foreground/background, screen left/right, seated/standing, near/far from exit or key object.
- Let power shift through blocking: one person steps closer, sits down, turns away, crosses behind another, enters light, blocks the exit, or becomes isolated in background.
- Keep eyelines readable. If the camera crosses the 180-degree axis, do it through a visible move around the characters or a neutral frontal/back view.
- Use focus or body blocking to change the subject rather than cutting: foreground listener sharp -> background speaker sharp -> key object sharp -> final face.
- Avoid making everyone move at once. In a short 10-15s one-take, usually one main mover and one reacting anchor is enough.

#### One-Take Character Reveal Ladder

Use this when a one-take scene must reveal several important characters in a hierarchy, family power tableau, courtroom/banquet/council confrontation, or period-drama group portrait. The useful pattern is progressive disclosure, not dumping all faces at once.

```text
single-character ECU/CU -> visible orbit or move behind the character -> lateral reveal of a second character -> pull-back to show hierarchy and space -> held group relation
```

Rules:

- Start with one face only when identity or authority matters. Keep other characters out of frame or deeply obscured until their reveal beat.
- Use the first character's shoulder, back, hair crown, sleeve, chair, or pillar as a foreground mask while the camera moves. This gives the reveal depth and prevents a random cut feeling.
- Reveal the next character from a motivated direction: slide past the first character's shoulder, pass a column, move around a table edge, or shift focus from foreground back to background.
- After the reveal, pull back or widen only when the spatial hierarchy matters: who stands, who sits, who is foreground/background, who occupies the main seat, who is visually suppressed.
- Keep every revealed character visually distinct: face shape, hairstyle, headdress, costume color, fabric texture, posture, status, and emotional baseline. Use compact identity tags such as `eldest legitimate son - deep teal brocade robe, tall crown`, `eldest legitimate daughter - vermilion gold-woven long dress`, rather than repeating full paragraphs in every beat.
- Do not reveal more than 2-4 key characters in a 10-15s one-take. If the scene needs more people, make extras background silhouettes or split into multiple clips.
- In final prompts, avoid long lighting/style ingredient lists. Put stable atmosphere once, then use reveal beats to describe what changes: face -> back silhouette -> second face -> widened courtyard/table hierarchy.

Useful compact phrase:

```text
One-take character reveal: first establish {character A}'s identity and pressure with an ECU, the camera circles to their shoulder and back to form a foreground occlusion, then slowly trucks along their right shoulder/table edge to reveal {character B}, and finally a Pull-Back opens up the primary and secondary positions in the {courtyard/hall/tabletop}; each character's identity is locked by distinct face shape, hairstyle, costume color, posture and gaze, with no duplicate faces or extra people.
```

#### One-Take Prompt Template

```text
Overview: a {duration} single-scene one-take long shot, {location}, {relationship/emotional conflict}. The camera starts from {opening spatial anchor} and moves continuously along {a clear path} without cutting; the emotion advances through character blocking, focus shifts, foreground occlusion, light changes and sound changes.

0-{a}s: {opening frame and spatial relationship}, {protagonist's initial action/mental state}, camera {Static / Slow Dolly-In / Track}, establishing {the exit/key object/the other person's position}.
{a}-{b}s: {character moves forward or relationship pressure rises}, the camera adjusts with {footsteps/gaze/hand movement}, using `Rack Focus` when needed from {foreground/object/listener} to {speaker/reactor}.
{b}-{c}s: {turning action or line}, character blocking changes the power relationship, the foreground {door frame/table edge/glass/fabric curtain} briefly occludes without breaking spatial continuity.
{c}-end: the camera lands on {final face/object/spatial consequence}, holding 1-2 seconds of silence, breathing, ambient sound or the afterglow of the action.
```

#### One-Take Failure Warnings

- Do not choose one-take for several locations, big time jumps, too many plot turns, or dense exposition.
- Do not use `one-take` as a label while describing invisible cuts, unrelated angles, or impossible camera positions.
- Do not overload the shot with every camera move. One main path plus one motivated focus or framing change is usually enough.
- Do not end at the exact moment of a line, kiss, slap, reveal, or door opening; hold the consequence.

## Dialogue-Driven Performance Control System / Dialogue-Driven Performance Control

Use this when the scene depends on spoken performance: accusation, rebuttal, confession, breakup, apology, interrogation, courtroom pressure, family confrontation, voice message, phone call, or a line that breaks the character's emotional defense.

This system is especially useful for dialogue scenes from 10-30s. Use 16-30s only when the line delivery, listener reactions, pauses, and emotional curve genuinely need the extra time; keep shorter scenes short instead of stretching them.

### Three-Layer Prompt Structure

For complex acting scenes, separate the prompt into three mental layers before writing the final copy:

1. **Global control layer**: duration, location, characters, identity anchors, costume, voice/sound mode, broad visual style, and any required aspect ratio or platform constraint.
2. **Shot timeline layer**: which shot covers which seconds, who is being observed, when view/focus changes, and why the camera changes attention.
3. **Performance control layer**: what the character wants in this line, how emotion changes, which words trigger the change, where the pause/breath happens, how eyes/face/body respond, and which reaction must not happen too early.

Do not let layer 1 consume the whole prompt. If a platform already provides visual style presets, keep style compact and spend more tokens on performance control.

### Scene-Level Performance Contract

Before writing facial beats, define the acting logic in one compact sentence. This is the scene's performance contract, not an abstract theme.

It should answer:

- What does each character need from the other right now?
- Which protective behavior lets them keep functioning: anger, politeness, denial, humor, caretaking, control, or speed?
- What do they fear will happen if they stop speaking or lose that protection?
- How should that motive shape voice, gaze, pauses, distance, and incidental movement?

Useful pattern:

```text
This is not a stage display of sadness. She speaks faster and faster, not to attack him, but because she fears that if she stops she will never get it all out; he stays polite and quiet, not out of coldness, but because taking care of her is how he stops himself from falling apart on the spot. The following lines, gazes, breathing and actions all serve this psychological mechanism.
```

Do not repeat this explanation under every beat. State the contract once, then express it through observable behavior.

### Voice Identity and Temporary Vocal State

Treat voice as part of character continuity, not a generic sound effect.

Lock stable voice identity when dialogue matters:

- vocal age and perceived gender presentation when relevant
- range/register, texture, resonance, and habitual speaking rhythm
- accent or dialect only when the user requests it or the setting makes it necessary
- each speaker's relative loudness and spatial position

Keep temporary vocal state separate from permanent identity:

- fatigue, hoarseness, recent crying, a blocked throat, breathlessness, illness, cold air, or suppressed panic
- how the voice changes under pressure: pitch narrows, pace accelerates, consonants harden, breath fails, or endings lose support

Preserve these anchors across cuts and continuation clips. Do not let a voice suddenly become younger, cleaner, louder, differently accented, or studio-polished without an on-screen cause.

### Nested Shot and Performance Timeline

Build the shot-level timeline first. Subdivide only the shot that carries dense dialogue, several trigger words, or a major emotional crack.

- Primary timing answers: which shot, whose face, and why the view changes.
- Secondary timing answers: how one performance develops inside that shot.
- Keep simple reaction shots simple. Do not fragment every shot into mechanical half-second instructions.
- Make all nested time ranges fit the parent shot and the dialogue delivery budget.

```text
SHOT 2 (3.5-18.0s): over-the-shoulder close shot on the woman, carrying the main pushback and the breaking of her defenses.
3.5-7.0s【Pushback】: ...
7.0-12.0s【Self-justification】: ...
12.0-18.0s【Crack】: ...
```

### Speaker and Listener Acting Tracks

Treat a dialogue scene as two linked performance tracks:

- **Speaker track**: intention, protective emotion, trigger words, voice, face, breath, gesture, and post-line residue.
- **Listener track**: what exact word lands, the delayed physiological or facial response, whether they try to interrupt, and what they suppress.
- When a non-speaker already has a task, choose one compatible ongoing activity and let the line enter, interrupt or coexist with it; preserve hand/prop ownership and finish or suspend the activity visibly. Do not freeze them in anticipation of their turn or invent busywork for every listener. Their eyes may register speech while the hand finishes its prior action; listening does not require staring continuously at the speaker.
- For several people receiving the same event, derive different reaction paths from each person's preceding state, knowledge and role: residual amusement fades for one, ongoing work stops for another, a third needs time to process. Use modest onset/order/amplitude differences when useful, not arbitrary staggered timers or a universal eyes-breath-mouth-body sequence. A common stimulus may legitimately cause simultaneous reactions; avoid only unmotivated identical choreography. Keep one clear reaction focus rather than giving every face equal detail.
- Give the listener a reaction shot when their internal change advances the story. Keep it restrained when the speaker still owns the dramatic center.
- Do not write generic reactions such as `he falls silent` when a visible sequence can show defense -> attempted reply -> swallow -> gaze avoidance -> realization.

Use three different trigger types when useful:

- **Speaker trigger**: a word changes the speaker's own face, voice, breath, or intention.
- **Listener trigger**: a heard word lands, followed by a believable delayed reaction.
- **Interruption trigger**: the listener understands where the sentence is going and enters before it finishes.

Do not make the listener display the final reaction before the relevant word or meaning arrives.

### Interrupted and Overlapping Dialogue System

Use this for arguments, panic, intimate confrontation, family conflict, interrogation, medical emergencies, or any scene where turn-taking itself carries emotion.

For every important interruption or overlap, define only what controls the performance:

1. **Entry trigger**: the word, unfinished syllable, gesture, or inferred intention that makes the second speaker enter.
2. **Entry motive**: denial, reassurance, fear of losing the chance to speak, correction, self-protection, or trying to stop a painful sentence.
3. **Overlap hierarchy**: who began first, who is foreground, relative volume, and whether the second voice supports, competes, or gently takes over.
4. **Yield behavior**: who retreats, continues underneath, changes sentence, or cannot regain the floor.
5. **Interrupted state**: preserve unfinished mouth shape, held breath, failed inhalation, gaze, or the hand motion already in progress.
6. **Audio-spatial continuity**: keep speaker identity, left/right position, distance, room reflection, and lip movement independent and stable.

Useful pattern:

```text
When she hears him say "I've already decid—" she realizes he is ending the relationship and, before the last syllable finishes, cuts in quietly: "Hear me out first." Their voices overlap naturally for about half a beat; his voice is not suddenly muted but loses force under her line and then stops, his mouth still holding the unfinished shape. She does not raise her volume to drown him out; she speeds up because she is afraid of losing her chance to speak; then he yields and his gaze drops.
```

Rules:

- Prefer semantic triggers and approximate natural overlap over hundredth-second micromanagement.
- Do not turn overlap into clean alternating dialogue, identical loudness, or one speaker muting unnaturally.
- Do not let both speakers repeat their full lines after the cut. Split a cross-cut sentence into explicit start and continuation fragments.
- Use overlap sparingly enough that speaker identity and lip-sync remain readable.

### Protected Performance Disfluency

Some irregular speech is intentional acting information, not a generation defect:

- stammering or repeated pronoun starts
- a word that forms in the mouth but has no sound
- failed inhalation, swallow, or throat closure before speech
- self-correction, abandoned syntax, or changing to a safer sentence
- an interrupted phrase that does not restart cleanly
- speech that briefly accelerates because stopping would cause emotional collapse

When used, name the psychological cause and the visible/acoustic evidence. Protect it from automatic smoothing, reordering, completion, or clean studio delivery.

Positive pattern:

```text
When he says "I—I was going to..." it is not a comedic stutter: the first "I" is voiced, the second is only a mouth shape with a failed inhale, his Adam's apple moves slightly and he swallows; he abandons the original sentence and switches to the safer "Don't worry." Do not complete the abandoned sentence, and do not repeat it at mechanical, evenly spaced intervals.
```

Avoid:

- comic stutter, rhythmic looping, audio glitch, frozen mouth, or duplicated syllables without motive
- every line containing a swallow, blink, failed breath, or repeated word
- using disfluency as decoration when fluent speech better serves the character

### Dialogue Playability Audit

Dialogue word count and average speech rate are risk indicators, not hard ceilings. Do not automatically shorten dense dialogue when rapid speech, interruption, overlap, or emotional urgency is the intended performance.

Audit the actual playable timeline:

- local pace for each phrase, including deliberate acceleration and deceleration
- simultaneous speech and how much wall-clock time overlap genuinely saves
- pauses, failed starts, breaths, swallowing, crying, and silence
- listener reactions that must remain visible
- mouth-critical lines that require the speaker on screen
- camera changes, blocking, hand action, and ending residue competing for the same seconds

Preserve all dialogue when the complete line order, lip-sync, emotional turns, reactions, and ending can still play naturally. Do not normalize an emotionally urgent exchange to one global words-per-minute value.

If timing is dense, simplify in this order before cutting dialogue:

1. remove decorative camera movement and unnecessary shot changes
2. reduce secondary gestures, repeated micro-expressions, and environment business
3. let dialogue continue across a reaction shot through a controlled `L-cut/J-cut`
4. preserve intentional overlap and local acceleration when motivated
5. only then explain the remaining conflict and offer a split or user-approved line edit

Do not silently delete plot-changing or character-defining lines. Conversely, do not claim dialogue is playable merely because the user wants every line: if slow delivery, long pauses, many failed starts, complex blocking, and reaction holds create a real conflict, state the risk and recommend a split.

### Scene-Specific Generation Priority

For a complex prompt, state a short priority ladder only when it helps resolve competing instructions.

```text
Dialogue-led: line order, speaker identity, mouth shapes, interruptions and vocal performance > listener reactions > continuous gestures and gaze > camera decoration and environmental detail.
Action-led: action cause and effect, spatial direction, contact and weight > body reactions > camera following > dialogue and environmental decoration.
Emotional close-up: psychological change, micro-expressions and breathing > voice and tear timing > lighting continuity > background motion.
```

When two instructions conflict, simplify the lower-priority instruction. A priority ladder is not permission to ignore continuity, safety, or the user's explicit must-have elements.

### Continuous Gesture and Relational Boundary

Use one recurring hand, prop, posture, or distance change as a continuous acting line when it carries the relationship.

```text
His right hand completes "raise -> hover -> lose strength -> fall" across three shots, and must not be raised again after a cut. The two stay about one meter apart throughout; not touching is not an ordinary prohibition but the visible boundary of a relationship that cannot close the distance right now.
```

Lock who may enter whose space, whether touch is allowed, and what approach, retreat, or withheld contact means. Do not let the model add an automatic embrace, hand-hold, kiss, or reconciliation that changes the scene's relationship state.

### Dialogue Across Cuts and Semantic Edit Points

Let dialogue and editing share one emotional syntax.

- A line may continue as offscreen dialogue across a reaction shot. Use a motivated `J-cut`, `L-cut`, or sound bridge when the listener's face is more important than the speaker's mouth.
- Preserve voice direction, room reflection, distance, and speaker identity across the cut.
- Cut on a semantic event: a trigger word lands, the sentence changes meaning, the voice first cracks, the listener is hit, or a vulnerable phrase is withheld.
- Do not divide dialogue shots by equal duration when the sentence structure suggests a stronger edit point.
- Do not sacrifice lip-sync clarity: show the speaker when mouth articulation carries the beat; move offscreen only when the listener reaction carries more dramatic information.

### Intentional Unfinished Lines

An unfinished line can be a complete dramatic action when the character cannot continue, is interrupted, abandons the sentence, or deliberately refuses to say the final thought.

To use it safely:

- mark the psychological or interpersonal reason the line stops
- state whether the last sound trails off, is cut by another voice, dies after a failed breath, or remains only as mouth shape
- do not let the model invent or speak the missing words
- show the consequence through held mouth, breath, gaze, listener reaction, hand state, or silence
- leave enough readable aftermath that the ending feels intentional rather than technically truncated

Do not use a dash at the final timestamp as a substitute for an ending. If no performance consequence follows, finish the line earlier or redesign the ending.

### Shot-Size Escalation by Emotional Access

Let framing tighten as the character's psychological defense opens.

- Keep `MCU/CU` or an over-shoulder composition while the character argues, explains, or maintains control.
- Move to `BCU/ECU` only when the protective layer cracks, a hidden truth is admitted, the voice breaks, or the final vulnerable line begins.
- Do not start at the tightest possible framing when the scene needs later visual escalation.
- Tie every push-in or tighter cut to a specific emotional access point, not to generic intensity.

### Emotion Barrier / Emotional Protective Layer

Do not jump directly from anger to crying, confidence to collapse, or sarcasm to confession. Real characters often use a protective emotion before the vulnerable emotion appears.

Common protective arcs:

```text
anger protects grief -> voice cracks -> attack fades -> vulnerability appears
sarcasm protects shame -> smile stiffens -> eyes drop -> apology becomes possible
calm protects panic -> breath shortens -> words slow -> body freezes
politeness protects resentment -> pauses sharpen -> mouth tightens -> direct accusation
```

Prompt rule:

```text
Write the protective emotion first, then the protective layer cracking, and finally the true emotion exposed. Do not let anger, sadness and tears all appear from the first second.
```

An optional return to defense can follow vulnerability when the relationship and story support it: a familiar name interrupts anger; the character briefly exposes hurt through a broken phrase, released jaw or avoided gaze; recognizing that exposure, they tighten again and redirect it into accusation or refusal. Bind the renewed defense to that trigger and changed intention, not simply a louder repetition. Do not require re-escalation in scenes that resolve through trust, acceptance or sustained vulnerability.

### Dialogue as Expression Timeline

Do not write a mood label and paste dialogue under it. Treat the line itself as the expression timeline.

For every crucial line, write:

- state before speaking
- first phrase delivery
- trigger word or emphasized word
- pause / breath / swallow
- eye line change
- mouth, brow, jaw, throat, or tear change
- body/hand reaction
- state after the line
- listener reaction when relevant

Positive pattern:

```text
Before speaking she first holds down her breath, and her gaze does not go to the other person right away. The first line, "You knew all along," is low in volume, her lips barely parting, as if she is still keeping up appearances; on "knew" she pauses half a beat and her gaze slides from his face to the table. The second line, "Then what am I?", is clearly softer and slower; when she looks up again the aggression is gone and her eyes start to well up, but the first tear still must not fall.
```

Bad pattern:

```text
She cries very sadly and says: "You knew all along, then what am I?"
```

### Trigger Words and Delay

When a line causes an emotional turn, mark the trigger word and delay the visible reaction by a believable fraction of time.

Examples:

- A character should not cry before hearing the plot-changing word.
- A character should not soften before saying the vulnerable phrase.
- A character should not explode before the accusation lands.
- First tear should appear only after the defensive layer breaks, not at the start of the line.

Useful instruction:

```text
Do not let the tears come early. Tears only begin to gather on the lower lashes after the key word is spoken, and the first drop falls only on the next failed inhale.
```

### AU/FACS Auxiliary Calibration

AU/FACS can help calibrate a close-up, but it is not the main language of the prompt. Always write visible natural-language actions first, then add optional AU tags only for high-stakes face close-ups.

Recommended use:

- Use AU only for long close-ups, extreme emotional control, crying restraint, anger restraint, shame, guilt, blackening, or close dialogue scenes where facial precision matters.
- Use compact tags, not long code strings.
- Include intensity only when it clarifies gradual change: `A` = barely visible, `B` = light, `C` = clear, `D` = strong, `E` = near maximum.
- Write onset -> peak -> release when possible.

Useful AU references:

- `AU1`: inner brow raise
- `AU4`: brow lower
- `AU5`: upper lid raise
- `AU7`: lid tighten
- `AU9`: nose wrinkle
- `AU15`: lip corner depressor
- `AU17`: chin raiser
- `AU23`: lip tighten
- `AU25`: lips part
- `AU26`: jaw drop

Positive pattern:

```text
Natural language first: the inner brows rise slowly, the corners of the mouth sink slightly, the chin begins to tighten; she opens her mouth to keep speaking but has no strength to make a sound. Supporting expression calibration: AU1 + AU15 + AU17, intensity rising from B to C, tears not yet allowed to fall.
```

Avoid:

- using AU as a magic formula without natural-language description
- listing too many AU codes in one beat
- making all facial muscles peak from the first frame
- treating one AU combination as a fixed emotion regardless of gaze, body, voice, and context

### Facial Action Timing

For important expressions, specify the change curve:

```text
onset -> peak -> release / transform
```

Example anger burst:

```text
Before speaking he presses his lips together, clenches his jaw, and pulls his brows inward and down. The first half of the line stays low; on "now" AU25 and AU26 suddenly strengthen, the lips part, the chin tightens, and the volume rises sharply and briefly. Right after the last word he shuts his mouth, the facial muscles retract quickly, and only heavier breathing remains.
```

### Eight-Dimension Acting Formula

Use this as an internal planning formula for dialogue-led acting. Do not print all labels unless the user asks for a table.

```text
Time block -> character's goal -> emotional protective layer/change -> line and trigger word -> facial action -> gaze and body -> voice/breath/pause -> state after speaking and the other character's reaction
```

Compact final-prompt pattern:

```text
{a}-{b}s: on the surface {character} wants to {goal}, but is actually using {protective emotion} to hold back {true emotion}. Before saying "{line}" they first {breathe/pause/look}; on "{trigger word}" {facial action, gaze, body or AU support}, voice {volume/speed/texture}; after speaking {afterglow state}, {other character's reaction}.
```

### Dialogue Performance Conditions

When dialogue is important, attach it to performance conditions:

- exact action moment when the line begins
- voice volume, breath, pace, and vocal texture
- physiological state such as swallowing, broken breath, clenched jaw
- listener's immediate reaction

Keep the dialogue playable within the assigned time. Dense dialogue may remain intact when motivated rapid speech, interruption, or overlap lets the complete performance land; word count alone does not require compression. If full delivery conflicts with required pauses, reactions, blocking, or ending residue, simplify lower-priority visual instructions first, then explain the remaining risk and propose a split or user-approved edit.

## 30s Psychological Stage Timeline

Use this pattern for 20-30s emotion-led scenes where the viewer must feel a full internal turn: farewell, breakup, confession, accusation, reunion, apology, forgiveness, acceptance, or choosing to let someone go. It is a bridge between dialogue-driven acting and ultra-close micro-expression work.

### Core Principle

Do not divide a 30s scene by clock time alone. Divide it by psychological tasks: what the character is trying to do inside this phase.

Good stage names are small verbs or emotional tasks:

```text
Pressing -> Resignation -> Remember -> Regret -> Letting go
Probing -> Defense -> Struck -> Confession -> Aftershock
Restraint -> Pushback -> Crack -> Admission -> Silence
```

Each stage should contain:

- stage title / psychological task
- visible action, expression, eye line, breath, voice, or body evidence
- one short line or a meaningful silence when needed
- how this stage differs from the previous stage
- a clear tear, smile, gaze, breath, or posture timing decision when relevant

### Action + Meaning Workflow

In `Cinematic adaptation strategy`, you may briefly explain why an action matters. In the copy-ready final prompt, keep the visible behavior and only a compact meaning note when it prevents ambiguity.

Good workshop reasoning:

```text
The "brief bitter smile" is not happiness but self-mockery and resignation; "looking back at him" is not an attempt to hold on but a wish to remember his face one last time.
```

Good final-prompt compression:

```text
3-10s【Resignation】: her gaze slowly leaves his face and drifts to the empty ground beside them; her eyelids lower, a very brief bitter smile tugs at the corner of her mouth and falls, her nostrils tighten slightly, her chest rises and falls once, as if swallowing back the hurt.
```

Avoid turning the final prompt into long prose analysis:

```text
Emotional analysis: this action symbolizes her inner sense of fate, regret, memories and a complicated life...
```

### Difference Between Similar Expressions

When the same visible expression appears twice, define the emotional difference.

- First smile may be self-mockery, politeness, defense, or disbelief.
- Last smile may be forgiveness, release, blessing, or exhausted tenderness.
- First gaze may be asking for an answer.
- Later gaze may be memorizing, accusing, forgiving, or saying goodbye.

Useful instruction:

```text
The earlier smile is self-mockery and resignation, the last smile is a tender letting go; do not generate both smiles as the same sweet or fake smile.
```

### Tear Timing and Delay

Control tears as timed events, not generic sadness.

Common sequence:

```text
Eyes reddening without tears -> tears held back -> the first tear falls after the protective layer loosens -> the second tear slides down during the final line or smile -> the ending keeps the tear tracks and the breathing
```

Rules:

- Do not let tears appear before the emotional trigger.
- If the character is restrained, hold tears for several seconds before the first drop.
- Name which tear matters: first tear, second tear, tear line, tear held on lower lashes, tear sliding to the lip.
- Do not overuse tears in every stage; one or two precise tear events are stronger than constant crying.

### Camera Push Bound to Emotional Access

Use camera movement only when emotional distance changes.

- Start with stable CU/BCU when the character is still guarded.
- Use a very slow push-in when the character stops defending or decides to reveal vulnerability.
- Use ECU only for the peak stage: the line, tear, smile, or gaze that changes the meaning.
- Keep the final frame long enough for the viewer to read the expression after the last line.

Do not add push-in, orbit, handheld shake, and rack focus together for a quiet emotional scene. One motivated push or a fixed camera is usually enough.

### 29-30s Farewell Template

Use as a structure reference, not as a fixed story:

```text
Overview: a 29-second realistic cinematic emotional long take; {character} faces "him/her" in front of the lens, centered on {relationship crisis}; it opens on a fixed CU and in the later part pushes in extremely slowly to an ECU. The whole piece completes its emotional curve through gaze, breathing, short lines, pauses and two clear falling tears—no loud crying, no breakdown.

0-3s【Pressing】: she looks straight into the lens, her eyes still clear with no tears, brows slightly knit, lips slightly parted, and says softly: "Do you really have to go?" After speaking she does not press further and stays in the waiting.
3-10s【Resignation】: her gaze slowly moves away and her eyelids lower; a brief bitter smile tugs at the corner of her mouth and falls, her nostrils tighten slightly, her chest rises and falls once, as if swallowing back the ache.
10-17s【Remember】: the camera pushes in extremely slowly; she looks back at the lens, her gaze slowly moving across the other person's face, her eyes red but the tears held back; her lips move slightly and then press together, her chin tightens, her throat moves gently, holding 0.5s of dead silence.
17-23s【Regret】: she lowers her eyes and the first tear falls silently onto her collar; she does not wipe it and does not sob. When she looks up again her gaze has changed from holding on to deep regret; her brows slowly relax and she shakes her head very slightly, like a silent sigh.
23-29s【Letting go】: the camera pushes to a tighter ECU; she makes an effort to raise a very light, very soft smile, and the second tear slides from the corner of her eye past her nostril and stops at her lips. In an almost inaudible but steadied voice she says: "Go." On "go" her voice trembles very slightly and is held down again. After speaking the smile stays on her face, her gaze does not move away, and the final 1-2s are left for the tearful smile and quiet breathing.
```

Compression rule: for 20-24s, reduce to 4 stages. For 10-15s, do not force this full pattern; use a shorter micro-expression timeline instead.

## Long Facial Close-Up Micro-Expression Timeline

Use this pattern when a long head or face close-up must carry the emotion. It is especially useful for quiet grief, restraint, guilt, disappointment, shock, or emotional freezing. The goal is natural transition, not sudden expression jumps.

Template:

```text
0-2s: the character keeps a calm expression, eyes gently lowered, lips naturally relaxed.
2-4s: the emotion begins to shift slightly; the lips slowly press together, the corners of the mouth start to drop little by little, and the eyes turn disappointed.
4-6s: the sadness becomes gradually clearer but stays restrained; the brows knit slightly, the lips stay lightly pressed, the eyes carry hurt and forbearance, and the eyes are slightly moist.
6-8s: the character settles into a forbearing, sad expression, as if trying hard to hold back tears. One or two small, natural tears or tear tracks appear on the cheek, but there is no loud crying and no sobbing; the emotion is quiet and restrained.
Throughout, the expression transitions naturally, the micro-expressions are delicate, with no sudden changes and no exaggerated crying.
```

Adapt the emotion words to the scene:

- Shock freeze: relaxed face -> smile stops -> eyes lose focus -> breath stops -> jaw locks.
- Suppressed crying: calm -> lips press -> eyes redden -> tear line forms -> silent breath trembles.
- Guilt: gaze avoids -> blink slows -> mouth tightens -> brow folds inward -> face lowers.
- Anger under restraint: still gaze -> nostrils flare -> jaw hardens -> fingers tense -> eyes stay wet but unblinking.

When using this pattern, keep the camera simple: `ECU/CU`, stable or very slow `Push in`, shallow depth of field, minimal background motion. Do not overload it with complex blocking.

### Ultra-Close Face Long Take: Emotional Arc System

Use this when the entire scene is an ultra-close face performance and the user wants a dense emotional arc without dialogue. This is not only for crying scenes. It can be adapted to grief, shame, love, shyness, joy, guilt, fear, jealousy, cold cruelty, blackening, resolve, or any story where emotion unfolds mainly through eyes and micro-expressions.

Core setup:

```text
Cinematic extreme facial close-up, fixed camera or extremely slow Push in; soft natural window light or candlelight casts faint shadows on the face. The character's costume and hair stay simple and real. In the first half there is as little body movement as possible; all of the performance is concentrated in the gaze, pupils, lower eyelids, corners of the mouth, lips, tears and breathing. No dialogue throughout.
```

General rules:

- The camera may represent another person if the scene is subjective, e.g. `the camera is her beloved; she looks into the lens as if talking face to face with her beloved`.
- Keep camera stable: fixed ECU/CU, no shake, no complex blocking.
- Use a clear emotional waveform, not a flat mood: recognition -> reaction -> concealment -> leak -> recovery or collapse.
- For beauty/identity-heavy close-ups, define hair, makeup, clothing, accessories, light, and face stability, but avoid turning it into a fashion poster.
- No dialogue unless the story needs it; the face performs the scene.
- The timeline can be 8-10s for full arcs, or compressed to 4 beats for shorter clips.

#### Complex Grief Arc

Use for ancient costume tragedy, betrayal, lost love, fate, grief after realization, or a character silently accepting irreversible loss.

Emotional waveform:

```text
0-1.5s: the unfocused eyes suddenly snap into focus, the pupils dilate slightly, the lower eyelids tremble slightly, showing pure shock and disbelief.
1.5-2.5s: the shock freezes into coldness; one corner of the mouth lifts into a very faint, almost mocking cold smile that does not reach the eyes; the gaze drops and lifts again, with a self-mocking, weary understanding.
2.5-4s: the cold smile gradually deepens into a quiet, slightly trembling smile, as if struggling to keep the last of her dignity; her eyes redden and tears fill the lower lashes but do not fall.
4-6s: the smile completely collapses; the lips press tight and then begin to tremble; the gaze completely loses focus, tears finally roll down in large drops, she lowers her eyelids, her chin quivers slightly, a silent choke.
6-7s: the aftermath of the sob has not faded; she slowly lowers her head, chin tucking slightly, an extremely light sigh escapes her chest, her shoulders sag slightly, as if dropping the last of her forced composure.
7-8s: she takes a deep breath and lifts her head again, her lips straining to curve into a trembling, tender smile; the tear tracks are not yet dry, and her eyes force out a clear sense of release.
8-9s: she raises a hand and carefully wipes the tears with the back of her fingers; the moment her hand touches the tears, the suppressed sobbing surges back, her shoulders jerk uncontrollably, the smile distorts in the tears, and new tears slide down between her fingers.
```

Use only when the prompt has enough time, usually 8-10 seconds. For shorter clips, compress to 4 beats:

```text
Shock snapping into focus -> cold self-mocking smile -> smile collapsing into tears -> forced release overwhelmed again by sobbing.
```

Avoid:

- sudden crying before the emotional logic arrives
- exaggerated sobbing or theatrical grimacing
- too much hand/body action in the first half
- beauty-filter skin that erases tear and eyelid detail
- using this full waveform for every sad scene; reserve it for major emotional turns

#### Shy Love / Seeing the Beloved POV Arc

Use when a character sees the person they secretly love, especially in ancient costume, youth romance, first love, reunion, or restrained affection. The camera can be treated as the beloved's point of view.

Core setup:

```text
Realistic cinematic photographic texture, soft natural afternoon window light, fixed camera position, extreme facial close-up, camera completely still. The character is a young lady secluded in her chambers in a wealthy ancient household; her hairstyle, hair ornaments, makeup and costume are refined but real. No dialogue and no second person throughout. The camera is the woman's beloved; her gaze, micro-expressions and emotional changes all look as if she is talking face to face with her beloved.
```

Emotional waveform:

```text
0-3s: she stops abruptly, her breath catching; her eyes widen slightly at the sudden sight of her beloved and her pupils dilate gently; once she recognizes the person before her, her eyes instantly curve softly and an irrepressible joy spreads warmly from deep within them.
3-5s: shyness rises in her, a faint rosy flush spreading across her cheeks. She hurriedly lowers her eyelids, lashes fluttering, yet cannot help looking up at the lens again; the corners of her mouth curl up uncontrollably and she tries hard to press them down, finally settling into a shy, sweet-but-timid small smile, her chin tucked in slightly.
5-8s: the smile suddenly freezes on her lips; her gaze darts away from the lens in panic, drifting left and right, not daring to look again. She turns her face to one side, the roots of her ears and her neck flushing from extreme shyness, lips pressed tight, her throat moving very slightly, her head lowered a little; only her fluttering lashes and slightly quickened breath betray her flusterment.
8-10s: after holding back for a long time, she finally summons the courage to look up timidly, gazing straight into the lens long and tenderly, as if to imprint her beloved's face on her heart. Her lashes flutter wildly, her nostrils flare slightly, she takes a silent deep breath and slowly lets it out; her lips relax, and secret sweetness and nervous anticipation bloom in a dazed, captivating smile.
```

Use this arc carefully:

- Best with one face, no second person visible.
- Keep the emotion sweet, restrained, and shy; avoid overt seduction.
- Add quality constraints for face stability when needed: face stable, clear features, natural motion, no blur, no flicker, no shake.
- If the scene is not romance, adapt the same structure: sudden recognition -> emotional leak -> concealment -> renewed courage.

#### Coquettish Soft Refusal Arc

Use for safe, non-explicit intimacy, playful sulking, shy protest, or a character saying something like `I don't want to` while the real emotion is closer to softness, trust, affection, and tiny willfulness. It must not read as real fear, coercion, or serious rejection.

Core setup:

```text
Fixed ECU/CU or an extremely slight Push in; the character faces the lens or the person close by, performance intensity kept at about thirty percent; no exaggerated cutesy gestures, no sexualized teasing; the focus is on the gaze, corners of the mouth, breathing, small finger movements and the breathy voice of the line.
```

Emotional logic:

```text
Overall this is not real dislike or refusal, but the small willfulness, soft endearing silliness and safe feeling of being doted on within a close relationship. The line can be "I don't want to," but the gaze, smile and body do not actually push the other person away.
```

Emotional waveform:

```text
0-1s: the character first looks at the lens/the other person, her hand alternating light and firm, her fingertips making small hesitant yet affectionate movements; her head tilts slightly to one side, her eyes carry a soft, cuddly reluctance, and the corners of her mouth press into a slightly awkward curve.
1-2s: the outer corners of her eyes curve slightly, hiding playfulness and the security of being indulged; her lips open and close gently and, in a very light, very soft, nasal breathy voice, she says: "I don't want to." The tone is more a coquettish push-back than a blunt refusal.
2-4s: after speaking, her gaze slips away for half a second and then sneaks back to the other person, and a faint smile creeps onto her lips despite herself; embarrassed, she lowers her eyes slightly, lashes fluttering, shoulders and neck relaxed, her body not pulling back.
4-6s: the light laugh is pressed back to her lips; the corners of her mouth press together and then let a little smile leak out, and her gaze softens further; at the end she keeps the close distance and soft awkwardness, as if still stubbornly arguing while already won over inside.
```

Compression phrase:

```text
She tilts her head slightly, her eyes dodging softly for a moment, the corners of her mouth pressing into an awkward curve, and says "I don't want to" in a very light breathy voice; then she sneaks a look back at the other person and cannot help a faint smile; her body does not pull back, and the emotion is a coquettish soft refusal rather than real resistance.
```

Avoid:

- turning `I don't want to` into fear, panic, disgust, or real refusal unless the story asks for it
- overt seduction, exposed body emphasis, or sexualized camera language
- exaggerated pout, cartoon acting, childish baby voice, or idol-drama overacting
- strong physical pushing, struggling, or coercive blocking

#### Exhausted Silent Collapse Arc

Use when a character has already endured too much and finally collapses inward without dramatic crying. Best for emotional exhaustion, quiet despair, grief after long restraint, hopeless acceptance, powerless love, or a character realizing they cannot change the outcome.

Core setup:

```text
Vertical close shot / extreme facial close-up, fixed camera or an extremely slight slow push, cinematic real-person performance. The character's face fills most of the frame, the head lightly covered by a soft translucent white veil or light-colored fabric; the clothing has real creases and a damp texture, the skin has a natural sheen and small tear tracks, the eyes are red-rimmed, the lashes wet with tears. The lower eyelids show a clear glint of tears. No exaggerated movement and no dialogue throughout; emotional exhaustion is expressed through gaze, lips, breathing, tears and the drooping head.
```

Emotional logic:

```text
This is not wailing but repressed, silent, heartbroken, wronged, disappointed crying that gradually loses strength. The character seems to have just suffered a great hurt, still holding on a little inside; the emotion moves from helplessness and deep sorrow to a sense of fate and a hollow collapse. In the end it is not an outburst but a quiet falling apart.
```

Emotional waveform:

```text
0-1s: the character's face is tilted slightly up, a three-quarter profile close to the lens, the eyes moist and red, the gaze empty and hurt, as if looking at someone. The lower eyelids are brimming with tears, the lips lightly pressed, the shoulders and neck slightly tense, the breathing very light.
1-3s: the gaze slowly falls from the front to below, the eyelids grow heavy, and the gaze shifts from looking at someone to sinking inward. Tears slide silently down the cheeks, the corners of the mouth press down slightly, the lips relax, and the expression turns from hurt to disappointment, as if the last bit of hope inside is slowly going out.
3-5s: she slowly lowers her head; the stillness and the loss of strength in the shoulders increase, the head droops little by little, and the eyes no longer look at the lens. The gaze hides below, the brows go from tense to weary, the lips close lightly and then part slightly, as if swallowing the crying back. The tear tracks on her face keep getting brighter, but there is no loud crying and no screaming, only a silent collapse.
5-8/9s: the head is fully lowered, naturally coming close to the fabric beside it, the eyes almost invisible. The whole person goes quiet; the emotion is not an outburst but the blankness after exhaustion. The shoulders sink slightly, the breathing is very shallow, and at the end she holds a slightly bowed posture, as if she no longer has the strength to cry.
```

Negative requirements:

- no exaggerated body movement
- no dramatic sobbing
- no screaming or visible shouting
- no sudden emotional jump
- no beauty-filter plastic skin
- keep face stable and realistic
- keep tears subtle, natural, and physically plausible

Useful tags:

```text
silent crying, restrained sobbing, fearful hollow eyes, downcast gaze, broken but quiet sadness, emotionally exhausted, quiet collapse
```

## Micro-Expression Action Library

Use these as modular facial-performance beats. Select only the beats that fit the story; do not stack too many expressions in one shot. For a 6-8s close-up, 3-5 beats are usually enough.

### Grief, Shock, and Emotional Freeze

- **Unfocused to dazed**: eyes that had focus suddenly strain wide, then the pupils dilate slightly and the gaze seems to stop on empty space.
- **Eyelid tremor**: the lower eyelids tremble slightly, as if the body is forcibly absorbing a blow.
- **Frozen smile**: the corners of the mouth stop in a half-smile that does not reach the eyes, then gradually lose their curve.
- **Gaze averted then raised**: the character's gaze drops, then lifts again, now carrying a touch of self-mockery, weariness or sudden understanding.
- **Tears suspended**: the eyes begin to redden, tears glisten on the lower lashes, brimming but not falling.
- **Tears rolling down**: the brimming tears finally roll down in large drops, flowing naturally along the cheeks.
- **Mouth losing control**: the smile completely collapses, the lips press tight, then begin to tremble uncontrollably.
- **Gaze losing focus**: the gaze completely loses focus, staring emptily ahead, as if all the light has gone out.

### Numbness, Exhaustion, and Forced Calm

- **Pupils scattered in fear**: the pupils dilate slightly and the gaze cannot settle, as if avoiding a situation too frightening to face directly.
- **Rapid eyelid tremor**: the lower eyelids tremble rapidly, an instinctive reaction to forcibly holding down emotion.
- **Eyes closed, held**: the character suddenly closes their eyes and holds for a second, as if pressing the emotion back into the body.
- **Settling into calm**: slowly lets out a long breath, the lips gradually loosen, the weight sinks, and the gaze changes from panic to weary calm.
- **Contemptuous sneer**: one corner of the mouth slowly and asymmetrically lifts to one side; the smile does not reach the eyes, and the gaze stays sharp.
- **Chin raised, sidelong glance**: the chin lifts and the gaze slants down at what is ahead, with a slight sense of looking down on it.
- **Cold scoff**: an extremely light, extremely cold exhale through the nose, small in size but clear in attitude.
- **Turning resolute**: the gaze drops, then focuses on a point ahead, the lashes stop fluttering, and when the eyes lift again the gaze has become a calm intensity.

### Surprise, Shyness, and Soft Vulnerability

- **Surprise**: the breath suddenly catches, the eyes widen slightly, the pupils dilate gently.
- **Eyes curving softly**: the eyes instantly curve softly, and an irrepressible joy spreads warmly from deep within them.
- **Shy and bashful**: cannot help lifting the eyes, then looks straight at the lens or the other person with restraint, the corners of the mouth curling up uncontrollably.
- **Blushing**: a faint rosy flush rises on both cheeks.
- **Smile pressed into a small smile**: tries hard to press the smile down, but it ends up hidden in a shy, sweet-but-timid small smile, chin tucked in slightly.
- **Bashfulness at being found out**: the gaze sneaks away from the lens, drifting left and right, not daring to look at the other person; the cheekbones are slightly pink, and the roots of the ears and the neck flush deeply from extreme shyness.
- **Pressing lips, swallowing**: the lips press together nervously, the throat moves very slightly once, the head lowers a little.
- **Shyly looking up**: timidly lifts the eyes again, giving a soft, warm direct gaze, lashes fluttering slightly, nostrils flaring a little.
- **Coquettish head tilt**: the head tilts slightly to one side, the eyes carry a soft, cuddly reluctance, the corners of the mouth press into a slightly awkward curve.
- **Breathy soft refusal**: the lips open and close gently, saying a short line in a very light, very soft, nasal breathy voice, for example "I don't want to," the tone like a coquettish push-back, not real dislike.
- **Dodging, then peeking**: the gaze slips away for half a second, then sneaks back to the other person, the eyes still holding closeness and security.
- **Holding back a smile**: the light laugh is pressed back to the lips, the corners of the mouth press together and then let a faint smile leak out, the body not pulling back.

### Calculation, Cruelty, and Dark Resolve

- **Smile draining away**: the smile is pulled from the face bit by bit, the raised corners of the mouth slowly flatten, and the laughter in the eyes seems drowned in dirty water.
- **Appraising and calculating**: the gaze focuses with scrutiny and calculation, as if weighing how useful the other person is.
- **Gaze turning sinister**: the gaze suddenly turns grim and fierce, the pupils contract slightly, the brows press down slightly, and the tail of the brow lifts in a barely noticeable curve.
- **Cold hook of the mouth**: the corner of the mouth is no longer flat but slowly, very subtly hooks up on one side—not a smile, but a cold understanding.
- **True nature revealed**: the whole face is like a mask peeling away, revealing a cold, hard bone structure.
- **Fierce gaze**: the eyes half-narrow like a hawk's, the whites of the eyes glint coldly under the hard light, and the gaze stabs straight in like a knife.
- **Face tightening**: the cheek muscles tighten, the jaw clenches lightly, and a vein on the forehead faintly pulses.
- **Venomous**: venom and hatred slowly well up from the depths of the eyes, the whites take on a faint bloodshot tint, and the gaze is like a viper baring its fangs, locked firmly on the other person.

### Tenderness, Disguise, and Controlled Performance

- **Doting**: looks straight into the lens, the gaze tender and focused, as if looking at someone deeply cherished; there is no guard in the eyes, and the corners of the mouth carry a very faint, melting smile.
- **Smile withdrawing**: the eyes suddenly go still for a moment, something deep within them is quietly drawn away, the pupils contract very subtly; the gaze slowly turns from soft to steady and dark, while the smile still floats on the surface.
- **Disguise peeling off**: the gaze sinks slightly downward, and when it lifts again there is no warmth left in the eyes, only a sharp, contained scrutiny; the smile at the corners of the mouth is slowly smoothed away, bit by bit.
- **Cold smile rising**: only one corner of the mouth lifts, the curve cold and cutting, like a cold blade opening at the lips; the eyelids narrow slightly and the gaze sinks completely.
- **True nature exposed**: the chin lifts slightly, and the lingering amusement and contempt in the eyes are magnified without limit. The whole face is utterly unfamiliar; the image freezes.

### Timing Guidance

- 0.25-0.5s: tiny flashes such as nostril breath, jaw tightening, eye flick, smile twitch.
- 0.5-1.0s: gaze change, blink hold, tear forming, mouth tightening, chin lift.
- 1.0-1.5s: full emotional transition such as smile fading, forced calm, shy glance returning.
- 1.5-2.0s: complex mask shift such as tenderness turning into calculation or smile becoming cruelty.

Always preserve natural transition: no sudden expression jumps, no exaggerated crying, no theatrical grimacing unless the story demands it.

## Emotion-to-Micro-Expression Map

When the user names an abstract emotion, translate it into visible beats. Choose 3-5 beats that fit the character, scene, and duration. Do not use every beat.

### Sorrow / Grief

- Eyes lose focus before tears appear.
- Lower eyelids tremble; blinking slows.
- Lips press into a thin line, then soften.
- Breath becomes shallow; shoulders slightly collapse.
- Tears gather at lower lashes, then one tear falls only if the scene needs visible release.

Typical phrase:

```text
The gaze first loses focus, then the lower eyelids tremble subtly; the lips slowly press together, the breathing becomes shallow, and the tears hang on the lower lashes without falling for a long time.
```

### Astonishment / Shock

- Breath stops for a beat.
- Eyes widen slightly, then freeze.
- Pupils subtly dilate.
- Jaw loosens or locks.
- Hands stop mid-action.

Typical phrase:

```text
Her breath suddenly stops, her hand halts in midair, her eyes widen slightly and then freeze completely, her pupils dilate slightly, as if she has not yet understood what was said.
```

### Holding Back Tears / Suppressed Crying

- Gaze drops to avoid being seen.
- Lips press hard, mouth corners pull down.
- Throat swallows once.
- Nose and breath tremble silently.
- Hand covers mouth only when the character is trying to hide sound.

Typical phrase:

```text
He quickly lowers his head, his lips pressed hard together, his Adam's apple moves once with difficulty, his breath trembles brokenly through his nose, but he makes no crying sound.
```

### Controlled Anger / Restrained Anger

- Stare becomes still and sharp.
- Jaw hardens; molars press.
- Nostrils flare slightly.
- Blink rate drops.
- Fingers tighten on object or fabric.

Typical phrase:

```text
His gaze suddenly goes still, he blinks less, his jawline tightens, his nostrils flare slightly, and his fingers silently tighten on the rim of the cup.
```

### Remorse / Regret

- Eyes avoid the other person's face.
- Brow folds inward, not upward.
- Mouth opens slightly but words fail.
- Chin lowers; body folds inward.
- Hand reaches halfway, then stops.

Typical phrase:

```text
He looks at the other person and then quickly looks away, his brows draw inward, his lips part but he cannot speak, and his outstretched hand stops in midair.
```

### Remorse and Shame / Guilt

- Eyes flick down and sideways.
- Blink becomes slow and heavy.
- Lips tighten asymmetrically.
- Shoulder or neck withdraws slightly.
- Voice lowers or pauses before key words.

Typical phrase:

```text
Her gaze drops away, her blinking slows, the corners of her mouth tighten asymmetrically, and her shoulders draw back slightly, as if she cannot bear the other person's gaze.
```

### Humiliation / Shame

- Head lowers more than gaze.
- Ears, neck, or cheeks redden if visually appropriate.
- Mouth becomes small and controlled.
- Eyes cannot hold contact.
- Body turns slightly away.

Typical phrase:

```text
She lowers her head, her eyes not daring to rest on the other person's face; the roots of her ears and her neck slowly flush, and her lips tighten into a very thin line.
```

### Timidity / Shyness

- Gaze lifts briefly, then escapes.
- Lips press, then a tiny smile leaks out.
- Eyelashes tremble.
- Fingers touch sleeve, cup, hair, or another small object.
- Breath lightens.

Typical phrase:

```text
She timidly looks up for an instant and then away, lashes fluttering slightly; a little smile leaks from the corners of her mouth despite herself, and her fingers unconsciously pinch her cuff.
```

### Coquettish Soft Refusal

- Emotional intensity stays low, around three out of ten.
- The spoken refusal is soft and brief, often a breathy line such as `I don't want to`.
- Eyes and mouth contradict the literal words: gaze dodges but returns, smile is hidden but leaks out.
- The body does not truly retreat; hands, shoulders, and distance remain relaxed or intimate.
- The tone is safe, trusting, and playful, not fear, coercion, disgust, or explicit seduction.

Typical phrase:

```text
She tilts her head slightly, the corners of her mouth pressing into an awkward curve, and in a nasal breathy voice says quietly "I don't want to"; her gaze slips away for half a second and then sneaks back, her eyes still soft, her body not pulling back—refusing in words while already won over inside.
```

### Held-back Love / Restrained Love

- Eyes soften before the mouth moves.
- Gaze lingers half a beat too long.
- Smile almost appears, then is contained.
- Breath steadies near the person.
- Hand moves toward contact, then stops.

Typical phrase:

```text
His gaze softens first, lingering on her face half a second longer; the corners of his mouth almost lift but are held down, and his outstretched hand stops very close to her.
```

### Envy / Jealousy

- Gaze fixes on the rival/object first, not the loved person.
- Mouth corners tighten.
- Smile becomes thin or delayed.
- Eyes return to the loved person with controlled sharpness.
- Fingers make a small possessive motion.

Typical phrase:

```text
She first looks at the hand resting on the other person's arm, the corners of her mouth tightening slightly, and only then looks up at him; her smile is thin, but her gaze turns sharp.
```

### Letdown / Disappointment

- Gaze lowers slowly, not suddenly.
- Tiny exhale through nose.
- Mouth corners fall with exhaustion.
- Shoulders lose structure.
- Eyes stop searching for explanation.

Typical phrase:

```text
Her gaze slowly lowers, a very light breath escapes through her nose, the corners of her mouth fall wearily, and her eyes stop asking.
```

### Release / Relief or Release

- Long exhale.
- Jaw and brow release.
- Eyes moisten but calm down.
- Shoulders drop slightly.
- Small smile appears only after the tension leaves.

Typical phrase:

```text
He slowly lets out a long breath; his jaw and brows finally loosen; his eyes are still wet but no longer tense, and his shoulders drop gently.
```

### Determination / Resolve

- Breath stops, then steadies.
- Eyes lock on a target.
- Chin lifts slightly.
- Blink stops for a beat.
- Hand completes a decisive action.

Typical phrase:

```text
She first holds her breath, then her gaze locks on what is ahead, her chin lifts slightly, her blinking stops for a beat, and the action in her hands finally settles.
```

### Emotional Numbness / Numbness

- Face becomes quiet, almost too still.
- Eyes stay open but unfocused.
- Mouth relaxes without expression.
- Reaction is delayed.
- Voice, if any, is flat and low.

Typical phrase:

```text
His face is quiet almost to the point of blankness, his eyes open but unfocused, his lips loose, every reaction half a beat slow.
```

### Dread / Fear

- Listening precedes looking.
- Pupils dilate; eyes widen but avoid full scream expression.
- Breath becomes shallow.
- Lips part slightly.
- Fingers grip clothing, doorframe, phone, or flashlight.

Typical phrase:

```text
She first stops and turns her ear to listen, then her eyes widen slightly, her pupils dilate, her lips part slightly, and her fingers silently clutch the hem of her clothes.
```

### Vengeance / Revenge Resolve

- Expression becomes calm, not wild.
- Tears or pain recede behind still eyes.
- Mouth corners flatten.
- Gaze sharpens on the target.
- Body becomes more upright.

Typical phrase:

```text
The tears in her eyes slowly retreat deeper, the corners of her mouth flatten, her gaze refocuses, her body straightens bit by bit, and only cold resolve remains on her face.
```

### Icy Menace / Cold Cruelty

- Smile stays on mouth only, not eyes.
- Eyes narrow slightly.
- Mouth corner lifts asymmetrically.
- Head tilts or chin lifts minimally.
- Voice, if any, is soft rather than loud.

Typical phrase:

```text
Only one corner of his mouth lifts, extremely slightly, the smile not reaching his eyes; his eyes narrow slightly, his chin lifts a little, and his voice becomes even softer.
```

### Contained Joy / Restrained Joy

- Eyes brighten first.
- Lips press to hide smile.
- Smile leaks through one corner.
- Breath catches lightly.
- Body leans forward a fraction.

Typical phrase:

```text
Her eyes light up first, then she immediately presses her lips together, but the smile still leaks out from one corner of her mouth, and her body unconsciously leans forward half an inch.
```

### Embarrassment / Awkwardness

- Smile freezes too long.
- Eyes flick sideways seeking escape.
- Throat swallow or dry laugh.
- Hand performs useless small action.
- Silence becomes the joke.

Typical phrase:

```text
His professional fake smile freezes on his face, his eyes dart sideways for help, his Adam's apple moves once, and his fingers uselessly press the phone screen off.
```

## Global Sound and Lighting Baseline

Sound and light are minimum production controls, but they should stay proportional to the scene. Do not bolt on long generic descriptions after every storyboard.

### Placement Hierarchy

1. **Opening/global baseline**: state the motivated main light source, direction or color-temperature relationship, broad contrast, sound bed, and music policy once.
2. **Shot-local change**: inside a shot, mention only changes caused by movement, screens, doors, weather, silence, impact, distance, or emotional focus.
3. **Closing continuity block**: for multi-shot dialogue, suspense, action, continuation, or sound/light-led scenes, add a compact `Overall sound and light` block that unifies voice trajectory, sound tail, source direction, skin tone, shadow continuity, and the ending state.

### Minimum Description Standard

- Give every final prompt at least one motivated light sentence. Name a believable source and what it does to the visible subject or space; avoid empty labels such as `cinematic light and shadow`.
- Use 2-4 concrete sound anchors for most scenes. Even a quiet scene needs a room tone, environmental bed, breath, object sound, or deliberate silence.
- For dialogue, specify the important voice trajectory, pauses/breath, speaker separation, and lip-sync expectation when the model supports generated speech.
- For suspense or shock, design sound narrowing, muffling, interruption, or one isolated sound when it serves the turn.
- For emotional close-ups, keep light direction stable and describe eye catchlight, wet-eye/tear reflection, or the loss of facial readability only when it carries emotion.
- For action, bind footsteps, cloth movement, weapon/object contact, impact, debris, and environment response to visible actions.
- For continuation, preserve the previous segment's main light direction, color temperature, sound bed, acoustic space, and music policy unless the story visibly changes them.

Compact ending block:

```text
【Overall sound and light】
Sound: no music, keeping only {2-4 scene sound anchors}; at {key line/emotional turn} {the sound field changes}, and at the end {breathing/ambient sound/object sound} decays naturally.
Light and shadow: {a believable main light source} comes in from {direction}, and {the warm-cool/light-dark relationship} stays continuous; it changes plausibly only when {characters move/doors and windows/screens/weather change}, and skin tone, eye highlights and shadow direction do not jump.
```

Do not repeat the full block when the same information is already stated clearly in a short single-shot prompt. Compress it into the opening summary instead.

## Sound Design Library

Sound should shape emotion and structure. Prefer concrete diegetic sound over generic music. Use silence actively. In short video prompts, 2-4 sound anchors are usually enough.

### General Sound Rules

- Default to no background music unless the user explicitly asks for music or the scene specifically requires source music. Write `No music / no background music; keep only the necessary spoken dialogue, ambient sound, action sound effects and object sounds`.
- Keep sound grounded in the scene: dialogue/voice, breath, footsteps, cloth, props, impacts, machinery, room tone, weather, crowd texture, and environmental sound.
- Avoid generic score words such as `dramatic music`, `epic BGM`, `sad piano`, or `tense soundtrack` unless music is explicitly requested.
- Use sound to mark turns: a phone vibration, cup click, door lock, monitor beep, thunder, or engine start can carry the story beat.
- Let key dialogue breathe. Do not bury it under music or loud ambience.
- Use sound reduction when shock happens: environment becomes muffled, then one small sound becomes sharp.
- Use sound tail for endings: rain continues, engine fades, room tone returns, music box stops, breath remains.
- Avoid generic phrases like `dramatic music`. If music is needed, describe its role: low cello drone, distant radio song, muted festival TV, single sustained note.
- If no music fits, explicitly say `No music, keep only ambient sound`.

### Subjective Sound-Perspective Arc

Use this when attention, recognition, grief, shock, intimacy, or realization changes how the character perceives the same space.

```text
Objective environment -> perceptual narrowing -> close human/animal/object detail -> rupture or held silence -> environment return
```

- **Objective environment**: establish the real room, street, station, bar, hospital, or crowd at normal distance.
- **Perceptual narrowing**: lower or soften distant ambience after a specific trigger; do not erase it completely.
- **Close detail**: bring forward breath, cloth, paw/foot contact, swallowing, hair, skin, metal, glass, or one restrained vocalization.
- **Rupture**: use a train pass, door slam, impact, announcement, machine start, or deliberate silence only when it belongs to the scene.
- **Return**: after the private beat, let room tone and distant life regain normal perspective so the world feels continuous.

The sound shift must be motivated by attention or an on-screen event. Avoid arbitrary underwater muffling, total silence, or dramatic sound effects that the environment cannot produce.

Compact pattern:

```text
In the first part, station announcements, footsteps and wheel-on-rail sounds keep their normal depth; once the character recognizes the other person, the distant sounds step back one layer but remain, and breathing, fabric and footfalls become the close layer; while the train blocks the view, the low frequencies and wind pressure briefly swell; when the blocking ends the station soundscape returns, leaving only the small sound of a last body landing or an object being set down.
```

### Hospital / Medical Corridor

Use for death notices, waiting, diagnosis, restrained grief.

- Fluorescent light buzz.
- Distant heart monitor beep or low equipment hum.
- Rubber soles on polished floor.
- Wheelchair wheel squeak.
- Curtain rail or metal tray sound.
- Air conditioner low drone.
- Sound can become muffled after bad news, leaving only breath and a single monitor beep.

Typical phrase:

```text
The only ambient sounds are the low hum of the hospital air conditioning, the regular beeping of a heart monitor in the distance, and the light brush of a nurse's soles across the floor; after the bad news lands, the corridor's soundscape instantly goes muffled, leaving only his breathing.
```

### Rainy Night / Car Interior

Use for breakup, confession, pressure, loneliness.

- Rain tapping windshield and roof.
- Wiper rubber scraping glass.
- Engine idle low vibration.
- Turn signal tick or hazard light click.
- Distant traffic softened by rain.
- Phone notification or seatbelt friction.
- Sudden silence after engine shuts off.

Typical phrase:

```text
The sound takes the low, hoarse scrape of the wipers across the windshield as its beat; the idling engine vibrates at low frequency in the cabin, and between lines there is only rain drumming on the roof.
```

### Home / Apartment at Night

Use for phone calls, grief, suspense, isolation.

- Refrigerator hum.
- Phone speaker hiss or vibration on wood.
- Neighbor footsteps through wall.
- Elevator or hallway sound far away.
- Clock tick if the scene needs time pressure.
- Fabric rustle, bare feet on floor.
- Room tone becoming empty after bad news.

Typical phrase:

```text
The voice on the phone carries a faint electrical hiss; in the room there is only the low hum of the fridge and the distant sound of an elevator running; after hanging up, the space suddenly goes empty, leaving only her broken breaths pressed into her palm.
```

### Kitchen / Domestic Intimacy

Use for awkward intimacy, family tension, quiet breakup.

- Coffee machine drip.
- Ceramic cup click.
- Water pipe hum.
- Chopsticks touching bowl.
- Knife against cutting board.
- Refrigerator door seal opening.
- Food steam and small tableware sounds can replace music.

Typical phrase:

```text
No music, only the coffee machine dripping drop by drop, the small clink of a ceramic cup touching the counter, and the two people's deliberately softened breathing.
```

### Old Room / Memory Object

Use for nostalgia, memory, identity, past/present montage.

- Music box mechanical winding.
- Paper, photo, or cloth friction.
- Dusty drawer creak.
- Floorboard soft groan.
- Distant childhood laughter as memory texture, not literal crowd noise.
- Sound distortion to enter memory; clean room tone to return.

Typical phrase:

```text
The clockwork turns with a dry click, the music box melody starts up haltingly, then mixes with very distant children's laughter; on returning to reality the melody jams, leaving only the low hum of the room's air conditioning.
```

### Train Station / Public Waiting Space

Use for reunion, departure, missed chances.

- Distant broadcast with indistinct words.
- Suitcase wheels on concrete.
- Train rail wind.
- Fluorescent buzz or station light flicker.
- Footsteps echo in a large empty space.
- Coat fabric in wind.

Typical phrase:

```text
The wheels of an old suitcase drag a hollow echo across the concrete floor, a distant announcement is muffled and unclear, and wind off the tracks sweeps across the platform, stretching the two people's silence out long.
```

### Office / Elevator / Light Comedy

Use for social embarrassment and timing jokes.

- Elevator ding.
- Fluorescent office hum.
- Phone speaker playback.
- Keyboard clacks.
- Coffee lid click.
- Awkward silence after a line.
- One small sound after silence can become the punchline.

Typical phrase:

```text
The recording played on the phone's speaker sounds dry and harsh in the elevator; after the words end everyone is silent for half a second, leaving only the elevator's ding.
```

### Palace / Period Drama Interior

Use for ancient costume grief, power, restraint.

- Candle flame flicker.
- Distant night watch drum or bell.
- Silk sleeve friction.
- Hairpin or bead ornament tiny sound.
- Footsteps behind screen.
- Paper decree unfolded.
- Silence should feel ritualized and oppressive.

Typical phrase:

```text
No music, keeping only the soft crackle of candle flames, distant night-watch drums and the rustle of sleeves; after the message is delivered, the side hall is as quiet as if pressed down by protocol.
```

### Disaster / Large Crowd

Use for crowd pressure, panic, public crisis.

- Alarm siren.
- Emergency broadcast.
- Metal groan.
- Glass or tableware sliding and breaking.
- Crowd shouts as a texture, not a muddy wall.
- One named character's voice must cut through the crowd.
- Let the crowd drop out briefly when the protagonist sees the key person/object.

Typical phrase:

```text
Alarms and announcements overlap, the metal hull lets out a low twisting groan, and plates slide down the tilted floor and shatter; when the mother sees the child, the crowd noise briefly goes muffled, leaving only her breathing and the hatch alarm.
```

### Product / Car / Premium Object

Use for brand-like texture without becoming an ad.

- Door close with weight and resonance.
- Engine ignition sequence.
- Leather seat friction.
- Paper folding or pen scratch.
- Tire on gravel.
- Watch crown click, metal bracelet shift, camera shutter, depending on object.
- Sound should feel precise, tactile, restrained.

Typical phrase:

```text
The car door closes with a heavy, clean thud and the wind outside is cut off instantly; at ignition the mechanical start-up sound goes from a short burst to a steady low roar, and the leather seats make a faint rubbing sound.
```

### Suspense Without Monster

Use for fear from space and implication.

- Door lock click.
- Phone vibration in another room.
- Floorboard creak.
- Refrigerator hum.
- Elevator far away.
- Breath becomes too loud.
- Do not use loud sting unless the user wants jump scare.

Typical phrase:

```text
After the lock clicks shut, the stairwell sounds are cut off and only the low hum of the fridge remains in the apartment; from deep in the bedroom a phone suddenly vibrates very faintly, one buzz, then stops.
```

### Wuxia / Action

Use carefully; current action rules need more reference refinement.

- Rain on bamboo leaves.
- Cloth sleeve cutting air.
- Metal clash with clear contact.
- Footsteps splashing water or landing on wood.
- Sheath friction before blade appears.
- Thunder delayed after lightning.
- Avoid muddy continuous clanging; make each weapon sound correspond to one clear action.

Typical phrase:

```text
The sound of rain on bamboo leaves fills the background, and every metal clash corresponds to a clear point of contact; when the blade is drawn half an inch from its sheath there is only one clean sheath sound, and the thunder breaks half a second late.
```

## Fight Choreography Prompt Pattern

Use this for staged combat, close-quarters fighting, underground ring scenes, wuxia exchanges, or short action beats where the physical sequence must remain readable. The goal is not literary intensity, but clear attack-defense-counter choreography.

### Core Principles

- Keep the number of active fighters small. For a 10-15s clip, 1v1 is safest; 1v2 or 1v3 needs a simplified focal exchange and explicit non-focal states. A 25-30s stylized 1v2 or 1v3 fight may carry more action changes when `Stylized Multi-Attacker Fight Control` below remains readable.
- Define each fighter's identity, outfit, body type, fighting attitude, and visual anchor before the action.
- Write action as a timed chain: attack line -> perception/reaction -> defense/evasion -> counter -> impact/recovery.
- When an action repeats, use `Repeated Action Recovery`: preserve the visible recovery path and changed trigger instead of looping the same pose or hiding the return in motion blur.
- Specify body orientation and footwork: step back, side slip, lower stance, lateral step, pivot, twist, sprawl, level change.
- Specify contact points: forearm block, palm parry, elbow cover, knee to midline, shoulder check, grip at waist, controlled throw.
- Show weight and physics: lowered center of gravity, torso rotation, braced feet, transferred momentum, dust burst, floor impact.
- Camera should respond to the action: handheld follow, low-angle tracking, short shake on near impact, tilt up during lift, snap tilt down on landing.
- Surrounding crowd should be background pressure only, not extra fighters unless the user asks.
- Keep safety and taste clear: staged and non-graphic. Default to non-lethal when the outcome is unspecified. If the user explicitly requires a fatal result, show it through defeat state and aftermath rather than gore or fetishized injury.

### Consequence, Space and Camera Continuity in Fights

Apply these controls when injury, exhaustion, environmental interaction or changing advantage carries the scene. They are not a mandatory defeat arc, prop checklist or fixed shot sequence. Preserve required story turns and outcomes; leave nonessential connective techniques flexible.

- **Consequences constrain capability:** after a decisive hit or accumulated exertion, carry one relevant limitation into the next action: interrupted breath shortens a counter, an unstable leg delays rising, or reduced grip changes a hold. Distinguish being driven back, recovering support, still able to interfere and unable to continue. An opponent may re-enter through a visible recovery and reachable route, not an undamaged reset. Do not force all opponents to recover or every action to pause and plant both feet. End-state fatigue survives victory or escape.
- **Space and props cause action:** let a body, doorway, table or stair turn constrain attack lanes and the number of attackers who can reach the focal exchange while others reposition or obstruct escape. A blocked attacker must adjust rather than strike through a partner. For story-critical prop use, establish access and necessary release/activation, then preserve grip, use, damage and release before the hands take another object. Show only consequential transitions, not a mechanical inventory. Dirt, water, debris and damage require an established source and contact; they cannot appear before their cause or spread to untouched areas.
- **Camera preserves evidence:** choose wider coverage for geography, support and displacement; closer coverage for meaningful contact or reaction; and a readable ending for the resulting positions and bodily cost. These are functions, not required shot counts or alternating angles. An action cut continues the same movement, direction and contact phase rather than replaying the strike or omitting its cause. Danger may briefly occlude the view or jostle the camera, followed by a motivated recovery of the subject and threat geometry; avoid fixed subsecond obscuration schedules. In a one-take, allow enough retreat, lateral movement or tilt to show essential action rather than locking every event to a tight shoulder view. Camera steadiness may follow changing control and settle on consequences; do not mandate shake, slow motion, shallow focus or a victory pose.

### Stylized Multi-Attacker Fight Control

Use this for heightened 1v2 or 1v3 action in which speed, acrobatics, simultaneous pressure, and a dense 16-30s action chain matter more than ordinary fight realism. Do not turn one successful example into a mandatory template; apply only the controls needed by the requested tone and duration.

**Combat-function signature**

- Give each fighter a compact, non-overlapping signature: weapon ownership and count, preferred distance, dominant attack plane or line, usual entry sector, rhythm, and recovery/re-entry behavior. Distinguish fighters by how they create pressure, not only by names or costumes.
- Preserve weapon ownership and count as hard continuity. Treat exact named techniques as execution vocabulary unless a move carries the story turn.

**Multi-attacker state continuity**

- Each beat has one readable focal exchange. Every other active fighter must remain in a purposeful visible state such as pursuing, re-angling, blocking an escape lane, recovering balance, retrieving the weapon line, changing height, or re-entering from a blind side.
- Do not write turn-taking combat. The non-focal attacker should shape the protagonist's next decision without launching a competing limb-heavy contact at the same instant.
- Use a short `Threat-Handoff Overlap / threat handoff overlap` when focal pressure transfers: `the current attack and defense have not fully ended -> the next attacker has already entered frame, raised a weapon in readiness, blocked the escape route, cast an approaching shadow, or applies pressure with clear footsteps/weapon sounds -> the two threats briefly overlap -> the main attacking relationship completes the handoff`. The next attacker must begin a readable pressure state before the current attacker fully exits or settles.
- Keeping all fighters fully visible is not mandatory. When the frame cannot hold three readable bodies, prove the off-screen attacker's continuing pressure with one precise cue—weapon entering the edge of frame, blocked escape space, moving shadow, approaching footfall, or a forced eyeline—then bring that attacker back on the next causal beat.
- Avoid long unopposed solo runs unless temporary separation is the intended story beat. Prefer one focal contact plus one preloaded or constraining threat over three simultaneous limb-heavy contacts.
- Carry the end state of one beat into the next: stance, travel direction, weapon line, height, balance, and distance become the next action's cause. Do not use `attack -> stop -> reset -> attack`.

**Hard state-change isolation**

- Treat disarming, weapon breakage, weapon transfer, exact weapon landing/embedding, a fighter becoming incapacitated, and a major environment collapse as hard state changes. These are continuity events, not decorative move vocabulary.
- Give one short beat or phase only one primary hard state change. Write it as `trigger -> visible process -> result -> confirmation`: name the hand/weapon or body involved, the causal contact, the travel or fall path, and a brief readable end state before the next event competes for attention.
- Do not stack a precise disarm, exact weapon endpoint, character fall, and a large debris/net/bag collapse inside the same beat. Combine two only when one directly causes the other and the causal chain plus final state can remain visible as a single event.
- For direct-video generation without approved references, `several fighters + dual wielding + mid-fight disarm + multiple exact weapon endpoints` is a high-risk control bundle. If dual wielding is not story-critical, prefer one visually distinct single weapon per fighter. If it is story-critical, dedicate a shot/beat or a suitable reference asset to that weapon state and remove competing hard state changes from the same interval.

**Instruction priority**

1. Hard invariants: fighter count and identity, no fusion/duplication, weapon ownership/count, location, required victory or defeat state.
2. Phase anchors: usually 3-5 indispensable structural events such as an opening near-miss, central pincer, reversal, environmental payoff, and final result.
3. Soft move vocabulary: spins, flips, slides, rebounds, counters, and connective actions that the model may sample or substitute within the same function.

If instructions compete, preserve hard invariants and phase anchors before exact move names, ornamental camera behavior, particles, or repeated negative constraints.

**Sustained high-intensity exception**

- A stylized 25-30s fight may stay at high pressure without a full pause when contrast is created through attack direction, height, distance, focal attacker, shot size, camera side, and environmental consequence.
- High intensity is not permission for visual sameness. Change the dominant relationship or spatial problem between phases, reserve one primary emphasis device such as a near-miss speed ramp or impact hold, and leave a short readable final state.
- Split only when simultaneous contacts, weapon paths, camera moves, and environment events can no longer be assigned a clear causal order. Do not split solely because the action-beat count exceeds one fixed number.

### Fight Prompt Length Budget

The copy-ready fight prompt must follow the duration-based ceiling (in English about 0.6 words per Chinese character): under 2000 Chinese characters for 1-15s, under 3200 Chinese characters for 16-24s, and under 4000 Chinese characters for 25-30s. This excludes `Story diagnosis`, `Cinematic adaptation strategy`, and optional reference-image prompts.

Recommended budget for a 10-15s fight:

- 1300-1800 Chinese characters total.
- 2-3 shots maximum.
- 6-10 timed action beats total.
- 2-4 active actions per shot.
- One short line each for environment, camera, style, and constraints; merge repeated information into the opening summary.

Recommended budget for a 16-24s fight:

- 1800-2600 Chinese characters total.
- 3-5 shots or one readable long-take chain with internal phases.
- 10-16 timed action beats total.

Recommended budget for a 25-30s fight:

- 2200-3400 Chinese characters total.
- Use more than 3000 only when the extra text protects action geography, timing, continuity, or physical readability.
- If the fight still needs more than 4000 characters, split it into consecutive clips instead of increasing action density.
- Organize dense choreography into 3-5 phase anchors. Additional connective actions may remain inside those phases when fighter states, weapon paths, and cause-effect order stay readable; otherwise split into consecutive clips.

Compression rules:

- State character appearance and wardrobe once; do not repeat them in every shot.
- State the location and overall light once; each shot only mentions new environmental reactions.
- Combine attack route, defense, and contact point into one concise beat.
- Do not repeat `real sense of weight`, `handheld camera`, `no gore`, or continuity constraints under every shot.
- Keep only action details that affect readability, physics, continuity, camera response, or model stability.
- For 1-15s fights, more than 10 distinct action beats normally signals overload and should be simplified or split. For 16-30s fights, do not apply a universal ten-beat cutoff: first compress named moves into functional chains and test whether each phase preserves fighter state, weapon ownership, spatial direction, contact, and recovery. Split only if those relationships remain unreadable. Choose a natural bridge such as a different angle/shot-size continuation, match-on-action, or a new completed action phase; use the first segment's tail frame only when exact body position is essential.

Compact action beat example:

```text
-00:03: A throws a right straight punch at the face; B steps back with the left foot and slips sideways, parrying the punching wrist outward with the forearm, and moves laterally off the punch line.
```

Avoid expanding one beat into separate lines for intention, movement, contact, and result unless the action would otherwise be ambiguous.

### Recommended Structure

```text
Duration:
Aspect ratio:
Genre:

Character references:
Character A: ...
Character B: ...

Overall style:
Location, ground material, light source, crowd position, camera style, action texture, safety limits.

SHOT 1（00:00-00:05）
Subject:
The two characters' positions, distance and surroundings.

Action:
-00:01: the attacker makes a clear attack; state the attack path and target.
-00:02: the defender reads the path; state the evasion direction and weight shift.
-00:03: the defender blocks/deflects/counters; state the point of contact.
-00:05: the opponent adjusts their guard or the crowd reacts, motivating the next shot.

Environment:
Ground, obstacles, crowd, dust, breakable objects.

Camera:
Camera position, focal length, how it follows, when it shakes/tilts up/tilts down.

Style:
Speed, weight, realism, genre-film texture.

Constraints:
Character consistency, onlookers do not rush in, no gore, no real injury.
```

### Useful Action Verbs

- attack: rear straight punch thrown, roundhouse kick sweeping at the ribs, knee driving into the centerline, low sweep at the shin, elbow strike pressing in, knife slashing across, sword tip flicking up diagonally
- evade: small step back, side slip, duck, dip and cut in, lean back to avoid, step laterally off the punch line, turn the hips to absorb force
- defend: horizontal palm parry, forearm block, elbow tucked and pressing down, both arms covering the head, shoulder bracing, sheath held crosswise to block, blade spine pressing down
- counter: ride the momentum into the inside line, backhand wrist grab, sheath butt strikes the wrist, shoulder charge breaks through, waist lock, throw using the forward momentum
- impact: wooden board bursts into dust, feet skid leaving dust marks on concrete, onlookers gasp and step back half a step, short crisp metallic sound

### Camera for Fight Scenes

- 24mm wide handheld for close pressure and spatial clarity.
- 35mm medium handheld for readable body movement.
- Low-angle tracking for level changes, knees, throws, and forward drives.
- Short shake only when fist, weapon, or body passes close to camera.
- Tilt up when a body is lifted; fast tilt down or snap pan on controlled landing.
- Avoid excessive blur. Action should be fast but readable.

### Fight Scene Cinematography Rhythm

Use action-film camera techniques to create immediacy, but apply them at specific beats. Do not make the whole scene shaky or tilted.

**Handheld physical shake**

- Use light handheld breathing throughout close combat for realism.
- Use short, sharp shake only on impact beats: punch lands, weapon clash, body hits table, door slams, foot lands after jump.
- Avoid continuous violent shake; it hides choreography.

Useful phrase:

```text
Handheld camera with a slight physical breathing feel; a short shake at the moment of impact, then it quickly steadies, keeping the action's contact points clear.
```

**Dutch angle**

- Use for imbalance, panic, losing footing, being surrounded, or a power shift.
- Best in brief shots, not as the default framing.
- Works well before a reversal: the frame tilts as the defender loses balance, then returns level when they regain control.

Useful phrase:

```text
The camera briefly goes to a slight Dutch angle, reinforcing the character's imbalance and the spatial pressure; after the successful counter the composition returns to level.
```

**Overcranking / overcranked slow motion**

- Use for one key moment only: flying kick, weapon crossing near the face, body lifted, glass/wood dust exploding, a decisive dodge.
- Keep the setup and recovery at normal speed, so the slow motion feels earned.
- Pair slow motion with clear sound change: impact sound drops low, breath or cloth movement becomes sharp, then real-time sound snaps back.

Useful phrase:

```text
At the key moment of impact, it drops into a brief overcranked slow motion, with dust and fabric spreading out in the backlight; after landing it returns to real-time speed immediately and the sound snaps back.
```

**Speed ramp / mixing fast and slow**

- Good rhythm: real-time rush -> brief slow-motion impact -> snap back to fast recovery.
- Use for sprint-then-kick, dodge-then-counter, leap-then-land, throw-then-ground impact.
- Do not speed-ramp every action; choose the emotional or physical peak.

Useful phrase:

```text
The action rhythm mixes fast and slow: the run-up and the charge stay at high real-time speed, the moment of impact is briefly overcranked, and the landing and reaction cut straight back to real-time speed.
```

**Special composition**

- Diagonal composition: useful for protector and protected character, two fighters facing off, or long weapon lines.
- Foreground obstruction: use pillars, door frames, hanging cloth, railings, classroom desks to add depth and danger.
- Low-angle wide shot: useful for heroic entrance, spear sweep, shield charge, or surrounded protagonist.
- Top shot or high angle: use sparingly for geography in crowd fights.

### Action-Fight Camera Movement Selection System

Choose camera movement from the action's dramatic need. Do not treat the following methods as a checklist. In a 10-15s fight, normally select 2-4 principal methods and give each one a clear job: establish space, follow displacement, clarify an exchange, emphasize a decisive impact, or create a motivated transition.

| Camera method | Best use | Writing rule |
|---|---|---|
| **Tracking Follow / follow shot** | pursuit, retreat, lateral exchange, fighters moving through a room | Follow the dominant movement direction and keep the next obstacle or destination visible; do not let the camera overtake the action without motivation. |
| **Visible Orbit / orbiting camera** | face-off, circling footwork, power reversal, showing a 180/360-degree arena | Orbit only while both fighters remain readable and the changing background explains the rotation. Preserve the axis through a visible move; avoid full orbits during limb-heavy grappling. |
| **Rapid Dolly In / rapid push-in** | a fighter commits, a guard breaks, a decisive strike begins | Push toward the intended contact point immediately before or during one major impact, then stabilize. Do not use repeated push-ins for every hit. |
| **Rapid Dolly Out / rapid pull-back** | reveal a fall, throw, environmental landing, new threat, or spatial consequence | Pull back to create physical room and show where the body/object lands. Use before or during large movement, not after the result has become unclear. |
| **Low-Angle Upward Shot / low-angle upshot** | forward drive, dominant stance, lift, leap, weapon rise | Keep feet or the force-generating body line visible; use briefly to magnify force without hiding contact or turning the move into a pose. |
| **Overhead / High-Angle Geography / high overhead shot** | group fight geography, encirclement, escape path, bodies changing formation | Use as an orientation beat, not the main impact view. Show lanes, spacing, exits, and who is surrounded. |
| **Slow-Motion Tracking / slow-motion follow** | airborne movement, decisive dodge, weapon crossing, debris burst | Reserve for one peak beat. Track the complete motion path, then return to real time for landing, recoil, and recovery. |
| **Whip Pan / panning sweep** | sudden attack from the side, opponent crossing frame, thrown object, fast defensive turn | Pan along the real action direction. End on a readable subject or landing point; do not use as random blur between unrelated actions. |
| **Whip-Pan Flash Cut / whip flash cut** | hide a cut at the instant of a strike, accelerate a direction change, join two matching motions | Cut inside the motion blur while preserving direction, speed, body pose, weapon hand, and screen position. Use once at a major acceleration beat. |
| **Micro-Montage Inserts / close-up inserts** | fists, feet, grip, eyes, weapon edge, impact preparation | Use 2-3 very short inserts only when they clarify cause and effect. Return to a wider readable shot before the main body action. |
| **Ped Up/Down or Crane Rise/Fall / vertical camera move** | stair pursuit, jump/drop, stand-up recovery, changing vertical advantage | Move vertically with the action and reveal the new level or destination. Do not substitute a tilt when the camera itself must change height. |
| **Foreground Occlusion Wipe / passing through walls and objects** | move between adjacent fight zones, disguise a cut, reveal a new attacker or room | Let a pillar, wall edge, vehicle, hanging cloth, or foreground body fully wipe the frame; emerge with matching movement direction and preserved spatial logic. |
| **Shot/Reverse Shot / reverse shots** | clarify attack-defense alternation, reaction, feint, stare-down | Keep eyelines and screen sides stable. Change horizontal angle by at least 30 degrees within the same scene and avoid adjacent near-identical shot sizes. |
| **Rotating Pan/Orbit / rotating pan** | circling duel, clinch rotation, chained attacks that revolve around one center | Let fighter rotation motivate the camera rotation. Keep a stable visual anchor in the environment so the viewer does not lose orientation. |
| **Impact Hold / frozen hold** | one decisive non-graphic hit, block, collision, or near-miss | Use an ultra-brief impact hold, near-freeze, or speed-ramp plateau rather than a long literal freeze. Preserve recoil, sound, and immediate recovery so the strike retains physical continuity. |

#### Selection by Fight Beat

```text
Establishing space: Overhead/High Angle, Visible Orbit, FLS/LS establishing shot
Chases and displacement: Tracking Follow, Whip Pan, Ped/Crane movement
Readable attack and defense: Shot/Reverse Shot, Micro-Montage Inserts, medium handheld tracking
Escalating force: Rapid Dolly In, Low-Angle Upward Shot, Rotating Pan/Orbit
Throws and landing points: Rapid Dolly Out, Ped Down, overhead geography
Climactic hit: Slow-Motion Tracking or Impact Hold, choose one dominant emphasis
Hidden cut: Whip-Pan Flash Cut or Foreground Occlusion Wipe, only with matched direction/action
```

#### Combination Rules

- Tie every camera move to a verb in the choreography: pursue, evade, rotate, lift, fall, reveal, strike, recover. If the camera move has no action cause, remove it.
- Keep the action chain readable before adding impact style. Show full bodies for footwork, throws, leaps, grappling reversals, and landings; use close inserts for preparation, grip, expression, or one contact detail.
- Do not combine rapid push, whip pan, orbit, Dutch angle, slow motion, and impact hold in the same beat. Choose one primary emphasis and at most one supporting camera response.
- For edited fights, preserve the 180-degree axis, screen direction, eyelines, weapon hand, and action velocity. Use match-on-action for cuts inside a strike, dodge, fall, or weapon swing.
- For continuous long takes, use only physically connected camera paths. Foreground wipes may disguise stitching, but the resulting shot must still feel like one navigable space.
- Let impact breathe for a fraction of a beat, then show recoil, pain response, balance recovery, environmental reaction, or the next threat. Do not freeze at contact and omit the physical result.
- Use camera movement to vary rhythm: readable setup -> mobile exchange -> one emphasized peak -> stable aftermath. In realistic fights, continuous maximum intensity usually weakens impact. In stylized 25-30s fights, pressure may remain high when direction, height, distance, focal attacker, shot scale, and environmental consequence keep changing; avoid repeated movement texture and still preserve one dominant emphasis and a readable aftermath.

Useful compact phrase:

```text
Camera movement is assigned by action function: an FLS follow shot establishes the chase direction, reverse shots keep the axis at attack-defense turns, a Rapid Dolly Out before a throw leaves room for the landing point, the decisive hit uses only one brief Impact Hold, then immediately returns to real-time speed and shows the recoil, panting and environmental feedback; do not pile up unmotivated whip pans, orbits and slow motion.
```

### Fight Rhythm Planning

A strong 10-15s fight should usually have a rhythm arc:

```text
0-3s: establish positions and the first strike, real-time speed, clear space.
3-7s: continuous attack and defense, close handheld, short shakes, clear points of contact.
7-10s: a brief pause or loss of balance; a Dutch angle/breathing/a stare-down creates a change of rhythm.
10-13s: explosive action—a sprint, a leap, a throw or a weapon counter.
13-15s: back to real time after the overcranked impact, leaving half a second to a second of afterglow.
```

For 30s split into two 15s prompts:

- Segment 1: pressure, first exchange, incomplete reversal, ending on danger or an unfinished action.
- Segment 2: continue the same story state from a new angle/shot size, complete the reversal, finishing impact, aftermath.

### Safety and Negative Constraints

Choose outcome-specific constraints. When no fatal result is requested, use:

```text
Cinematic stunt fight, non-lethal, no gore, no real injury; keep the characters' faces, hair color and costumes consistent; no limbs clipping through bodies, no extra hands or feet, no weapon deformation, no confused action direction; onlookers only react in the background and do not rush into the fight.
```

When the user explicitly requires a fatal result, preserve the narrative outcome without graphic injury:

```text
Cinematic stunt fight, non-gory; death is expressed only through the decisive action, loss of ability to act, the state of being down, and the survivors' relationships, with no open wounds, dismemberment, spray or injury voyeurism; keep character identities, weapon ownership and where the bodies fall continuous.
```

### Common Failure Fixes

- If the fight becomes chaotic, reduce active actions to 2-3 clear exchanges.
- If bodies deform, reduce grappling complexity and avoid simultaneous limb-heavy actions.
- If spatial direction is unclear, anchor the fighters: `A on the left of the frame, B on the right of the frame`, then maintain screen direction.
- If impact lacks weight, add stance, momentum transfer, floor reaction, dust, cloth movement, and a short camera shake.
- If the crowd distracts, describe them as dark silhouettes forming a fixed semicircle.

## Hong Kong Crime Long-Take Close-Quarters Fight

Use this for 1990s Hong Kong crime action, rain-soaked alley fights, car-side brawls, gangland chases, and brutal close-quarters 1v1 scenes where the user wants an unbroken handheld long take. Abstract the reference into transferable action design; do not depend on naming or imitating a specific living choreographer.

### Core Feel

- Style: gritty Hong Kong crime realism, wet neon, narrow alley, handheld 35mm film grain, practical tungsten/neon light, rain mist, steam, wet asphalt.
- Camera: one continuous handheld take unless the user asks for cuts; full-body readability comes first, then close body texture.
- Action: no posing, no decorative martial-arts display, no impossible fantasy movement. Favor boxing, elbows, knees, clinch, wrestling, wall/car impact, ground control, neck escape, and short-range survival movement.
- Physics: every attack needs stance, momentum, contact point, recoil, environmental reaction, and pain/breath feedback.
- Safety/taste: staged movie fight, adult performers, non-graphic injury only. Use rain/sweat/minor blood spray sparingly; no gore, no fetishized damage.

### One-Take Action Chain

Write the fight as an uninterrupted cause-and-effect chain:

```text
spatial anchor -> weapon/object threat -> evasion -> entry -> takedown/clinch -> environment impact -> ground control -> reversal/lock -> body shot -> escape -> counter elbow/knee/punch -> camera orbit/reframe -> finishing impact -> breath/aftermath close-up
```

Keep one dominant direction at a time. The camera may orbit, but the fighters' positions, distance to walls/cars/doorways, and screen direction must remain understandable.

### Useful Beat Library

- opponent grabs pipe/bottle/brick and swings horizontally
- protagonist ducks under the swing and shoots forward into a waist/body lock
- both bodies crash into a parked car, shutter door, wall, trash bins, or wet pavement
- camera stays close to torsos during the scramble, then widens just enough to keep limbs readable
- mounted position with short staged punches; defender covers, bridges, turns the hips, and reverses
- clinch against car hood or wall; knee to ribs or thigh; elbow to jaw/shoulder line
- rear headlock/neck control, followed by hand fighting, chin tuck, hip turn, and escape
- final controlled slam into a car hood, shutter, padded wall, stacked boxes, or breakaway surface
- final breath: both bodies stop for 1-2s, rain and engine metal sound continue, camera pushes to wet face close-up

### Camera and Spatial Continuity

- Start with a strong alley geography: wall on one side, parked car or shutter on the other, wet ground, exit direction, neon source.
- Use handheld lateral tracking as the fight starts; avoid random shake before impact.
- Keep both fighters' full bodies visible during throws, takedowns, and reversals.
- Go close only for grounded scrambling, clinch pressure, breath, hands fighting for grip, or facial aftermath.
- A 180-degree camera orbit is allowed inside a one-take fight only if the orbit is visible and motivated by the fighters rotating or colliding through space.
- If the camera must come very close, immediately re-open the frame before the next large body action.
- Do not hide contact with excessive blur, foreground obstruction, or chaotic whip pans.

### Environment and Sound Feedback

Bind each heavy action to visible and audible consequences:

- pipe swing cuts through rain -> water beads scatter past lens
- shoulder drive into car -> metal panel booms, rainwater jumps, alarm chirps or hood dents slightly
- body hits wet ground -> splash, clothing sticks, breath knocks out
- elbow or knee lands -> short grunt, head/torso recoil, handheld jolt
- clinch scrapes along shutter -> metal rattle
- final car-hood impact -> controlled dent, rainwater sprays, then breath and rain dominate

Use diegetic sound only: rain, footsteps splashing, metal impact, cloth friction, breath, grunts, pipe scraping, car alarm chirp, distant city hum. No background music by default.

### Prompt Template

```text
Overview: a 10-15 second one-take Hong Kong-style crime action long shot, {location and period atmosphere}, two adult characters fighting at close quarters. A handheld camera follows continuously, keeping spatial continuity and full-body action readable throughout, no music.

Action chain:
0-2s: {spatial anchor}; the opponent grabs {object} from {direction} and swings it horizontally, the attack line aimed at {the head/upper body, non-lethal areas}; the protagonist {ducks/slips sideways/steps back} to avoid it, and the camera follows from the side.
2-5s: the protagonist lowers their center of gravity and cuts in, {waist grab/shoulder charge/leg control}, using the forward momentum to drive the opponent into {a car/a wall/a roller shutter}, and the environment produces {a metallic sound/a splash/a vibration}.
5-8s: the two roll or grapple {beside the car/on the ground/by the wall}; the protagonist gains brief control, and the opponent completes a reversal with {a block/a bridge roll/a neck lock/a counter-clinch}; the camera stays close to the bodies but keeps the limb relationships clear.
8-12s: the protagonist breaks free and counters with {a hand release/a hip turn/a knee strike/a reverse elbow}; rain, sweat and a few non-gory scrape marks fly; the camera rotates half a turn around the two, or a visible 180-degree orbit.
12-15s: the protagonist completes one controlled finishing move, driving the opponent into {a surface that can take it}, and the environment clearly deforms or shakes; the last 1-2 seconds are left for panting, the camera slowly pushing in to a rain-covered facial close-up.

Constraints: adult performers, cinematic stunt fight, non-gory; real human body mechanics, continuous action chain, no posing, no flying or exaggerated martial arts, key contact points not blocked, no limbs clipping through bodies, no excessive motion blur, no background music and no subtitles.
```

### Compression Notes

For final prompts under the duration-based character ceiling, compress this pattern by keeping location and one-take structure, the strongest action beats, environment feedback for major impacts, camera continuity/readability rules, diegetic sound, and negative constraints. Cut repeated style tags first. Do not cut attack-defense causality or final breathing room.

## Tavern Brawl / Environmental Fight Pattern

Use this for messy but readable fights in taverns, inns, warehouses, gambling rooms, markets, docks, alleys, or any place where the environment is part of the choreography. This pattern differs from clean ring combat: the scene should use furniture, bottles, pillars, stairs, railings, walls, lamps, dust, and bystanders as action texture.

### Environmental Action Logic

- Start each beat with a clear spatial anchor: who is near the table, pillar, stairs, counter, door, wall, or crowd.
- Make the environment react to impact: table legs scrape, stool flips, wine jars shatter, dust bursts, wooden planks crack, lamps swing, crowd backs away.
- Use objects as temporary obstacles, shields, or impact surfaces, not random decoration.
- Keep one active action per beat. If a fighter kicks a stool, the stool's path and effect should be clear.
- Write the cause-and-effect chain: body movement -> object contact -> object reaction -> opponent reaction -> camera reaction.
- When wind, waves, a moving vehicle/platform or a slippery surface actually changes the action, also use the reverse chain: environment change -> lost support or blocked route -> body adjustment -> new action/result. Establish the forcing direction and available support, and keep loose objects responding consistently. Example: The deck tilts, and loose wooden barrels slide toward the low side; the character loses balance with it, grabs the railing to steady himself, then continues the original action. Use only the environment changes needed for the beat; do not add a disaster to an ordinary scene.
- Use short environmental aftermath to sell weight: broken wood settles, liquid spreads, dust hangs in light, bystanders freeze or step back.

### Body and Object Contact Points

Useful contact points:

- palm hits table edge
- shoulder drives opponent into pillar
- boot hooks stool leg
- elbow knocks wine jar aside
- forearm blocks bottle swing
- knee pins opponent against table
- back slams into wooden wall
- hand grabs collar or belt before throw
- opponent rolls across tabletop and knocks bowls aside

Typical phrase:

```text
He drops his right shoulder and rams into the opponent's chest; the opponent's back slams hard into a wooden pillar, the oil lamp on the pillar swings wildly, the wine bowls at the edge of the table jump half an inch, and the camera gives a short shake with the impact.
```

### Camera Switching for Environmental Fights

- Establishing shot first: show room layout, fighters, crowd, tables, door, stairs, or counter.
- Medium handheld tracking for body movement through space.
- Low-angle close shot for kicks, stool sweeps, feet sliding, and floor impact.
- Over-shoulder shot for an incoming object or surprise attack.
- Fast pan or whip pan only when following a thrown body/object; keep the landing clear.
- Short impact shake on collision with table, pillar, wall, or floor.
- Cut to close-up of object reaction only if it helps clarity: cracking tabletop, spinning bottle, dust burst, blade or fist stopping short.
- After a big impact, hold half a beat so the viewer understands the result before the next attack.

### Shot Beat Template

```text
SHOT X（00:00-00:04）
Subject:
A is on the left side of the wooden table, B is in front of the counter, onlookers back against the walls, and the tables and chairs form a narrow passage.

Action:
-00:01: A turns sideways to dodge the wine jar B swings, and the jar grazes past his shoulder and smashes into a wooden pillar.
-00:02: A presses the table edge with his left hand and hooks a wooden stool off the floor with his right foot, kicking it at B's knees and forcing B back.
-00:03: B raises an arm to knock the stool away, splinters and dust fly; using the cover, A charges in half a step and drives his shoulder into B's chest.
-00:04: B's back slams into the counter, the wine bowls on the counter fall off one after another, and the onlookers scatter with cries.

Camera:
Handheld medium shot trucking alongside; a brief blur as the stool flies past in front of the lens; the camera shakes lightly at the moment of impact with the counter, then holds half a beat to confirm the result.
```

### Tavern Brawl Negative Constraints

```text
No crowd rushing into the fight, no props floating randomly, no tables and chairs jumping position, no clipping, no extra limbs, no excessive motion blur, no gory injuries.
```

### Suppression Burst -> Dead Pause -> Finishing Stunt Rhythm

Use this pattern for an intense staged fight where one character overwhelms another, then the scene breathes for a moment before a final cinematic stunt impact. Best for abandoned classroom, warehouse, underground ring, hallway, locker room, train carriage, or other confined spaces with breakable environment.

This pattern is different from exchange-based choreography. It has three dramatic phases:

1. **Suppression combo / Suppression burst**: one fighter pins or restricts the other and delivers rapid close-range stunt strikes.
2. **Dead silence pause / Dead pause**: the aggressor releases, steps back, both breathe, and the space becomes tense.
3. **Finishing stunt impact / Finishing stunt impact**: the aggressor sprints, jumps, kicks, throws, tackles, or slams the opponent into a controlled breakaway environment.

Recommended structure:

```text
Shot 1 (00:00-00:05)
Subject: A on the left of the frame, B on the right of the frame, B pinned against {furniture/a wall/the ring edge/a train seat}.
Action:
00:00-00:01: A restricts B's movement with {hand/forearm/collar grab/shoulder pressure}.
00:01-00:04: A throws a rapid series of close-range cinematic stunt punches/elbows/knees; B leans back, defends and absorbs the impacts, his body hemmed in by the environment.
00:04-00:05: the combo's rhythm reaches its peak, and the camera gives a short shake with each strike.
Camera: handheld medium shot, camera position basically fixed, a short violent shake on each strike; a slight fisheye vignette can be used to create claustrophobic pressure.

Shot 2 (00:05-00:08)
Subject: A releases B, and B leans beside a support that is about to collapse.
Action:
00:05-00:06: A steps back half a step or a step, arms hanging, breathing hard, eyes still locked on B.
00:06-00:08: B loses support and leans on {the chair back/the wall/the railing/the table edge}, dazed but still struggling to stand.
Camera: medium shot pulling back slightly, slight handheld movement, the rhythm shifting from violent to a tense pause.

Shot 3 (00:08-00:15)
Subject: A sprints in fast from one side, B stands swaying in front of the wrecked environment.
Action:
00:08-00:10: A suddenly takes a run-up, hair, hem and jacket flying with the movement.
00:10-00:12: A leaps into the air or bursts forward, delivering a high stunt flying kick/shoulder charge/knee strike/over-the-shoulder throw aimed at non-lethal areas such as the upper chest, shoulder or torso; the action can go into clear slow motion.
00:12-00:13: at the moment of impact the camera almost freezes, the environmental props burst and collapse, splinters, dust and debris rise in the backlight; B flies backward or falls in a controlled stunt move.
00:13-00:15: B lands dazed and drained but still alive; A lands and stops in the foreground breathing hard, and the final image holds on a wide shot of the wreckage.
Camera: a wide shot pans quickly to follow the run-up; at the moment of the flying kick or impact it cuts to an action close-up and slow motion; then the camera tilts down or trucks to follow the backward flight/landing, finally resting on a wide shot of the environmental damage.
```

Key writing points:

- Make the initial restriction clear: collar grip, shoulder pin, forearm press, wall pin, chair/table limit, cage edge.
- Rapid strikes should remain staged and non-lethal. Avoid detailed gore; use impact, breath, recoil, furniture vibration, dust.
- The pause is essential. It gives the viewer time to feel the previous impact and prepares the final burst.
- The finishing stunt should target non-lethal areas such as upper chest, shoulder, torso, midline, or controlled side impact.
- Environmental breakaway must be readable: stacked desks, broken chairs, wooden crates, cardboard boxes, padded railing, breakaway wall panels.
- Use lighting particles to sell impact: dust in side backlight, wood chips in cold light, fabric and hair movement.
- Keep identities stable during fast movement: repeat hair color, hairstyle, clothing, and visual anchors in every shot.

Useful style phrases:

- `oppressive, violent, claustrophobic, cold grey-blue tones, high-frequency strike shakes`
- `a brief dead silence before the outburst, a suffocating sense of standoff`
- `high-impact cinematic action stunts, strong light-shadow contrast, falling into brutal dead silence after the climax`
- `fisheye lens vignette and slight distortion, the physical shake of handheld camera`
- `strong side backlight through venetian blinds, dust particles floating in the light beams`

Safety constraints for this rhythm:

```text
Only a cinematic stunt fight: non-lethal, no gore, no death, no broken bones, no broken necks, no open wounds, no clear serious injury; characters land in controlled stunt moves and are still alive; keep the characters' faces, hair color, build and costumes consistent.
```

### Epic Crowd Fight / Protector Entrance

Use this pattern for cinematic crowd fights where a central character is surrounded and a protector or hero enters to break the siege: palace coups, throne hall sieges, bodyguard rescues, battlefield entrances, gang encirclement, spear/sword heroics, and multi-segment continuation using previous final frames.

This pattern is about action staging, character hierarchy, continuity, and camera movement. Do not force a 3D animation style unless the user explicitly requests it.

Core cinematic intent:

```text
A cinematic epic group battle: the protagonist is surrounded layer upon layer, and a guard/general/hero makes a forceful entrance as the action anchor, breaking the siege with sweeping long-weapon strikes, flying kicks, charges, slow-motion impacts and high-speed follow shots. The image emphasizes character positions, crowd pressure, character continuity, spatial layering and a strong sense of impact.
```

Continuity rules:

- Preserve the same visual style across all segments, but let the style follow the user's requested medium: live-action cinematic, realistic period drama, stylized fantasy, 3D animation, etc.
- State that character faces, costumes, hairstyles, weapons, soldier designs, and location remain consistent with previous segment/reference material.
- If continuing, do not default to copying the previous tail frame as the next first frame. Choose a bridge: different shot size/angle for continuous danger, match-on-action for unfinished movement, or a new 15s shot group for the next completed action phase.
- Use material references explicitly when present, e.g. `positions of the princess and the ancient soldiers per reference material 1`, `last frame of the previous video per reference material 2`.
- Keep the location name consistent, such as `Golden Throne Hall`, `abandoned classroom`, `underground fight ring`, `palace gate steps`, or the user's exact scene label.

Recommended segment structures:

**1. Encirclement setup, 5-8s**

```text
Image 1: a low-angle side follow shot of the central character walking toward the center of power or the center of the space; the camera slowly rises and pushes in to a profile close-up; the character's gaze snaps sideways and with one arm they flick a sleeve/draw a sword/raise a hand, the robe or weapon tracing a huge arc in the air. At the instant of the action the camera pulls back to a wide shot, and the central character is tightly surrounded at close range by soldiers/enemies.
Image 2: cut to close shots of several enemies' faces; the enemies raise their weapons high, ready to attack, and roar the key line in unison. No background music, keep only ambient sound effects and voices, no subtitles.
```

**2. Protector entrance and crowd fight, 12-15s**

```text
Image 1: the protector drops from above or cuts in at high speed from outside the crowd, landing directly in front of the person being protected, and swings a long spear/long saber/sword sheath/shield in a sweeping heavy blow that knocks down several enemies in the front row; if there is a line, the tone is cold and ruthless. Then cut to a diagonal composition with facial close-ups of the protector and the protected on the left and right, expressions fitting their identities.
Image 2: the camera stays close on the protector continuing to fight through the crowd—long-weapon sweeps, short flying kicks, shoulder charges, turning counterattacks—with multiple shot changes, alternating high-speed orbiting follow shots, slow motion, facial close-ups and high-speed tracking. Enemies crowd in densely, surrounding layer upon layer; the protector lands heavy blows on many enemies, the action flowing in one go, with strong visual impact.
```

**3. Clip bridge continuation, 5-8s**

```text
Image 1: continue from the danger state of the previous segment, but do not copy the previous segment's last frame; open on a medium-long rear-side angle instead, with the protector and the protected moving closer or standing shoulder to shoulder, fighting off the enemy together. No dialogue, only fight sound effects and ambient sound effects, no background music, no subtitles.
```

Action design rules:

- For mass fights, do not ask every enemy to perform unique actions. Use `several enemies in the front row`, `rebels surrounding layer upon layer`, `enemies crowding in densely`, and keep one hero action as the visual anchor.
- Hero action can be heightened but should match the requested tone: falling from above, spear sweep, flying kick, shield charge, high-speed tracking, slow motion impact.
- Maintain readable hierarchy: protected character as emotional center, protector as action anchor, soldiers/enemies as surrounding pressure.
- Combine fast action with one or two hero close-ups to preserve character emotion and identity.
- If the scene is very crowded, use wide shots for geography and close-ups for identity, not medium shots full of indistinct bodies.

Sound and text constraints:

```text
No background music; generate only fight sound effects, ambient sound effects, roars, weapon clashes, footsteps and robes cutting the air. No subtitles in the image.
```

Negative constraints:

```text
Keep the characters' appearance, costumes, hairstyles, weapons and the enemies' look consistent; no style drift, no subtitles or watermarks, no facial deformation, no costume or hairstyle jumps, no runaway enemy count that loses the main subject, no weapon deformation, no clipping.
```

## Dialogue and Offscreen Lines

When dialogue carries the plot turn, write the actual line. Avoid vague placeholders.

- Phone call: include the caller's key sentence, even if muffled or offscreen.
- Doctor, police, family notice: include the exact notice line in plain speech.
- Inner monologue or voiceover: mark it as `inner monologue (OS)` or `voiceover`, and place it on the time axis.
- Keep lines short enough for the shot duration.

Examples:

```text
A lowered male voice comes through the phone: "I'm sorry... there was a crash. He didn't make it."
The doctor takes off his mask and says quietly: "We did everything we could, but she didn't make it."
```

### Dialogue Timing Budget

Estimate delivery time before assigning dialogue to a shot. For Mandarin lines count Chinese characters without punctuation; for English lines count words.

Suggested Mandarin delivery rates:

- 2-3 Chinese characters/second: whisper, grief, hesitation, restrained confession, breath-broken speech.
- 3-4 Chinese characters/second: natural dramatic conversation.
- 4-5 Chinese characters/second: urgent command, argument, panic; use sparingly because clarity and lip-sync become less stable.

Suggested English delivery rates:

- 1.5-2 words/second: whisper, emotional hesitation.
- 2-3 words/second: natural dramatic speech.
- 3-4 words/second: urgent speech; avoid long lines at this speed.

Add time beyond spoken words:

- 0.3-0.8s before a difficult line for breath, eye contact, or hesitation.
- 0.3-0.8s for a meaningful pause inside the line.
- 0.5-1.5s after the line for the listener's reaction.
- 1-2s at the end of the video for performance or editing room.

Practical formula:

```text
Required shot duration = spoken line time + pre-line action/pause + the other person's reaction + time to complete the camera move
```

Examples:

```text
"We did everything we could, but she didn't make it." 10 words.
For a restrained, slow announcement estimated at 2 words/second, pure speech is about 5 seconds; if the shot is only 4 seconds, shorten the line or split off the reaction rather than cramming it in.
```

```text
"So you're just notifying me." 5 words.
At a slow, repressed pace of 1.5 words/second it is about 3.3 seconds; leave another 1 second of silent reaction, so the shot needs at least about 4.3 seconds.
```

Rules:

- Do not assign two substantial lines plus a complex body action to a 2-3s shot.
- If dialogue runs long, shorten the line before speeding up delivery.
- Important lines should finish before the final 1-2s ending breath.
- Offscreen dialogue still consumes time and must be budgeted.
- Simultaneous overlapping lines should be short and intentionally motivated.

## Light and Atmosphere

Make atmosphere physical:

- Moving streetlight stripes across a face.
- Wind lifting hair, paper, grass, shirt collar, dust.
- Window reflections splitting the face.
- Hard light cutting through blinds.
- Cold interior shadow versus warm exterior light.
- Engine vibration, cloth friction, footsteps on wood, room tone, breath, sudden silence.

Prefer dynamic light over static adjectives. Say what the light does to the face, object, or space.

## Output Modes

Select the lightest mode that satisfies the user's workflow.

### Concise mode / Compact Mode

Trigger examples: `just give me the prompt`, `no analysis`, `only the finished result`, `concise version` (users may write these in any language).

Output:

```text
【Final video prompt】
...
```

Rules:

- No visible diagnosis or strategy.
- Omit references unless requested or essential.
- Keep the final prompt compact and copy-ready.
- Still run all diagnosis, timing, continuity, compression, and safety checks internally.

### Workshop mode / Workshop Mode

Default for ordinary requests and iterative revision.

Output:

```text
【Story diagnosis】
【Cinematic adaptation strategy】
【Reference images to generate first】
【Final video prompt】
```

Rules:

- Keep diagnosis and strategy concise and correctable.
- Treat the output blocks above as conditional: follow the selected production path and actual asset state in `../SKILL.md`. Direct-video work omits full reference prompts by default; reference-first work delivers only the current required stage and continues when assets/approvals permit.
- The duration-based character ceiling applies only to the final video prompt.

### Continuous short-film mode / Continuous Short-Film Mode

Use for long-story splits, repeated `continue` (in any language), multi-part episodes, or projects requiring stable recurring characters and locations.

Output:

```text
【Continuity summary】
Character profiles:
Scene profiles:
Story state at the end of the previous segment:
How this segment connects:
What this segment advances:

【Reference assets】
Reused:
New:
Updated state:

【Final video prompt for this segment】
...

【Anchors for the next segment】
Ending story state:
Actions/emotions/props to connect from:
Character/prop state:
```

Rules:

- Keep canonical character and scene records stable across segments.
- Each segment advances one main event or emotional turn.
- Do not reuse the previous tail frame by default. Preserve story state, identity, space, props, and emotional residue; choose the bridge that best fits the next segment.
- Add reference prompts only for new visual anchors or meaningful state updates.
- Each segment remains under 30s and its final prompt under the duration-based character ceiling.

## Short-Drama Hook and Narrative Drive Diagnostic

Use this only when the user asks for a breakout short drama, strong hook, suspense reversal, high-concept premise, cliffhanger, serial episode, or when a plot-driven input clearly lacks propulsion. It is a diagnosis and optional repair tool, not the default screenplay template for every cinematic prompt.

Do not activate it merely because a video is short. Skip or greatly reduce it for emotional close-ups, quiet relationship scenes, atmosphere films, product/person texture films, choreography demonstrations, or complete plots whose strength comes from performance rather than suspense.

### Six Optional Narrative Functions

| Function | Diagnostic question | Playable screen evidence |
|---|---|---|
| **Anomalous event / Anomaly** | What is visibly wrong, impossible, misplaced, or unexpectedly changed? | a future-dated parcel, a second key, a familiar voice from an empty room, an impossible name on a screen |
| **Immediate goal / Immediate Goal** | What must the protagonist obtain, prevent, open, reach, prove, hide, or escape right now? | hand reaching for the parcel before someone returns, running toward a closing lift, hiding evidence before a knock |
| **Rule or cost / Rule or Cost** | What constraint changes behavior, and what is lost if the character fails? | a deadline, one forbidden action, limited attempts, exposure, separation, arrest, loss of trust; it need not be literally deadly |
| **Real-world resistance / Active Obstacle** | Who, what, or which physical condition actively blocks the immediate goal? | security stops entry, a jammed door, a witness approaches, power fails, time expires |
| **Identity or information reversal / Information Reversal** | What new evidence changes the meaning of what the viewer just saw? | the helper owns the missing phone, the victim sent the warning, the apparent exit is the trap |
| **Unfinished answer / Unresolved Question** | Which specific story question remains open after the visible beat completes? | who sent it, why the voice is hers, what waits behind the door, whether the warning is truthful |

These are functions, not six compulsory plot points. A 15-30s video often needs only 3-4. Combine compatible functions instead of overloading the scene:

```text
Anomaly appears -> immediate goal and rule/cost established -> resistance escalates -> information reversal that leaves a specific unanswered question
```

Do not force a separate `deadly rule` when ordinary stakes are stronger or more believable. Use `rule or cost` as the broader category. Do not add an identity reversal merely to create surprise; an object, message, behavior, or changed interpretation can carry the reversal.

### Responsibility Boundary

- **Complete plot supplied**: diagnose only. Preserve its causality, tone, and ending unless the user asks for a stronger hook or rewrite.
- **One function is weak or missing**: state the gap in `Story diagnosis`; propose one minimal repair in `Cinematic adaptation strategy`.
- **The repair changes identity, motive, world rules, culprit, relationship, or ending**: use direction-confirmation mode before writing reference images or the final prompt, unless the user explicitly delegates creative control.
- **The user asks for breakout/strong-hook creation or delegates freely**: add only the smallest number of functions needed to create propulsion, then continue to cinematic translation.
- **Performance-led scene**: do not import anomaly, countdown, reversal, or cliffhanger unless the supplied story already contains them.

### Beat Design, Not Mechanical Timing

A beat is a change in the viewer's question, the character's tactic, the perceived chance of success, or the cost of failure. Do not change the plot every fixed number of seconds merely to imitate pace.

Useful emotional-information progression:

```text
Question -> tension -> brief hope -> higher cost -> new question
```

Choose only the changes the selected duration can play. If dialogue, physical action, reaction, and ending residue cannot fit, remove a function or split the story instead of accelerating everything.

### Translate Functions into Filmable Evidence

Do not print abstract screenplay labels inside the copy-ready prompt. Convert each selected function into action, object state, dialogue, sound, framing, or reaction.

Bad:

```text
An identity reversal happens here, and the ending leaves suspense.
```

Better:

```text
The access-control screen lights up, and beside the girl's ID photo it shows "Deregistered three years ago"; her hand stops above the sensor, and the security guard behind her looks up at the same moment. From the end of the corridor comes her own voice: "Don't look back."
```

### Open Answer, Completed Screen Beat

Do not confuse a cliffhanger with an unfinished generation. Complete the immediate action, reveal the evidence, then hold the consequence for 1-2 seconds while the larger answer remains open.

```text
The door is pushed open a crack and her own voice comes from inside; she stops at once, her knuckles still pressed against the door edge, the cold light from the crack falling into her wet eyes. The voice continues for one second, and the image holds on her neither daring to push the door open nor to step back. Who is inside remains unanswered.
```

Avoid:

- ending mid-sentence or mid-action merely to manufacture suspense
- adding an unrelated villain, secret identity, supernatural rule, or countdown
- treating confusion as mystery; the viewer should know the specific question being withheld
- fitting all six functions into a simple 8-15s performance scene
- replacing emotional causality with constant information tricks

## Structure Selection

Choose structure before writing shot details. Always state the chosen structure in the diagnosis, and explain the reason in one sentence. If more than one structure fits, choose one primary structure and one secondary support.

### Structure Selection Table

| Structure | Use When | Best For | Avoid When | Prompt Strategy |
|---|---|---|---|---|
| **Single-scene one-take / Single Take** | One space, one continuous emotional shift, few actions, no major time jump | restrained grief, confrontation pause, ritual, waiting, subtle intimacy | many locations, action complexity, multiple plot turns | Use the Ordinary Drama One-Take Blocking System: one camera path, start frame, blocking shift, motivated focus change, foreground depth, sound continuity, held ending |
| **Single-scene continuity editing / Multi-Shot Sequence** | One location but several physical beats or reaction angles are needed | kitchen tension, hospital corridor, car interior conflict, interrogation | very abstract memory, large time span | Use 3-5 shots: establish space, key object/action, face reaction, ending breath |
| **Jump-cut compression / Jump Cuts** | Time needs compression while staying in one emotional thread | preparation, decision, panic escalation, ritual, product/person process | scene requires smooth emotional realism | Use repeated visual anchor; each cut advances state clearly |
| **Montage sequence / Montage** | Memory, dream, symbolic contrast, parallel images, theme rather than linear action | childhood recall, grief objects, identity transformation, longing | direct dialogue scene, precise physical action | Use sound or object as transition anchor; keep fragments sensory and partial |
| **Continuous action cutting / Continuous Action Editing** | Character moves through space under pressure | chase, escape, crossing rooms, storm/rain movement | tiny emotional beats, complex multi-person combat without reference | Keep direction consistent; define start/end spatial goal; limit actions |
| **Fight action design / Fight Choreography** | 1v1 or limited multi-person staged combat with clear attack-defense beats | boxing, close combat, controlled stunt throw, wuxia exchange, underground ring | many attackers, unclear character references, gore, lethal injury emphasis | Define roles, attack line, defense, counter, footwork, contact point, camera response, safety constraints |
| **Multi-person dialogue cross-cutting / Dialogue Cross-Cutting** | 2-4 people in one scene, power shifts through speech and silence | family dinner, office confrontation, breakup, negotiation | no meaningful dialogue or no relationship tension | Define seating/standing positions, who holds power, key lines, reaction shots |
| **Long close-up micro-expression / Close-Up Micro-Expression** | Emotion is carried mainly by face/head with minimal action | shock, suppressed crying, shame, hidden love, inner collapse | plot needs many events or spatial movement | Use ECU/CU, stable or slow push, timed facial-muscle progression |
| **Product/person texture film / Product-Person Texture Film** | Product, place, or persona matters as much as plot | car, watch, founder, artist, venue, premium object | story requires many dramatic turns | Use tactile details, material, light, sound, controlled gesture, brand-like restraint |
| **Large-scene compression / Large-Scene Compression** | Crowd, disaster, ceremony, battlefield, launch, courtroom, banquet | chaos with one human anchor, public pressure, group reaction | no clear protagonist or visual anchor | Pick one visual anchor; show crowd as pressure; use 4-5 clear nodes |
| **Long-story split / Sequential Prompt Split** | Playable content exceeds 30s or final prompt would exceed the duration-based character ceiling, even if the user's text is short | reunion, investigation, travel, multi-stage emotional arc, multiple actions or location changes | one small moment already fits under 30s | Split by emotional turning points; make each segment a complete 15-30s mini-arc and define a bridge type for the next segment |
| **Story continuation / Continuation Segment** | User approves a segment and asks to continue | short-film sequences, clip bridges, multi-part emotional arcs | no prior segment context exists | Continue from previous story state, preserve identity/scene/props, choose a bridge type, add only one new event |
| **Subjective shot / POV or Subjective Camera** | User needs immersion into a character's perception | fear, dizziness, memory trigger, entering unknown space | multi-character dialogue needs facial reactions | Use breath, hand edges, focus shifts, sound distortion; keep POV coherent |
| **Match cut / Match Cut Structure** | Two times/places/actions mirror each other | past vs present, childhood/adulthood, before/after identity | simple linear action is clearer | Match hand, object, gaze, light, or sound across cuts |

### Cross-Time or Cross-Space Match Cut

When choosing a match cut across time or place, specify the few visual invariants needed to connect the cut (object screen position/size, camera height/angle, or motion phase), then the intentional changes (location, light, costume, age or injury state). A hard cut is not a gradual morph. Distinguish it from match-on-action within one continuous event. Preserve the user's intended memory, imagination, reality shift or ambiguity; do not invent a resurrection or other story mechanism to explain the edit.

Example: a low angle sees the ball stop in front of the dog's paw; hard cut, keeping the ball's position and the camera position, the ground changes to a sunlit field, and the same dog, now healthy, steps up and picks up the ball in its mouth. The ball is the transition anchor; the whole scene is not required to stay the same, and the illness or injury does not vanish without reason within the same continuous time and space.

### Quick Decision Rules

- If the core is **one emotion changing inside one body**, choose `Long close-up micro-expression` or `Single-scene one-take`.
- If the core is **relationship pressure through words**, choose `Multi-person dialogue cross-cutting`.
- If the core is **a body moving toward a goal**, choose `Continuous action cutting`.
- If the core is **a staged fight**, choose `Fight action design`; keep fighters few and action beats explicit.
- If the core is **time, memory, or symbolism**, choose `Montage sequence` or `Match cut`.
- If the core is **a process compressed into moments**, choose `Jump-cut compression`.
- If the core is **a product/person/place aura**, choose `Product/person texture film`.
- If the core is **large chaos but one person matters most**, choose `Large-scene compression`.
- If the playable content cannot breathe within 30s, choose `Long-story split` even when the user's written description is short.
- If the user asks to continue from an approved prompt, choose `Story continuation`.

### Hybrid Structures

Use hybrid labels when useful, but do not overcomplicate the final prompt.

Examples:

- `Main structure: Multi-person dialogue cross-cutting; support: Long close-up micro-expression`
- `Main structure: Continuous action cutting; support: Subjective shot`
- `Main structure: Fight action design; support: close handheld impact feel`
- `Main structure: Montage sequence; support: Match cut`
- `Main structure: Large-scene compression; support: single-character visual anchor`
- `Main structure: Story continuation; support: match-on-action bridge`

### Structure Failure Warnings

- Do not choose single take just because it sounds cinematic; use it only when the action can physically unfold in one continuous space.
- Do not choose montage when the user needs a clear cause-and-effect event.
- Do not put more than one major location change into a short single-take prompt.
- Do not write large crowd scenes without a visual anchor.
- Do not write long dialogue at the final second. Give reaction and aftertaste.

## Director-Level Shot Continuity Rules

Use these rules when writing multi-shot prompts. They make the prompt feel directed and editable, not just visually descriptive.

### Generation Execution Stability

Use these rules for the copy-ready final prompt, especially when the scene has reference images/videos, dialogue, action, one-take blocking, continuation, or important props.

**First-frame reconstructability**

The opening of the final prompt should let the model rebuild the first frame without hidden memory. Include the visible subject, start posture/action state, screen position and depth, facing direction, gaze, held or contacted prop, shot size, camera angle/height/axis, and main motivated light source when it affects composition. The first frame should not be a vague setup unless the story deliberately reveals the subject later.

The visible subject does not have to be a person. It can be an empty location, key prop, vehicle, screen, building, landscape, or aftermath state. If the first frame is empty or object-led, define location layout, foreground/midground/background, key object position/state, weather or environmental motion, sound cue, shot size, camera angle/height/axis, and motivated light source when relevant.

**One shot, one core action, one core camera behavior**

Each shot should have one main action path and one main camera behavior. A shot can contain small supporting reactions, but the viewer should know which action the model must prioritize and what the camera is doing. If a continuous shot needs multiple movement phases, serialize them with clear settle points. If the action and camera compete, simplify the camera or split the shot.

**Ending-state lock when needed**

Do not add a separate ending field by default. But when a prompt will be continued, split, repaired, generated from first/last frames, or depends on a product/prop/action endpoint, state the final visible condition inside the last shot: character pose, gaze, body contact, prop location/state, focus, composition, and emotional residue. A completed action becomes a visible final state, not something to replay in the next clip.

The ending state may also be empty or object-led. In that case, lock what remains on screen: the empty space, door/window/light state, fallen or placed prop, screen state, vehicle position, weather/sound continuation, focus, and composition.

**Story-critical prop state**

For phones, letters, cups, rings, weapons, reports, U-disks, photos, keys, documents, and other plot-changing objects, describe physical state with the same care as body action:

- who holds or touches it
- which hand or support point is used
- grip/pressure/orientation
- contact with body, table, floor, pocket, bag, door, another person, or device
- visible change during the shot
- final visible location and state

If a prop changes owner, position, orientation, damage, wetness, light state, screen state, or readability, show the action that changes it.

**No optional branches in final prompts**

The final prompt should not contain unresolved options such as `or`, `or else`, `A/B`, `pick one of two`, `optional`, `could... or could...`, or `any of`. Make one director choice before delivery. Variants are allowed only when the user explicitly asks for multiple versions.

### Shot Size Progression

Avoid cutting between two adjacent shot sizes that are too close, because it can feel like a jump cut rather than an intentional edit.

Avoid:

- Wide shot -> medium shot
- Medium shot -> close shot
- Close shot -> close-up
- Close-up -> extreme close-up

Prefer stronger size contrast or a motivated bridge:

- Wide shot -> close shot / close-up
- Medium shot -> close-up / extreme close-up
- Close-up -> medium shot / wide shot
- Wide shot -> environmental prop insert -> close-up

Do not use adjacent shot sizes when the user has explicitly prohibited them. Otherwise an exceptional adjacent-size cut requires a specific editorial reason; do not use action or sound as a blanket exemption.

### Camera Angle Change

When cutting between different camera angles within the same scene, and especially between shots of the same subject or same interaction, change the camera's horizontal angle by at least 30 degrees. This prevents awkward jump cuts and gives the edit a real perspective shift.

This rule applies only inside the same scene or continuous spatial relationship. When cutting to a new scene, new location, new time, or a clearly different spatial setup, do not force a 30-degree angle change; prioritize the new scene's geography, mood, and opening composition.

Examples:

- Shot 1: front-left 3/4 angle.
- Shot 2: side angle over the other character's shoulder, at least 30 degrees away.
- Shot 3: reverse angle or object insert.

Do not write repeated same-angle close-ups inside the same scene unless the scene intentionally uses a locked-off long take.

### 180-Degree Axis and Eyeline

Establish an imaginary axis through the interacting characters or along the main direction of movement. Keep the camera on one side of that axis so screen positions and gaze directions remain understandable.

For two-person dialogue:

- If A is established on screen-left looking right, keep A looking right in later close-ups.
- B should remain on screen-right looking left.
- Over-the-shoulder reverse shots must preserve these eyelines.

Cross the axis only when motivated by one of these methods:

- show the camera physically moving across the axis
- use a neutral shot directly on the axis
- insert a clear re-establishing wide shot after the crossing
- let a character visibly move across the axis and create a new spatial relationship

Do not silently flip character positions between adjacent shots.

### Asymmetric Body Geometry

The interaction axis does not require equal eye height or conventional shoulder-to-shoulder coverage.

- For adult/child, standing/seated, human/animal, wheelchair, bed, floor, or large-creature scenes, define each subject's functional eyeline and vertical relationship.
- Keep screen side and gaze direction stable while adapting camera height and foreground anchors to anatomy and mobility.
- Do not stretch, lift, or reposition a low subject merely to imitate a standard human over-shoulder shot.
- When a character lowers to the other's level, show the body transition and let the camera descend or widen with physically plausible parallax.

### Motivated Foreground Occlusion Transition

A train, door, passing person, pillar, vehicle, curtain, smoke bank, darkness, or large foreground object may briefly cover the frame to perform a reveal, disappearance, time shift, or scene bridge.

Requirements:

- the occluding object must belong to the established space and move on a plausible path
- preserve axis, screen direction, camera position, light logic, and sound continuity across the cover
- define what changes while hidden and lock the first visible state after reveal
- keep the cover long enough to read but not so long that it becomes an unexplained blackout
- let the object produce synchronized parallax, reflection, wind, pressure, shadow, or sound when relevant

Do not use an occlusion to hide an impossible continuity reset. The reveal must feel like a motivated cinematic transition, not model drift.

### Screen Direction and Entry/Exit

- A character exiting frame-right should normally enter the next connected space from frame-left, continuing the same travel direction.
- In a chase, maintain pursuer and target screen direction unless the turn is shown.
- In a fight, keep A/B screen positions stable until a visible pivot, pass, throw, or camera move changes them.
- Vehicles, running characters, thrown objects, and gaze direction should preserve momentum across cuts.

### Handedness, Props, Costume, and Body State

Track continuity details across shots:

- which hand holds the phone, cup, letter, sword, gun, ring, or bag
- where the prop is placed after release
- whether clothing is buttoned, wet, torn, dusty, or displaced
- hair position, makeup tears, sweat, blood-free injury state, and visible marks
- which cheek has a tear track or which sleeve is damaged
- whether a character is standing, kneeling, seated, leaning, or facing a particular direction

If a continuity state changes, show the action that changes it.

### Spatial Continuity Record

For dialogue, action, continuation, or multi-part scenes, internally track:

```text
Character A: screen position / facing / hand holding the object / posture
Character B: screen position / facing / hand holding the object / posture
Key prop: position / state
Main light source: direction / color temperature
Entrances/exits: position
Direction of movement: left to right / right to left / toward camera / away from camera
```

Do not print this record unless the user asks for a continuity sheet, but use it when writing the prompt.

### Insert / Transitional Shots

Use insert shots when the scene needs breathing room or when long dialogue needs visual punctuation.

Good inserts:

- a hand tightening around a cup
- rain running down a car window
- a phone screen going dark
- chopsticks stopping above a bowl
- a candle flame shaking
- a ring, letter, key, cup, sword, music box, or old sweater
- empty chair, doorway, hallway, window reflection

Use inserts to:

- break long dialogue without losing tension
- show what a character avoids saying
- create a pause before a reveal
- bridge between two similar shot sizes
- give the editor a cutaway

Do not overuse inserts. In a 10-15s prompt, 1-2 inserts are usually enough.

### Ending Breath

Do not end the video on a line delivery, sudden facial expression, or unfinished action unless the user explicitly wants an abrupt cut. Leave 1-2 seconds for:

- a silent reaction
- breath settling
- eye contact holding
- sound tail
- the object after the action
- a character choosing not to speak
- a held reaction, sound cue, prop state, or unfinished action that can bridge into the next segment

This is especially important for dialogue, crying, confession, shock, and confrontation scenes.

### Match-on-Action Editing

When one action is important, split it across two different shot sizes or angles so the edit feels intentional.

Pattern:

```text
Shot 01: medium shot, the character raises a hand toward the door handle, the action begins.
Shot 02: close-up, fingers grip the door handle and slowly turn it, continuing the same action.
```

Good match actions:

- reaching for a cup, ring, key, letter, sword, phone, door handle
- turning the head to look back
- raising a hand to wipe tears
- sitting down, standing up, stepping forward
- drawing a blade or pushing it back into the sheath
- starting a punch in medium shot, landing/parrying in close shot

Rules:

- The second shot should continue the same action, not restart it.
- Change shot size and horizontal camera angle.
- Keep object hand/side continuity clear.
- Use this to make simple actions feel cinematic without adding extra plot.

## Novel Excerpt to Cinematic Prompt

Use this pattern when the user provides a novel paragraph, web-fiction excerpt, prose scene, or heavily internalized narrative.

### Adaptation Principle

Do not translate the prose sentence by sentence. A video prompt should preserve the dramatic intention and emotional turn, then rebuild it as a short playable scene.

Priority order:

1. Preserve the core relationship and conflict.
2. Preserve the visible emotional turn.
3. Preserve the key spoken line if it drives the plot.
4. Preserve the most cinematic object, gesture, or environment motif.
5. Compress or omit backstory, explanation, repeated description, and decorative metaphor.

### Novel Text-Length Tiers

Character counts below are for Chinese source text; for English text use about 0.6 words per character.

Use length as a workload estimate, subordinate to `Execution Decisions and Agent Capabilities` and the adaptation-scope rule in `../SKILL.md`.

- Under roughly 1500 Chinese characters: one clear 6-30s event may suffice; check playable content rather than assuming the whole passage fits.
- Roughly 1500-3000 Chinese characters: identify the strongest scene for a highlight request, or preserve the full causal spine across clips for full coverage.
- Over roughly 3000 Chinese characters or a full chapter: establish a scene-selection or continuous structure before detailed prompts. Full coverage is already selected by `full adaptation` / `full coverage` / `continuous short film`; do not ask the user to choose highlights instead. If scope is genuinely unresolved and changes the deliverable materially, ask one scope question.

Do not mechanically split prose into one prompt per 30 seconds. Use filmable scene units, continuity, and requested coverage. A structure table is preparation for requested final prompts, not an automatic approval gate; respect structure-only and explicit approval-first requests.

### Long Novel Entry Decision

When a long novel input arrives, decide the entry path before writing final prompts:

```text
If the user wants a single standout video: pick or list the segments as asked, then deliver the requested prompt
If the user wants a full adaptation / coverage of the whole text / a continuous video: first build the 【Series structure table】, then continue with the full prompts requested
If the user only wants the structure or asks to confirm first: deliver the structure, then stop or wait for the corresponding confirmation
If the scope still cannot be inferred and it affects the deliverable: ask only this scope question
```

`Filmable segment selection table` is for choosing the strongest filmable moments. It is selective and does not guarantee full coverage.

`Series structure table` is for full-story adaptation. It should include:

- segment number and suggested duration
- covered plot beat
- emotional turn
- key characters on screen
- location and continuity state
- key props or new visual references needed
- bridge purpose for the next segment

After establishing the continuous structure, continue the requested final prompts when scope is clear and required assets are available. Wait only for a reserved user approval, unresolved material decision, or required asset. If the host requires batches, label completed and remaining segments plus the next continuation state; do not imply that a partial batch completes full coverage.

### Diagnosis Fields for Novel Inputs

Use these fields in workshop mode when they help the user see the adaptation decision:

```text
Core conflict of the source text:
Main visualizable event:
Inner-life description that cannot be filmed directly:
Suggested to keep:
Suggested to compress or externalize:
Scope covered by this prompt:
```

Keep this section concise. It is for adaptation clarity, not literary analysis.

### Prose-to-Image Translation Map

- Inner monologue -> eyes avoiding contact, breath change, hand tension, delayed response, repeated gesture, brief voiceover only when necessary.
- Backstory -> one prop, photo, scar, letter, phone screen, room detail, costume state, or a short line.
- Metaphor -> light, weather, reflection, shadow, sound, physical motif, or actor behavior.
- Authorial explanation -> blocking, distance between characters, who initiates/retreats, who occupies power position in frame.
- Long emotional paragraph -> 3-5 micro-expression beats with time marks.
- Memory or flashback -> object insert, reflection, sound bridge, short montage, or split into another segment if important.
- Worldbuilding -> one clear establishing shot or scene reference prompt, not a full encyclopedia.

### Compression Rules for Novel Inputs

- If one excerpt contains setup, reveal, argument, collapse, and aftermath, choose only the turns that can naturally play within one 30s prompt and recommend splitting the rest.
- For highlight adaptation, state the selected scene explicitly before the final prompt and treat other material as context. For full coverage, preserve the causal sequence regardless of source length.
- For 3000+ character excerpts, output a scene-selection list first. Do not output a long chain of final prompts unless requested.
- If the original has many adjectives, keep only those that change lighting, costume, texture, performance, or mood.
- If the original contains multiple named characters, keep only the characters who affect this moment on screen.
- If the original dialogue is too long, rewrite it into 1-2 short playable lines while preserving meaning and emotional subtext.
- If the original depends on private thought, create an external action anchor: cup, sleeve, ring, phone, letter, door, blade, window, cigarette, bed sheet, scarf, or another story-specific object.

### Final Prompt Requirements for Novel Inputs

- The final prompt must read like a shootable scene, not a synopsis.
- Include concrete time allocation, physical action, camera behavior, performance detail, sound, and ending breath.
- Do not include literary commentary such as "symbolizes", "hints at", or "expresses" unless immediately tied to a visible action.
- When preserving prose language as voiceover, keep it short and timed; avoid turning the whole scene into narration.
- If the scene is part of a longer chapter, mention what this prompt covers and what should continue in later segments.

### Continuous Novel Adaptation Continuity

When adapting a novel into multiple consecutive video prompts, keep a compact continuity record and avoid redundant restatement.

- If two consecutive segments use the same characters, same costumes, same location, same lighting, and same key props, do not repeat the full character and scene descriptions. Use phrases such as `continuing from the previous segment's story state`, `Su Min keeps the same outfit and tired makeup`, or `keep the same warm-cool night light in the study`.
- Still repeat the minimum anchors needed for model stability: character name, approximate age, current emotional residue, current costume state, location, and the key prop currently in hand or in frame.
- If a new character appears, add a concise character description and optional new character reference prompt.
- If the story enters a new location, add a concise scene layout and optional clean scene plate prompt.
- If a character changes clothing, makeup, injury, wet/dusty state, or hairstyle, describe the change and treat it as the new continuity state.
- If a new key prop becomes narratively important, describe its appearance, initial position, and who holds or moves it. Track where it ends after the segment.
- If the only change is emotional progression, do not regenerate identity or scene descriptions; describe the emotional residue from the previous segment and the new emotional turn.
- Use the previous segment's story state as the continuity anchor between adjacent prompts. A previous tail frame may be used as a reference, but it should not be treated as the required first frame of the next video.

## Continuation and Clip-Bridging Workflow

Apply `continuity_director_contract.md` first: prior tail frames are state references by default, not bound opening compositions. Audit the inter-clip cut as well as internal cuts, and check reference coverage before compiling unseen angles.

Use when the user says `continue`, `keep writing`, `next segment`, `next shot`, `pick up from the last one` (in any language), or when a long story is split into adjacent clips.

### Continuation Principles

- Continue from the previous story state, not necessarily from the previous final image.
- Keep character identity, age, hairstyle, clothing, makeup, injury state, and emotional residue consistent.
- Keep setting, lighting, weather, time of day, color palette, camera texture, and sound bed consistent unless the story intentionally changes.
- Keep key props consistent in design, position, and narrative meaning.
- Progress emotion instead of replaying it.
- Add only one main new event or emotional turn per short segment; a 16-30s segment may include a fuller setup-turn-aftermath arc if it stays playable.
- Let each segment feel like a complete small dramatic unit. Do not force a long-take continuation across clips if a shot-group structure is more natural.
- Leave the ending as a useful next bridge: a held reaction, an unfinished action, a prop state, a sound cue, or a completed mini-arc that can lead into the next beat.

### Clip Bridge Types

Choose one bridge before writing the next prompt:

1. **Continuous Drama Bridge / bridge by changing shot size and angle**: use when the previous ending must continue immediately, but the next video should not copy the same frame. Start the next clip from the same story moment with a different shot size and camera angle, such as CU -> WS, MS -> BCU, over-shoulder -> reverse angle, or side angle -> frontal angle. Preserve axis, eyeline, body direction, prop state, and emotional residue.
2. **Match-on-Action Bridge / bridge mid-action**: use when the previous clip ends on an unfinished action. End segment 1 as the hand begins to open the door, body starts to turn, sword begins to draw, person starts to fall, lips begin to speak, or fist begins to swing; start segment 2 from a new angle/shot size continuing the same action, not restarting it.
3. **Shot-Group Bridge / bridge by shot group**: use when each clip is a complete small scene or emotional beat. Segment 2 does not need to start from segment 1's tail frame. It should start with a strong new shot that belongs to the next mini-arc while preserving character, scene, prop, costume, light, sound, and emotional continuity.

Use the previous tail frame only when exact body position, blocking, injury/damage state, or object position is critical. Otherwise, treat it as one reference asset among others, not as a required first-frame instruction.

### Continuation Diagnosis

Use this compact form:

```text
【Continuation check】
Ending state of the previous segment: ...
Emotional progression of the next segment: ...
Bridge type: bridge by changing shot size and angle / bridge mid-action / bridge by shot group
Continuity notes: character costumes, scene lighting, key props, action direction and emotional residue need to carry over...
```

### Reference Image Rules for Continuation

- If the next segment uses the same character, same scene, and same key props, say: `Reuse the existing character/scene/prop references; no new reference images.`
- If exact continuity is needed, optionally add: `You may refer to the body posture/prop positions in the previous segment's last frame, but the next segment's opening does not need to copy the same frame.`
- If a new character appears, add `new character reference image`.
- If a new location appears, add `new scene reference image`.
- If a new key prop appears, add `new key prop reference image`.
- If a costume, injury, makeup, or emotional state visibly changes and must remain stable later, add an updated character reference.

### Continuation Opening Phrases

Use clear continuity phrases in the final prompt:

```text
Continue from the previous segment's story state, but open with a new shot size and angle: ...
Keep the same character, the same costume, the same scene lighting and the same prop positions.
The emotion at the end of the previous segment is not reset; it keeps moving from ... to ...
```

```text
Bridge mid-action: at the end of the previous segment the character has just begun to ...; this segment opens with a ... shot from a ... angle continuing the same action; the action does not restart, only the unfinished part is completed.
```

```text
Bridge by shot group: this segment is the next 15-second mini-story and does not copy the previous segment's last frame; carry over the characters, scene, props and emotional aftermath, and enter the next event from a new, effective opening shot.
```

### Good Continuation Moves

- Shock -> numb stillness.
- Numbness -> one decisive action.
- Suppressed crying -> private collapse.
- Argument -> silent aftermath.
- Discovery -> cautious approach.
- Reunion recognition -> first touch.
- Chase miss -> breathless decision.
- Suspense sound -> slow move toward source.

### Bad Continuation Moves

- Repeating the same reveal from the previous segment.
- Jumping to a new location without a transition or user request.
- Changing clothing, lighting, age, or prop design accidentally.
- Adding more plot events than the selected duration can naturally play.
- Copying the previous tail frame as the next first frame by habit, especially when a new angle, match-on-action, or complete shot-group opening would be smoother.
- Starting with a generic establishing shot that ignores the previous emotional or action state.

## Generated-Result Surgical Repair

Use this only when the user provides a generated video, frames, or a concrete description of the rendered result and asks for correction. Diagnose the gap between the intended result and the visible/audible result; do not treat prompt wording alone as proof of the cause.

For evidence-based attribution, read `one_take_emotional_coverage.md`, section `Generated-result evidence and attribution`. Separate observed failure, prompt omission/conflict, execution deviation and unverified causes. One output cannot establish a model's inherent limit; sampled frames cannot verify unheard dialogue or prove the absence of hidden cuts.

### Repair Scope

Choose no more than three dominant failures that materially affect the video:

- identity or reference drift
- body, contact, prop, or action-chain mechanics
- spatial continuity, screen direction, or camera path
- performance timing, expression, or emotional progression
- dialogue order, lip-sync, voice identity, overlap, or sound balance
- light-source continuity, exposure, material response, or unwanted commercial polish
- pacing, shot density, ending state, or missing reaction time

Separate a local control failure from a structural failure:

- **Local failure:** the story beat, blocking, space, and successful visual/audio facts still work. Preserve them and revise only the smallest clauses controlling the failed result.
- **Structural failure:** the story beat, action causality, blocking, topology, or camera path cannot produce the intended result. Rebuild only the affected shot or beat, while keeping every unrelated successful fact stable.

Do not add more style words or a longer negative list when the real cause is missing action causality, impossible body mechanics, unclear space, conflicting camera instructions, or unplayable timing.

### Success Lock and Single-Variable Revision

Before revising, internally separate:

```text
Locked: the characters, costumes, scene, time and weather, spatial topology, prop states, action order, camera axis, light direction, dialogue, sound or ending state that already worked and that the user did not ask to change
Change only this round: the variable the user specified, or the smallest control item that explains the main failure
```

If the user says `only change the camera movement`, `only fix the action`, `don't change the character`, `keep this version's lighting`, or gives another single-variable instruction, change only that axis. Update dependent physical consequences only when necessary; for example, a new camera position may require compatible framing and occlusion, but it does not authorize rewriting dialogue, wardrobe, lighting, or story. Do not turn a physical camera-position change into a new narrative viewpoint or mood such as voyeurism, surveillance, horror, threat, or intimacy unless the user requested that meaning.

If the requested single change cannot coexist with a locked fact, identify the exact conflict instead of silently changing additional variables.

### Output

In workshop mode, keep the repair response compact:

```text
【Generation result diagnosis】
Main failure:
Likely cause:

【Locked】
...

【Minimal repair prompt】
...
```

If the user asks for prompt-only output, return only the repaired copy-ready prompt. Do not claim a frontend supports deterministic local editing unless the user has established that capability.

Method inspiration: `zy-cinematic-realism` result-repair and invariant-lock workflow (CC-BY-NC-4.0). This section is independently adapted for timed video, motion, dialogue, sound, and shot continuity rather than copied as an image workflow.

## Prompt Compression

Final prompts should be direct and proportionate to scene complexity. The character ceiling is duration-based and is not a target. It applies only to the copy-ready final prompt, not to the diagnosis or strategy sections in workshop mode.

Length targets (counted in Chinese characters; an English prompt needs about 0.6 words per character, so 1000 characters ≈ 600 words):

- 500-800 Chinese characters: simple one-person, one-action, one-emotion scenes.
- 800-1300 Chinese characters: default range for most 8-15s cinematic prompts.
- 1300-2000 Chinese characters: complex 10-15s scenes such as multi-person dialogue, large-scene compression, montage, long-story splits, or spatial action.
- 1600-2600 Chinese characters: recommended range for 16-24s prompts with longer dialogue, multi-shot progression, emotional development, or complex blocking.
- 2200-3400 Chinese characters: recommended range for 25-30s prompts with a complete emotional arc, multi-character dialogue, action geography, or strict continuity control.
- 3400-4000 Chinese characters: exceptional range for complex 25-30s prompts only; every added instruction must materially improve generation reliability.

If the prompt exceeds 1300 characters for <=15s, 2400 characters for 16-24s, or 3000 characters for 25-30s, each extra detail must improve generation stability, emotional clarity, spatial continuity, sound/performance timing, or failure prevention. Treat 3000 characters as a soft threshold for 25-30s prompts and 4000 as the absolute ceiling. If an added detail does not help the render, cut it.

- Do not include empty boilerplate such as `Video model: general AI video model`. If no model is specified, omit it.
- Put duration and structure into the first summary line.
- Merge repeated labels.
- Keep only the strongest sensory details.
- Remove generic praise words like "premium", "stunning", "blockbuster feel" unless replaced by concrete light, motion, sound, or performance.
- If more detail is required, split into multiple prompts instead of overloading one.

### Automatic Compression Ladder

When a final prompt is too long, compress in this order. Preserve story causality, action clarity, dialogue, continuity, and ending breath as long as possible.

1. Remove repeated style adjectives and duplicate quality terms.
2. Merge global setting, lighting, sound, and continuity details into the opening summary.
3. Delete decorative details that do not change action, emotion, composition, or generation stability.
4. Combine adjacent micro-expression beats that express the same emotional change.
5. Combine attack, defense, contact point, and result into one concise action beat.
6. Shorten dialogue while preserving the plot-changing meaning.
7. Reduce insert shots and secondary crowd/environment reactions.
8. Shorten negative constraints to the scene-specific minimum.
9. Reduce shot count or action beat count.
10. If the scene still cannot fit under the duration-based ceiling or 30 seconds, split it at an emotional/action turning point.

Never remove first:

- the core plot turn
- key spoken information
- spatial direction and continuity anchors
- attack-defense causality in fight scenes
- the emotional reaction after the turning point
- the final 1-2s breathing room

Compressed formatting rules:

- Prefer semicolon-separated action chains over repeated labels.
- State lens/camera only when it changes or materially affects the shot.
- Do not repeat `no music, no subtitles, consistent characters` under every shot; place them once in the summary or final constraints.
- Replace long literary metaphors with visible behavior.

### Compression Audit

After compression, verify:

- no missing cause-and-effect step
- dialogue still fits its time
- character/prop positions remain clear
- ending breath remains
- final prompt stays readable rather than becoming telegraphic fragments

## Character Consistency Bible

Use for recurring characters, reference-image workflows, long-story splits, and continuation. Keep one canonical profile per character and derive all image/video prompts from it.

### Canonical Character Record

```text
Character ID/name:
Identity and era:
Adult age:
Height and build:
Face shape and bone structure:
Eye/eyebrow/nose and lip features:
Skin tone and skin texture:
Hairstyle/hair color/hair accessories:
Base makeup:
Main costume and materials:
Footwear/accessories:
Habitual gestures or posture:
Voice baseline:
Personality and emotional baseline:
Must not change:
May change with the story: sweat, tears, dust, wounds, clothing state, etc.
```

Rules:

- Keep identity traits stable; do not rewrite facial features with new synonyms that may drift the character.
- Separate permanent traits from temporary state.
- Use adult ages explicitly when romance, intimacy, combat, or nightlife is involved.
- Keep one primary costume per continuous scene. Show any costume change on screen or state a time/location transition.
- Track visible temporary state: wet hair, loosened hairpin, tear track, dusty sleeve, torn cuff, bruising, missing accessory.
- In continuation, repeat only the identity anchors needed by the model, not the entire bible.

### Multi-Character Relationship Record

```text
Relationship:
Height/build contrast:
Power relationship:
How they address each other:
Baseline sense of distance:
Who initiates / who avoids:
Eye-contact and touch boundaries:
Current unresolved conflict:
```

Use this to keep dialogue, blocking, intimacy, and confrontation consistent.

## Scene Spatial Continuity Bible

Use for multi-shot dialogue, action, continuation, and any location revisited across clips.

### Canonical Scene Record

```text
Scene ID/location:
Era and time:
Weather:
Spatial shape and scale:
Foreground:
Midground:
Background:
Door/window/entrance and exit positions:
Key furniture/obstacles:
Initial positions of key props:
Main light source direction/color temperature:
Secondary light and practical light sources:
Ambient sound bed:
Main axis of movement:
Safe activity zone/action path:
Must not change:
May change: damage, smoke and dust, standing water, lighting state, etc.
```

### Per-Shot Continuity Delta

Do not rewrite the whole scene for every shot. Track only changes:

```text
State before the shot: character and prop positions
Action in this shot: who moves/picks up/puts down/breaks what
State after the shot: new positions, facing, hand holding the object, object state
```

Rules:

- A prop remains where it was placed until a visible action moves it.
- Doors, windows, lights, chairs, vehicles, and breakable objects keep state across cuts.
- Damage accumulates; broken glass, spilled water, dust, torn clothing, and extinguished lights do not reset.
- For continuation, the previous ending defines story state and continuity facts, not necessarily the exact first frame of the next segment. The next segment may begin with a new angle/shot size, a match-on-action continuation, or a new shot group.
- If moving into a new room or zone, show or clearly motivate the spatial transition.

### Background Autonomy

In public, working, domestic, or inhabited spaces, background life should continue independently of the protagonist unless the plot gives it a reason to react.

- Give extras, staff, traffic, machinery, animals, screens, weather, or household routines a low-intensity baseline behavior.
- Keep background action sparse enough not to steal focus, but do not freeze the entire space during emotional dialogue.
- Avoid synchronized crowd turns, collective staring, random filming, or everyone stopping at the same instant.
- When the subjective sound field narrows, visual background movement may remain normal; perception changes without the world literally stopping.
- After the private emotional beat, returning ambience or ordinary background motion can re-establish that life continues.

## Visual Reference Image Prompt Patterns

Use these optional text-to-image prompts as visual anchors before video generation. They are not the final video prompt. Keep them consistent with the final prompt. The user may generate these references first for more control, or skip them and generate video directly.

Reference prompts should be complete enough to generate usable production references, not vague mood labels. Match the current segment's story state: costume, hair, dirt, wetness, injury, makeup, emotional baseline, prop ownership, light, weather, and setting should fit what is happening in that video segment. Do not reuse a generic character portrait if the character is currently running, grieving, injured, soaked, disguised, transformed, or in a different costume.

### Reference Prompt Completeness Standard

Use this standard whenever reference prompts are output:

- **Character reference**: identity/role, age range, ethnicity/era when relevant, face shape and temperament, hairstyle, body type or posture, clothing and costume state, visible dirt/wetness/injury/makeup, emotional baseline, shot size, background/light, film texture, and constraints such as non-fashion, non-glamour, non-monsterized, natural performance.
- **Single-character isolation**: a character reference for one person must describe only that person. Do not include other visible characters, relationship blocking, another person's hands/shoulders, hugging, holding, protecting, chasing, fighting, or looking at another named person. These details can cause image generation to create extra inconsistent characters.
- **Scene reference**: exact location type, spatial layout, foreground/midground/background, entrances/exits, action path, obstacles, key furniture/vehicles/architecture, practical light source and color mood, materials, weather/atmosphere, era, and whether it should be `no people`.
- **Key prop/product reference**: object type, era, material, color, scale, wear marks, story-specific identifiers, current state, owner/placement if important, light/background, and detail clarity.
- **Relationship/two-shot reference**: both identities, screen-left/screen-right positions, height/distance, eye lines, body tension, costume state, shared environment, and power relationship.

Keep references complete but purposeful. Do not output long inventories of irrelevant fashion details, room objects, or texture adjectives that the current video will never use.

### Reference Output Decision Strategy

Choose references by the production problem being solved:

| Need | Recommended Reference | Notes |
|---|---|---|
| Stable single character identity | Character identity reference | One visible person only; neutral or current emotional baseline, clear face/hair/costume |
| Two-character height, distance, or chemistry | Relationship/two-shot reference | Use only when blocking or physical relationship matters |
| Stable room/location layout | Clean scene plate | No people; show entrances, depth, light sources, action path |
| Story-critical object/product | Key prop/product reference | Only if its design must remain stable or readable |
| Exact opening composition | First-frame reference | Match the first shot's framing and initial body state |
| Continuation between clips | Existing references + optional previous tail frame | Use tail frame only when exact posture, blocking, prop position, or damage state matters |
| New character in existing scene | New character reference only | Reuse existing scene references and continuity state |
| New location in continuation | New clean scene plate | Add only when the story actually enters the new location |

Priority order:

1. Character identity reference, when faces must remain stable.
2. Clean scene plate, when spatial layout matters.
3. Existing continuity state from previous segment, when continuing.
4. Previous tail frame, only when exact body/prop/spatial state matters.
5. Relationship/two-shot reference, when blocking/chemistry matters.
6. Key prop/product reference, only when central.

Do not provide redundant references. A simple face close-up usually needs only one character reference. A complex period dialogue may need two separate character references plus one clean scene plate. Add a relationship/two-shot reference only when shared blocking or chemistry must be controlled.

### First-Frame vs Identity Reference

- Identity reference: neutral or baseline expression, readable face/hair/costume; used to preserve who the character is.
- First-frame reference: exact pose, framing, gaze, prop position, and scene state at video start; used to control how the shot begins.
- Do not confuse them. A stylized portrait may preserve identity but be a poor first-frame reference.

### Relationship / Two-Shot Reference

Use when the video depends on height difference, seating positions, intimate distance, confrontation geometry, or who occupies visual power.

Include:

- both adult characters' identity anchors
- screen-left/screen-right positions
- body distance and eyelines
- costume and height/build contrast
- scene light and camera height
- no complex action; this is a blocking reference

Do not use a relationship/two-shot reference as a substitute for identity references when each character needs stable faces. Generate individual character references first, then a two-shot reference only if the scene needs relationship geometry.

### Character Reference

Purpose: stabilize identity, age, temperament, costume, and facial baseline.

Include identity/role, age range, ethnicity/era if relevant, face impression, hair, body type/posture, clothing, current costume state, visible dirt/wetness/injury/makeup when relevant, emotional baseline, shot size, lighting/background, film texture, and color palette.

Single-character rule:

- Describe only this one person.
- Do not mention other characters by role or name, such as daughter, mother, father, lover, enemy, police, doctor, crowd, corpse group, or partner.
- Do not describe interaction with another person, such as holding a child, protecting someone, hugging, kissing, grabbing, fighting, being chased by a visible person, or looking at a named person.
- If the character's emotional baseline is relational, translate it into that person's solo body evidence. For example, write `protective tension in her shoulders and alert eyes`, not `protecting her daughter`.
- If the video requires multiple people in one still image, use `Relationship / Two-Shot Reference` instead of a single-character reference.

Template:

```text
Character reference image: single-character image, only {identity/character} appears, {age range/ethnicity or era}, {face shape and presence}, {hairstyle and body posture}, {costume and current state: clean/torn/soaked/dusty/bloodstained but not gory/makeup changes}, {emotional baseline and eye state, expressed through visible single-person performance}, {camera distance}, {light and background}, realistic cinematic texture, desaturated tones, fine natural skin texture, not a glamour pose, not a fashion editorial, natural performance, no other people.
```

Example:

```text
Character reference image: a woman in classical Chinese style, around twenty-seven, slender and restrained, oval face, gentle features but with a sense of fatigue, black hair in a low bun, a plain blue-grey palace dress, a few silver hairpins, a calm expression but slightly moist eyes, head close-up, candlelight from the side, a dark palace background, realistic period-film texture, desaturated tones.
```

### Scene Reference

Purpose: stabilize layout, light source, materials, and action space.

Include location, spatial layout, foreground/midground/background, entrances/exits, light source, color temperature, key objects, usable action path, obstacles, atmosphere/weather, era, and materials. Use `no people` when the scene reference should be clean.

Template:

```text
Scene reference image: {location and era/genre}, {spatial structure and camera direction}, foreground {...}, midground {...}, background {...}, entrance/exit {...}, usable movement line {...}, obstacles/key objects {...}, {main light source and color tone}, {weather/smoke/haze/materials and atmosphere}, realistic cinematic set texture, clear spatial depth, no people.
```

Example:

```text
Scene reference image: a late-night apartment of a woman living alone, one continuous space from the entryway to the living room; in the left foreground the entryway shoe cabinet, in the midground a half-dark living room, in the right background a half-open bedroom door; a small warm-yellow entryway light mixes with cold blue city light from the window; low-light realist cinematic texture, clear spatial depth, no people.
```

### Key Prop Reference

Purpose: stabilize objects that carry story information.

Use only for important props: old sweater, music box, rejection letter, phone, ring, sword, cup, car, watch.

Template:

```text
Key prop reference image: {prop name and purpose}, {era/material/color/size}, {wear, stains, damage or signs of use}, {story-relevant marks or readable features}, {current state and placement/holder}, {light and background}, realistic cinematic prop texture, macro or close shot, clear detail.
```

Example:

```text
Key prop reference image: a rusty old music box, dark red wooden case, worn corners, oxidized metal clockwork, fine scratches on the lid, sitting on an old wooden table, moonlight from the side, macro close shot, realistic cinematic prop texture, clear detail.
```

### Product or Vehicle Reference

Purpose: stabilize premium object structure and material.

Template:

```text
Product reference image: {product/vehicle}, {color and material}, {angle}, {environment and light}, realistic brand-film cinematic texture, accurate structure, natural materials, no incorrect text or logos.
```

### Reference Image Count

- Use 1 reference for a simple emotional close-up.
- Use 2 references for most scenes: character + scene.
- Use 3 references only when a prop/product is central or the scene is historically/stylistically demanding.
- Avoid giving separate reference prompts for every minor object.
- In compact mode, omit reference prompts unless explicitly requested or essential for control.
- In workshop mode, follow the chosen production path: reference recommendations are optional for direct-video work, while required assets in reference-first work remain explicit dependencies. Do not describe a required production reference as optional.
- In continuous-short-film mode, maintain references as a reusable asset list and mark each as `Reused`, `New`, or `Updated state`.

### Continuation References

- For continuation, reuse existing character/scene/prop references and previous continuity facts by default.
- Add new reference prompts only for new visual anchors.
- If using a previous tail frame, treat it as optional state guidance, not a required first frame. The scene reference can be omitted unless the camera moves into a new space.
- If a new character enters an existing scene, provide only the new character reference and state that the existing scene reference remains unchanged.
- If a character's visible state changes in a way the next clip must preserve, output an updated character reference with the new clothing, hair, dirt, wetness, injury, makeup, carried prop, and emotional baseline.
- If the same location changes materially, output an updated scene reference only for meaningful changes such as new damage, smoke, rain, fire, darkness, blocked exits, moved vehicles, broken furniture, or changed light source.

### Reference Consistency Check

Before finalizing, ensure reference prompts and video prompt share:

- same character age, clothing, hairstyle, and emotional baseline
- same setting, era, color palette, and lighting
- same key prop design
- same current-state details: dust, wetness, injury, makeup, costume damage, carried objects, scene damage, weather, and light state when relevant
- no contradiction between still-image pose and video action.
- single-character references contain exactly one visible person and do not smuggle in other characters through relationship wording or interaction actions.
- relationship/two-shot references are used only when multiple people intentionally need to appear together.

## Negative Constraints

Use negative constraints only when they prevent likely generation failure:

Write the desired content and action path positively first. Negative constraints are not the main steering wheel; they are a small guardrail after the positive target is clear. If a model does not handle negative language well, replace outcome-critical negatives with positive instructions.

- No cartoon look, no plastic skin, no excessive skin smoothing.
- No incorrect text, watermarks or subtitles.
- No background music, no extra score; keep only the necessary spoken dialogue, ambient sound, action sound effects and object sounds.
- No extra limbs, facial distortion or clipping.
- No excessive fast cutting if continuity matters.

### Negative Constraint Library

Pick the smallest useful set for the scene. Avoid bloated lists that repeat every possible failure mode.

**Universal core**

```text
Negative constraints: no subtitles or watermarks, no background music, no facial distortion, no extra fingers or limbs, no cartoon look.
```

When the scene has no visible hands or full body, omit hand/body constraints.

**Emotional close-up**

Risks: overacting, sudden emotion jump, plastic skin, beauty filter.

```text
No exaggerated wailing, no sudden expression changes, no excessive skin smoothing, no plastic skin, no facial distortion.
```

**Dialogue scene**

Risks: theatrical acting, messy mouth movement, bad eye lines, subtitles.

```text
No stage-play acting, no exaggerated arguing, no constantly flapping mouth shapes, no confused eyeline directions, no subtitles or watermarks.
```

**Romance or intimacy but non-explicit**

Risks: sexualization, melodrama, unwanted physical escalation.

```text
No explicit sexual suggestion, no sudden hugging or kissing, no exaggerated idol-drama acting, no excessive soft-focus smoothing.
```

**Suspense without monster**

Risks: horror clichés, jump scare, supernatural insertion.

```text
No ghosts or monsters, no gore, no jump-scare faces, no screaming, no exaggerated horror music.
```

**Action, chase, or physical movement**

Risks: motion confusion, duplicated bodies, impossible direction, warped limbs.

```text
No clipping, no confused spatial direction, no extra limbs, no characters teleporting, no excessive motion blur.
```

**Wuxia or combat**

Risks: fantasy overextension, weapon deformation, messy multi-person fights.

```text
No flying fantasy, no exaggerated light effects, no gore, no weapon deformation, no clipping limbs, no chaotic multi-person action.
```

This area still needs stronger reference examples before heavy use.

**Crowd, disaster, or large scene**

Risks: uncontrolled crowd, protagonist lost, disaster becoming monster/fantasy.

```text
No runaway number of people, no losing the protagonist, no sea monsters or supernatural, no excessive gore, no deformation of the scene structure.
```

**Product, vehicle, or premium object**

Risks: ad-like exaggeration, fake material, object deformation.

```text
No ad-style showy flourishes, no plastic texture, no deformation of car body or product structure, no excessive slow motion, no incorrect text or logos.
```

**Period drama or ancient costume**

Risks: modern styling, fantasy game look, costume inconsistency.

```text
No modern makeup, no modern jewelry, no cheap photo-studio period style, no game-CG look, no costume or hair-ornament jumps.
```

**Memory, dream, or montage**

Risks: too clear, too literal, over-glowy fantasy.

```text
No excessive dreamy glow, no turning it into horror, no memory images that are too complete and clear, no illogical scene jumps.
```

**Phone, screen, or text**

Risks: unreadable text, random letters, fake UI, subtitle pollution.

```text
No incorrect generated text, no garbled interfaces, no excessive phone-screen text, no subtitles or watermarks.
```

If key information is on a phone, prefer offscreen voice or a simple visible notification rather than relying on readable screen text.

**Food, hands, or table scenes**

Risks: hand/finger errors, object warping, continuity issues.

```text
No deformed fingers, no tableware clipping, no deformed chopsticks, no jumps in the number of cups or plates.
```

### When to Omit Negative Constraints

Omit or shorten them when:

- The user asks for a very compact prompt.
- The scene has few generation risks.
- The final prompt is near the duration-based character ceiling.

Minimum fallback:

```text
Negative constraints: no subtitles or watermarks, no background music, no facial distortion, no style drift.
```

## Quality Self-Check

Run this silently before giving the final answer. Do not print it unless the user asks for a critique, debug pass, or improvement report.

### Story and Structure

- Does the diagnosis name the emotional core and visual core?
- Is the chosen structure explicitly stated and justified?
- If the short-drama hook diagnostic was activated, was it justified by the user's request or plot type, and were only the useful narrative functions selected instead of forcing all six?
- If a proposed hook repair changes identity, motive, world rules, culprit, relationship, or ending, did the user request it, delegate creative control, or confirm the direction first?
- If the ending withholds an answer, does the immediate screen action still complete and leave a readable 1-2s consequence rather than stopping mid-line or mid-action?
- Does the duration fit the content instead of defaulting to 30s?
- Was duration/splitting judged by playable content rather than source text length alone, including event count, dialogue time, actions, emotional reactions, scene changes, camera moves, and ending breath?
- If the story exceeds 30s or the duration-based character ceiling, does the answer recommend splitting and clearly state what this prompt covers?
- If this is a split prompt, has the bridge type been chosen: different shot size/angle continuation, match-on-action, or complete shot-group continuation?
- For delayed recognition, mystery, time displacement, or hidden identity, does each character react only to evidence they have actually received, with known facts, new evidence, reasonable inference, and remaining unknowns kept distinct?
- Does the audience question evolve after each meaningful answer instead of repeating the same mystery, and do key questions reveal character values rather than merely explain the plot?
- If a retrospective reversal or deceptive montage is used, are objective truth, character perception, and audience belief tracked separately, with no character reacting beyond their actual perception?
- Do at least two earlier image or sound beats remain compatible with both the surface interpretation and the later revealed truth, rather than functioning as unrelated memory decoration?
- Does the reveal use previously prepared action, composition, direction, contact, object, or sound evidence instead of introducing an unsupported final fact or explanatory speech?
- If sound recontextualization or a camera-stability arc is used, does each change carry a specific perceptual or dramatic function while preserving action and spatial readability?
- If the ending depends on emotional change, was an earlier behavior, boundary, contact attempt, object action, or posture established so the final completion, stopping, reversal, transfer, or recontextualization feels earned?

### Prompt Usability

- Is the final prompt copy-ready and under the correct duration-based character ceiling when possible?
- Is the chosen output mode appropriate to the user's request: compact, workshop, or continuous-short-film?
- If the draft was too long, was the automatic compression ladder applied before splitting?
- For fight prompts, has the copy-ready final prompt stayed within the duration-based ceiling, with action beats limited to what the selected duration can clearly show?
- Is there no empty boilerplate such as `Video model: general AI video model`?
- Does the first summary line include duration and structure?
- Are technical terms useful rather than decorative?
- Can the first frame be reconstructed from the final prompt? If character-led, are visible subject, start state, screen position/depth, facing direction, gaze, prop contact, shot size, camera angle/axis, and motivated light source clear? If empty or object-led, are location layout, foreground/midground/background, key object/environment state, sound cue, shot size, camera angle/axis, and motivated light source clear?
- Does each shot have one core action path and one core camera behavior, with multiple camera phases serialized only when necessary?
- If the prompt requires continuation, split clips, first/last frames, complex blocking, repair, or a product/prop endpoint, is the final visible ending state clearly locked inside the last shot, whether it is character-led, empty, or object-led?
- Are story-critical props described with holder/hand, grip or support point, orientation, contact relationship, visible change, and final location/state?
- Has the copy-ready final prompt removed unresolved options such as `or`, `or else`, `A/B`, `pick one of two`, or `optional`, unless the user explicitly requested variants?
- Are professional shot-size, camera-movement, and focus terms written with standardized English abbreviations where appropriate, such as `ECU`, `VCU`, `BCU`, `CU`, `MCU`, `WS`, `KS`, `FLS`, `LS`, `ELS`, `MS`, `MLS`, `Dolly In/Out`, `Pan Right/Left`, `Tilt Up/Down`, `Track Right/Left`, `Crane/Jib`, `Arc/Orbit`, `Zoom In/Out`, `Dolly Zoom`, `Whip Pan`, `Rack Focus`, `Focus Pull`, `Handheld`, and `Static`?
- Does each named camera movement have a clear dramatic function: intimacy, context reveal, gaze/action following, scale, power shift, disorientation, transition, urgency, or deliberate stillness?
- If the prompt uses cinematic lighting, is the amount of lighting detail proportional to the scene? For ordinary scenes, is lighting kept to one compact motivated phrase instead of a full breakdown?
- If the prompt uses detailed cinematic lighting, does it specify Key Light, Fill Light, Rim Light or Soft edge highlight, Background/Volumetric Light, concrete surfaces touched or hidden by light, tonal structure such as `Low-key High Contrast` when relevant, color-temperature meaning when relevant, and the emotional/story meaning of the light-shadow design?
- If `Hard side-top Key Light` or `hard side-top light from upper right` appears, is there a believable source in the environment and a story reason for such hard light?
- If the scene has movement, does light interact with the movement through passing windows, doors, headlights, screens, weather, dust, fabric, breath, or moving shadows instead of remaining a static adjective?
- Are abstract words translated into visible action, light, sound, object, or performance?
- Has every abstract effect or theme been converted into eye-observable screen evidence instead of left as a label?
- Have physically, spatially, emotionally, or temporally contradictory instructions been removed or rewritten?
- Is the desired action path written positively before using any `don't...` constraints?
- Are details limited to what reduces ambiguity, supports continuity, clarifies emotion, or prevents likely failure, rather than over-specifying every pixel?
- If reference-image prompts are included, are they optional, concise, and consistent with the final video prompt?
- Are reference types selected by production need rather than outputting character, scene, and prop prompts mechanically?
- Is an identity reference distinguished from an exact first-frame reference?
- When actual reference images are available, does the compiled video prompt use only facts visibly confirmed in those images rather than silently inheriting planned details from the earlier image prompts?
- Were active references checked for watermarks/logos, garbled text, malformed anatomy, accidental people/objects, harmful crops, and other artifacts likely to propagate into video, with repair/cleaning recommended instead of relying on negative prompts?
- Are reference-image prompts complete enough for image generation, including current segment clothing, appearance, dirt/wetness/injury/makeup, emotional baseline, scene layout, light, materials, and action space where relevant?
- Do reference prompts avoid generic portraits or generic empty scenes when the current segment requires a specific costume state, disaster state, period styling, transformation, or emotional condition?
- For every single-character reference, does the prompt describe only one visible person and avoid mentioning other characters, relationships, or interaction actions that could generate extra people?
- If two or more characters need to appear together, has that been placed in a separate relationship/two-shot reference instead of contaminating individual identity references?
- For continuation, does the next prompt continue the previous story state while preserving identity, scene, lighting, sound bed, and key props without blindly copying the previous tail frame?

### Time and Rhythm

- Are time blocks playable, with enough duration for action, camera movement, line delivery, and reaction?
- If the user gave a short but content-dense plot, has it been split or narrowed instead of crammed into one 30s prompt?
- Is key dialogue or peak action not placed at the final instant?
- Does the ending leave 1-2 seconds for breath, reaction, sound tail, or visual afterimage?
- Are there too many events for the duration? If yes, remove details or split.
- Is shot duration based on dramatic weight instead of equal mechanical division?

### Dialogue and Sound

- If the plot implies a key spoken line, is the actual line written?
- Are phone calls, doctor/police notices, confessions, breakups, voice messages, or offscreen lines concrete?
- For a complex performance-led scene, does one compact performance contract define what each character wants, what protects them, and what they fear will happen if they stop or lose control?
- Are stable voice identity and temporary vocal state separated and preserved across cuts: age/register, texture, rhythm, requested accent, relative loudness, spatial position, plus current fatigue, hoarseness, recent crying, blocked breath, or panic?
- Is key dialogue playable in the time block at the intended local pace, including overlap, interruptions, pauses, failed starts, listener reactions, and ending residue?
- Were word count and average speech rate used only as risk indicators rather than automatic compression rules?
- If dialogue is intentionally dense, were camera moves, secondary gestures, and environment detail simplified before proposing line cuts?
- If a real timing conflict remains, was it explained with a split or user-approved edit instead of silently deleting key dialogue or forcing unnatural speed?
- If dialogue drives the acting, does the prompt treat the line as an expression timeline rather than placing a mood label before quoted text?
- For complex dialogue, is the shot-level timeline established first, with nested performance timing used only inside the shot that genuinely needs it?
- Are speaker and listener acting tracks both designed, with the listener reacting to a specific heard word without stealing the dramatic center?
- Does each important interruption identify its semantic entry trigger, motive, overlap hierarchy, yield behavior, and interrupted mouth/breath state?
- During overlapping dialogue, are speaker identity, independent lip movement, relative volume, sound direction, distance, and room reflection stable?
- If stammering, a failed start, self-correction, or an unfinished phrase is intentional, is its motive clear and is it protected from smoothing, reordering, completion, comic repetition, or audio-glitch behavior?
- If dialogue crosses a cut, are offscreen voice direction, speaker identity, acoustic continuity, and the semantic reason for the cut clear?
- If one sentence crosses a cut, is it divided into clear start/continuation fragments rather than accidentally repeated in full?
- Do edit points follow trigger words, meaning shifts, voice breaks, listener impact, or withheld phrases rather than equal time slicing?
- Does shot size tighten only when psychological access deepens, preserving visual escalation for the emotional crack or vulnerable line?
- Are trigger words, emphasis, pauses, breath, gaze changes, facial/body reactions, and post-line state tied to the actual wording?
- If a character moves from anger/sarcasm/calmness into vulnerability, is there an emotion barrier and a believable crack before crying, confession, or collapse?
- Are tears, voice breaks, outbursts, forgiveness, or surrender delayed until the line or reaction actually earns them?
- Does the shot have enough time for dialogue, physical action, camera movement, and reaction without rushing?
- Does each recurring gesture continue its previous phase across cuts, and does interpersonal distance or no-touch blocking preserve the relationship state?
- If a line intentionally remains unfinished, is the speech failure itself motivated and followed by enough visible or audible consequence to feel complete rather than accidentally truncated?
- If a generation priority ladder is used, does it resolve competing instructions without discarding continuity, safety, or the user's explicit must-have elements?
- Does sound design include concrete diegetic sound rather than generic music?
- Does the final prompt establish a concise sound bed with 2-4 concrete anchors, even when the scene is quiet?
- Does the prompt avoid background music by default and keep only necessary dialogue/voice, ambient sound, Foley, movement, object, and action sound effects?
- Is silence or sound reduction used when it would strengthen shock, tension, or aftermath?
- If sound becomes subjective, is there a motivated arc from objective environment through perceptual narrowing and close detail to rupture/silence and believable environment return, without arbitrary total muting?

### Character Performance

- If human performance realism is central, is the visible behavior driven by one clear psychological motive rather than isolated facial expressions?
- Do expression, eye line, voice texture, pause placement, mouth corners, brow, jaw, breath, and body language serve the same inner state?
- Are incidental gestures state-driven and low-motivated by the moment, rather than decorative posing or random action?
- Do head, eyes, neck, shoulders, breath, hands, sleeves, and weight shift move as a linked body system instead of isolated parts?
- Are emotions expressed through eyes, lips, jaw, breath, hands, posture, and timing?
- For intense emotional scenes, is there a continuous chain from inner conflict to physiological reaction, micro-expression, action anchor, and decisive behavior?
- Does the recurring hand/prop/posture anchor evolve continuously instead of resetting between beats?
- For long close-ups, is there a smooth micro-expression timeline with no sudden jump?
- Are 3-5 micro-expression beats chosen instead of an overloaded facial-action list?
- If AU/FACS appears, is it only auxiliary calibration after visible natural-language facial action, with compact intensity and no long code dump?
- Do important facial expressions have onset, peak, and release/transform rather than appearing fully formed from the first frame?
- Is the performance natural for the character's situation, age, status, and relationship?
- Are tears, crying, anger, or fear restrained unless the story specifically needs a large outburst?
- For recurring characters, are permanent identity traits separated from temporary state such as tears, sweat, dust, injury, or costume damage?
- For a non-human performer, are emotion and recognition expressed through species/design-appropriate sensory orientation, body tension, movement, breath/mechanical rhythm, distance, contact, and age/energy limits rather than human-style facial acting?
- Does a non-human subject preserve its established age, injury, energy, anatomy, and locomotion even when emotional intent changes quickly?

### Camera and Visual Logic

- Was the aspect ratio explicit, inherited from an actual production frame/continuation, or safely defaulted without unnecessary questioning?
- If `9:16 vertical` is active, was the scene deliberately recomposed for a narrow canvas rather than side-cropped from horizontal grammar?
- In vertical output, are faces, eyes, hands, key props, head/foot room, entry/exit paths, and final action endpoints protected inside a readable action corridor?
- Are two-person/group relationships expressed through depth, `OTS`, height, focus, reflection, masking, or motivated coverage rather than several subjects squeezed against the side edges?
- Are horizontal moves short enough to retain the subject and land on a visible target, and are vertical moves motivated by real height/depth/action information?
- Do literal first/tail frames and other composition-controlling references match the target ratio, with horizontal-to-vertical reframing inspected instead of assumed?
- If the scene uses phone realism, documentary realism, period candlelight, low-key crime, commercial product, or another visual mode, are camera, light, focus, grain/noise, stabilization, skin texture, and spatial scale consistent with that single shooting condition?
- Does every final prompt include at least one motivated light source or scene-level light baseline, with direction, color relationship, or visible effect stated concretely?
- In a multi-shot or continuation prompt, do light direction, skin tone, shadow position, sound bed, and acoustic space stay continuous unless a visible event changes them?
- When a character touches an object, is there believable before/contact/pressure/aftermath logic with weight, friction, resistance, shadow, reflection, or cloth response?
- Do hair, clothing, props, light, reflection, sound, or room tone respond subtly to character motion so the person does not feel pasted onto the background?
- Is the camera movement physically plausible?
- Is camera movement motivated by gaze, body movement, emotional distance, or object interaction rather than decoration?
- Has the prompt avoided piling up multiple camera moves in one beat when a single `Static`, `Dolly-In`, `Pull-Back`, `Pan`, `Tracking`, or `Handheld` choice would be clearer?
- If this is a one-take scene, does it have a clear start frame, physically possible camera path, blocking/focus change, foreground/background depth, stable screen direction, and held ending?
- If a first-frame reference is supplied, does it lock the opening state without freezing all later framing? Are explicit locked-camera constraints honored, while true one-take requests forbid cuts but still allow continuous motivated reframing, focus and physical camera travel?
- If the content needs several evidence, reaction, power, or aftermath beats, was a motivated multi-shot progression considered instead of defaulting to a static long take? Does every new view change what the audience knows, feels, or can physically verify?
- For reference-driven motion, were visible hand/foot positions, body support, reach, furniture clearance, prop weight/friction, action path, and exit space checked before writing contact and movement?
- If this is a one-take multi-character reveal, are characters revealed progressively with foreground masking, lateral movement, or pull-back hierarchy, and are their faces, hairstyles, costumes, postures, and emotional baselines distinct enough to avoid repeated faces?
- If `Rack Focus` or `Focus Pull` appears, does it shift attention between meaningful subjects such as face/object, foreground/background, reflection/body, or hand/reaction?
- Before a large body action, does the framing create enough physical space to show it clearly?
- Does each shot have a clear subject and composition?
- For action or crowd scenes, is spatial direction clear?
- For large scenes, is there one visual anchor the model can follow?
- For product/person texture scenes, are materials, tactile details, and light concrete?
- For memory/dream scenes, is there a transition anchor such as sound, object, gesture, or match cut?
- In multi-shot prompts, do adjacent shots avoid overly similar shot sizes unless motivated?
- When cutting between shots of the same subject or interaction inside the same scene, does the camera angle change by at least 30 degrees? If cutting to a new scene or location, is the new opening composition clear instead of forcing the 30-degree rule?
- Is the 180-degree axis preserved, or is any axis crossing visibly motivated?
- Do dialogue eyelines remain matched across reverse shots?
- Are entry/exit and travel directions continuous across connected spaces?
- Are handedness, prop position, costume state, tears/injury marks, and body posture continuous?
- For recurring scenes, are doors, furniture, lights, damage, props, entrances, and action paths consistent with the scene bible?
- In continuation, does the previous ending define continuity facts while the next opening uses the most natural bridge type rather than forcing the exact same tail frame?
- Are insert shots used when long dialogue or emotional pauses need breathing room?
- Does the ending leave a 1-2s performance pause or visual/sound tail?
- If one action is split across shots, does the second shot continue the same action with match-on-action continuity?
- Are action, light change, environmental reaction, and sound effect bound to the same readable event where appropriate?
- When the event itself is less important than the realization, does the prompt stay on the observer and use sufficient offscreen sound, eyeline, object/environment response, or delayed reaction instead of an unnecessary insert?
- For unequal height, body geometry, mobility, or species, are camera height, foreground anchor, gaze direction, and relationship axis adapted without forcing a conventional human over-shoulder composition?
- If a foreground occlusion performs a reveal, disappearance, time shift, or bridge, is the occluder motivated and are before/after geography, axis, light, sound, parallax, and final state locked?
- In inhabited locations, do background people and systems maintain plausible independent low-intensity behavior rather than freezing, staring, gathering, or mirroring the protagonist without cause?

### Negative Constraints

- Are negative constraints scene-specific and concise?
- Do they target likely failures: subtitles/watermarks, face distortion, extra fingers, hand errors, motion confusion, style mismatch, modern styling in period scenes, fake product material?
- Are irrelevant constraints omitted?

### Safety and Taste

- Does the prompt avoid explicit sexual content, sexualized minors, and non-consensual sexual material?
- For violence, does it focus on staging, suspense, consequence, or emotion rather than gore?
- Does intimacy stay within the user's requested tone and boundaries?

### Final Pass

- Would a video model know what to show in each second?
- Would a director or cinematographer understand the scene's physical execution?
- Is the prompt cinematic because of concrete choices, not generic adjectives?
- Is the answer useful for workshop mode: diagnosis and strategy concise, final prompt dominant?
