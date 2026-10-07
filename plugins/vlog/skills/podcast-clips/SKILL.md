---
name: podcast-clips
description: Recipe for cutting shorts from a long podcast, interview, livestream or talk in BashCut (long → short) — classify the source, propose about twice the clips needed by quote (media resolve-range, selects set), the standalone test, a blind second pass with publish/review/drop verdicts, the user picks, one sibling project per kept clip (project derive), then each is edited as a talking-head short; length, padding and hook ranges with sources. Use after bashcut.vlog:plan picked podcast-clips, or when the user has a long recording and wants several short clips from it. Triggers: "cắt podcast", "cắt clip ngắn từ video dài", "cắt shorts từ livestream", "clip podcast", "highlight phỏng vấn", "podcast clips", "long to short", "repurpose", "cắt nhiều clip".
---

# Podcast clips (long → short)

Reply in the user's language. One long source becomes several shorts; each short is its own project. The selection
is the hard part: the select-by-quote loop, the blind pass and `project derive` are `bc:rough-cut`'s; this recipe
adds the genre's ranges and order. The edit of each clip then follows `bashcut.vlog:talking-head`. Plan with `bashcut.vlog:plan`. A
measured reference (shorts from a channel the user points to) wins over the ranges here (T15 §7).

## Ranges

Outputs per clip: vertical → `shorts`, `tiktok`, `reels`; a topic clip for YouTube → `youtube-1080`. Write each chosen
value and its reason in the plan.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Short clip length | 15–90 s; one-liners shorter, stories longer (T06 §3) | the moment sets it (setup + turn + payoff), then the platform's `maxSeconds` caps it | `bashcut platforms get <id>`; `selects list` from/to |
| Topic clip length | 1–6 min (T06 §3) | source length and platform | as above |
| Yield | not a quota: sources report about 1 clip per 2–3 min of source against 1 per 5–10 min (T06 §3, a contradiction) | how dense the talk is; fewer is fine | report the count and why you kept N |
| Candidates | about 2× the clips you need, expecting 30–45 % duds (T06 §3) | a sharp talk has fewer duds | `bashcut selects list` counts per status |
| Hook `hookSeconds` | the strongest **complete** sentence, 1.5–3 s (T06 §7) | a long sentence needs the top of the band; a cold open (a line from later moved to the start) only when the best line is more than about 10 s into the clip (T06 §7) | `bashcut review layout --to F`, `transcript words --to F` |
| Cut padding | in 50–150 ms before the first word, out 80–300 ms after the last (T06 §3) | tighter for energy, looser for a trailing reaction or laugh; never past the next word | `bashcut media resolve-range` edge facts; `bashcut review sync` |
| Clean cut points | gaps of 400 ms or more are clean; 150–400 ms need a look; under 150 ms are unsafe (T06 §3) | music or room noise under the gap | `bashcut media speech-map --media <id>` → `gaps` |
| Length vs target | within ±10–15 % of the planned length (T06 §3) | a clip that needs its full payoff runs over; say so | `bashcut review run` (brief length, info) |
| Pauses inside a clip, framing, captions | as `bashcut.vlog:talking-head` | — | see that recipe |
| Two cameras: shot dwell | 3–12 s, varied with energy, never random; cutaways to the listener 2–4 s (T19 §3, §7) | a fast debate cuts sooner; a long answer holds | `bashcut review shots --summary` |

## 1. Read and classify the source

1. `bashcut media transcribe --media <id>`, then `bashcut media transcript --media <id> --as text` (phrases with
   times) and `bashcut media speech-map --media <id>` (speech and gaps).
2. Classify it (T06 §4): **words** (the value is in what is said: trust the transcript), **reactions** (laughs, a
   heated exchange: listen and look, a laugh is a lagging marker of the moment before it) or **visual** (a demo, a
   reveal: look at frames, `bashcut media frames --media <id> --from <s> --to <s> --sheet`).
3. Two cameras or a separate audio recorder: sync them first (`bashcut media sync`, `bc:footage-survey`).

## 2. Propose by quote, never by typed times

1. Read the transcript and pick about twice the clips you need.
2. Resolve each by what was said: `bashcut media resolve-range <media> --quote "<the words as said>"`, or for a long
   passage `--words FIRST-LAST` with word indices from `bashcut media transcript --media <id> --as words`. It returns
   from/to seconds and frames, whether each edge lands mid-word or mid-sentence, and the nearest word and sentence
   edges before and after. Move an unsafe edge to the nearest sentence edge; never type raw seconds (T06 §4).
3. Store each as a select with the quote, the reason (setup, turn, payoff in one line) and the evidence (what you
   measured or looked at): `bashcut selects set selects.json --base-rev N`. They start as `candidate`; the user sees
   them in the Media panel.

**Standalone test** (T06 §7) for every candidate: no unresolved "he / it / that" pointing outside the clip, no "as I
said earlier", the payoff is inside the clip, and no stitching across "but / however". A clip that fails is dropped or
widened.

## 3. Blind second pass

Hand the candidates to a fresh sub-agent that sees only each clip's text with one sentence of context on each side,
not your reasons (T06 §4). It returns **publish**, **review** or **drop** with a one-line reason per clip. Mark the
drops: `bashcut selects set rejects.json --base-rev N` with `[{"id":"…","status":"rejected","reason":"<why>"}]`. Expect about a third to drop.

## 4. The user picks

Show the table: quote, length, the hook sentence, the verdict, and why you rank it. Request the strategy gate:
`bashcut checkpoint request G2 --summary "<N clips proposed, M recommended>"`, poll `bashcut checkpoint status`. Mark
the chosen ones `kept` (`bashcut selects set` with `{"id":"…","status":"kept"}` rows).

## 5. One project per clip

`bashcut project derive` writes one sibling project per kept select, with the same canvas, outputs, review profile,
brief and layers, the media and only that range on Main. The open project does not change. Open each in turn
(`bashcut project open <folder>`) and edit it as a short:

- Hook: the strongest complete sentence first (the cold open rule above), then the clip in order.
- Tighten pauses, punch-ins at word boundaries, word-by-word captions: `bashcut.vlog:talking-head`.
- A landscape source in a vertical output: reframe each shot on the speaker with a transform zoom and position, and
  check it with `bashcut ui frame`. Never trust a blind centre crop of a two-shot; when nobody fits, use a fitted
  frame instead (T19 §4).
- A title card or chapter label only when the clip needs context the first sentence does not give.

## Rhythm, transitions and graphics

| What | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Framing change | every 4–6 s (T07 §7), by punch-in or a camera switch | a dense argument changes more often | `bashcut review shots` → `cut.sameFraming` |
| Snap punch | 1.1–1.15× on a strong word; 4–6 in a 60 s reel (T08 §3) | the clip's headroom | `bashcut timeline get` → `scale.maxZoomNative` |
| Transitions | hard cuts and punch-ins; 0–1 special transitions per clip (T08 §7) | — | `bashcut review shots` → count `cut.kind` |
| Graphics | 0–2 per clip: a keyword (`vlog-keyword`) on the claim word, a name label at the start (T13 §3: 3–8 per minute is for explainers, sparser here) | the face carries the clip | `bashcut review layout` |

## Review notes

- One camera repeats its framing by nature: `framing` at `info`; jump cuts still warn and are fixed with punch-ins.
- A viewer notices: a clip that starts mid-thought, a cut inside a word, a laugh with its joke cut off. These are
  blockers; a slightly long pause is not.
- `needs_user`: which clips to keep, the speakers' names and titles for labels, permission to post a guest's words,
  the outputs per clip.
