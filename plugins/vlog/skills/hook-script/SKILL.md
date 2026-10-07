---
name: hook-script
description: Write the words of a vlog in BashCut — the hook line and hook title (a number or a question in the first 1–3 s), the voiceover or talking script section by section at a speakable pace, on-screen text and the CTA, timed to the recipe's structure. Use when a vlog needs a hook, a voiceover script, titles or captions written (not transcribed), or the user says the opening is boring. Triggers: "viết hook", "câu mở đầu", "mở đầu nhàm", "viết kịch bản", "viết lời thoại", "viết lời đọc", "script vlog", "tiêu đề video", "caption trên video", "CTA".
---

# Hook and script

Reply in the user's language; write the viewer-facing words in the video's language (`contentLanguage` in
`project get`). Use the structure of the active recipe (`recipe.skill` in `project get`, see `bashcut.vlog:plan`).

## The hook (first 1–3 s)

One line on screen (`vlog-hook-question`, hook-title preset) and, if someone speaks, the same idea said. It needs a
**concrete number or a question**, about what the viewer gets — the review flags an opening without either.

| Pattern | Example |
|---|---|
| cost / time + question | "48H Ở ĐÀ LẠT HẾT BAO NHIÊU?" |
| result first | "VIDEO NÀY DO AI DỰNG TRONG 5 PHÚT" |
| verdict as question | "3 TRIỆU CÓ ĐÁNG?" |
| number of things | "5 QUÁN PHẢI ĂN Ở QUẬN 4" |
| surprise / contrast | "QUÁN VỈA HÈ NGON HƠN NHÀ HÀNG?" |

Write 3 options, pick the one that matches the best shot of the footage, keep it under 8 words on screen. Never open
with a greeting or "hôm nay mình…".

## The script

- Section by section from the recipe, each with its length. Speakable pace: 165–235 Vietnamese syllables a minute
  (about 3–4 syllables a second); a 7 s section holds about 20–25 syllables. Count, do not guess.
- One fact or feeling per sentence; numbers as the viewer would say them ("bốn lăm nghìn").
- Real speech first: when the footage has the person talking, cut from their lines (`captions generate`, then read
  `captions export`); write voiceover only for what is missing (`bc:voiceover` produces it).
- Text on screen repeats the key word or number of the line, never the whole sentence.

## On-screen text and CTA

- Captions 3–6 words a line (`bc:captions-text`); titles and cards from the vlog pack (`library list --tag hook`,
  `--tag section`, `--tag price`, `--tag cta`).
- CTA: one action only (save, follow, comment a question, buy), 1–3 s at the end; match the platform (Shorts and
  TikTok: "follow"; Reels: "lưu lại"; YouTube: "xem video tiếp theo").
- AI-made pictures or voices, sponsorship: add `vlog-disclosure` with the right wording.

Show the hook options and the script to the user before producing voiceover.
