---
name: hook-script
description: Write a vlog's words: story options, 3–5 hooks checked against real shots, the script as beats (job, on-screen, source) sized to the measured speaking rate, on-screen text and CTA. Use for a hook, script, voiceover, titles, or a boring opening. Triggers: "viết hook", "câu mở đầu", "mở đầu nhàm", "viết kịch bản", "viết lời đọc", "CTA".
---

# Hook and script

Reply in the user's language; write viewer-facing words in the video's language (`contentLanguage` in `project
get`). Read `project data plan` (sections, mode, existing beats) and `project data brief` first, and use the active
recipe's structure (`recipe.skill`, see `bashcut.vlog:plan`).

Numbers below are sample ranges with their source (T02 = script notes, T10 = voiceover notes). A **measured** rate of
this speaker or voice always replaces them.

## 1. Who owns the sound

Before writing a word, decide per stretch who owns the sound: real speech, action sound (a sizzle, a crowd), music,
silence or narration (T02 §4). Narration is a choice; **none** is valid when the footage speaks for itself.

- `media speech-map --media <id>`: where the real speech is, and its gaps.
- `narration windows --min-seconds <n>`: stretches with no spoken word and no voiceover, with the share music and
  footage sound cover (the larger owns it; neither is silence), the shots under them and their section. `n` = the
  shortest line you would write (about one short sentence); `--levels` shows how loud the mix is there.

**Real speech first**: build from the person's own lines (`media transcript --as text`; keep the last clean take of a
repeat) and write voiceover only for the gaps. Narration that describes what the picture shows is cut (T02 §4).

## 2. Story options (create mode)

In `create` mode write **2–3 story options** before the script (T00 §3, T02 §3): the spine in one sentence, which
sections and shots carry it, its hook, what it leaves out; recommend one. `directed` mode: one. `revision` mode: keep
the `frozen` sections' lines word for word. Store them as the plan's `options` (`--merge`) and the choice in
`decisions`.

## 3. The hook

A promise in the first seconds: one line on screen (`vlog-hook-question` or the text template that suits the video,
`bc:captions-text`; two short lines with the keyword alone on one) and, if someone speaks, the same idea said. Write
**3–5 options of different kinds** (T02 §3, §7) and pick against the best shot and, once a cut exists, the opening
frames (first words, first text, first cut and described subjects).

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
| Hook window | short-form 1–3 s; long-form up to about 15 s (T02 §3, sources contradict) | platform, length, whether the viewer chose to watch | `transcript words --to F`, `review layout --to F` |
| Hook text on screen | about 6 words or fewer per frame; about 60 characters at most in 9:16 (T14 §3) | font size, hold | `review layout` → `longestLineChars`, `holdSeconds` |
| Options compared | 3–5, show the best 2 (T02 §3) | — | — |

- **Text and speech in the opening (`hookSeconds`) say the same thing.** A title asking one question while the voice
  says another reads as two messages (a critic flagged it in a one-prompt ad): write the on-screen hook from the
  spoken line, or speak the title.
- The hook promises only what the body pays off, and the CTA closes it. Never open with a greeting or "hôm nay
  mình…". Record the hook and its shot in `decisions` and the pair as the plan's **`promise`** `{hook, payoff}`. Every
  video has one; the strategy and draft audits check that the payoff answers the hook.

## 4. The budget from the measured rate

Size every line to its window with a **measured** rate, never a fixed table:

- **The creator speaks**: `speech rate --media <id>` → per speaker p10/p50/p90 in the language's unit (syllables for
  Vietnamese, characters for Chinese, Japanese and Korean, else words).
- **A synthesized voice**: `capabilities get voice.synthesize --voices` → `measuredRate`. None yet: one test line
  with `voice speak` (nothing is placed), then `speech rate --voice <provider/voice>`.
- **Per window**: `narration windows --rate <units per second>` adds how many units fit. Budget at p50, margin from
  the p10–p90 spread (T02 §7), not a fixed ×0.85.

Before any measurement these are a sanity check only (T02 §3): Vietnamese articulation rate (pauses removed)
4.7–5.3 syllables a second (4.74 in Bradlow, Interspeech 2019,
https://www.isca-archive.org/interspeech_2019/bradlow19b_interspeech.pdf; 5.22 in Pellegrino et al., Language 2011);
overall rate (pauses kept) 200–245 syllables a minute (read audiobooks, Vu et al., ACL 2025, PhoAudiobook,
https://aclanthology.org/2025.acl-short.81.pdf; its words a minute read as syllables). No study measures vlog speech
directly. English 2.0–3.5 words a second (150 wpm common, 210 measured for one creator); Chinese 3–4 characters a
second.

A line that does not fit: cut or split its job, or move it to another window. **Never speed the voice up to fit**
(T02 §4); a mild stretch up to about 1.1× only after rewriting failed, slow-down 0.82–0.95× (T10 §3). 0.3–1 s of
silence at a line end is often right (T10 §7).

## 5. The script as beats

One row per beat, section by section:

| Beat | Section | Owner | Window and budget | Line (as heard) | Job | ON SCREEN | Source |
|---|---|---|---|---|---|---|---|
| b1 | hook | VO | 0–2.4 s, ~9 syllables | "Hai ngày Đà Lạt, hết bao nhiêu?" | claim (promise) | the pull at 120 fps + hook title | — |
| b4 | place 2 | real speech | C0031 0:40–0:46 | (the seller's line) | context | the seller, price board | C0031 0:41 |
| b5 | place 2 | VO | 3.1 s, ~12 syllables | "Bốn lăm nghìn một tô, rẻ nhất chuyến đi." | interpretation | `vlog-price-tag` "45K" | price board, C0033 0:02 |

- **Job** per line: context, causal link, foreshadow, interpretation, transition, claim, CTA. A line without a job is
  deleted (T02 §4).
- **ON SCREEN**: what the picture shows while it is said, and any text. Text repeats the key word or number, never
  the whole sentence; captions or a card carry a line, not both (T13 §4).
- **Source** for every fact (number, price, name, place, superlative): a frame of the footage, the user, or a link
  with its date. No source: cut the claim or ask (T02 §4).
- One fact or feeling per sentence; numbers as said ("bốn lăm nghìn"), digits on screen. Write for the ear: one
  continuous thought per beat; split for captions afterwards.

## 6. Counterfactual review

Before showing the script (T02 §4):

1. **Delete each beat** in your head: if the story still works, cut it.
2. **Mute the voiceover**: does the picture still tell it? Lines that only describe the picture go.
3. **Audio only**: does it make sense without the picture?
4. **Quote the weakest line exactly** and fix or remove it. Check `promise.hook` against the last beat.

After the rough cut, check the pair on the edit (opening and close words and titles): the close must answer the
opening; if the cut changed either end, update `promise` with a reason.

## 7. Into the plan, then the script gate

Write `beats` [{id, section, text, job, onScreen, treatment?, source}] (text = exact words heard; treatment, when
clear, one of bc:visual-plan's names) and the `promise` into the plan (`--merge`); `bc:visual-plan` turns them into
`plan.visuals`. Show the hook options, story options and script, then request G4 before any voice is made. After
voiceover and editing, `script check` shows per beat how much was heard as written: fix the beats or the edit, not
the measurement. `bc:voiceover` makes the voice; place the take whose `unitsPerSecond` is closest to the rate you
sized for.

## On-screen text and CTA

- Captions per the recipe's caption range (`bc:captions-text`); titles and cards from the vlog pack (`library list
  --pack Vlog --tag hook|section|price|cta`).
- CTA: one action (save, follow, comment a question, buy), held 1–6 s by platform and CTA (T07 §3). Examples, not
  rules: Shorts and TikTok often "follow", Reels "lưu lại", YouTube "xem video tiếp theo".
- Labels and sponsorship: `bashcut.vlog:plan` §4 (nothing AI, stock or effect labelled; sponsorship said early with
  `vlog-disclosure` in the user's wording).
