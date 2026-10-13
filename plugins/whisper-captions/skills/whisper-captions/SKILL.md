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
4. `dropDoubtful` (user scope, on by default) leaves out text Whisper likely invented over music or ambient sound
   ("Thank you.", "We're back." on a quiet shot). A segment is left out when a measured score passes a threshold:
   `minAvgLogprob` (default -1.0; clear speech is about -0.5 to -0.1, invented text -2 to -6; useful -1.5 to -0.8),
   `maxCompressionRatio` (default 2.4, text repeating itself; useful 2.2 to 2.8) or `maxNoSpeechProb` (default 0.8,
   useful 0.6 to 0.9; ignored with large-v3 turbo, which always reports 0). These are starting points, not verdicts:
   when real but noisy or accented speech goes missing, lower `minAvgLogprob` (for example -1.4) or turn the filter
   off for that media; when invented lines still appear over music, raise it toward -0.8.

## Transcribe

1. `bashcut media list` to find the media that has the speech.
2. `bashcut captions generate --media <id>` (add `--replace` to redo that media's captions, `--from`/`--to` in source
   seconds for one part, `--word-style highlight|karaoke|reveal` for words as they are spoken). It is a background
   job: poll `bashcut jobs status` until it finishes.
3. When several transcribers are installed, `--provider bashcut.whisper-captions.local` picks this one.
4. To read what was said before placing anything, `bashcut media transcribe --media <id>` (a job) keeps the whole
   file's transcript, and `bashcut media transcript --media <id> --as text --format text` reads it. Each word
   carries Whisper's `confidence`; `noSpeechProb` only when the model really measured it (`precision.noSpeechProb`
   is false with large-v3 turbo: do not read silence from it). `captions generate` places captions from it
   without transcribing again; after changing `vocabulary`, add `--fresh` (or `media transcribe --force`).

## Check

- Read the captions with `bashcut timeline get --format text` and look for misspelled names. Add them to
  `vocabulary` and run again with `--replace --fresh`, rather than fixing many captions by hand. Words with a low
  `confidence` in `media transcript --as words` are the ones to check first.
- Look at one frame with `bashcut ui frame <frame>` to confirm the captions fit the safe area.

## When it fails

- "Install Dependencies…" in Plugins: the model and its Python are not installed yet (about 1.9 GB). Only the user
  can approve that; tell them, and do not retry until they have.
- Silent or music-only media gives no captions: say so instead of retrying. When the error says doubtful segments
  were left out and the user hears speech there, run again with `dropDoubtful` off or a lower `minAvgLogprob`.
