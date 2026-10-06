# AI Media Studio

A BashCut plugin implementing the Vibi voiceover, voice library, visible Gemini/Imagen image and Veo/Gemini video watermark tools, and scene-script workflow from [Editor-AI-App](https://github.com/Akai1Shuichi/Editor-AI-App). BashCut owns projects, editable timelines, captions, rendering and export. No PyQt application is embedded.

Version **0.0.1**, plugin **bashcut.ai-media-studio**, provider **bashcut.ai-media-studio.vibi**. Requires **plugin API 8** with panel, dock, sheet, imageCompare and audio support. Older BashCut builds list the plugin as outdated. The proposed layout from the implementation plan is used: Studio in the left rail, Voices in the right dock, and Watermark check / Build timeline in sheets.

## Install for development

From the registry repository:

```sh
scripts/dev-link.sh ai-media-studio
```

In an API 8 BashCut build, open Plugins, choose **Trust**, then **Install Dependencies**. The install recipe downloads uv, a private Python 3.12, numpy, Pillow, requests, certifi and imageio-ffmpeg (including ffmpeg). Users need neither Homebrew nor system Python. BashCut's native approval is required for Trust and dependency installation.

Enter the Vibi API key in **Options**. This is a `secret` option held in the Keychain. Credentials are never stored in the plugin's preference file, view state or results. Network errors never include raw HTTP responses, request headers or signed download URLs. API authentication uses `xi-api-key` only against `https://api.vibi.pro`; media downloads carry no API key.

## Studio and Vibi Voices

Open **Vibi Voices** in the dock and click **Load voices**. Sources include community, ElevenLabs default/shared, MiniMax system/cloned, and CapCut. Filter by search, language or gender; navigate pages of up to 100 voices. **Preview** downloads a sample into the plugin cache; **Use** chooses the default voice; **Favorite** remembers a row. The chosen voice is saved in `BASHCUT_PLUGIN_DATA` and takes precedence over the Voice ID / provider options. This is the API 8 workaround for the host not permitting plugins to set their own options.

Choose model and voice settings in the native options. MiniMax maps ISO language codes to full names and uses speed/pitch/volume; ElevenLabs uses speed/stability/similarity; CapCut uses speed/pitch without a model ID. If switching provider leaves a model belonging to another provider, the first model for the new provider is used. Speech uses the open project's content language. Studio generates one take and offers audio playback and **Import last SRT captions** when **Request SRT transcript** is enabled. Credit balance refreshes only when requested.

```sh
bashcut voice speak "Xin chào" --provider bashcut.ai-media-studio.vibi --takes 1 --keep-takes
bashcut plugins run bashcut.ai-media-studio.speak --params '{"text":"Xin chào","takes":1}'
bashcut plugins run bashcut.ai-media-studio.credits
```

**Paid-take guard:** `maxTakes` defaults to 1, with a maximum of 3. Set the Voice panel / CLI take count to 1. Larger requests fail before checking the account or sending paid synthesis tasks; the plugin does not silently return fewer takes and cause BashCut to charge for repeated requests. Long text splits at sentence boundaries where possible, with a hard limit of 3500 characters per part. Each task polls every 1.5 seconds for up to 180 seconds. Generated parts are concatenated into one MP3 per take; SRT cue times are offset by each preceding part's measured duration. A requested but missing transcript fails visibly. Progress continues while Vibi is processing. Cancel stops local polling/downloads; Vibi may still bill a task already submitted.

## Watermark check

On image or video project media, use **Remove Gemini image watermark…** or **Remove Veo / Gemini video watermark…**. A comparison sheet shows the original versus cleaned preview. Choose mode and optional mask scale/offset, click **Preview** after any changes, then **Save to project**. Video actions require native confirmation and report progress. Results are new files in the project's generated plugin output folder, registered with an `addMedia` operation. Originals are never replaced.

File actions also work without selecting project media:

```sh
bashcut plugins run bashcut.ai-media-studio.clean-image-file --params '{"path":"/absolute/image.png","mode":"auto","preview":true}'
bashcut plugins run bashcut.ai-media-studio.clean-image-file --params '{"path":"/absolute/image.png","mode":"classic","preview":false}'
bashcut plugins run bashcut.ai-media-studio.clean-video-file --params '{"path":"/absolute/video.mp4","mode":"veo3","preview":false}'
```

Image modes are `auto` and `classic`, preserving PNG alpha. Video modes are `veo3` for the small text overlay and `gemini` for the star. Scale 0 and blank offset fields mean the source algorithm's defaults. Video is decoded to RGB, processed with numpy and encoded with libx264 CRF 16; audio is copied. Input audio must be compatible with MP4. Variable-frame-rate footage is output at the probed constant frame rate. The Gemini seam healing is vectorized and matches the reference pixel algorithm. These masks remove the visible corner overlay; invisible SynthID is outside this plugin's scope.

## Build timeline

Open the Build timeline sheet from Studio, enter the four input paths, and click **Preview / dry run**. The native action's file parameters also provide file pickers. Strict scripts follow [examples/scenes.json](examples/scenes.json): sequential SC IDs, ordered required fields, contiguous SRT timestamps starting at zero, optional motion, and final `end_at: "AUDIO_END"`. Legacy subtitle mappings and version-1 edit documents are accepted. Image matching keeps the reference's scene-prefix, numeric and index fallbacks, deterministically preferring clean versions.

```sh
bashcut plugins run bashcut.ai-media-studio.build-timeline --params '{"scenes":"/absolute/scenes.json","images":"/absolute/images","audio":"/absolute/voice.mp3","srt":"/absolute/voice.srt","dryRun":true}'
```

Review the duration, missing images and motion warnings. **Build timeline**, or the same CLI action with `dryRun:false`, commits the edit. An empty main video layer is required; existing work is never replaced. Every source must exist, all scenes must fit the audio, and captions must have valid timing. Build refuses inputs or project revisions changed after preview.

Media metadata, clips, voiceover, captions and native motion keyframes are included in **one `timeline.apply`**. This deliberately improves on the plan's successive `media.import`, `clip.motion` and `captions.import` calls, which would each create separate undo entries. Both preview and commit use BashCut's validation; one Undo removes the complete build. Dynamic layer IDs and rational project FPS are read from the host. Overlapping captions get separate text layers. The plugin preserves subtle/medium zoom and pan strength through keyframes; drift maps to subtle pan, and shake remains still with a warning. Export using BashCut.

## Tests and packaging

Tests use generated media, fake host sessions, mocked HTTP and `VIBI_FAKE=1`; they never contact the real Vibi API. A dedicated CI workflow installs the test runtime and runs the complete suite. Repository-wide tests can skip optional media tests when those dependencies are absent.

```sh
uv venv --python 3.12 /tmp/studio-tests
uv pip install --python /tmp/studio-tests/bin/python -r plugins/ai-media-studio/requirements.txt
PYTHONDONTWRITEBYTECODE=1 /tmp/studio-tests/bin/python -B -m unittest discover -s plugins/ai-media-studio/tests -v
python3 scripts/package.py ai-media-studio
python3 scripts/build-registry.py --check
```

Generate a complete sample input folder with the test Python:

```sh
/tmp/studio-tests/bin/python examples/generate.py /tmp/studio-demo
```

`VIBI_FAKE=1` is for a directly launched test provider; production requests do not enable fake mode from UI options. The protocol reader continues handling overlapping requests and cancellation while workers perform network calls or wait for host results, including when Studio calls its own voice provider through `voice.speak`. Output is newline-delimited JSON only. Python bytecode writing is disabled to avoid changing the trusted bundle at runtime.

All state lives in `BASHCUT_PLUGIN_DATA`; previews, thumbnails and review plans live in `BASHCUT_PLUGIN_CACHE`. Generated takes and clean outputs live inside the project. No Downloads directory is created.

## Validation status (2026-10-07)

- 40 Python tests pass with the private Python 3.12 runtime; no real Vibi calls or credits spent.
- Current upstream API 8 Swift `PluginManifest.validate` accepts the manifest. The native `Project.applying` engine validates a generated scene edit with new voice/caption layers and overlapping captions, and one inverse edit restores all original tracks and media.
- A generated 10-second, 1920×1080, 30 fps clip (300 frames) cleaned in **4.292 seconds** on this arm64 Mac, with bundled ffmpeg and Veo mode. This is one generated-media benchmark, not a guarantee for other footage or machines.
- Registry and archive packaging checks pass. `versions.json` intentionally has no published release; the generated registry stays unchanged.
- Connected development BashCut currently reports API 6, so native UI interaction, screenshots and live end-to-end API 8 acceptance remain unverified. Live paid synthesis also needs the user's API key.

## Provenance

Core algorithms and masks are adapted from Editor-AI-App at the commit recorded in [NOTICE](NOTICE). The Veo text mask retains Frédéric Guigand's MIT notice in full. The reference repository has no top-level license file at that commit; this plugin's notice does not relicense that code. Resolve distribution licensing before a registry release.

To repeat the optional native edit/undo check against a current API 8 BashCut checkout:

```sh
BASHCUT_CORE_PATH=/absolute/BashCut/Packages/BashCutCore swift build --package-path plugins/ai-media-studio/tests/native
STUDIO_NATIVE_VALIDATOR="$PWD/plugins/ai-media-studio/tests/native/.build/debug/StudioValidation" /tmp/studio-tests/bin/python -B -m unittest discover -s plugins/ai-media-studio/tests -v
```
