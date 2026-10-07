---
name: publish
description: Finish a vlog in BashCut for posting — one export per output platform of the project, a separate cut when another platform needs another frame or a shorter length, a cover frame, and the post caption with hashtags per platform. Use when the edit passed review and the user wants to post it, export for TikTok, Reels, Shorts or YouTube, or needs a caption, hashtags or a thumbnail. Triggers: "xuất video", "đăng TikTok", "đăng Reels", "đăng Shorts", "đăng YouTube", "caption đăng bài", "hashtag", "thumbnail", "ảnh bìa", "xuất nhiều bản".
---

# Publish

Reply in the user's language. The project lists what it is made for in `output.presets` (`project get`); the first
one is the platform the review checked.

## Before exporting

The review must pass with the measured picture and loudness (`bc:edit-workflow`, "Review before export"): no error.
Loudness is measured from a normalized export, so the last draft is exported with `--normalize-audio`.

## One export per output

```sh
bashcut export start --preset reels --name market-vlog-reels --normalize-audio --include-srt
bashcut export status
```

- Outputs of the **same shape** (Reels, TikTok, Shorts): one export each with its preset; the picture is the same,
  only the name and the target change. Check the edit fits the strictest one first: Reels' caption bar is the tallest
  (20 %), Reels and Shorts take at most 3 minutes.
- Another **shape** (a YouTube 16:9 version of a vertical edit) or a **shorter** cut: a separate edit. Save, copy the
  project folder (`<name>-youtube`), open the copy, `project format --canvas landscape`, set its `output.presets`,
  reframe and re-place text, review again, export. Never squeeze one edit into both shapes.

## Cover frame

Pick the frame with the hook's subject and the hook text readable (`ui frame F`, read the PNG). Report its frame
number and time so the user can choose it as the cover in the app they post to. YouTube: suggest a separate thumbnail
with 3–5 big words; it is not made in BashCut yet.

## Post caption and hashtags

| Platform | Caption | Hashtags |
|---|---|---|
| TikTok | hook line + one detail + question for comments, ≤150 characters | 3–5: topic, place, format (#dalat #reviewdoan #vlogdulich) |
| Reels | hook line, 2–3 short lines, CTA "lưu lại" | 3–8 |
| Shorts | the title is the hook (≤60 characters) | 2–3 in the title or description, #shorts optional |
| YouTube | title ≤60 characters with the number or question; description with sections and timestamps from the section markers | 3 in the description |

Write them in the video's language; never invent facts the video does not show (prices, addresses).
