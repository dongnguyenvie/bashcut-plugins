---
name: ideate
description: Find the angle of a vlog in BashCut before planning — footage first (media inventory, contact sheets, described shots, transcripts), 3–5 angles each backed by real shots and a source, research only when it changes the choice, "nothing solid" when nothing holds, a 3-hook screen per idea against actual shots, a decision table with a recommendation, then the project brief written with `project set-data brief` (each field stated, inferred or confirmed, with its source). Use before bashcut.vlog:plan when the user has footage but no clear angle, asks what to make, wants ideas, titles or a topic, or the brief is empty. Triggers: "làm video gì", "ý tưởng video", "góc kể", "nên kể gì", "chủ đề", "brainstorm", "lên ý tưởng", "footage này làm được gì", "ideas", "what should I make".
---

# Ideate: find the angle

Reply in the user's language. This skill decides **what the video is about** and writes it down as the project brief.
`bashcut.vlog:plan` then decides how to make it. The footage limits which angles are honest: an idea the footage cannot
show is the most common failure of a footage-first editor (T01 §4).

Numbers below are sample ranges with their source (T01 = the ideation notes). They are starting points; the user's
own history and what the footage holds come first.

## 1. Read what is already known

- `bashcut context get` and `bashcut project data brief` — an existing brief: keep `confirmed` fields, ask only about the
  rest.
- `bashcut knowledge prefs` and `bashcut knowledge facts` — the creator's preferences, channel, audience, past lessons.
- `bashcut media inventory` — what the footage holds: clips, seconds, capture times and places (grouped on a grid),
  orientation, speech seconds and languages, what is measured, transcribed and described.
- `bashcut workflow gates` — whether G1 (brief) asks the user.

## 2. Angles from the footage first

When there is footage, angles come from it (T01 §7):

1. **Look.** Contact sheets: `bashcut media frames --sheet` (every media by default, or `--media <ids>`). Read the
   PNGs. Describe what you saw in the closed vocabulary with `bashcut media describe <shots.json> --media <id>
   --base-rev N` (size, move, subjects, people, on-screen text, best moment). Facts only; no verdicts.
2. **Listen.** For clips with speech: `bashcut media transcribe --media <id>`, then `bashcut media transcript --media
   <id> --as text`. Strong lines, numbers said aloud, a question someone asked, a surprise.
3. **Group.** Clusters from the inventory: places (location groups), times (capture times: one day, one evening, a
   route), people, and speech moments.
4. **Derive 3–5 angles**, each from evidence you can name: "48 h in Đà Lạt: 6 place clusters, prices said in 4 clips"
   or "the noodle stall: 3 min of the cook talking, one strong line at 01:12". Fewer angles when the footage is narrow
   (T01 §3: 3–10 candidates; fewer when footage exists, because it limits the angles).

No footage yet (the video will be shot or generated): 5–10 angles from the user's prompt and research (T01 §3).

## 3. Research only when it changes the choice

Search the web only when a fact or trend would change which angle wins, and only with a tool that can search. Never
invent trends, numbers or "what is viral".

| Step | Sample range | Why it varies |
|---|---|---|
| Sub-questions | 1–4, written by you (T01 §7) | one for a clear topic; more for a niche the user does not know |
| Lookback for trends | 7–30 days (T01 §3, last30days and openclaw) | none for evergreen topics (a recipe, a how-to); short for news |
| Depth | quick 8–12 items per source, deeper only for high stakes (T01 §3) | stop early when sources agree |
| Evidence floor | corroborated by 2 or more independent sources (T01 §3) | raw engagement floors depend on platform size; do not copy them |
| Own history | a pattern from the creator's own videos needs at least 4 samples to compare (own-median multiples, T01 §3); label confidence low under 10 videos (T01 §3, a contradiction between sources) | only when the user gives their numbers |

Every idea carries its **source** (a clip and second, the user's words, a URL with its date) and, for a trend, **why
now**. When nothing is corroborated, write **"nothing solid"** and say what you looked at. That is a valid result;
never pad a list (T01 §4).

## 4. Screen each idea with 3 hooks

For each angle, write 3 hooks of different kinds (a number, a question, a contrast, the result first, a strong line
from the footage) and check each against an **actual shot**: name the media and second that would play under it
(T01 §7). Drop an idea when no hook has a shot behind it, or keep it and list the shots that are missing. A hook makes a
promise; the angle must be able to pay it off with what exists.

No scores. Composite scores (/40, "virality") read as precise but are not measurements (T01 §4); compare in words.

## 5. Decision table

Show 2–3 angles as a table and recommend one, with the reason:

| Angle | Best hook (with its shot) | Evidence and source | Missing | Length range | Outputs |
|---|---|---|---|---|---|
| … | "48H Ở ĐÀ LẠT HẾT BAO NHIÊU?" over C0012 at 3.2 s | 6 places, prices said in 4 clips | no night shot | 45–75 s | tiktok, reels |

Ask at most 1–3 questions, only for what changes the result and cannot be read from the footage: platform, length,
audience (T01 §3). Put each question as a choice with your recommendation.

Length ranges are a choice for the brief, not a rule: the platform's `maxSeconds` is the only hard limit
(`bashcut platforms get <id>`), and "sweet spots" contradict between sources (T17 §3).

## 6. Write the brief

Write the brief as project data. Each field is `{value, status, source}`:

- `stated` — the user said it (source: "user, message 2");
- `inferred` — you read it from footage, prompt or prefs (source: "media inventory: 41 portrait clips");
- `confirmed` — the user approved it at the brief gate.

```json
{
  "goal": {"value": "a cost guide for a 2-day trip", "status": "inferred", "source": "prices said in 4 clips"},
  "audience": {"value": "students planning a cheap weekend", "status": "stated", "source": "user"},
  "outputs": {"value": ["tiktok", "reels"], "status": "inferred", "source": "41 of 44 clips portrait"},
  "angle": {"value": "48h in Đà Lạt, what it cost", "status": "inferred", "source": "decision table, option A"},
  "lengthSeconds": {"value": {"min": 45, "max": 75}, "status": "inferred", "source": "6 place sections × 6–9 s (travel recipe)"},
  "notes": {"value": "no night shot; ask before using stock", "status": "inferred", "source": "coverage"},
  "ideas": [
    {"angle": "48h cost guide", "hooks": ["48H Ở ĐÀ LẠT HẾT BAO NHIÊU?"], "evidence": "C0012 3.2 s, C0031 0:40",
     "source": "footage", "chosen": true},
    {"angle": "the best cheap food", "source": "footage", "missing": "close-ups of 3 dishes"}
  ],
  "references": [{"url": "<link the user gave>", "learn": "cost overlays", "notToCopy": "their music and look"}]
}
```

```sh
bashcut project set-data brief brief.json --base-rev N
```

Write only what you know; leave a field out rather than guess. Review compares the brief's length and outputs with the
edit, as info. For a reference, write what to learn **and what not to copy** (T01 §4).

**Brief gate (G1).** `bashcut checkpoint request G1 --summary "<angle, length, outputs, audience, what is missing>"
--attach <contact sheet>`; poll `bashcut checkpoint status`. Approved: set the approved fields to `confirmed` with
`bashcut project set-data brief brief.json --merge --base-rev N`. Changes: update and ask again. The gate is skipped only
when `workflow gates` says so.

Then continue with `bashcut.vlog:plan`.

## Avoid

- Ideas the footage cannot show, and facts in a hook or title that the video does not show (T01 §4).
- Unsourced statistics presented as grounded ("AI narration loses 70 % retention"); generic industry averages instead
  of the creator's own history (T01 §4).
- A fixed story spine chosen before looking at the material.
- Random template hooks; scores presented as truth.
