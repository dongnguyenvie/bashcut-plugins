---
name: travel
description: Recipe for a travel vlog or travel guide in BashCut, vertical by default — hook with a cost or time number, numbered place sections with place cards, a cost recap and a save/follow CTA; pacing, text, sound and look intent and the review profile to set. Use after bashcut.vlog:plan picked travel, or when the user edits footage of a trip, a city, places or a route. Triggers: "vlog du lịch", "review chuyến đi", "đi Đà Lạt", "48h ở", "lịch trình", "travel vlog", "travel guide", "ăn chơi ở", "check-in".
---

# Travel vlog

Reply in the user's language. Apply the profile with `bashcut.vlog:plan` step 2, then edit with `bc:edit-workflow`
using the values below.

## Profile

```json
{"outputs": ["reels", "tiktok", "shorts"],
 "review": {"minShotSeconds": 0.8, "maxShotSeconds": 4.5, "maxStillSeconds": 3, "hookSeconds": 3,
            "severities": {"still": "error"}}}
```

Landscape footage for YouTube: `["youtube-1080"]` with `maxShotSeconds` 8 and `maxStillSeconds` 5.

## Structure (45–75 s vertical)

| Part | Length | What |
|---|---|---|
| Hook | 2–3 s | the most striking shot plus `vlog-hook-question`: a number the viewer wants (cost, hours, days) and a question — "48H Ở ĐÀ LẠT HẾT BAO NHIÊU?" |
| Sections ×4–6 | 6–8 s each | one place or one step of the route; `vlog-section-chip` ("2/5 · CHỢ ĐÊM") as it starts, `place-card` with the name, `vlog-price-tag` when money is said |
| Recap | 4–6 s | the total (cost table as stacked lines, or the route in one map shot) |
| CTA | 2–3 s | `vlog-cta` ("LƯU LẠI ĐỂ ĐI NHÉ!") over the nicest wide shot |

Mark each section with `upsertSection` (label = place name) so review and the user see the structure.

## Cuts and motion

- 13–16 cuts a minute: 3–4.5 s per shot; faster (1–2 s) in the hook and when listing things.
- Every still or locked-off shot moves: Ken Burns (`ken-burns-in`/`-out`, `bc:effects`); a photo never sits still
  longer than 3 s.
- Between sections: `vlog-whip-fast` or a hard cut on a beat (`bc:beat-cut`); inside a section, hard cuts only.
- Walking, driving and food shots: speed ramp through the boring middle (`speed-ramp`).

## Shots to look for (survey) and to shoot

Establishing wide of each place, a detail (sign, food, ticket), the person in the place (selfie or from behind),
movement between places (feet, vehicle, window), the view at the best moment (sunset, night lights). Missing an
establishing shot: use the widest shot of the place, or a stock picture labelled `vlog-disclosure` when it is not
the user's own (`bc:stock-images`).

## Text and voice

- Captions from the voice (`bc:captions-text`), bold-outline, 3–6 words a line; keep them above the platform's
  caption bar (the review checks it).
- Voiceover when the footage has none: 165–235 Vietnamese syllables a minute, one fact per section
  (`bashcut.vlog:hook-script`, `bc:voiceover`).
- Numbers are always on screen when said (price, time, distance).

## Sound

Upbeat music bed, clearly under the voice (ducked); natural sound of each place for the first second of its section;
a whoosh on the whips. Loudness is the platform's target — do not set it here (`bc:audio-mix`).

## Look

Intent: bright, warm and clean, skies not blown out, skin natural. Measure the footage first and grade to that intent
(`bc:color-grade`); never apply fixed numbers. One look for the whole video; night shots may stay cooler.

## Review notes

A frozen picture (a photo or a locked-off shot without motion for over 3 s) is an error in this recipe, not a
warning: give it Ken Burns or cut it shorter. "Repeated framing" between two clips of one place is fixed
with a punch-in, not ignored.
