---
name: hook-script
description: Write the words of a vlog in BashCut — 2–3 story options, 3–5 hook options checked against real shots, the script as beats where every line has a job, an ON SCREEN note and a source for each claim, sized to each window with the measured speaking rate of the creator or the chosen voice (speech rate, narration windows), a counterfactual review that quotes the weak line, on-screen text and the CTA; the beats go into the edit plan and script check compares them with what is heard. Use when a vlog needs a hook, a story, a voiceover or talking script, titles or text written (not transcribed), or the user says the opening is boring. Triggers: "viết hook", "câu mở đầu", "mở đầu nhàm", "viết kịch bản", "viết lời thoại", "viết lời đọc", "script vlog", "kể chuyện thế nào", "tiêu đề video", "caption trên video", "CTA".
---

# Hook and script

Reply in the user's language; write the viewer-facing words in the video's language (`contentLanguage` in
`bashcut project get`). Read `bashcut project data plan` (sections, mode, existing beats) and `bashcut project data brief` first, and
use the structure of the active recipe (`recipe.skill` in `project get`, see `bashcut.vlog:plan`).

Numbers below are sample ranges with their source (T02 = script notes, T10 = voiceover notes). A **measured** rate of
this speaker or voice always replaces them.

## 1. Who owns the sound

Before writing a word, decide per stretch of the edit who owns the sound: real speech, action sound (a sizzle, a
crowd), music, silence or narration (T02 §4). Narration is a choice; **none** is a valid answer when the footage
speaks for itself.

- `bashcut media speech-map --media <id>` — where the real speech is, and its gaps.
- `bashcut narration windows --min-seconds <n>` — stretches with no spoken word and no voiceover, with the share
  music and footage sound cover (`covered`; the larger one owns it, neither is silence), the shots under them and the section they fall in. Choose `n` from the shortest line
  you would write (about one short sentence); add `--levels` to see how loud the mix is there.

**Real speech first**: when the footage has the person talking, build from their lines (`bashcut media transcript
--media <id> --as text`; keep the last clean take of a repeat). Write voiceover only for the gaps. Narration that
describes what the picture already shows is cut (T02 §4).

## 2. Story options (create mode)

In `create` mode, write **2–3 story options** before the script (T00 §3, T02 §3): for each, the spine in one sentence,
which sections and shots carry it, its hook, and what it leaves out. Recommend one. In `directed` mode (the user gave
the story) write one; in `revision` mode keep the `frozen` sections' lines word for word. Store the options with
`bashcut project set-data plan options.json --merge --base-rev N` (`options` field) and the choice in `decisions`.

## 3. The hook

The hook is a promise in the first seconds: one line on screen (`vlog-hook-question`, or the text template that suits the video, `bc:captions-text`; two short lines with the keyword alone on one) and, if
someone speaks, the same idea said. Write **3–5 options across different kinds** (T02 §3, T02 §7) and pick against the
best shot of the footage and the hook facts once a cut exists, over the opening frames: `bashcut transcript words
--to F` (first words), `review layout --to F` (first text), `review shots --to F` (first cut, described subjects).

| Kind | Example |
|---|---|
| cost / time + question | "48H Ở ĐÀ LẠT HẾT BAO NHIÊU?" |
| result first | "VIDEO NÀY DO AI DỰNG TRONG 5 PHÚT" |
| verdict as question | "3 TRIỆU CÓ ĐÁNG?" |
| number of things | "5 QUÁN PHẢI ĂN Ở QUẬN 4" |
| surprise / contrast | "QUÁN VỈA HÈ NGON HƠN NHÀ HÀNG?" |
| a strong line from the footage | the speaker's own sentence, moved to the start |

| Check | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Hook window | short-form 1–3 s; long-form up to about 15 s (T02 §3, a contradiction between sources) | platform, length, whether the viewer chose to watch | `bashcut transcript words --to F`, `review layout --to F` |
| Hook text on screen | about 6 words or fewer per frame (T14 §3); about 60 characters at most in 9:16 (T14 §3) | font size, how long it holds | `bashcut review layout` → `longestLineChars`, `holdSeconds` |
| Options compared | 3–5, show the best 2 (T02 §3) | — | — |

The hook promises only what the body pays off, and the CTA closes that promise. Never open with a greeting or "hôm nay
mình…". Record the chosen hook and the shot under it in `decisions`.

## 4. The budget from the measured rate

Size every line to its window with a **measured** rate, never a fixed table:

- **The creator speaks**: `bashcut speech rate --media <id>` → per speaker p10/p50/p90 in the content language's unit
  (syllables for Vietnamese, characters for Chinese, Japanese and Korean, else words).
- **A synthesized voice**: `bashcut capabilities get voice.synthesize --voices` → `measuredRate` per voice and
  language. No measurement yet: make one test line with `bashcut voice speak "<line>"` (nothing is placed), then
  `bashcut speech rate --voice <provider/voice>`.
- **Budget per window**: `bashcut narration windows --min-seconds <n> --rate <units per second>` adds how many units fit
  each window. Use the p50 rate for the budget and the p10–p90 spread as the margin (T02 §7), not a fixed ×0.85.

Before anything is measured, these are samples only (T02 §3): Vietnamese about 3–4.5 syllables a second (the old
165–235 a minute here was unsourced and must be measured); English 2.0–3.5 words a second (150 wpm is common, 210 was
measured for one creator); Chinese 3–4 characters a second.

When a line does not fit: cut or split its job, or move it to another window. **Never speed the voice up to fit**
(T02 §4); a mild stretch of up to about 1.1× only after rewriting failed, slow-down to 0.82–0.95× (T10 §3). Leaving
0.3–1 s of silence at a line end is often the right answer (T10 §7).

## 5. The script as beats

One row per beat, section by section:

| Beat | Section | Owner | Window and budget | Line (as heard) | Job | ON SCREEN | Source |
|---|---|---|---|---|---|---|---|
| b1 | hook | VO | 0–2.4 s, ~9 syllables | "Hai ngày Đà Lạt, hết bao nhiêu?" | claim (promise) | the pull at 120 fps + hook title | — |
| b4 | place 2 | real speech | C0031 0:40–0:46 | (the seller's line) | context | the seller, price board | C0031 0:41 |
| b5 | place 2 | VO | 3.1 s, ~12 syllables | "Bốn lăm nghìn một tô, rẻ nhất chuyến đi." | interpretation | `vlog-price-tag` "45K" | price board, C0033 0:02 |

- **Job** per line: context, causal link, foreshadow, interpretation, transition, claim, CTA. A line without a job is
  deleted (T02 §4).
- **ON SCREEN**: what the picture shows while it is said, and any text. Text repeats the key word or number of the
  line, never the whole sentence; captions or a card carry a line, not both (T13 §4).
- **Source** for every fact: a number, a price, a name, a place, a superlative. A frame of the footage, the user, or a
  link with its date. No source: cut the claim or ask the user (T02 §4).
- One fact or feeling per sentence; numbers as the viewer would say them ("bốn lăm nghìn"), digits on screen. Write for
  the ear: one continuous thought per beat; split for captions afterwards.

## 6. Counterfactual review

Before showing the script, test it (T02 §4):

1. **Delete each beat** in your head: if the story still works without it, cut it.
2. **Mute the voiceover**: does the picture still tell the story? Lines that only describe the picture go.
3. **Audio only**: does it make sense without the picture?
4. **Quote the weakest line exactly** and fix or remove it. Check the hook's promise against the last beat.

## 7. Into the plan, then the script gate

Write the beats as `beats` [{id, section, text}] (text = the exact words to be heard) with `bashcut project set-data
plan beats.json --merge --base-rev N`. Show the hook options, the story options and the script to the user, then request the script
gate before any voice is made: `bashcut checkpoint request G4 --summary "<hook, story, beats>"` and poll `bashcut
checkpoint status`. After voiceover and editing, `bashcut script check` shows per beat how much was heard as written
and where; fix the beats or the edit, not the measurement.

`bc:voiceover` produces the voice: `voice speak` measures the takes, you place the one whose `unitsPerSecond` is
closest to the rate you sized for (`voice place`).

## On-screen text and CTA

- Captions per the recipe's caption range (`bc:captions-text`); titles and cards from the vlog pack (`library list
  --pack Vlog --tag hook`, `--tag section`, `--tag price`, `--tag cta`).
- CTA: one action only (save, follow, comment a question, buy), held long enough to read: 1–6 s by platform and CTA
  (T07 §3). Fit it to the platform's culture as examples, not rules: Shorts and TikTok often "follow", Reels "lưu lại",
  YouTube "xem video tiếp theo".
- AI-made pictures or voices, sponsorship: add `vlog-disclosure` with the wording the platform needs (`bashcut
  platforms get <id>` → `disclosure`).
