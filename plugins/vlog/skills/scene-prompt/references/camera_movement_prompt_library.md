# Camera Movement Prompt Library

This library reorganizes the 46 categories from [AI Camera Movements](https://aicameramovements.com/) to translate story functions into executable camera-movement prompts. It does not copy the source site's text entry by entry, and it does not require every video to use complex camera movement.

## Usage principles

Read this library only when camera movement changes emotional distance, reveals information, follows action, shows a shift in power, establishes space, or completes a transition.

1. Decide the story function first, then choose the camera movement; never pick a "cool camera move" first and force the story to fit it.
2. Each shot usually uses only one main movement; a 6–15s video usually uses 0–3 main movements in total.
3. Every use must state clearly: the starting subject/shot size, the camera's actual path or lens change, direction, speed, the new information the frame reveals, and the ending subject/composition.
4. `Pan/Tilt/Zoom` are changes of lens direction or focal length while the camera position stays put; `Dolly/Truck/Tracking/Crane` are actual camera displacement. Do not mix them up.
5. Rewrite the modules below to fit the characters, setting and moment; never stack them verbatim. Write the final prompt in the chosen output language, keeping only cinematography terms and common English abbreviations as-is.
6. If the reference images do not show the space a new angle needs, first add a scene/keyframe reference, or switch to a movement the current space can support.

## A. Static, pan and tilt (7)

| # | Camera movement | Story function | Prompt module |
|---|---|---|---|
| 01 | `Static` | Restrained performance, waiting, awkwardness, intimidation, comic pause | `Static`: the camera stays locked at the same height, angle and distance throughout; let the character's actions and changes within the frame carry the rhythm, and end on a stable composition. |
| 02 | `Pan Right` | Following an eyeline or sound to reveal a character/space on the right | Start on the current subject and `Pan Right`; the camera position does not move and turns smoothly to the right horizontally; follow the eyeline or sound source to gradually bring in the target, and stop on a readable composition. |
| 03 | `Pan Left` | Following an eyeline or sound to reveal a character/space on the left | Start on the current subject and `Pan Left`; the camera position does not move and turns smoothly to the left horizontally; let the new information on the left enter the frame, and settle steadily on the target. |
| 04 | `Whip Pan Right` | Sudden shift of attention, surprise, action link | A clear starting subject triggers a `Whip Pan Right` that whips quickly to a new target on the right; brief motion blur is allowed mid-move, and the landing point is immediately sharp again. |
| 05 | `Whip Pan Left` | Sudden shift of attention, surprise, action link | A clear starting subject triggers a `Whip Pan Left` that whips quickly to a new target on the left; brief blur mid-move, ending precisely on the second subject. |
| 06 | `Tilt Up` | Revealing a character from a detail, building height, standing up or a threat | With the camera position fixed, `Tilt Up`: move the view upward from a low detail along a vertical structure, keep the subject's axis clear, and land on the key target above. |
| 07 | `Tilt Down` | Moving from the face to hands/props, the aftermath of a fall, a clue down low | With the camera position fixed, `Tilt Down`: tilt down from the subject above along the action or structure, and land on the hands, a prop, footsteps or the result on the ground. |

## B. Focal-length changes (6)

| # | Camera movement | Story function | Prompt module |
|---|---|---|---|
| 08 | `Slow Zoom In` | A sense of observation, slow focusing, mild psychological closing-in | The camera position does not move; use a `Slow Zoom In` to tighten the shot size slowly; the subject stays sharp throughout, ending on a tighter but stable composition. |
| 09 | `Slow Zoom Out` | Revealing the environment, loneliness or a hidden relationship | The camera position does not move; use a `Slow Zoom Out` to widen the view slowly; the subject stays recognizable as the surrounding space is gradually revealed, ending stable. |
| 10 | `Fast Zoom In` | Quickly emphasizing a clue, a reaction or a comic beat | Use a `Fast Zoom In` to tighten quickly onto the key face or object; the change is decisive but the target stays readable, and the landing does not shake. |
| 11 | `Fast Zoom Out` | Suddenly revealing a situation, a relationship or an absurd contrast | Use a `Fast Zoom Out` to expand quickly from the subject to the environment or group relationship; keep the central clue recognizable, ending on the full spatial result. |
| 12 | `Crash Zoom In` | Strong discovery, action impact, stylized emphasis | At the key trigger point, do one `Crash Zoom In` that slams instantly toward the core target; keep only one strong landing, then hold steady. |
| 13 | `Crash Zoom Out` | Strong reversal, suddenly exposing the full consequence | At the reversal or impact point, do one `Crash Zoom Out` that instantly reveals the larger situation; keep the relationship between the subject and the new environment clear, ending stable. |

## C. Push, pull and follow (9)

| # | Camera movement | Story function | Prompt module |
|---|---|---|---|
| 14 | `Dolly In` | Emotional closeness, pressure, a moment of realization | The camera actually moves toward the subject in a straight-line `Dolly In`, with stable height and viewing direction; as the distance shrinks the emotion tightens, and it stops on the key expression or object. |
| 15 | `Dolly Out` | Isolation, farewell, revealing consequences or the environment | The camera actually moves away from the subject in a straight-line `Dolly Out`; the character is gradually surrounded by space, and at the end the newly revealed environment or relationship carries the meaning. |
| 16 | `Tracking Shot` | A character moving through space, continuous action, experiencing a place | The camera moves with the subject along the route, matching the character's pace; keep the character readable while layers of the environment slide past, and keep the direction at the end. |
| 17 | `Follow Shot / OTS` | Following a character into an unknown space, keeping the destination | The camera follows from behind the character at shoulder height, using the back or shoulder as a foreground guide; the path and destination ahead stay clear. |
| 18 | `Reverse Tracking` | Walk-and-talk, closing in, pressing questions | The camera is directly in front of the moving character and backs up in sync; keep the face and upper body stable and readable, with the background unfolding behind the character. |
| 19 | `Side Tracking` | Side-by-side relationships, running, a procession or a sense of journey | The camera keeps a parallel distance from the subject in a `Side Tracking` move; keep the profile or three-quarter profile, with the direction of motion consistent throughout. |
| 20 | `Low Tracking` | Footsteps, wheels, escape, power and speed | The camera follows along the route at ground level or below the waist; emphasize footsteps, wheels or ground feedback while keeping the direction of travel and obstacles visible. |
| 21 | `Vehicle Tracking` | Driving, chases, travel and a sense of speed | The camera moves in the same direction as the vehicle at matching speed, keeping the vehicle relatively stable in frame while the road and background keep streaming past; end on a clear relationship of motion. |
| 22 | `Chase Shot` | Urgent pursuit, escape and an unstable on-the-ground feel | The camera follows the moving subject quickly and closely, with controlled responsive adjustments allowed; never lose the subject, and keep the path, obstacles and goal ahead readable. |

## D. Lateral moves, vertical moves and circling (11)

| # | Camera movement | Story function | Prompt module |
|---|---|---|---|
| 23 | `Truck Right` | Revealing relationships sideways, creating parallax or getting around an obstruction | The whole camera moves right along a horizontal straight line in a `Truck Right`, with the lens direction basically unchanged; use parallax between foreground, midground and background to reveal new spatial relationships. |
| 24 | `Truck Left` | Revealing relationships sideways, creating parallax or getting around an obstruction | The whole camera moves left along a horizontal straight line in a `Truck Left`, with the lens direction basically unchanged; let the obstruction move away and form a new lateral composition. |
| 25 | `Pedestal Up` | Elevated status, emerging from behind an obstruction, vertical restructuring | The camera keeps a level orientation and rises vertically as a whole in a `Pedestal Up`; no tilting up, ending by reorganizing the subject relationships from a higher viewpoint. |
| 26 | `Pedestal Down` | Dropping to the height of a character/object, lowering the sense of power | The camera keeps a level orientation and descends vertically as a whole in a `Pedestal Down`; no tilting down, ending with the target shown steadily from a lower height. |
| 27 | `Slider Right` | Subtle parallax in a quiet space, a glimpse or a shift in a relationship | The camera slides slightly and slowly to the right in a `Slider Right`; the foreground, characters and background produce delicate parallax, finally revealing a new angle on the right. |
| 28 | `Slider Left` | Subtle parallax in a quiet space, a glimpse or a shift in a relationship | The camera slides slightly and slowly to the left in a `Slider Left`; use the change in foreground obstruction to rearrange the frame, finally settling on a new angle. |
| 29 | `Push Past / Pass-by` | Entering a space, passing a doorframe/a character's shoulder, revealing depth | The camera pushes forward and skims closely past a clear foreground edge or opening; the foreground slides past the lens, and the move ends inside the space behind it. |
| 30 | `Arc Right` | A shift in relationship power, turning from front-on to profile | The camera moves right around the subject along a shallow arc, with relatively stable distance and height; the background changes with the angle, ending at a new observation point on the right. |
| 31 | `Arc Left` | A shift in relationship power, turning from front-on to profile | The camera moves left around the subject along a shallow arc, with relatively stable distance and height; keep the subject clear, ending on a new angle on the left. |
| 32 | `Orbit Clockwise` | Ritual, standoff, a sense of rotating space, complete observation | The camera does a clockwise `Orbit` around the subject at a steady radius; the subject stays the visual center while the background produces continuous rotational parallax, stopping steadily at the planned angle. |
| 33 | `Orbit Counterclockwise` | Ritual, standoff, a sense of rotating space, complete observation | The camera does a counterclockwise `Orbit` around the subject at a steady radius; keep the subject's scale and readability, stopping steadily at a clear new position. |

## E. Body-mounted camera (2)

| # | Camera movement | Story function | Prompt module |
|---|---|---|---|
| 34 | `Handheld` | On-the-ground feel, tension, documentary texture, slight imbalance | Use a restrained `Handheld`, with the camera at a height a human operator could manage; only subtle breathing-like sway and follow corrections, with the subject clear throughout. |
| 35 | `Snorricam` | Body-bound action experience, running, subjective imbalance or psychological confinement | The camera is fixed in front of the character's torso, facing the character; the torso stays relatively stable in frame while the head and limbs still move naturally, and body turns and displacement drive the background changes; when the character stops, the background settles too. The camera cannot independently circle, push/pull or zoom, and the rig stays out of frame; leave room in the composition for the paths of key hand and prop actions. Choose the duration by the story; when the user explicitly asks, it can run through the whole segment, not just as a brief psychological effect. |

## F. Crane and aerial (5)

| # | Camera movement | Story function | Prompt module |
|---|---|---|---|
| 36 | `Crane Up` | Revealing the scale of the environment from a character, loneliness or the full view of a ritual | The camera rises smoothly in a `Crane Up` while keeping the character or location recognizable; as height increases a larger space is revealed, ending by emphasizing the relationship of scale. |
| 37 | `Crane Down` | Entering a character from the environment, arriving at the center of the event | The camera descends smoothly from a higher viewpoint in a `Crane Down`; gradually press attention down onto the character or target on the ground, ending at the core of the event. |
| 38 | `Drone Push In` | Approaching a location, establishing a large-scale route and destination | The drone flies smoothly forward through open space in a `Drone Push In`; the route and destination stay clear throughout, ending on a closer aerial composition. |
| 39 | `Drone Pull Back` | Expanding from a character/building to the landscape and overall consequences | The drone pulls back smoothly in a `Drone Pull Back`; the subject gradually shrinks but is never lost, larger landscape is revealed layer by layer, ending by emphasizing the scale of the environment. |
| 40 | `Helicopter Shot` | Cities, mountains and rivers, convoys, war or tracking the big picture | Use a high-altitude `Helicopter Shot` moving along a wide, gentle arc; keep the landscape or distant moving subject readable, ending on a stable large-scale composition. |

## G. Special photography and time-space movement (6)

| # | Camera movement | Story function | Prompt module |
|---|---|---|---|
| 41 | `First-Person View / POV` | Immersive entry, observing, reaching out and bodily experience | Use `POV`, with the camera at the character's eye height moving naturally with walking or reaching; keep an arm or body at the edge of the frame as a spatial reference. |
| 42 | `Tilt-Shift` | A miniature-model feel for cities/crowds, compressed time or detachment | Use a high, oblique `Tilt-Shift` view, with only the subject area forming a narrow sharp band and the top and bottom gradually blurring; the camera is fixed or makes only small smooth moves. |
| 43 | `Infinite Zoom` | Entering inside an image, recursive worlds, dream-layer transitions | Keep doing an `Infinite Zoom` around a single central target; each layer fills the frame and then naturally becomes the next layer's space; the center and direction of motion must not drift. |
| 44 | `Earth Zoom Out` | Rising from a personal location to city, landscape and planetary scale | Pull back upward quickly and continuously from a clear location, revealing in turn the neighborhood, the city, the landscape and the Earth; the original location always remains the implied center. |
| 45 | `Time-Lapse` | The passage of time, changes in weather/crowds/construction/light | Use a fixed-camera `Time-Lapse`, with the camera angle and horizon unchanged; environmental motion is compressed and sped up, ending with the result of time in the same composition. |
| 46 | `Pass-Through Objects` | Completing a spatial transition through doors, mirrors, walls or holes | The camera pushes toward a clear surface or opening and passes through into the space on the other side; keep the transition point centered, with the direction, speed, light or shape relationships before and after forming a continuous bridge. |

## Quick story index

- Restrained performance, pauses, intimidation: `Static`, a very slow `Dolly In`
- Eyeline/sound reveals: `Pan`, `Tilt`, `Rack Focus`
- Closeness or pressure in a relationship: `Dolly In`, `Arc`
- Leaving, loneliness, consequences: `Dolly Out`, `Crane Up`
- Walk-and-talk: `Reverse Tracking`, `Side Tracking`
- Entering an unknown space: `Follow Shot / OTS`, `Push Past`
- Chases and escapes: `Chase Shot`, `Low Tracking`, restrained `Handheld`
- Shifts in power or positioning: `Arc`, `Truck`, `Pedestal`
- Sudden shift of attention: one `Whip Pan` or `Crash Zoom`
- Large-scale scope: `Crane`, `Drone`, `Helicopter Shot`
- Body-bound action experience or subjective imbalance: `Snorricam`, with the duration decided by the action and the user's request; for very rare major turning points of realization, `Dolly Zoom` can be used
- Time-space/physical transitions: `Pass-Through Objects`, `Infinite Zoom`, `Time-Lapse`

## Output check

- Is the camera movement triggered by a specific action, sound, eyeline, piece of information or change in emotion?
- Are the starting point, direction, speed, movement path and landing point all visible?
- Can the camera actually move in this setting, or does it pass through characters, walls or furniture?
- Does the camera movement steal time from the dialogue, action, performance and the lingering ending?
- Across multiple shots, are the 180-degree axis, eyelines, left/right positions, direction of travel and prop states maintained?
- If removing the camera move costs the story nothing, change it to `Static` or a simpler shot.
