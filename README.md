# BashCut plugins

The plugin registry for [BashCut](https://github.com/dongnguyenvie/BashCut). There is no server: BashCut reads
[`registry.json`](registry.json) from this repo, downloads plugin archives from this repo's GitHub Releases and checks
their SHA-256 before anything runs. Plugins use BashCut's out-of-process plugin API 2
([Writing plugins](https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md)).

| Plugin | What it does |
|---|---|
| [Antigravity](plugins/antigravity) | Adds Google's Antigravity CLI as an agent terminal, with BashCut tools, skills, project conversations and its own bypass-permissions setting |
| [Silence Markers](plugins/silence-markers) | Adds a section marker at every quiet stretch in the selected clip |
| [Whisper Captions](plugins/whisper-captions) | Captions from speech on Apple Silicon (Whisper large-v3 turbo via MLX, MIT): Vietnamese and about 100 languages, timed per word, split into even lines; `captions.transcribe` provider |
| [VieNeu TTS](plugins/vieneu-tts) | Vietnamese voiceover on this Mac (VieNeu-TTS v3 Turbo, Apache-2.0): 25 voices, voice cloning; `voice.synthesize` provider |
| [Director](plugins/director) | BashCut's editing agent in the agent dock: chat with Claude, GPT, Gemini and others using your API key; it edits through BashCut's commands. Needs BashCut with plugin API 4; `agent.chat` provider |

## Layout

```text
registry.json                 catalog BashCut reads — generated, never edited by hand
publishers.json               schemaVersion and publishers (source of registry.json)
plugins/<slug>/versions.json  the plugin's listing at its last release and its published versions (source)
plugins/<slug>/plugin.json    manifest (bashcut.plugin/1)
plugins/<slug>/bin/…          entrypoint and helpers
plugins/<slug>/listing.json   store listing: name and summary ({en, vi, …}), category, platforms, minAppVersion
plugins/<slug>/tests/         tests run by CI (not shipped)
plugins/<slug>/build.sh       optional: builds compiled helpers or bundles (CI and package.py run it; not shipped)
plugins/<slug>/src/           optional: sources for build.sh (not shipped)
samples/<slug>/               examples for plugin authors (never published), such as samples/terminal-agent
scripts/package.py            zip + SHA-256 + signature; --register records the version in versions.json
scripts/build-registry.py     generates registry.json from the sources (--check in CI)
```

## Why registry.json is generated

Each release or yank writes only its own `plugins/<slug>/versions.json`, so changes to different plugins never touch
the same source file, and BashCut still downloads one `registry.json` (one request, one consistent snapshot).
`scripts/build-registry.py` rebuilds it deterministically; CI fails when it is out of date. A merge or rebase
conflict in `registry.json` is resolved by running the script again — the release workflow does that itself when
two releases race. The listing in `versions.json` is a snapshot of the released `listing.json` and manifest, so
unreleased changes on `main` never reach users.

## Registry format

```json
{
  "schemaVersion": 1,
  "publishers": {"bashcut": {"name": {"en": "BashCut"}, "keys": [], "verified": true}},
  "plugins": [{
    "id": "bashcut.silence-markers", "name": {"en": "Silence Markers", "vi": "Đánh dấu im lặng"},
    "summary": {"en": "Adds a section marker at every quiet stretch…", "vi": "Thêm mốc tại mọi đoạn im lặng…"},
    "publisher": "bashcut", "category": "audio",
    "capabilities": [], "actions": ["bashcut.silence-markers.mark"], "hooks": [],
    "versions": [{
      "version": "0.1.0", "apiVersion": 2, "minApiVersion": 2, "minAppVersion": "0.0.1",
      "platforms": ["macos-arm64", "macos-x86_64"],
      "url": "https://github.com/dongnguyenvie/bashcut-plugins/releases/download/silence-markers-v0.1.0/bashcut.silence-markers-0.1.0.zip",
      "sha256": "…", "signature": null, "size": 3352, "downloadBytes": 0, "releasedAt": "2026-10-03"
    }]
  }]
}
```

Display text (`name`, `summary`, and in manifests `title`, `help`, `confirm`) is a language map such as
`{"en": "Silence Markers", "vi": "Đánh dấu im lặng"}`; a plain string means English, and a map with several
languages must include `en`. Adding a language is adding a key — no new fields. `package.py` rejects the old
`titleVi`/`nameVi` style.

Each archive holds one folder named after the plugin id. The registry keeps the newest 3 versions of each plugin.

## Signatures

`signature` is `ed25519:BASE64` over the 32 raw bytes of the archive's SHA-256. BashCut checks it before
downloading and shows *Signed by BashCut*; a signature that matches no key is refused, an unsigned archive gets a
warning. The BashCut public key is compiled into the app (`PluginSignature.firstPartyKeys`) and mirrored in
`publishers.bashcut.keys` here for `scripts/verify-registry.swift`; the app ignores registry keys for `bashcut`.

- The private key is the `BASHCUT_SIGNING_KEY` Actions secret (base64 raw 32 bytes). An offline copy is in the
  maintainer's login keychain as "BashCut plugin signing key (ed25519)".
- `release.yml` refuses to publish without it, uploads `<archive>.sig` next to the zip and verifies the registry.
- `scripts/sign-registry.py` signs versions published before signing existed (it re-downloads and checks each
  archive first); `scripts/sign.swift` is the signer both use.
- Rotating: ship the new public key in a BashCut release first, then switch the secret; keep the old key in the app
  for one release cycle.

## Withdrawing a version

`scripts/yank.py <id> <version> "<reason>"` marks a version `"yanked"` in its `versions.json` and regenerates
`registry.json`; commit both and push. BashCut stops offering it,
tells users who have it why, and Updates offers the newest good version. `--undo` restores it. Never re-publish a
yanked version number.

## Rules for users who are not developers

Installing a plugin is one click in BashCut; users never open Terminal, install Homebrew or fix a Python. So:

- A dependency is either a tool every Mac has (`package.py` keeps the list: `sh`, `curl`, `afconvert`, `ditto`,
  `osascript`…) or has an install recipe that downloads it into `BASHCUT_PLUGIN_DATA`. `python3`, `git`, `swift` and
  Homebrew tools are refused: on a fresh Mac they are missing or ask to install the Command Line Tools.
- Plugins written in TypeScript ship one esbuild bundle and need only Node.js, which their recipe downloads from
  nodejs.org when the Mac has none (see Director: `build.sh` runs `npm ci` with the lockfile; `node_modules` is never
  shipped). Their tests use `node:test` and run with `npm test` when the folder has a `package.json`.
- Small plugins are compiled Swift (see Silence Markers: `build.sh` makes a universal binary with AVFoundation, no
  runtime needed). Plugins that need Python bring their own with `uv`, like VieNeu.
- Probes must exit 0 when the tool works (`afconvert -h` exits 2, for example).

## Testing locally

Run `plugins/<slug>/build.sh` first when the plugin has one. `scripts/dev-link.sh <slug>` symlinks a plugin into `~/Library/Application Support/BashCut/Plugins/`. Open
**Plugins** in BashCut and choose **Trust** once; changes to `plugin.json` or the entrypoint ask for Trust again,
other files can change while you iterate. `scripts/dev-link.sh <slug> --remove` unlinks it. Plugins with heavy
models have a fake mode for tests and CI (for VieNeu, `VIENEU_FAKE=1`).

Samples link the same way: `scripts/dev-link.sh samples/terminal-agent` adds a sample agent CLI to the agent dock
(`agent.terminal`, plugin API 5). Its README explains how to turn it into a real CLI plugin such as Gemini CLI.

Versions stay `0.0.x` while plugins are in beta.

## Publishing

1. Change `plugins/<slug>`, bump `version` in `plugin.json`, merge to `main`.
2. Tag and push: `git tag silence-markers-v0.2.0 && git push origin silence-markers-v0.2.0`.
3. The `Release plugin` workflow tests the plugin, zips it, creates the GitHub Release with the archive and its
   `.sha256` and `.sig`, re-downloads and checks it, then commits the signed version to `versions.json` and the
   regenerated `registry.json`.

A version is never re-published: bump it instead.

## Installing

In BashCut, open **Plugins › Browse**, choose **Install**, review the source, checksum and dependency plan, and
approve. Updates appear under **Updates**; **Installed › Remove** uninstalls. Agents can run
`bashcut plugins search` and `bashcut plugins install <id>`, but only the user approves an install.

By hand: download the zip from Releases, unzip it into `~/Library/Application Support/BashCut/Plugins/`, open
**Plugins** and choose **Trust**.

## License

MIT. See [LICENSE](LICENSE).
