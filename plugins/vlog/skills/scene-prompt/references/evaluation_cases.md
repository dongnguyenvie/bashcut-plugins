# Formal Evaluation Set

Use this file only when testing or revising the skill. Do not load it during ordinary prompt generation.

## Scoring Rubric

Score each case out of 100:

- Story diagnosis and structure choice: 15
- Duration and pacing feasibility: 15
- Camera, axis, eyeline, and spatial continuity: 15
- Character performance and emotional clarity: 15
- Dialogue timing and sound design: 10
- Reference-image consistency: 10
- Prompt clarity, compression, and length compliance: 10
- Scene-specific negative constraints and safety: 10

Pass levels:

- 90-100: strong prompt-text result; actual media quality still requires generated-result review
- 80-89: usable with minor revision
- 70-79: major weakness in one area
- below 70: revise rules or output strategy

Automatic failure conditions:

- final prompt exceeds the duration-based character ceiling without recommending a split
- single segment exceeds 30 seconds
- repeats a resolved approval, executes an unapproved media action, omits requested deliverables without a stated blocker, or claims unavailable image/video verification
- key plot-changing dialogue is omitted
- dialogue cannot physically fit its assigned time
- continuation resets character, scene, prop, or emotional state
- action direction becomes contradictory or axis flips without motivation
- unsafe explicit sexual content, sexualized minors, or gore-focused violence

## Evaluation Procedure

For each case:

1. Generate the answer in the mode/stage requested by the case; use workshop mode only when unspecified. Keep explicit approval boundaries and host capability conditions.
2. Measure only the copy-ready final prompt against the duration-based character ceiling.
3. Check timing beat by beat.
4. Mark continuity states: position, direction, held object, costume, light, emotional residue.
5. Record failures and update rules only when the failure is generalizable.

---

## Case 01: Quiet Grief Close-Up

Input:

```text
An imperial palace woman in ancient China learns that the man she loves deeply will be ordered to die tomorrow. She stands alone before the candlelight, unable to cry aloud, and can only slowly accept the news. Require a 10-second extreme facial close-up with a fixed camera, no dialogue.
```

Expected:

- Structure: long close-up micro-expression / emotional arc.
- No unnecessary scene cuts or body blocking.
- Smooth progression from reception to restraint to one controlled release.
- Character reference only; scene reference optional.
- No background music; candle, breath, distant drum may remain.
- Final prompt target: 500-800 characters.

Failure checks:

- sudden crying before emotional buildup
- too many facial beats for 10s
- theatrical grimacing or beauty-filter language

## Case 02: Two-Person Dialogue and Axis

Input:

```text
At the New Year's Eve dinner table, the father announces that he is selling the old house, the mother silently avoids the subject, and the daughter realizes her parents decided long ago. 15 seconds, multi-person dialogue, restrained conflict.
```

Expected:

- Structure: dialogue cross-cutting with one insert shot.
- Establish father, mother, daughter positions.
- Preserve screen-left/right and eyelines in close-ups.
- Key lines are explicit and timed.
- Insert may use chopsticks, bowl, steam, or hand movement.
- Dialogue ends before final 1-2s silence.

Failure checks:

- reverse-shot eyelines flip
- three long lines packed into a few seconds
- no reaction time after daughter's final line

## Case 03: Phone-Call Shock

Input:

```text
Late-night apartment: a girl gets a phone call telling her that her boyfriend died in a car accident. She chats lightly at first; after hearing the terrible news her smile freezes, and after hanging up she covers her mouth and sobs silently. 15 seconds, three jump-cut segments.
```

Expected:

- Caller states the actual news.
- Dialogue delivery time fits.
- Smile freeze uses micro-expression progression.
- Phone remains in the same hand unless a transfer is shown.
- Sound shifts from phone noise/room tone to muffled shock and suppressed breath.
- Ending leaves silent aftermath.

Failure checks:

- vague phrase such as “the other person delivers the terrible news”
- phone changes hands or position without action
- crying starts instantly

## Case 04: Suspense Spatial Continuity

Input:

```text
A girl who lives alone comes home and finds an unfamiliar key in the entryway; after walking into the living room she hears a phone vibrating in the bedroom. 15 seconds, no ghosts or attackers appear.
```

Expected:

- Scene reference defines the entryway, living room and bedroom door spatial relationship.
- Character movement direction remains continuous.
- Suspense comes from sound and withheld information.
- No jump scare, monster, or unexplained location flip.

Failure checks:

- bedroom switches screen side
- protagonist teleports between spaces
- loud horror music replaces environmental sound

## Case 05: Match-on-Action Emotional Prop

Input:

```text
Two people who have broken up reach for the same cup at the same moment in the kitchen early in the morning; after their fingers touch, both pretend nothing happened. 10 seconds.
```

Expected:

- Use match-on-action: medium start of reach -> close continuation at cup.
- Change shot size and horizontal camera angle.
- Cup position and which hands touch remain consistent.
- One short exchange only; leave ending breath.

Failure checks:

- reach action restarts in the second shot
- cup jumps location or hand side
- adjacent similar shot sizes without motivation

## Case 06: 1v1 Fight Choreography

Input:

```text
In an underground ring in an abandoned warehouse, two adult women fight a 10-second live-action bout. Round one: probing punches and kicks; round two: close-in reversal throw. A crowd watches but does not take part.
```

Expected:

- Structure: fight choreography.
- 2 shots, 6-8 total action beats.
- Attack line, evasion, contact point, footwork, weight transfer, camera response.
- Stable A/B screen positions until a visible pivot or throw.
- Use 2-4 principal camera methods selected for specific fight beats; no unmotivated stacking of orbit, whip pan, push-in, slow motion, and impact hold.
- Final prompt 1300-1800 characters when the selected duration is 10-15s; longer 16-30s fight prompts may use up to 2800 characters if every beat is necessary.
- Staged, non-lethal, no gore.

Failure checks:

- more than 10 action beats
- crowd enters fight
- throw occurs without level change/grip/momentum setup
- camera tricks obscure contact points, landing positions, or the attack-defense chain

## Case 07: Environmental Fight

Input:

```text
A falling-out in an ancient gambling house: a wandering jianghu gambler uses the gambling table, dice cup, long bench and wooden pillar to turn the tables on two thugs. 15 seconds, no gore.
```

Expected:

- Clear room layout and environmental anchors.
- Cause-effect chain: body -> prop contact -> prop reaction -> opponent reaction -> camera reaction.
- 2-3 shots, no more than 10 beats.
- Props do not teleport or randomly break.
- Final prompt under the duration-based character ceiling.

Failure checks:

- too many simultaneous attackers/actions
- furniture positions change between shots
- impact lacks environmental consequence

## Case 08: Large-Scene Compression

Input:

```text
On a stormy night a passenger ship lists; passengers flee, a mother pushes against the crowd looking for her child, and finally sees him through a closing watertight door. 15 seconds.
```

Expected:

- One visual anchor: mother's distinctive clothing.
- Crowd acts as pressure, not competing protagonists.
- 4-5 clear story nodes maximum.
- Spatial direction toward the watertight door remains consistent.
- Child's line, if used, finishes before final held reaction.

Failure checks:

- protagonist lost in crowd
- disaster spectacle overwhelms story
- final line lands at 15.0s with no breath

## Case 09: Long Story Split and Tail Frame

Input:

```text
30-second story: a man who has not come home in many years reunites with his aged mother at an old train station late at night. Split it into two 15-second segments, and use the first segment's last frame to generate the second.
```

Expected:

- Segment 1: discovery and approach; stable tail-frame composition.
- Segment 2: preserves the previous story/action state; recognition and touch, with a motivated differentiated opening angle unless a same-shot extension is explicit.
- Same clothing, light, bench, sweater, positions, and sound bed.
- Each final prompt under the duration-based character ceiling.

Failure checks:

- second segment resets the event or repeats discovery; a motivated new angle preserving story state is allowed
- mother already recognizes him in segment 1
- prop or lighting changes

## Case 10: Continuation with New Character and Location

Input:

```text
Previous segment: a girl in her apartment gets a call saying her boyfriend has died; it ends with her curled up on the floor. Continue with the next segment: she rushes to the hospital and meets her boyfriend's sister for the first time.
```

Expected:

- Continuation diagnosis explains emotional and spatial transition.
- Reuse protagonist reference; add new sister character reference and hospital scene reference.
- Preserve protagonist clothing, phone, tear state, and emotional residue unless a time gap is stated.
- Do not replay the phone reveal.

Failure checks:

- no new visual references
- protagonist appears freshly composed without transition
- too many hospital events in one segment

## Case 11: Vague Input Handling

Input:

```text
I want a really stunning, really cinematic video.
```

Expected:

- Ask one concise question covering missing foundation: protagonist, setting, and intended emotion/transformation.
- Do not invent a full story immediately.

Failure checks:

- generic spectacle prompt
- asks for lenses, lighting, or other technical details before story foundations

## Case 12: Reference Consistency

Input:

```text
A young lady of an ancient household suddenly sees her beloved by the window in the afternoon; 10-second extreme facial close-up, no dialogue. First give the character reference image, then the video prompt.
```

Expected:

- Character prompt and video prompt match age, hairstyle, hairpins, clothing, light, makeup, and emotional baseline.
- Camera may represent the beloved's POV.
- No second person visible.
- No contradictory lighting or fashion-poster pose.

Failure checks:

- character details drift between reference and video prompt
- overt seduction replaces restrained shy love
- camera movement conflicts with fixed-close-up request

## Case 13: Automatic Compression

Input:

```text
Please compress a 15-second prompt containing 3 characters, 4 shots, two dialogue exchanges, a rainy-night argument inside a car and one getting-out-of-the-car action to under 2000 characters, while keeping the story and emotion.
```

Expected:

- Apply the compression ladder before splitting.
- Remove repeated style/light/sound descriptions first.
- Preserve plot-changing dialogue, spatial continuity, reaction, and ending breath.
- If still overloaded, reduce shot/event count or recommend splitting.

Failure checks:

- removes the core reveal or listener reaction
- compresses into unreadable fragments
- leaves repeated style boilerplate while cutting causality

## Case 14: Character Bible Continuity

Input:

```text
Three consecutive ancient-style short segments use the same 26-year-old palace woman: in segment one her hairpin is intact, in segment two her left hairpin falls out as she flees, and in segment three she hides in a side hall and the story continues.
```

Expected:

- Canonical identity remains stable.
- Temporary state updates after segment 2: left hairpin missing, hair slightly loose, clothing wet/dusty if established.
- Segment 3 does not restore the missing hairpin.
- Reference assets mark `updated state`, not a new identity.

Failure checks:

- face, age, costume, or hair color drifts
- missing accessory resets
- state change occurs without visible action

## Case 15: Scene Bible and Prop State

Input:

```text
Generate two consecutive segments in the same late-night apartment: in segment one the girl puts her phone on the right side of the living-room floor and walks toward the bedroom; in segment two she hears a knock and returns to the living room.
```

Expected:

- Apartment layout, bedroom side, door, light direction, and travel direction remain stable.
- Phone remains on the floor until picked up on screen.
- The second segment begins from the previous tail-frame state.

Failure checks:

- phone appears in hand without pickup
- bedroom/door swaps side
- lighting or time resets

## Case 16: Output Mode Selection

Inputs:

```text
A: Just give me the final prompt, no analysis.
B: Diagnose the story first; I want to adjust it together.
C: This is a 5-segment continuous short film; please keep characters and scenes consistent.
```

Expected:

- A uses compact mode.
- B uses workshop mode.
- C uses continuous-short-film mode with character/scene continuity and tail-frame anchors.

Failure checks:

- outputs the same structure for all three
- compact mode includes unnecessary references
- continuous mode omits reusable continuity records

## Case 17: Coquettish Soft Refusal Close-Up

Input:

```text
In an intimate but safe relationship, a young woman says softly "I don't want to"; she is not really refusing, but being a little petulant, shy and willful in the way of someone who is doted on. 6-second fixed facial close-up, nothing explicit, no exaggerated coquettishness.
```

Expected:

- Structure: ultra-close face long take / coquettish soft refusal arc.
- The line `I don't want to` is explicitly written and timed.
- Performance reads as gentle, safe, playful softness: gaze dodges then returns, mouth suppresses a smile, body does not retreat.
- No real fear, coercion, disgust, explicit seduction, childish baby voice, or cartoonish pout.
- Final prompt target: 500-800 characters.

Failure checks:

- interprets the refusal as fear or non-consent
- turns the scene into overt sexualization or exposed-body emphasis
- uses exaggerated idol-drama acting instead of subtle micro-expression
- omits the spoken line

## Case 18: General Camera Movement Function

Input:

```text
15-second psychological suspense: in an empty subway station, a man discovers that the person on the opposite platform looks exactly like him. First ordinary waiting, then he hears a glitching announcement, looks up and sees the opposite side, the world suddenly feels off-balance, and in the end he does not run, he just freezes.
```

Expected:

- Camera movement is selected by function, not stacked as decoration.
- Ordinary waiting can use `Static` or subtle `Handheld`; discovery can use `Pan` or `Push-In`; psychological vertigo may use one brief `Dolly Zoom` or `Dutch Angle Static`.
- No more than 2-3 principal moves in the final prompt.
- Movement has readable start/end subjects and leaves 1-2s frozen aftermath.
- Station geography and screen direction remain clear.

Failure checks:

- piles up `Push-In`, `Orbit`, `Zoom`, `Whip Pan`, `Handheld`, and `Dutch Angle` in the same beat
- uses `Dolly Zoom` without a major realization
- camera movement obscures the double's position or the protagonist's reaction
- ending cuts immediately at the discovery without aftermath

## Case 19: Live Performance Realism

Input:

```text
At home at night by the dining table, a young woman explains to the camera why she did not go to her friend's wedding. She looks calm on the surface but actually cares a lot about it. 10 seconds, handheld phone-footage feel, waist-up medium close-up, a glass of water on the table.
```

Expected:

- Strategy mentions live performance realism or psychological motive.
- Performance is driven by one motive: restrained explanation of something that matters to her.
- Eye line, pauses, voice pace, mouth corners, breath, and small gestures align with that motive.
- Body language is low-amplitude and incidental: slight head dip, small nod, fingers near cup, sleeve adjustment, tiny weight shift.
- Biomechanics are linked: eyes move before head, neck/shoulders follow, breath affects chest/voice, hand movement involves wrist/forearm/sleeve.
- Object contact has weight and sequence: fingertips approach cup, contact, slight pressure/friction, cup remains stable.
- Environment responds subtly: hair, sleeve folds, cup reflection, warm light/shadow, room tone.
- Camera/light/focus stay consistent with phone indoor realism; no commercial studio look.

Failure checks:

- fixed fake smile or empty eyes
- gestures added only to make the frame busy
- isolated head/hand movement with frozen shoulders and no breath
- hand/cup penetration, cup drift, or object movement before contact
- character feels pasted onto the background
- phone realism mixed with perfect studio lighting, plastic skin, or ad-like stabilization

## Case 20: Ordinary Drama One-Take Blocking

Input:

```text
15-second one-take: in the kitchen late at night, a wife discovers the diagnosis report her husband hid under the sink. The husband walks in from the living room wanting to explain; she does not question him right away, she just slowly pushes the report back where it was, and finally the two look at each other in silence across the kitchen island.
```

Expected:

- Structure: single take, ordinary drama one-take blocking.
- Clear start frame and spatial anchors: kitchen island, sink cabinet, living-room entrance, report.
- One physically possible camera path, not multiple invisible cuts.
- Blocking changes relationship pressure: wife near sink/island, husband entering from living-room side, island between them at the end.
- Use `Rack Focus` or `Focus Pull` only if it clarifies report -> wife reaction -> husband entrance.
- Keep screen direction, prop position, lighting, and body distance continuous.
- End with 1-2s held silence after the report is pushed back.

Failure checks:

- says one-take but describes unrelated camera angles or cuts
- report jumps from hand to drawer/counter without visible action
- husband teleports into the kitchen or changes side of the island
- uses too many camera moves instead of one coherent path
- ends on the line/reveal without silence or reaction

## Case 21: One-Take Character Reveal Ladder

Input:

```text
15-second one-take ensemble in the courtyard of an ancient mansion: the eldest legitimate son, the eldest legitimate daughter, a son by a concubine and a daughter by a concubine, four people in a hidden standoff. Start on a facial close-up of the eldest legitimate son, and gradually reveal the others through orbiting, back-view occlusion, lateral tracking and pulling back, ending in the courtyard's power positions. No dialogue.
```

Expected:

- Structure: single take with character reveal ladder.
- Starts on one face only, then reveals others progressively rather than showing all four at once.
- Uses foreground/back/shoulder/table/column masking to keep the one-take path physical.
- Each character has distinct identity anchors: face impression, hair/headdress, costume color/material, posture, status, emotional baseline.
- Pull-back or widening clarifies hierarchy and courtyard layout.
- Stable lighting/atmosphere is summarized once; night courtyard light stays physically plausible: moonlight as soft ambient/edge light, face readability from lantern/candle/corridor/window spill or stone/table bounce, no hard moonlight cutting a face without source logic.
- No duplicate faces, extra people, modern objects, or identity drift.

Failure checks:

- describes cuts while claiming one-take
- reveals four people too fast with no spatial logic
- characters have similar faces/clothes or duplicated identity
- camera path circles/passes through impossible space
- lighting and style tags crowd out blocking, identity, and hierarchy
- cold moonlight or abstract cinematic lighting creates an unrealistic hard face spotlight in an outdoor courtyard

## Case 22: Prompt Sampling Range Control

Input:

```text
Make a 10-second shattered-memory flashback: a girl stands at a station on a rainy night, and a car crash, a red umbrella, broken glass and a text message flash through her mind. It should feel cinematic; the emotion is suddenly remembering the truth.
```

Expected:

- Strategy names the abstract effect and translates `shattered-memory flashback` into visible fragments rather than leaving it as a style label.
- Final prompt uses a small number of concrete memory shards, such as rain on glass, red umbrella reflected in a puddle, headlight flare, phone vibration, glass shards catching light, and the girl's eyes refocusing.
- The memory fragments are physically compatible; no object is asked to break into fragments and form an impossible unrelated shape at the same time.
- The desired action path is written positively: the girl freezes, visual shards intrude, her gaze locks onto one clue, and she realizes the truth.
- Negative constraints are short and secondary, focused on likely failures such as no subtitles/watermarks, no background music, no face distortion, and no over-glowy fantasy.
- Details are limited to the strongest 4-5 visual anchors so the 10s clip remains playable and not over-specified.

Failure checks:

- only says `shattered-memory flashback` or `cinematic effects` without visible screen evidence
- relies on `no chaos, no blank staring, no failure` instead of describing the desired visual/action path
- contains contradictory object behavior, impossible lighting, or incompatible camera movement
- lists too many fragments, props, overlays, camera moves, and emotions for 10 seconds
- negative constraints become longer than the positive creative prompt

## Case 23: Execution Stability and Prop Endpoint

Input:

```text
12-second suspense scene: in an office late at night, a female lawyer finds key evidence on a USB drive on her desk. She has just plugged it into the computer when footsteps sound outside the door; she immediately pulls out the USB drive, hides it in her left cuff, and pretends to keep reading documents.
```

Expected:

- Final prompt opening is reconstructable: office layout, woman position, desk/computer/U-disk start state, shot size, angle, gaze, and practical light source are clear.
- Each shot has one core action and one core camera behavior; camera movement does not compete with the U-disk handling.
- U-disk state is precise: where it starts, which hand inserts it, when it is pulled out, how it is hidden in the left sleeve, and where it ends.
- Ending state is locked because this can continue: woman seated or standing, left sleeve hiding the U-disk, file in front of her, gaze/face pretending calm, door/footstep direction established.
- No unresolved options such as `or`, `or else`, `A/B`, `optional`.
- Sound includes diegetic anchors: computer USB sound, distant footsteps, paper movement, breath or room tone; no background music by default.

Failure checks:

- starts with a vague office mood and does not specify the first frame
- says `she hides the USB drive` without holder/hand/contact/final location
- uses several competing camera moves in one shot
- ends before showing the hidden U-disk state and her cover behavior
- includes optional branches like `hides it in her cuff or a drawer`
- relies mainly on negative constraints instead of positive stable action

## Case 24: Dialogue-Driven Performance Control

Input:

```text
15-second emotional accusation scene: late at night in the living room, a woman finally learns that three years ago her husband hid from her the news that her father was critically ill. At first she does not cry; she pushes back calmly, saying: "You knew all along, didn't you? Then what were these three years to me?" The first line is on the attack; in the second line her voice softens when she reaches "me", and only at the end does the first tear fall. The husband sits across from her in silence.
```

Expected:

- Strategy mentions dialogue-driven performance control, trigger words, or emotion barrier.
- The prompt does not write `the woman says, crying sadly` as a single mood label. It treats the dialogue as the expression timeline.
- The first line is still protected by anger or cold control; grief does not appear fully at the start.
- The trigger word is clear, especially `me` or `three years`; the second line changes voice, gaze, face, and body after that word.
- Pauses, breath, short inhale, swallowing, gaze drop, mouth tightening, or jaw release are tied to the line delivery.
- First tear is delayed until after the protection layer cracks; it does not fall before or during the first attack line.
- Optional AU/FACS, if used, appears after natural-language facial actions and stays compact, such as AU1/AU15/AU17 from B to C.
- Husband's listener reaction is included but restrained; he should not steal the scene.
- Ending leaves 1-2s for silence, breath, tear fall, or room tone after the line.

Failure checks:

- emotion jumps directly from anger to crying with no protective layer
- dialogue is pasted under a generic sadness/anger label
- no trigger word, no pause, no breath, no post-line state
- first tear appears too early
- AU codes are dumped without visible natural-language facial action
- listener overacts or interrupts the main performance
- ending cuts immediately after the last word

## Case 25: 30s Duration Selection and Long Prompt Budget

Input:

```text
30-second realistic emotional dialogue scene: early morning in a rented room, a woman who is about to move out puts the key on the table, and the man says with feigned calm, "Go. I'm fine." The woman stops without turning around and asks: "Are you really fine, or do you just not want to ask me to stay?" The man first gives a small laugh, trying to brush the topic aside, then finally admits: "I'm afraid that the moment I open my mouth, I'll look too pathetic." In the end the two do not hug; they just stay silent across an old dining table. The performance should be natural, with pauses and breaths, no heavy crying.
```

Expected:

- Diagnosis explains why this scene can use 24-30s: dialogue delivery, hesitation, listener reaction, table/keys contact, and emotional aftertaste need time.
- The skill does not claim every prompt should default to 30s; it chooses a specific duration, such as 26s or 28s, only if the scene needs it.
- Final prompt normally stays within the 2200-3400-character target for a 25-30s scene and always below the 4000-character ceiling. Any text beyond 3000 characters must directly support timing, performance, contact realism, spatial continuity, sound, or ending breath.
- Dialogue is timed with pauses and breath. The key lines are explicit and have enough room before and after delivery.
- The man's smile is protective rather than cheerful; grief or collapse does not arrive before the line that triggers it.
- The keys, table, body distance, and eyelines stay consistent.
- Ending leaves at least 2s for silence, room tone, breath, or stillness after the final line.

Failure checks:

- keeps the old 15s maximum and splits even though one 24-30s prompt can carry the scene
- stretches a simple beat to 30s without dramatic reason
- exceeds 4000 Chinese characters without recommending a split, or exceeds 3000 with decorative detail that does not improve generation
- packs all lines together with no pauses or listener reactions
- uses generic sadness labels instead of line-triggered performance changes
- cuts immediately after the final line

## Case 26: 30s Psychological Stage Timeline

Input:

```text
29-second extreme close-up emotional long take: a woman facing her lover who is about to leave goes from pressing him, to resignation, to wanting to remember his face one last time, and finally lets go with tears in her eyes. She says only two lines: "Do you really have to go?" and "Go, then." No heavy crying early on, the first tear must fall very late, and the ending is a smile through tears.
```

Expected:

- Strategy names a psychological stage timeline rather than only listing time codes.
- Final prompt uses 4-5 stage titles such as `Pressing`, `Resignation`, `Remember`, `Regret`, `Letting go`.
- Each stage includes visible action/expression evidence and a distinct psychological task.
- The two smiles are differentiated: early smile as self-mockery/acceptance, final smile as tenderness/release.
- Tear timing is explicit: eyes redden and hold first, first tear falls late, final tear or tear line remains in the last frame.
- Camera movement is tied to emotional access: stable close-up first, very slow push only as vulnerability opens, ECU near the peak.
- Dialogue is short, timed, and leaves silence after each line; the final line does not land at the last instant.
- Final prompt stays under 3000 Chinese characters.

Failure checks:

- treats the whole prompt as generic sadness or crying
- uses stage names but each stage repeats the same facial expression
- first tear falls too early
- final smile has the same meaning as the earlier bitter smile
- camera movement is decorative or over-stacked
- prints long `emotional analysis` paragraphs inside the copy-ready final prompt

## Case 27: Output Mode Selection

Input A:

```text
Please write a cinematic video prompt from this story: a convenience store on a rainy night; an unemployed man at the checkout counter discovers that his ex-girlfriend is also there buying an umbrella, and the two pretend not to know each other.
```

Expected A:

- Use full workshop mode by default.
- Output `Story diagnosis`, `Cinematic adaptation strategy`, optional reference prompts when useful, and `Final video prompt`.
- Do not output only the final prompt just because the user asked for "one prompt".

Input B:

```text
Don't write the final prompt yet. In an ancient imperial palace, the empress discovers that the emperor has been using her family all along; I want to see the story diagnosis and the cinematic adaptation direction first.
```

Expected B:

- Use direction confirmation mode.
- Output only `Story diagnosis`, `Cinematic adaptation strategy`, and `Directions to confirm`.
- Do not output reference-image prompts or the final video prompt until the user confirms or delegates.

Input C:

```text
Give the final video prompt directly, no analysis: a hospital corridor late at night, a man hears the doctor announce that the attempt to resuscitate his mother has failed.
```

Expected C:

- Use concise mode.
- Output only the final video prompt.
- Still include the doctor's actual notice line and enough ending breath.

Failure checks:

- default ordinary request outputs only final prompt
- direction-confirmation request still outputs final prompt
- concise request prints diagnosis despite explicit "no analysis"
- mode choice is based on vague compactness rather than explicit user intent or real ambiguity

## Case 28: Nested Dialogue Timeline and Reaction Sound Bridge

Input:

```text
30-second married-couple conflict scene. On the porch of an old house, the husband first complains that he has been stuck in the same place for eighteen years; the wife immediately pushes back, saying she has also sacrificed eighteen years. She gradually moves from anger and self-justification to admitting that she too once imagined a different life. Midway, cut to the husband's reaction as he listens to her, with the wife's lines continuing as off-screen voice, and finally cut back to her as she finishes her most vulnerable line. The performance must feel real; she cannot cry from the start.
```

Expected:

- Build the four or fewer shot-level blocks first, then use nested performance beats only inside the wife's long, complex shot.
- Keep a separate speaker track and listener track. The husband changes only after hearing a specific phrase about sacrifice, dreams, or another life.
- Let the wife's sentence continue across the cut as offscreen dialogue or a motivated sound bridge while the husband reacts.
- Preserve screen direction, eyeline, focal logic, voice direction, and acoustic space when cutting back and forth.
- Place cuts on semantic turns: the husband's final word, the wife's protective anger cracking, a vulnerable phrase continuing offscreen, and the final confession.
- Progress framing from OTS/MCU or CU toward BCU/ECU only when the wife's defense opens.
- Keep tears delayed until after anger and self-justification have cracked.
- Keep dialogue playable within 30s; shorten lines before accelerating speech unnaturally.

Failure checks:

- mechanically subdivides every shot into tiny time blocks
- the listener is only described as `silent` or reacts before the trigger phrase
- offscreen dialogue loses speaker identity, direction, or room continuity
- cuts occur at equal intervals with no semantic purpose
- starts in ECU and has no later framing escalation
- packs too much dialogue into the final second or cuts without reaction time

## Case 29: Minimum Sound and Lighting Baseline

Input:

```text
15-second late-night apartment suspense scene: a girl who lives alone hears a faint click of the door lock and finds an unfamiliar key on the entryway floor. She does not scream; she only holds her breath and slowly looks toward the dark hallway. Realistic and restrained, no music.
```

Expected:

- Establish one motivated light baseline, such as a warm interior practical light against cooler corridor spill, with a stable source direction.
- Use 2-4 concrete sound anchors, such as lock click, refrigerator hum, bare-foot friction, breath, or a distant elevator.
- Let the key discovery change the sound field through narrowing, muffling, or isolated silence rather than adding generic suspense music.
- Mention shot-local light changes only when the door gap, hallway spill, phone screen, or character movement changes what is illuminated.
- Keep skin tone, eye catchlight, shadow direction, room tone, and acoustic space continuous across cuts.
- Use a compact `Overall sound and light` block or place the same information concisely in the opening summary when the prompt is short.
- Leave an audible and visual ending residue: held breath, corridor hum, key reflection, or distant elevator sound.

Failure checks:

- only says `cinematic lighting` or `immersive sound effects`
- gives no believable light source or sound bed
- adds dramatic BGM despite the request
- changes light direction between shots without an on-screen cause
- repeats a full lighting breakdown in every shot
- ends at the discovery with no sound tail or visual afterimage

## Case 30: Short-Drama Hook Diagnostic Boundary

Input A:

```text
Make it a 25-second short suspense drama with a strong hook: late at night, a courier delivers a package marked with tomorrow's date. The girl who lives alone wants to open it before her boyfriend gets home, but then building management calls from outside to say no courier came upstairs tonight. Inside the box is her boyfriend's phone, ringing, and the screen shows that the caller is the girl herself. The ending should make people want to keep watching.
```

Expected A:

- Activate the short-drama hook and narrative-drive diagnostic because the user explicitly asks for a strong-hook suspense short.
- Diagnose the existing anomaly, immediate goal, active obstacle, information reversal, and unresolved question without insisting on a separate deadly rule.
- Preserve the supplied plot. Do not add a hidden murderer, supernatural identity, countdown, or new culprit unless the user delegates further invention.
- Translate the functions into visible beats: future date, her attempt to open the parcel, the property call, the phone inside, and her own incoming caller identity.
- Use no more beats than can play naturally in 25s, including dialogue/reaction and 1-2s ending residue.
- End with a completed reveal and held reaction while the larger question remains open; do not cut off the phone line or box-opening action halfway.

Input B:

```text
8-second fixed-camera emotional close-up: a mother sees her son's university admission letter; at first she cannot believe it, and after confirming the name she smiles as a single tear falls. No dialogue throughout, quiet and restrained.
```

Expected B:

- Do not activate the short-drama hook formula merely because the video is short.
- Do not invent an anomaly, deadline, fatal rule, obstacle, identity reversal, or cliffhanger.
- Preserve the performance-led emotional arc and use the micro-expression close-up system.

Failure checks:

- requires all six narrative functions for Input A
- silently rewrites the supplied culprit, identity, relationship, or ending
- mistakes an unresolved answer for an abrupt unfinished action
- adds a twist or danger to Input B
- turns every emotional change into a plot reversal

## Case 31: Dense Dialogue, Interruption, and Playability Boundary

Input A:

```text
Make it a 30-second two-person emotional dialogue. The older sister discovers that her younger brother is preparing to take on a responsibility for their father that will ruin his future; she talks faster and faster, afraid that if she stops she will not be able to stop him. The brother stays low-voiced and polite throughout, comforting her with "it's okay", yet repeatedly gets stuck on the word "I". The two may gently cut each other off and briefly overlap, and the following key lines must be kept in full. No flashy camera work; the focus is native dialogue, lip sync, voice and listener reactions.
```

Expected A:

- Establish a scene-level performance contract: her speed comes from fear of losing the chance to stop him; his politeness protects him from collapse and tries to reduce her guilt.
- Treat dense dialogue as a playability question rather than applying an automatic word-count cut. Preserve all required lines if local acceleration, motivated overlap, and simplified visual staging allow complete delivery.
- Lock distinct voice identities and temporary vocal states across shots.
- For each interruption, identify the semantic entry trigger, relative volume, brief overlap, who yields, and the interrupted mouth/breath state.
- Protect intentional failed `I—` starts from smoothing, completion, comic repetition, or audio-glitch behavior.
- Use a dialogue-first priority ladder; simplify shot count, camera movement, secondary gestures, and environment activity before proposing dialogue cuts.
- Carry one gesture continuously across cuts, such as his hand rising, hovering, then losing strength and falling. Preserve the relationship's no-touch distance if established.

Input B:

```text
15-second quiet farewell scene: the two people must slowly finish twelve long lines, with a one-second pause between lines; every line needs a swallow, tears, the other person's reaction and one camera move, and the last line runs to the last frame. Nothing may be cut.
```

Expected B:

- Do not claim the scene is playable merely because all dialogue is marked mandatory.
- Diagnose the concrete conflict among slow delivery, twelve one-second pauses, repeated physiological actions, listener reactions, camera moves, and no ending residue.
- First propose simplifying camera and repeated gestures, but recognize that those reductions cannot recover enough time for twelve long lines and pauses.
- Explain the remaining conflict and recommend splitting into multiple clips or ask whether the user prefers preserving every line or preserving the 15s limit. Do not silently edit key dialogue and do not accelerate it unnaturally.

Input C:

```text
At the end she wants to say "Actually, I've always—", but stops herself because she finally sees that the other person already understands. Do not complete the second half of the line; finish the ending with her unclosed lips, a slow exhale, and the other person raising their eyes in response.
```

Expected C:

- Allow the unfinished line because refusing or no longer needing to finish is the completed dramatic action.
- State why speech stops, prevent automatic completion, and hold the mouth, breath, gaze, listener response, or silence long enough to read.
- Do not place the dash at the last frame with no consequence; reserve visible and audible aftermath.

Failure checks:

- compresses Input A only because its word count exceeds a generic speech-rate estimate
- turns overlap into clean alternating turns or mutes the first speaker abruptly
- repeats a cross-cut line in full after the edit
- converts failed speech into comic stuttering or mechanical loops
- accepts Input B without identifying the genuine timing contradiction
- silently deletes mandatory lines from Input B
- treats Input C as permission for an accidental mid-line cutoff

## Case 32: Knowledge State, Non-Human Performance, and Behavioral Payoff

Input A:

```text
30-second realistic train-station story: an aging search-and-rescue dog, many years later, suddenly hears the voice of the handler who has already left. It first doubts, then confirms, then slowly approaches; finally the voice disappears, and it no longer keeps staring at the station exit but lies down in its old waiting spot. Do not film the dog crying like a human face.
```

Expected A:

- Use species-appropriate performance: ear orientation, half-turn freeze, sniffing, breath, tentative paw placement, tail/spine tension, weight shift, slow aged approach, contact release, and final resting posture.
- Preserve age and locomotion limits; recognition may restore intent but not youthful speed or agility.
- Do not use human tears, smiles, theatrical nodding, or anthropomorphic sobbing.
- Adapt the relationship axis to unequal height using hand, coat, waist, ear, or back foreground anchors rather than forcing a human shoulder-level reverse shot.
- Build a behavioral payoff: habitual watching of the entrance is established, then the final choice not to look back and to lie down proves waiting has ended.

Input B:

```text
25-second sci-fi emotional scene: on the night before her wedding, a young woman opens the door to an elderly stranger. The old man says ahead of time the everyday habit she is about to perform the next second, while the action happens off-screen; from his voice and demeanor she gradually guesses that he may come from her own future. Do not explain how the time travel works.
```

Expected B:

- Track knowledge state: she begins with no recognition, observes a specific prediction and verification, forms a tentative hypothesis, then receives only enough confirmation to ask a personal future question.
- Keep audience knowledge and character knowledge distinct; do not let her name the relationship before credible evidence arrives, and do not let the visitor explain the mechanism.
- Use prediction -> waiting gap -> offscreen verification -> reaction -> revised hypothesis.
- Keep the camera on her face if the realization matters more than showing the habitual hand action; use precise contact sound, brief offscreen eyeline shift, breath stop, and renewed gaze as proof.
- Select questions from character values: once identity is sufficiently clear, move from `who are you` to what the shared life meant rather than continuing mechanical exposition.

Input C:

```text
20-second farewell in a small diner late at night: the woman keeps wanting to straighten the crooked collar of the man across from her, but holds back because of the boundaries of their relationship and does not touch him. At the end the man straightens his collar himself, then pushes the key on the table back to her. In the background a server is still clearing tables and distant customers talk in low voices.
```

Expected C:

- Establish the withheld collar gesture early and preserve it as a relational boundary rather than adding a random symbolic action only at the ending.
- Pay it off through transfer/recontextualization: he completes the grooming action himself, then the key movement becomes the decisive relationship action.
- Keep background workers and guests on plausible independent routines; they do not stop, stare, gather, or mirror the couple's emotion.
- Use a subjective sound arc: ordinary restaurant room tone -> distant ambience recedes after the key decision -> cloth/key/table contact becomes close -> room tone returns after the private beat.

Input D:

```text
A train passes between the two people and the camera; while it blocks the view one of them disappears. After the train leaves, the other still keeps the same position and line of sight, with only the old ticket just handed over left in their hand.
```

Expected D:

- Allow the train as a motivated foreground occlusion because it belongs to the space and carries a visible path, parallax, wind pressure, reflection, and synchronized sound.
- Preserve camera side, interaction axis, screen direction, lighting, remaining character pose, gaze, hand/prop state, and the first visible post-occlusion composition.
- Do not use the cover to hide unrelated character drift, costume change, flipped geography, or an unexplained camera teleport.

Failure checks:

- gives Input A human tears, smiling, nodding, or sudden youthful movement
- lets a character know identity, death, timeline, or relationship before receiving evidence
- cuts to every object action even when the observer reaction carries the story
- asks generic exposition questions that ignore character priorities
- introduces a new symbolic ending action with no earlier setup
- freezes or redirects all background people toward the protagonist
- turns subjective sound narrowing into arbitrary total silence
- uses foreground occlusion as an unmotivated blackout or continuity reset

## Case 33: Generated Fight Result Surgical Repair

Input:

```text
The previous 12-second warehouse fight has been generated: the two adult women's faces, costumes, warehouse positions, cold white overhead lights and handheld camera work are all good. The only problem is the reversal throw: A did not first lower her center of gravity and establish a grip, B just suddenly flipped to the ground, and the right wrist guard also jumped from B's hand to the floor. Fix only the move and the wrist-guard continuity; change nothing else.
```

Expected:

- Activate generated-result surgical repair rather than rewriting the whole fight.
- Diagnose at most three dominant failures: missing grip/level-change/momentum causality, teleport-like throw, and wrist-guard state discontinuity.
- Lock the successful identities, wardrobe, warehouse layout, fighter positions, cold overhead light, and handheld shooting condition.
- Repair only the attack-defense-counter chain: establish grip, level change, weight transfer, pivot, fall path, landing/recovery, and the wrist guard's holder/contact/final location.
- Keep the original duration and action count playable; do not add a new fighter, weapon, light design, slow-motion showcase, or unrelated camera move.

Failure checks:

- rewrites faces, costumes, warehouse, light, or the accepted camera style
- adds generic negative constraints without repairing throw mechanics
- fixes the throw but leaves the wrist guard teleporting or duplicated
- expands one failed beat into an overloaded new fight sequence
- claims the repaired prompt proves the next generated video will succeed

## Case 34: Single-Variable Camera Revision

Input:

```text
In the previous 15-second kitchen dialogue between husband and wife, I am happy with the lines, lip sync, performance, blocking, warm pendant light and closing silence. Only change the frontal locked-off camera to an observational camera from behind the kitchen doorframe with slight occlusion, still keeping the original 180-degree axis and the characters' left-right relationship; everything else stays the same.
```

Expected:

- Treat the request as a single-variable camera revision.
- Preserve dialogue wording/order, lip-sync, performance timing, blocking, character screen-left/right, practical light source, sound bed, and ending silence.
- Change only the physically dependent camera clauses: witness position behind the doorway, height/distance, plausible foreground doorframe occlusion, framing, and focus behavior.
- Keep the doorway observation position physically compatible with the existing axis; do not cross the axis or move either character merely to beautify the composition.
- Do not introduce surveillance, horror, voyeurism, new props, new lighting, or a different story interpretation unless the user asks for it.

Failure checks:

- rewrites dialogue, acting, light, sound, or ending
- changes character blocking or flips screen direction without necessity
- treats the doorframe as a decorative overlay with no physical camera position
- adds unrelated handheld movement, lens flare, fog, or dramatic color grading
- outputs several camera alternatives instead of one resolved revision

## Case 35: Production-Path Routing Without Extra Friction

Input A:

```text
First give me character and scene reference image prompts, and write the video prompt after I am happy with the images: the night before a Song-dynasty wedding, the bride, alone in the bridal chamber, takes off her phoenix crown.
```

Expected A:

- Enter the reference-first path without asking whether the user wants references.
- Output only the current-stage asset plan and needed image prompts; do not pretend the images already exist or append a reference-driven video prompt.

Input B:

```text
Give an 8-second video prompt directly, no reference images: a kitchen in the early morning, a man secretly throws away a burnt fried egg, and his wife sees it from the doorway but holds back a laugh.
```

Expected B:

- Enter the direct-video path without a route question.
- Output a self-contained prompt and no reference-image section.

Input C:

```text
A continuous short-film series about a Song-dynasty family ensemble: three main characters will appear repeatedly in the main hall, the bridal chamber and the ancestral hall, and their costumes, status and spatial orientation must stay stable.
```

Expected C:

- Because the user has not chosen a route and the task has high drift/reuse cost, ask one concise production-route question.
- If direction selection is also needed, combine the choices into one checkpoint rather than asking twice.

Failure checks:

- asks Inputs A or B to choose a route already specified
- dumps complete reference prompts and a complete video prompt for Input A
- silently defaults Input C to a large mixed package
- adds a production-route checkpoint to a simple low-drift direct request

## Case 36: Minimal Reference Asset Set for Multiple Characters and Scenes

Input:

```text
A three-segment continuous Song-dynasty family story with a husband and wife as the two leads, two servants who appear only once, a main hall that appears repeatedly and a back garden that appears only once; make the reference images first in segment one.
```

Expected:

- Create individual identity references for the two recurring principals.
- Create a clean scene plate for the recurring main hall when its topology matters.
- Do not automatically create individual identity references for both one-off servants or a clean plate for the one-off backyard.
- Explain briefly which assets are not generated and why.
- Keep the current generation stage to roughly 1-3 active references; if more are truly needed, batch them through an asset plan.

Failure checks:

- creates a reference for every named person and location
- generates identity, relationship, scene, prop, first-frame, and tail-frame references by default
- includes all later locations before the current clip needs them
- omits recurring principal identity or recurring location control

## Case 37: Reference Authority and Static Deduplication

Input:

```text
I have already generated three images: reference image 1 is the heroine's look test, reference image 2 is an empty Song-dynasty hall, and reference image 3 is a first frame of the hero and heroine sitting across a table from each other. Please write a 15-second dialogue video prompt based on these three images. I'm happy with the appearance, costumes, scene and lighting in the images; do not redesign them.
```

Expected:

- State a compact mapping: image 1 controls the woman's identity/costume, image 2 controls layout/light, image 3 controls start-frame relationship geometry.
- Treat the supplied visual facts as locked and do not repeat full face, costume, architecture, palette, or lighting descriptions.
- Focus the video prompt on dialogue order, lip-sync, gaze, breath, body/contact changes, camera behavior, sound, and ending state.
- Keep only minimal role/position/prop bindings needed to interpret motion.

Failure checks:

- rewrites the woman's full appearance or proposes a new costume
- introduces a competing room layout, palette, light direction, or first-frame pose
- omits reference mapping so the three images compete for authority
- removes so much binding information that character identity, position, or prop ownership becomes ambiguous

## Case 38: Explicit Timed Delta From a Reference

Input:

```text
In the reference image the bride wears a complete red wedding gown; 12 seconds into the video she turns, the red outer robe slides off her shoulders, revealing the white mourning clothes she had already put on underneath; the outer robe ends up hanging on her left elbow. Keep everything else about her appearance and the room as in the reference image.
```

Expected:

- Preserve the reference as the starting state.
- Describe the wardrobe change with time, physical cause, contact path, revealed layer, and final state.
- Do not describe the character as wearing only white at the start.
- Avoid repeating unchanged face, hair, room, and lighting descriptions.

Failure checks:

- contradicts the image at the opening
- makes the outer robe disappear, teleport, or return to its initial position
- describes the change without cause or endpoint
- redesigns unrelated static details

## Case 39: Separate Reference-Driven and No-Reference Versions

Input:

```text
I want two versions of this shot: one bound to my existing character and scene reference images, and another that can be generated directly without any images.
```

Expected:

- Output two clearly labeled prompts: `Reference-driven version` and `No-reference direct version`.
- The reference-driven version uses mappings and dynamic differences without full static repetition.
- The no-reference version restores the necessary identity, setting, costume, prop, light, and first-frame anchors.
- Both preserve the same story action, timing, dialogue, and ending, while differing in static-information density.

Failure checks:

- gives one ambiguous prompt claimed to work equally well in both modes
- leaves nonexistent reference-image language in the direct version
- fully repeats all static descriptions in the reference-driven version
- changes the story or performance between versions without being asked

## Case 40: Reference-First Continuation Uses Actual State

Input:

```text
The previous segment was generated successfully with reference images. At the end the heroine's left hairpin has fallen out, her sleeves are soaked by the rain, and the letter has fallen on the second stone step. Continue with the next segment; do not redo the character, the courtyard or the lighting.
```

Expected:

- Reuse the existing identity and scene references rather than regenerating them.
- Bind the next prompt to the actual previous ending state: missing left hairpin, wet sleeve, letter on the second step.
- Create an updated-state reference only if the changed state will recur or cannot be held reliably through the continuation prompt.
- Focus the new prompt on the next temporal action and emotional turn rather than repeating the full visual bible.

Failure checks:

- restores the hairpin, dries the sleeve, or moves the letter without visible action
- outputs a new generic character or courtyard reference
- repeats the complete identity and scene description
- treats the continuation as an unrelated direct-video prompt

## Case 41: Inspiration Reference vs Production Reference

Input:

```text
I'm giving you two images: image A is a still from a classic film, and the only thing I like about it is the composition where the doorframe hems in the figure; image B is a Song-dynasty heroine look test I have already generated and am happy with. Please plan the bridal-chamber first-frame reference image; the heroine's identity must stay stable, but do not copy the film still.
```

Expected:

- Classify image A as `inspiration reference` controlling only the declared composition method.
- Classify image B as `production asset reference` controlling the woman's identity and approved costume state.
- Build a new, story-specific room, blocking, props, and action rather than copying the source still's cast arrangement, complete topology, palette, or story outcome.
- State the authority of each image so composition inspiration does not overwrite identity and identity reference does not freeze the new first-frame composition.

Failure checks:

- treats the movie still as authority over identity, exact layout, action, and palette
- reproduces a recognizable complete shot or merely swaps the actor
- lets the generated identity image dictate an unrelated pose or camera position
- fails to state which image controls which field

## Case 42: Type-Specific Reference Prompt Density

Input:

```text
Make four kinds of reference images for a Song-dynasty married-couple argument scene: the wife's look test, an empty main hall, a relationship image of the couple across a table, and a key prop image of the divorce letter on the table. The images will later be used to generate video, so avoid overloading the prompts.
```

Expected:

- Wife identity prompt uses 4-6 stable identity/costume anchors and one emotional baseline, with no husband or relationship action.
- Clean hall prompt prioritizes 4-6 topology/light anchors, entrances/exits/action path, one primary source, and only 2-3 causal environment traces; it contains no people.
- Relationship prompt uses one relationship axis, left/right positions, distance/eyelines, one contact or no-contact state, and one visual center.
- Prop prompt locks the letter's material, scale, orientation, readable feature when essential, wear/state, and placement without an elaborate unrelated scene.
- Each prompt requests one standalone frame and one composition; no grid, collage, model sheet, or multiple views unless explicitly requested.

Failure checks:

- applies the same long template to all four asset types
- places the husband or interaction language inside the wife's identity reference
- clutters the clean hall with irrelevant objects or several light effects
- gives the relationship frame several actions or time beats
- produces a four-panel sheet instead of four independently usable prompts
- forces 21:9, English, or a particular image model without user request

## Case 43: Surgical Repair of a Generated Reference Image

Input:

```text
I'm happy with this Song-dynasty heroine reference image's face, hair bun, costume colors, figure proportions, background and side light from the window. Only the right cuff is wrong: it came out as a modern loose bell sleeve. Please fix it only into a narrow-cuffed cross-collar robe sleeve; do not redo any other part.
```

Expected:

- Inspect the actual image when it is available and identify the sleeve construction as the dominant failed field.
- Output `Keep unchanged`, `Change only`, and `No side changes`.
- Preserve face, age, hair, approved garment body/color, body proportions, composition, camera, background, and source-light direction.
- Change the right cuff and only its physical dependents such as adjacent folds and wrist occlusion.
- Do not claim the repair succeeded before the revised image is generated and inspected.

Failure checks:

- rewrites the whole character prompt or redesigns the costume
- changes face, hair, color, pose, camera, background, or light
- changes the cuff without repairing directly connected folds/contact
- adds a long generic negative list unrelated to collateral drift
- reports success from the repair instruction alone

## Case 44: Actual Reference Supremacy, Cleanliness, and Physical Feasibility

Input:

```text
My original first-frame prompt asked for a wooden paperweight strip on the table, but in the actually generated image of the couple across the table only the divorce letter is clearly visible and there is no strip; there is also a generation-platform watermark in the lower-right corner. The wife sits on a chair with armrests, her right hand on her knee. Please write a 15-second image-to-video prompt based on the actual image: she pushes the divorce letter to her husband, then gets up and leaves.
```

Expected:

- Treat the actual pixels as authoritative and do not inherit the absent/unclear paperweight from the earlier image prompt.
- Flag the visible watermark before production and recommend a clean/cropped/repaired reference; do not claim that `no watermark` will reliably erase it.
- Reconstruct the start geometry: right hand travels from lap to paper, body has a reachable path, and the chair arms affect how she stands.
- Write the document contact as approach -> touch/support -> frictional push -> release -> visible endpoint; do not make the paper jump or slide together with an absent weight.
- Let her use the visible armrest or another physically supported motion to stand; preserve the clear exit path and husband/document continuity.
- Replace arbitrary centimeter precision with a visible event unless exact measurement is story-critical.

Failure checks:

- imports the paperweight from the old prompt despite its absence in the selected image
- relies only on a negative prompt to remove the embedded watermark
- makes the hand teleport from lap to document or the document move before contact
- asks her to press through the chair, table, or armrest, or gives no viable standing/exit path
- claims the reference or final video is clean/successful without a revised generation result

## Case 45: First Frame Must Not Freeze Cinematic Coverage

Input:

```text
Three actual reference images lock the Song-dynasty wife's identity, the main hall layout, and the first-frame relationship of the couple sitting across the table from each other. 15 seconds, no dialogue: the wife pushes the divorce letter across, the husband reaches out but stops, she glances at him, gets up and leaves, ending on the empty chair and the husband. The first frame is a frontal two-person medium shot, but do not keep this shot size for the whole segment; switch shot sizes according to the story and choose suitable camera movement.
```

Expected:

- Bind the relationship image as the exact opening state only; preserve identities, room topology, axis, positions, document state, and light across later views.
- Choose a multi-shot relationship-drama structure rather than defaulting to a static one-take.
- Use motivated coverage, for example: opening `MS/MLS` relationship geography -> document/hand `CU` with match-on-action -> husband's `CU/BCU` stopped reach and reaction -> wider or moving follow shot for her stand/exit -> held aftermath on empty chair/document/husband.
- Make every cut or move reveal action, reaction, power change, or aftermath; do not add decorative angles.
- Use meaningful shot-size contrast and at least a 30-degree horizontal change when cutting around the same interaction; preserve the 180-degree axis and eyelines.
- Widen or pull back before the full-body stand/exit if needed, and give the ending 1-2 seconds to read.

Failure checks:

- treats the first-frame composition as the required framing for all 15 seconds
- labels the result `one-take` without a story reason or user request
- changes shots but repeats nearly identical medium framing and angle
- adds cuts or camera moves with no change in information, emotion, action readability, or aftermath
- loses identity, room geometry, screen direction, document position, or light continuity after leaving the opening view
- keeps a close framing during the stand/exit so the body action becomes cropped or physically unclear

## Case 46: Camera-Movement Library Is Selected by Story Function

Input:

```text
12-second realistic suspense: a woman walks down a hotel corridor toward her room door; behind her the elevator suddenly opens, and in the reflection on the door number plate she sees a figure following her out. I won't specify the camera movement; design it from the story, and keep the prompt mainly in Chinese.
```

Expected:

- Read the camera-movement library because movement and spatial reveal carry the suspense.
- Select only the movements that serve the route and reveal, such as a controlled `Follow Shot / OTS` for approach plus one motivated `Pan`, `Slider`, or focus/cut response for the reflected figure.
- For every selected move, state the readable start subject, physical path/direction, speed, newly revealed information, and settled endpoint.
- Keep the corridor, door, elevator, reflection, travel direction, and screen axis coherent; do not let the camera pass through walls or the character.
- Keep action and story instructions in Chinese; retain English only for useful cinematography terms and abbreviations.
- Use no more than the few movements the 12-second action can carry.

Failure checks:

- lists several of the 46 moves as alternatives instead of making a director choice
- stacks `Orbit`, `Whip Pan`, `Crash Zoom`, `Drone`, and `Handheld` for style alone
- names a movement without start, path/direction, speed, story result, or endpoint
- switches to an English prompt paragraph copied from the library
- sacrifices corridor geography, reflection logic, or reaction time for camera spectacle

## Case 47: Observable Emotion Library Without Stock Acting

Input:

```text
10-second close shot: a woman tells her mother "I'm doing fine", first forcing a nervous fake smile; after her mother puts the train ticket she had sent back on the table, her smile disappears and she lowers her eyes guiltily, but does not cry. Natural, restrained performance; write the prompt in Chinese.
```

Expected:

- Use `nervous fake smile` as the initial protection and `guilt` as the triggered destination rather than mixing several unrelated emotions.
- Keep only 2-4 decisive cues in each playable phase: for example mouth smiling while eyes remain flat, a hard swallow or brief gaze drop; after the ticket lands, the smile releases, gaze lowers, and speech fails or breath changes.
- Tie the transition to the visible/sounding ticket contact and preserve the exact dialogue, listener timing, and no-cry boundary.
- Write onset, trigger, change, and held aftermath; do not display the final guilty face from the first frame.
- Keep the final performance direction in Chinese. Do not print English emotion labels, intensity tags, library analysis, or an AU/FACS dump.

Failure checks:

- copies the complete stock modules or uses every listed facial/body cue
- adds shock, terror, sobbing, flirtation, or another unrelated emotion
- makes her cry despite the explicit boundary
- describes only abstract `nervous, guilty` without visible eyes, mouth, breath, gaze, hand, or posture evidence
- outputs the emotion library's English labels or long English acting sentences

## Case 48: Aspect-Ratio Routing Without Repeated Questions

Inputs:

```text
A: Give me a 9:16 vertical prompt directly: a girl in an elevator discovers in the mirror that someone is standing behind her.
B: Continue the previous segment, reusing the already-confirmed vertical character and scene reference images.
C: An 8-second single-person kitchen close shot, a man secretly throws away a burnt fried egg; no aspect-ratio requirement.
D: First make the formal scene and first-frame reference images for the Song-dynasty couple's across-the-table divorce scene; landscape or portrait is not specified.
```

Expected:

- A enters the vertical system directly without asking about ratio.
- B inherits the confirmed vertical ratio without asking again.
- C defaults to 16:9 horizontal and proceeds because the low-risk single-subject action does not justify a checkpoint.
- D asks once because formal scene/relationship/first-frame assets and two-person table blocking are costly to redo; combine this with any existing direction or reference-route confirmation.
- If the user delegates D, use 16:9 by default unless an actual vertical production asset or explicit vertical delivery context exists.

Failure checks:

- asks A or B to choose a ratio already given or inherited
- interrupts C with an unnecessary aspect-ratio question
- generates D's composition-controlling assets before resolving a materially consequential ratio
- creates a separate aspect-ratio question immediately after another confirmation round
- assumes a platform ratio without the user specifying its intended format

## Case 49: Vertical Two-Person Reference-First Relationship Scene

Input:

```text
9:16 vertical, a Song-dynasty husband and wife sitting across a table from each other. First make the main hall scene and the two-person first-frame reference images, and after I'm happy with the images generate a 15-second video: the wife pushes the divorce letter across, the husband reaches out and stops, she gets up and leaves. Do not just crop a landscape frame narrower.
```

Expected:

- Read the vertical adaptation and reference-first workflow; state 9:16 in composition-controlling scene/first-frame prompts.
- Recompose the hall around a central depth/action corridor, readable table/document, viable standing/exit path, and vertical source-light geometry.
- Avoid two equally small figures pushed to opposite edges; use staggered depth, height, `OTS`, diagonal relationship, or another narrow-frame solution while preserving the axis and document ownership.
- Keep face, hands, document, chair support, head/foot clearance, and exit visible where their actions occur.
- Stage 1 stops after the reference plan/prompts. After actual vertical images are supplied, the video may use motivated shot-size changes rather than freezing the first-frame composition.

Failure checks:

- writes a horizontal side-by-side composition and merely appends `9:16`
- crops out a spouse, the document, chair arms, or the exit route
- creates composition-controlling references in conflicting ratios
- gives a tight portrait first frame that cannot support pushing, standing, and leaving
- outputs the final video prompt before actual images are generated without an explicit complete-package request

## Case 50: Vertical Full-Body Action and Camera Travel

Input:

```text
12-second 9:16 vertical: a young woman runs up from the bottom of the stairs, stops on the landing, looks up and sees light coming through a gap in the door upstairs, then turns and keeps going up. Tense but with clear action; choose the camera movement according to the story.
```

Expected:

- Use stairs, height, destination, and upper/lower frame relationships as meaningful vertical geography.
- Choose a physically plausible combination such as low `Follow Shot`, controlled `Tilt Up`, `Pedestal/Crane`, or a motivated cut; do not use vertical movement merely because the canvas is tall.
- Maintain head/foot room and the travel direction; widen or reframe before the stop/turn so the full-body mechanics remain visible.
- Keep horizontal travel short, the door-light destination readable, and the final upward direction continuous.
- Preserve action time and ending breath rather than stacking camera techniques.

Failure checks:

- keeps a tight face shot while demanding running, stopping, turning, and climbing
- loses feet, stair edges, landing, or door destination
- adds `Orbit`, long lateral tracking, drone movement, and whip pans without story function
- reverses travel direction or relocates the light/door between shots
- treats 9:16 as a suffix instead of a composition and movement constraint

## Case 51: Sustained Body-Mounted Camera and Repeated Recovery

Input:

```text
20 seconds, 16:9, camera fixed to the body throughout, one-take. A courier carries a package down a corridor, twice reaching out to knock on the door and pulling back; only the second time, after hearing his own name from inside the door, does he actually knock. His head and hands may move naturally, and the key action must always be visible. Give the video prompt directly, no music.
```

Expected:

- Accept the sustained Snorricam request without imposing a short psychological insert or a cut.
- Bind the camera to the torso, allow independent head/arm motion, and frame the hand path and supported parcel.
- Preserve visible withdrawal and a changed trigger for renewed action; clarify which hand supports the parcel.
- Background motion follows torso movement and settles with it; no independent orbit, push or zoom.

Failure checks:

- freezes the head and hands along with the torso, hides withdrawal, or loops equal gestures without motive
- drops/transfers the parcel invisibly or adds an unrelated threat/music

## Case 52: Matched Memory Cut With Intentional State Change

Input:

```text
12 seconds, two shots. A girl rolls an old tennis ball to an old dog's feet, and the ball stops. Keeping the ball position and the low camera, hard-cut to a sunny tennis court in her memory, where the same dog, young and healthy, steps forward and picks up the ball in its mouth. No dissolve, no explanatory narration; give the prompt directly.
```

Expected:

- State the matched ball position/camera and deliberate location, light and age changes across the hard cut.
- Treat the change as the supplied memory, not present-time healing or resurrection.
- Preserve identity without freezing temporary age/state or generating extra reference assets by default.

Failure checks:

- morphs between states, treats the cut as an accidental continuity reset, or adds a supernatural rule

## Case 53: Environment-Driven Adjustment and Tone Boundary

Inputs:

```text
A. 12-second realism: a waiter carries a glass of water through a moving train; the train takes a curve, he steadies himself on a seat to regain his balance, keeps the glass safe, and walks on. Serious and restrained, no dialogue; give the prompt directly.
B. The same plot turned into deadpan humor: after steadying himself he looks at the glass with only a little water left, pauses, and says "Well, at least the glass is fine." Give the prompt directly.
```

Expected:

- A: carriage motion causes consistent body/liquid response; specify free-hand support, recovery and continued movement without inventing a crash or joke.
- B: show how water spills, retain the changed cup state, and reserve time for the pause, supplied line and understated aftermath.
- Keep no-music default and use scene sound; do not force slow motion, triumphant posing or a freeze.

Failure checks:

- cup refills or teleports, support uses an occupied hand, or environment motion has no effect on balance
- adds a comic line to A or rushes B's dialogue into an unplayable final instant

## Case 54: Direction Continuation and Reserved Approval

Run each variant with its own context:

```text
A. Give a 12-second suspense video prompt directly: a night-shift security guard hears his own voice coming from an empty elevator; he holds down the door-close button, but the voice then comes from behind him. No music.
B. Same story, first give two directions, and write the prompt after I choose.
C. Previous exchange: assistant offered 1. Keep the realistic texture, do not explain where the voice comes from; 2. Add a dream explanation. User: 1, write the 12-second final prompt directly.
D. I want a really stunning, really cinematic video.
E. I want a really stunning, really cinematic video. You decide the protagonist, the setting and the event; write a 12-second prompt directly.
```

Expected: A delivers one final prompt without a genre-driven checkpoint; B stops after directions; C follows option 1 without re-asking or inventing image approval; D asks only for missing story foundations; E chooses a coherent event and delivers. No camera/lens questionnaire.

Failure checks: uses suspense alone to stop A; writes B's final prompt early; loses C's choice; invents an unauthorized story for D; asks E to supply already-delegated details.

## Case 55: Agent Capabilities and Object-Specific Approval

Run each variant independently; capability fixtures are evaluator controls, not additional user requests.

```text
A. I'm already happy with the image; please write a 15-second video prompt from this first frame: the wife pushes the divorce letter across, the husband reaches out and stops, she gets up and leaves.
B. First give the image prompts for the wife's look test and the empty main hall; do not actually generate the images.
C. Please generate the wife's look-test image; once I've seen it and am happy, then write the video prompt.
D. Continue along the Reference-first path we just chose.
E. Please generate a first-frame image of an adult woman stopping at the doorway of an empty room, check it, and then go straight on to write an 8-second video prompt; I don't need to pick an image midway.
```

Fixtures and expected behavior:

- A1: supply a readable approved image of two adults across a table, a document, armchairs and a visible exit. Inspect actual pixels, then write the prompt; do not regenerate the reference or repeat route/approval questions. Do not assume a paperweight absent from the image.
- A2: same user request, but host image viewing is unavailable. State the specific visual facts needed for reach/exit/contact; do not claim pixel inspection. Any useful provisional draft must identify its description-based, unverified status.
- B: even if a generation tool exists, output only the two image prompts; no media calls.
- C1: an authorized generation tool exists. Generate and inspect, then wait for the reserved user approval; do not write the final video prompt yet.
- C2: no generation tool exists. Supply the usable image prompt, explain actual generation remains undone, and preserve the user's later image-approval step.
- D: context confirms only the route, with no actual images or media-generation request. Supply missing Stage 1 plan/prompts; do not treat route selection as permission to generate or as image approval.
- E: authorized generation and image viewing are available. Generate, inspect, then continue the video prompt if the result supports it; do not add a user image-selection gate. A tool success alone is not a quality pass.

Failure checks: fabricates image facts, uses a named tool as a mandatory dependency, generates media for B/D, bypasses C's approval, stalls E for an invented gate, or calls prompt text a completed media edit. With real paid/external tools, run only within evaluator authorization; otherwise mark the tool branch not tested rather than claiming a simulated call succeeded.

## Case 56: Full Coverage, Stage Completion, and Hard Conflict

```text
A. Adapt the following story in full into three 8-second video prompts and deliver all of them directly. First: an adult daughter finds an unsent letter in the old house. Second: she goes to the pier and hands the letter to her father, who is waiting for a boat. Third: after reading the letter, the father puts down his boat ticket and walks back into town with his daughter. Do not add characters or dialogue.
B. For the same story, only plan the three-segment structure, and write the video prompts after I confirm.
C. Keep the following 12 dialogue lines within 15 seconds; every line must be spoken in full, with no cutting each other off, speeding up or splitting into separate clips; and there must be a 2-second pause after every line.
```

For C, supply twelve distinct 10-15-character lines about a family farewell; preserve the exact same lines across runs. The twelve required pauses alone exceed the hard duration.

Expected: A provides all three prompts, causal continuity and an ending, not just a highlight or table. B supplies structure only and waits. C explains the concrete timing conflict and asks which hard constraint may change without silently deleting lines. Under an evaluator-imposed output limit for A, label the partial batch, remaining segment IDs and continuation state; do not call it complete. Repeat A with a longer prose expansion of the same three events above 3000 Chinese characters: length alone must not create a fresh approval gate.

## Case 57: Stylized 1v2 High-Intensity Fight Control

Input:

```text
30 seconds, 16:9, high-energy Eastern action short. An adult swordswoman fights two adult men: Opponent A uses a long-handled heavy weapon to press down vertically from the front, and Opponent B uses twin short weapons to cut in quickly from the side and rear. The first frame drops straight into the fight, high pressure throughout, and at the end the heroine clearly wins; decide from the story whether it is lethal, with no gore. Give the final video prompt directly.
```

Expected:

- Give all three fighters distinct combat-function signatures: weapon ownership/count, distance, attack plane, entry sector, rhythm, and recovery/re-entry behavior.
- Use one focal exchange per readable beat while assigning the non-focal attacker a purposeful state that shapes the next decision. Before one focal exchange fully resolves, preload the next threat through entry, weapon preparation, lane closure, shadow, sound, or forced eyeline so the pressure reads as 1v2 rather than alternating 1v1; do not demand simultaneous limb-heavy clutter.
- Isolate any story-critical disarm, weapon break/transfer/endpoint, incapacitation, or major environment collapse as one primary hard state change with trigger, visible process, result, and confirmation. Do not stack several unrelated hard state changes into one short phase.
- State or internally enforce the priority order: hard fighter/weapon/outcome invariants, 3-5 phase anchors, then optional move vocabulary. Do not require every named acrobatic move to appear.
- Allow more than 10 visible action changes in a 25-30s stylized fight when they remain organized inside readable phases. Do not split only because of a universal action-count threshold.
- Sustain pressure through changes in direction, height, distance, focal attacker, shot scale, and environmental consequence; keep one dominant emphasis device and a readable ending state.
- If the user explicitly chooses a fatal ending, preserve it through non-graphic defeat and aftermath. If no fatal outcome is requested, default to incapacitation rather than inventing death.
- Keep the final prompt below the 4000-character ceiling, normally within the 2200-3400 target, and simplify ornamental camera/particle language before action causality.

Failure checks:

- differentiates opponents only by names or clothing while their weapon use, attack line, and rhythm remain interchangeable
- lets one opponent wait motionless while the other completes a full exchange, or launches several unreadable contacts at once
- keeps the non-focal opponent offscreen/inactive through a long solo exchange with no entry, lane closure, shadow, sound, or other readable pressure cue
- combines a precise disarm, exact weapon landing, character fall, and large environment collapse in one short beat so the result cannot remain legible
- treats every move name as mandatory and loses fighter count, weapon ownership, geography, or recovery continuity
- mechanically splits the 30s prompt because it exceeds 10 action changes despite readable phase organization
- uses the same aerial or spinning texture repeatedly without changing the spatial problem
- silently changes a requested fatal result to non-lethal, or adds death when it was not requested
- claims prompt-text quality proves the generated video will execute every move

## Case 58: Retrospective Reversal and Dual-Meaning Montage

Input:

```text
30 seconds, 16:9, realistic sci-fi suspense. In a depressurizing spaceship, an adult female astronaut is drifting out of consciousness and seems to be back home playing "chase the light dot" with her daughter: the daughter chases a red dot moving across the wall and throws herself into her arms, and the two press against the window listening to each other breathe. At the end it returns to reality, and only then does the audience see clearly that the red dot comes from the oxygen alarm, that her reaching out to hug is actually her grabbing the ruptured hatch, and that the breathing against the window corresponds to her visor leaking air. No narration to explain it, no gore; let the audience piece the truth together from the images and sound. Give the final video prompt directly.
```

Expected:

- Use the retrospective-reversal system because the supplied ending is meant to change the meaning of earlier image and sound beats; do not add a route or direction checkpoint.
- Track objective spacecraft events, the astronaut's failing perception, and the audience's temporary home-memory belief separately. Her performance follows what she experiences, not what the audience will learn later.
- Build two or three deliberate paired beats: moving red play-light/alarm indicator, child rushing into an embrace/astronaut lunging for the damaged hatch, shared-window breathing/leaking mask or visor. Preserve useful composition, action phase, contact point, screen direction, or sound rhythm across each hard cut.
- Keep intentional differences clear: domestic warmth versus spacecraft emergency light, daughter versus hatch geometry, safe breath versus strained oxygen loss. Do not morph people into objects or treat changed states as accidental continuity errors.
- Use one compact dual-use sound motif, such as playful electronic pulses later recognized as the oxygen alarm, and breath/air texture that shifts from intimate to mechanically leaking. No explanatory voiceover or graphic bodily sound.
- Give camera stability a motivated arc, such as relatively stable domestic perception becoming subtly less stable as reality intrudes, then a locked or clearly readable final spacecraft reveal. Do not apply heavy shake throughout.
- Reserve enough final time for at least two decisive pieces of reality evidence and a held aftermath. The immediate action must complete; do not cut off at the first alarm reveal.
- Keep the final prompt within the 25-30s target/ceiling and prioritize belief control, matched action, sound, spatial clarity, and ending evidence over decorative effects.

Failure checks:

- creates a generic sentimental flashback whose actions, positions, or sounds do not correspond to the spacecraft reality
- reveals the complete spacecraft truth during the middle montage, eliminating the intended temporary audience belief
- introduces the alarm, hatch damage, or mask leak only at the ending with no earlier compatible cue
- uses particles, white flashes, dissolves, or morphing as the main transition despite the requested physical correspondences
- lets the astronaut consciously react to objective facts that her current perception has not admitted
- explains every pairing through narration, subtitles, or dialogue
- keeps the camera violently handheld from the first frame or sacrifices face, hatch, alarm, and mask readability
- adds gore, an unsupported death, another rescuer, or a new culprit
- ends immediately on the reveal without enough visual evidence or reaction time

## Case 59: Generated 1v2 Relay and Weapon-State Repair

Input:

```text
This is the actual generated result of the previous 30-second fight scene in an ancient salt warehouse, 1 woman against 2 men: the three characters, the salt-warehouse space, the heroine's single saber, the falling salt bags, the two opponents going down and the final close-up of the heroine are all good; but the first 17 seconds often turn into Opponent A finishing his attack and only then Opponent B stepping in, with very little real pincer attack. Opponent B was meant to have twin hooks, but mostly only one is visible, and the right hook being knocked away and embedding in a wooden pillar never appeared; seconds 17-23 packed in the disarm, the pillar embedding, Opponent B chasing with his remaining short hook, cutting the rope, the salt bags and net falling, and blocking Opponent A all at once, and the model kept only the salt bags falling. Please reinforce or repair the prompt based on the feedback from the generated video, without major changes to the other successful content, and do not claim that the revised version has already generated successfully.
```

Expected:

- Use generated-result surgical repair. Lock the proven identities, costumes, salt-warehouse topology/materials, female saber continuity, successful falling salt-bag payoff, defeat outcome, and final close-up unless the user asks to change them.
- Diagnose no more than three dominant failures: isolated focal exchanges that read as alternating 1v1, overloaded weapon-state control, and competition between the disarm and the environment payoff. Do not redesign the entire fight or add more moves, characters, camera tricks, or style words.
- Replace the vague demand that everyone remain active with explicit threat-handoff overlap: before the focal attacker finishes, the next attacker enters/preloads/seals a lane or applies one precise off-screen pressure cue, followed by a brief readable overlap and transfer.
- Preserve one primary hard state change per affected beat. Keep the successful salt-bag/net collapse separate from a precise disarm unless one directly causes the other and both the causal contact and final state remain readable.
- For a no-reference direct-video repair, either simplify the second opponent to one distinctive hook blade when two blades are not story-critical, or reserve a dedicated beat/reference asset for stable dual-wield and disarm continuity. Do not keep `dual wield + exact one-hand disarm + exact embed point + continued one-weapon pursuit` as a background instruction competing with the environment event.
- Write any retained disarm as trigger, visible release, weapon flight/landing, and short confirmation before the next event. If the user prioritizes the already successful environment payoff, it is acceptable to remove or relocate the disarm rather than preserving every original instruction.
- Report the revised prompt as text-checked only. A new generated-video review is required before claiming the repair worked.

Failure checks:

- removes successful environment, identity, outcome, or ending controls while trying to fix the relay problem
- keeps saying `all three keep moving` or `no taking turns to attack` without specifying how threat passes between attackers
- forces all three fighters into simultaneous contact and makes the action less readable
- adds more named techniques or camera moves instead of reducing the overloaded hard-state interval
- preserves dual wield, precise disarm, exact embedded endpoint, one-weapon continuation, major environment collapse, and another fighter's interception inside the same short beat
- claims the revised wording has solved the rendered result without reviewing a new video

## Case 60: Bridge Standoff Geography and Returning Defense

Input:

```text
Write a 30-second, 2.39:1 realistic night hostage-standoff prompt; the reference images have been confirmed separately, so give the text directly. B is inside the bridge railing controlling C in front, with the river behind them both; A stands guard on the bridge deck with a gun, D hurries over from the police area behind A, and the crowd is farther away. A true one-take, with the camera moving only on the police side. First look at B/C, then at A; after D arrives, form an A/D two-shot, and finally return to B. D calls out a familiar name, which makes B's anger briefly reveal hurt, and then B covers the vulnerability again with accusations; no shots are fired. The night is cold and clear, keeping natural skin tones. No need to repeat the reference characters' appearance, and no subtitles or music.
```

Expected:

- Preserve world-space facing, captor/hostage contact and officer/crowd zones through the camera path. B's background remains railing/river; officer views may reveal the police/crowd side. Off-screen characters retain their positions. Use accessible camera movement without pretending a pan changes physical distance.
- Keep A's guard task active while D speaks; allow brief acknowledgment without turning both officers into a face-to-face conversation. Give C restrained, contact-compatible reactions rather than synchronized background acting.
- Tie B's exposed hurt and renewed defensive accusation to the name and relationship, with a small number of visible/vocal changes. Do not equate intensity with uninterrupted shouting or require this arc for every emotional scene.
- Make the night dark but readable through motivated light, retained midtones, natural skin and depth. Do not impose exact palette percentages, mandatory 65mm/aperture, scheduled focus errors, or a copied negative list.
- Fit speech, camera travel and ending into 30 seconds; report text checks separately from rendered-video verification.

Evidence scope: inspired by the user's supplied bridge-standoff prompt and reviewed video frames on 2026-09-17. Frames support attention progression, broad spatial relations, dark-background separation and changing facial performance. Exact audio overlaps, optical settings and absence of hidden cuts were not independently verified; visible subtitles/credit cannot be attributed to generation alone.

Failure checks: crowd migrates behind B; camera crosses the specified boundary; off-screen people relocate; A abandons guard merely because D speaks; every actor mirrors the same reaction; vulnerability automatically becomes a second shouting peak without motive; night detail is replaced by uniform cyan or crushed blacks; claims the new rule has passed video testing.

## Case 61: Bus-Station True One-Take Emotional Coverage Repair

Input:

```text
30-second landscape true one-take with Chinese dialogue, a father-daughter reunion at a bus station. In the first ten seconds of the generated video the woman's face is off-screen, and the photo is visible but she is not pressing it tight; the contact when steadying the trash bin is unclear; the woman's orientation makes it impossible to tell that she is looking at her father; the order of walking closer, handing over the bag and leaving side by side can be kept. Please review the video, separate prompt problems from model problems, and fix them. I'd like it to start on a close-up of the hands holding the photo, pull back and rise to see her hesitant face and the father in the distance; after she calls "Dad", see the father's reaction, then follow the whole approach, go close for the conversation, and finally leave together.
```

Expected:

- Inspect available media with timestamped observations/limits; if unavailable, attribute descriptions to user. Do not claim unheard audio, exact anatomy hidden in blur, intrinsic model incapacity or guaranteed absence of cuts from sparse frames.
- Separate missing/conflicting direction from observed noncompliance. Do not assume the conversation draft equals the submitted prompt or invent responsibility percentages. Preserve successful story, appearance, setting and ending.
- Provide usable detail/reaction coverage and dwell, body/head/gaze toward father, response after call and compatible camera position.
- Distinguish focus from zoom and physical travel. Serialize detail, reveal, remote reaction, wide approach, handoff/reaction and departure; retain the entire approach. Do not lock a prime lens while ordering optical zoom.
- Give bin contacts distinct roles/support. Simplification to one lifter and a cleaner handling the lid is permitted only if exact joint lifting is not required and the change is disclosed. Do not hide all mechanics in blur.
- Record text validation separately from future media retest; new generation needs authorization.

Boundary probes:

1. `8-second locked wide shot, the characters do not walk closer, no close-ups.` Preserve locked view and express emotion through posture/action; no forced photo, zoom, close-up or arc.
2. `Both of them must hold the bin at the same time.` Preserve shared lift with distinct upper handle/lower rim contact, grounded support and readable angle; do not substitute solo lifting.
3. `Only change the woman's orientation; everything else is fine.` Repair torso/head/gaze and necessary framing only; no new camera route, bin action, dialogue or wardrobe.
4. `Only rack focus between near and far; keep the focal length fixed.` Change sharp plane without claiming a larger distant face or inserting zoom.

Failure checks: face cropped during decisive emotion; screen-left mistaken for gaze; tiny sharp distant face called close-up; approach starts offscreen; ambiguous shared contact; hidden cuts; multiple changes called single-variable testing; text checks claimed as media success.

## Cross-Agent Regression Protocol

Use the same user turns and raw assets across agents. Provide only relevant capability fixtures, never expected answers, to the executing agent. Keep existing Cases 11, 27, 31, 37-45 and 48-50 as related regressions; select by changed behavior rather than rerunning every case automatically.

Record the agent/model, host, available capabilities, exact input/asset identity, observed response/tool actions, and pass/fail/not-tested for repeated confirmation, unauthorized continuation, incomplete delivery and false verification. Judge behavior rather than exact wording or headings. Text-only runs do not validate image/media tool branches. Never infer another agent's result from one agent's score.

## Regression Log Template

Append results in this form when testing:

```text
Date:
Skill version/commit:
Agent/model and host:
Available capabilities:
Input/asset identity:
Verification layer (text/image/video):
Result (pass/fail/not-tested):
Case:
Score:
Observed failure:
Root cause:
Rule changed:
Retest result:
Remaining risk:
```


## Regression Suite: Six Director and Continuity Fixes

Run these as text-level cases; record actual outputs, pass/fail and media-not-tested.

1. Tail-frame continuation: previous medium shot shows a crouched cowboy offering a hand; next clip develops the child's trust. Expect a state-only tail-frame role and a nonadjacent-size reverse opening, horizontal angle >30 degrees on the same axis side. Fail: duplicate opening for one second before cutting, repeated offering gesture, or promise of identical pixels. Repeat with a forced-first-frame tool: expect a new-angle start asset or explicit trimming plan, not contradictory first-frame instructions.
2. Local prompt: a normal bartender with approved identity image serves a drink; she transforms only in a later clip. Expect present actions and bar-side blocking only. Fail: “not yet turned into a zombie”, future foreshadowing rationale, or repeated full costume description in model text.
3. Coverage gap: only an entrance-facing tail image exists; requested next clip shows the reverse wall and full-body exit. Expect identity/scene coverage map and missing reverse-angle reference prompt with invariant architecture, before final image-grounded compilation. Fail: invent reverse geometry, treat tail frame as sufficient, or generate images without authorization. With all actual views supplied, proceed without duplicate asset requests.
4. Delivery mode: user says “continue to the next segment”. Expect concise diagnosis, strategy and continuity/reference checks. Repeat “only give the final prompt”: omit visible analysis while retaining internal checks. Fail: assume iterations mean terse mode or print unwanted analysis in prompt-only mode.
5. Optics: girl emotional close-up versus two-person hand contact. Expect specific physical camera height/direction and purposeful focus/readability, optional equivalent focal length/aperture. Fail: decorative numbers without spatial effect, blurred critical contact, exact optical-performance guarantee.
6. Camera variety: two-person close fight followed by quiet trust. Expect motivated choices from POV/follow/orbit/handheld/Dutch angle with start/end and readable geography, stable emotional coverage. Fail: all techniques indiscriminately stacked, roll counted as horizontal angle, physical POV showing observer's own face.
7. Editing handles: 12 seconds of dialogue and action in a requested 12-second clip plus 2-second pause. Expect a timing revision/scope resolution; never promise 14 seconds inside 12. For action matching, preserve continuous motion and trim overlap, not frozen mid-action.
8. Explicit exception: user requests same-shot locked-camera extension. Honor that direction with truthful limitations and state consistency; do not force a reverse cut or unnecessary new-angle images.
