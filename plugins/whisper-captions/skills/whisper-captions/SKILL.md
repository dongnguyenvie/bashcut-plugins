---
name: whisper-captions
description: Transcribe speech into captions with the local Whisper plugin, spell names right with its vocabulary option, and check the result. Use when the user wants captions or subtitles from what is said, or when Whisper captions have wrong names or lines that are too long. Triggers: "phụ đề", "tạo sub", "nhận giọng nói", "whisper", "sai tên riêng".
---

# Whisper captions

Whisper Captions provides `captions.transcribe` on this Mac (Whisper large-v3 turbo, MLX). Nothing leaves the Mac.
The bc:captions-text skill covers caption style and placement; this one covers getting the words right.

## Before transcribing

1. Place the clips on the timeline first: captions follow the clips where the media is heard.
2. Put the names and terms of this video in the `vocabulary` option (project scope, comma separated, up to 500
   characters), for example places and people the user mentioned:
   `bashcut plugins option bashcut.whisper-captions --option vocabulary --value "Buôn Đôn, Buôn Ma Thuột"`.
3. `maxCharacters` (user scope, 16–84, default 42) splits long sentences. Leave it unless the user asks for shorter
   or longer lines; vertical video reads better around 32.

## Transcribe

1. `bashcut media list` to find the media that has the speech.
2. `bashcut captions generate --media <id>` (add `--replace` to redo that media's captions, `--from`/`--to` in source
   seconds for one part, `--word-style highlight|karaoke|reveal` for words as they are spoken). It is a background
   job: poll `bashcut jobs status` until it finishes.
3. When several transcribers are installed, `--provider bashcut.whisper-captions.local` picks this one.

## Check

- Read the captions with `bashcut timeline get --format text` and look for misspelled names. Add them to
  `vocabulary` and run again with `--replace`, rather than fixing many captions by hand.
- Look at one frame with `bashcut ui frame <frame>` to confirm the captions fit the safe area.

## When it fails

- "Install Dependencies…" in Plugins: the model and its Python are not installed yet (about 1.9 GB). Only the user
  can approve that; tell them, and do not retry until they have.
- Silent or music-only media gives no captions: say so instead of retrying.
