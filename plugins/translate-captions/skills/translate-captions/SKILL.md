---
name: translate-captions
description: Translate a project's captions into another language while keeping their timing and look, cover subtitles already burned into the footage, and run the Vietsub TikTok batch. Use when the user wants Vietsub, subtitles in another language, a foreign clip re-captioned, or old subtitles hidden. Triggers: "vietsub", "dịch phụ đề", "dịch sub", "phụ đề tiếng Việt", "che phụ đề cũ", "che sub cũ", "translate captions".
---

# Translate Captions

Plugin `bashcut.translate-captions` adds three actions (Tools panel and Plugins menu):

- `bashcut.translate-captions.translate`: translates every caption on the caption layers with the user's own Gemini
  or OpenAI key (or an OpenAI-compatible server on this Mac). Timing, style and word style stay; word timings are
  dropped, so words are spread over each caption.
- `bashcut.translate-captions.cover`: looks at the first seconds of each video on Main for subtitles burned into the
  picture and hides them, then moves the captions onto the cover.
- `bashcut.translate-captions.install-preset`: saves the "Vietsub TikTok" batch preset.

## Vietsub one clip

1. Captions of what is said first: `bashcut captions generate --media <id>` (a job). Whisper detects the spoken
   language when the project has none; check the words with the whisper-captions skill.
2. Hide the old subtitles before styling: `bashcut plugins run bashcut.translate-captions.cover --params
   '{"mode": "auto"}'` (a job). `data.videos[].subtitles` says what was found (box as shares of the picture, line
   height, lines, examples); `fixedText` lists text that never changes (a channel name, a sign), which is never
   treated as a subtitle. Modes: `auto` (zoom when 1.12× is enough, else a band), `band`, `zoom` (up to 1.2×),
   `detect` (report only). `extraLinesAbove` (0–4) grows the band over a blurred strip or a second subtitle row above
   the found one. `coverLogos` also boxes fixed text; use it only on footage the user has the rights to, and say so.
   Run it again to replace the earlier cover.
3. Translate: `bashcut plugins run bashcut.translate-captions.translate --params '{"target": "vi", "glossary":
   "Manman; grizzly = gấu xám"}'` (a job). Put names of people, places and brands from the brief in `glossary`
   (`term` keeps it, `term = translation` forces one). `tone` is natural, casual or formal; `maxCps` (default 17)
   asks for shorter lines. `data.tooFast` counts lines still faster than that.
4. Look at the result: `bashcut ui frame <frame> --phone` on a few lines, and `bashcut review run`.

## Without an API key: translate yourself

When the action fails with `no_key`, the user has not added a key (Settings › Plugins › Translate Captions; only the
user can, it goes to the Keychain). Offer to translate the captions yourself instead:

1. `bashcut captions export --as json`: `revision`, and per cue `item`, `seconds`, `text`.
2. Translate each cue on its own, in order, using its neighbours for meaning: the same number of lines, nothing merged
   or split, names as in the brief, numbers as digits, at most about 17 characters per second of the cue (say it
   shorter rather than cramming), no quotes or notes.
3. Apply all of them as one edit, dropping the old word timings:
   `bashcut timeline apply ops.json --base-rev <revision> --label "Translate captions to Vietnamese"` with
   `[{"op": "setProperties", "item": "<item>", "patch": {"text": "<translation>", "words": null}}, …]`.
4. Check as in step 4 above.

## Many clips: the Vietsub TikTok batch

`bashcut plugins run bashcut.translate-captions.install-preset` saves the preset (once). Then
`bashcut batch run --preset "Vietsub TikTok" --inputs <clip1>,<clip2>,…` (the user approves the batch once in the app;
follow it with `bashcut batch status --wait 110`). Each clip becomes a portrait project: import and place, captions
of the spoken language, caption style, cover, translate to Vietnamese, review checks, a TikTok and a Shorts export.
The translate step needs the key: without one those items stop at that step; translate them yourself as above and
export with `bashcut export start --presets tiktok,shorts`.

Caption look: Whisper captions come in the system font, regular weight, which sinks into a busy picture. Restyle
them like the usual drama subtitle, bold italic with a thin outline (the batch preset does this):
`bashcut captions style style.json --base-rev last` with
`{"font": "AvenirNext-HeavyItalic", "size": 0.052, "fill": "#FFFFFF", "stroke": "#000000", "strokeWidth": 4}`.
An outline above about 6 fills the letters in at this size.

## Limits

- Burned-in subtitles are found with on-screen text reading (Apple Vision): stylised or very small text, or
  subtitles only after the first `seconds` (default 30), can be missed. Report what `data.videos` says.
- The band is opaque by default: BashCut blends in linear light, so a band below about 0.97 opacity lets white
  subtitles show through.
- The cover follows a clip's zoom, pan and tilt but not keyframed motion; check moving shots.
- Translation quality is the service's: read the translated captions before exporting, and fix names with
  `bashcut captions replace`.
