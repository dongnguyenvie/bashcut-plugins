# Image Generation

AI illustrations for a BashCut edit with the user's own key: the `image.generate` provider behind `bashcut image
generate` and brand kit mascot poses (`bashcut library brand-pose --generate`).

- **Services:** Google Gemini (`gemini-2.5-flash-image` by default) or OpenAI (`gpt-image-1` by default). The
  **Endpoint** option points the OpenAI mode at any server with `/v1/images/generations` and `/v1/images/edits`,
  such as a local model, so a local option needs no new plugin.
- **Key:** Plugins → Image Generation → API key (kept in the Keychain). Nothing is sent without one.
- **One batch per request:** every scene's prompt with the project's style lock (`image style`: style text, reference
  pictures, seed) and size. Each scene is one call; the picture is cropped to the asked shape and scaled to the asked
  size, written as `<id>.png`. A refused scene goes into `failed` and the rest are kept; a refused key stops the batch.
- **Same character:** reference pictures go with every scene (Gemini inline images, OpenAI `images/edits`), with a line
  asking to keep their character and drawing style.

Plugin id `bashcut.image-gen`, written in Swift (Foundation, CoreGraphics, ImageIO); nothing to install.

## Files

- `bin/provider`: the entrypoint BashCut runs, built by `build.sh` (not in git)
- `build.sh`: builds `bin/provider` (universal binary) from `src/`; not shipped
- `plugin.json`: manifest: the `image.generate` provider (paid) and its options
- `src/Handlers.swift`: the request, the two services and the picture fitting
- `src/main.swift`: the protocol (requests, responses, progress)
- `tests/test_plugin.py`: runs the entrypoint like BashCut against a mock Gemini/OpenAI server on 127.0.0.1; not shipped

## Test

```sh
./build.sh
python3 -m unittest discover -s tests -v
```

The tests never use a real key or the network.
