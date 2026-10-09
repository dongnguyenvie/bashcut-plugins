---
name: publish
description: Finish a vlog in BashCut for posting — read each output's platform facts (platforms get: length, bit rate, title limits, cover aspect, chapter and disclosure rules, each with its source), one export per output with its caption mode, a separate cut for another shape, cover candidates checked at phone size (export cover, then look), YouTube chapters from section markers (export chapters), and the post title, caption and hashtags sized from data plus sourced ranges. Use when the edit passed review and the user wants to post it, export for TikTok, Reels, Shorts or YouTube, or needs a title, caption, hashtags, chapters or a cover. Triggers: "xuất video", "đăng TikTok", "đăng Reels", "đăng Shorts", "đăng YouTube", "caption đăng bài", "hashtag", "thumbnail", "ảnh bìa", "chương YouTube", "xuất nhiều bản".
---

# Publish

Reply in the user's language. The project lists what it is made for in `output.presets` (`bashcut project get`); the
first one is the primary platform. Platform facts are **data with a source and a date**, not numbers to remember:
read them for every output, and when a fact is missing from the data, say so instead of filling it in (T17 §4).

## 1. Read the platform facts

`bashcut platforms get <id>` for each output (`tiktok`, `reels`, `shorts`, `youtube`; `bashcut platforms get --facts`
for all at once). Every field is `{value, kind hard|recommended|info, source, checked, confidence}`:

| Fact | Use it for |
|---|---|
| `maxSeconds` | the hard length limit; the only length rule |
| `shape`, `safeArea.*` | the frame and where the app's interface covers it (review already checks them) |
| `targetLUFS`, `maxTruePeakDbTP` | the export's loudness target (`--normalize-audio` uses it) |
| `bitrateMbps` | the platform's recompression line; vertical presets already export under it |
| `title.maxChars`, `title.visibleChars` | the hard title cap and how much shows before it is cut (where the data has them) |
| `cover.aspect` | the cover or thumbnail shape `export cover` writes |
| `chapters` | the chapter rule `export chapters` checks |
| `disclosure` | the platform's rule for AI-made or altered content (its upload toggle) |

A `hard` fact is a limit; a `recommended` one is a sourced default you may leave with a reason; `info` is context.
Quote the source when you tell the user a limit.

## 2. Before exporting

The review must pass with the measured picture and loudness (`bc:edit-workflow`, "Review before export"): no error.
Loudness is measured from a normalized export, so the last draft is exported with `--normalize-audio`. Request the
draft gate: `bashcut checkpoint request G5 --summary "<length, outputs, what was left on purpose>"`, poll `bashcut
checkpoint status`.

**Length**: the moment sets it; `maxSeconds` caps it. **Never trim to a "sweet spot"**: published sweet spots
contradict each other (Shorts 30–45 s in one source, "avoid 30–45 s" in another; TikTok 21–34 s or 15–30 s; T17 §3).
Mention one only as context when the user asks, with its source.

## 3. One export per output

Captions per output: `output.captions` maps a preset to `{mode burn|sidecar|both|none, format srt|vtt, track}`. Set it
when the outputs need different handling (vertical apps usually burned in; YouTube landscape often a sidecar file the
viewer can switch off, T09 §7), with one `setProjectProperties` edit (`bashcut timeline apply`), then export:

```sh
bashcut export start --preset reels --name market-vlog-reels --normalize-audio
bashcut export status
```

- Outputs of the **same shape** (Reels, TikTok, Shorts): one export each with its preset; the picture is the same,
  only the name, the target and the bit rate change. Check the edit fits the strictest output first: review checks
  every output's safe zones and `maxSeconds`.
- Another **shape** (a YouTube 16:9 version of a vertical edit, a 4:5 feed version) or a **shorter** cut: a separate
  edit. Save, copy the project folder (`<name>-youtube`), open the copy, `bashcut project format --canvas landscape
  --base-rev N`, set its `output.presets`, reframe and re-place text, review again, export. Never squeeze one edit into
  both shapes (T17 §4).
- `--bitrate` only for a measured reason; `export status` reports the bit rate written and the delivered file's
  checks.

## 4. Cover

1. Pick 2–3 candidate frames from real frames: `bashcut timeline sheet` (or `--text` to see frames with text), the
   hook's subject large, the hook text readable, no fake interface (T17 §4).
2. Write each candidate at the outputs' cover aspects: `bashcut export cover <frame>` (each output's `cover.aspect`,
   else its shape); `--aspect 16:9,9:16` to choose.
3. **Look at phone size**: `bashcut export cover <frame> --size 320` and read the PNGs. A cover is chosen at about
   320 px wide in a grid: the text must still read and be at least about 1/8 of the frame's height; 3–5 big words,
   fewer is often better (T17 §3: guizang tests at 320 px; ≤3 words in another source).
4. Report the chosen frame number and time, and the files in `render/`. The user sets the cover in the app they post
   to; YouTube takes the 16:9 still as a custom thumbnail.

## 5. Chapters (YouTube)

`bashcut export chapters --platform youtube` lists chapters from the section markers and checks each rule of the
platform's `chapters` fact (first at 00:00, the least count, the shortest chapter). Fix a failing rule in the edit's
markers (rename, merge a short section), not in the text. `--write` saves `render/chapters-youtube.txt` for the
description.

## 6. Title, caption and hashtags

Write them in the video's language. Hard caps come from the data; style is a sourced range you choose inside.

| Item | From the data | Sample range (style) | Why it varies |
|---|---|---|---|
| YouTube / Shorts title | `title.maxChars` (hard), `title.visibleChars` | the number or question of the hook in the visible part; about 40 characters show on mobile, 60 on desktop (T17 §3) | the device most viewers use |
| TikTok / Reels caption | no cap in the platform data yet: check the app | the hook line, one detail, a question or CTA; front-load it, the feed shows only the first line or two | where the "more" cut falls in each app |
| Hashtags | not in the data | TikTok 3–5, Reels 3–8 (earlier vlog practice, T17 §3); YouTube tags 5–12 (T17 §3) | topic, place, format; a niche needs fewer, broader ones |
| YouTube description | — | the sections with chapter times from `export chapters`, sources and credits | — |

- Only claims with a source: prices, addresses, names and numbers the video shows or the brief sources (T01 §7). Never
  invent facts.
- Disclosure: never burn an AI, stock or "minh hoạ" label into the video; it makes it feel unnatural. When
  generated shots or voices are placed, read the platform's `disclosure` fact and tell the user in the summary to
  switch on the platform's own AI label at upload. A sponsored video says so in the first seconds with
  `vlog-disclosure`, in the user's wording.
- Credits: licensed music and stock as their licenses ask.

Report: per output the file, length, bit rate and loudness from `export status`; the cover files and frame; the
chapter list and any rule it fails; the title, caption and hashtags per platform; and which facts came from data
(with their `checked` date) and which are ranges you chose.
