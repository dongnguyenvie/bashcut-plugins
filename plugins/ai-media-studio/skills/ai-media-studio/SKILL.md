---
name: ai-media-studio
description: Generate Vibi voiceover, browse ElevenLabs/MiniMax/CapCut voices, remove visible Gemini/Veo watermarks, or build a BashCut timeline from scenes.json, images, voice and SRT. Use when the user explicitly requests these tools.
---

# AI Media Studio

Plugin: `bashcut.ai-media-studio`, API 8. Read `plugins list`, `plugins health` and `context get` first. A saved project must be open. Trust and dependency installation are approved by the user in BashCut; never approve them through automation.

## Vibi speech

The user enters a Vibi API key once in the plugin options; BashCut stores it in Keychain. Never request a key in chat, log it or print option values. API requests and voice generation need internet access and Vibi credits.

Use the Voices dock tab to choose a default voice. The choice is stored in plugin data because API 8 cannot set its own options; it takes precedence over the Voice ID / provider options. Models, speed, stability, similarity, pitch, MiniMax volume and the SRT switch remain native plugin options. Language comes from the project's content language.

```sh
bashcut voice speak "Xin chào" --provider bashcut.ai-media-studio.vibi --takes 1 --keep-takes
bashcut plugins run bashcut.ai-media-studio.speak --params '{"text":"Xin chào","takes":1}'
bashcut plugins run bashcut.ai-media-studio.credits
```

The default paid-take limit is 1. An oversized take count fails before any paid call; do not repeatedly retry. Increasing `maxTakes` permits at most 3 paid takes. Speech splits at 3500 characters, polls for up to 180 seconds per part and concatenates the parts with bundled ffmpeg. SRT files sit beside the generated audio. Use Studio's **Import last SRT captions** or `captions import` to import them. Voice previews use downloaded samples and spend no TTS credits.

## Visible watermarks

Choose the watermark action on project media for a before/after sheet, or use a file action:

```sh
bashcut plugins run bashcut.ai-media-studio.clean-image-file --params '{"path":"/absolute/source.png","mode":"auto","preview":true}'
bashcut plugins run bashcut.ai-media-studio.clean-image-file --params '{"path":"/absolute/source.png","mode":"classic","preview":false}'
bashcut plugins run bashcut.ai-media-studio.clean-video-file --params '{"path":"/absolute/source.mp4","mode":"veo3","preview":true}'
```

Image modes: auto / classic. Video modes: veo3 (small text) / gemini (star). Scale 0 and blank offsets use the defaults. After changing settings, preview again before Save. Video execution has native user confirmation and can take minutes. Progress is available through `jobs status`, cancellation through `jobs cancel`. Originals remain intact; clean files are registered in project media. This removes the visible corner overlay; it does not remove invisible SynthID.

## Scenes to timeline

```sh
bashcut plugins run bashcut.ai-media-studio.build-timeline --params '{"scenes":"/absolute/scenes.json","images":"/absolute/images","audio":"/absolute/voice.mp3","srt":"/absolute/voice.srt","dryRun":true}'
```

Review missing images, duration and motion warnings. Then use the Build timeline sheet or repeat the action with `dryRun:false`. The main video layer must be empty. No files are imported and no timeline edits occur during preview.

Strict scripts contain ordered fields: id (SC01, SC02…), character, character_info, prompt, subtitle_ids, start_at, end_at; optional motion. Start at zero, use contiguous HH:MM:SS,mmm cuts and end the final scene with AUDIO_END. Legacy subtitle mappings and version-1 edit documents are also supported. Clean images are preferred. Missing images, invalid captions and stale revisions stop the build.

One validated edit adds scene images, motion keyframes, voiceover and captions; one Undo removes the complete build. Drift maps to subtle pan. Shake stays still with a warning. Export with BashCut.
