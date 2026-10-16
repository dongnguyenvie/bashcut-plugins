# Translate Captions

Vietsub and other caption translations for a BashCut edit, with the user's own key.

- **Translate captions…** (Tools panel, Plugins menu): every caption on the caption layers is translated into one of 12
  languages (Vietnamese by default) and keeps its timing, style and word style; old word timings are dropped. Lines
  go in batches of 40 with their on-screen seconds and a character budget (`maxCps`, default 17), the three lines
  before the batch, the project brief, and a glossary of names and terms. A line the service leaves out is asked
  again once; one that still has no translation is kept and reported.
- **Cover burned-in subtitles…**: on-screen text reading (`media.ocr`) over the first 30 seconds of each video on
  Main finds subtitles (centred lines whose text changes) apart from fixed text (logos, signs). They are hidden by an
  opaque band on the Overlay layer, with the captions moved onto it, or by zooming them out of the frame when 1.12×
  is enough. Options: extra lines above (for a blurred strip), band opacity, and covering fixed text and logos (off by
  default; only for footage you have the rights to).
- **Add the Vietsub TikTok batch preset**: saves `presets/vietsub-tiktok.json` to BashCut's batch presets: import,
  captions of the spoken language, caption style, cover, translate to Vietnamese, review checks, TikTok and Shorts
  exports.
- **Services:** Google Gemini (`gemini-2.5-flash` by default) or OpenAI (`gpt-4.1-mini` by default). The **Endpoint**
  option points the OpenAI mode at any server with `/v1/chat/completions`, such as a local model (no key needed on
  127.0.0.1 or localhost).
- **No key:** the action says to ask the agent; the plugin's skill tells Claude Code, Codex or the AI Editor how to
  translate the captions itself (`captions export` → `timeline apply`).

Plugin id `bashcut.translate-captions`, written in Swift (Foundation, CoreGraphics, ImageIO); nothing to install.
Needs BashCut with plugin API 10 or later (the Tools panel).

## Files

- `bin/provider`: the entrypoint BashCut runs, built by `build.sh` (not in git)
- `build.sh`: builds `bin/provider` (universal binary) from `src/`; not shipped
- `plugin.json`: manifest: options (service, key, model, endpoint) and the three actions
- `presets/vietsub-tiktok.json`: the batch pipeline the third action saves
- `skills/translate-captions/SKILL.md`: the agent skill, including translating without a key
- `src/Handlers.swift`: dispatch and shared request helpers
- `src/Translate.swift`: batching, instructions and the two services
- `src/Cover.swift`: finding burned-in subtitles and covering them
- `src/Preset.swift`: saving the batch preset
- `src/main.swift`: the protocol (requests, responses, progress, host calls)
- `tests/test_plugin.py`: runs the entrypoint like BashCut, with host calls answered by fixtures and a mock
  OpenAI-compatible server on 127.0.0.1; not shipped

## Test

```sh
./build.sh
python3 -m unittest discover -s tests -v
```

The tests never use a real key or the network.
