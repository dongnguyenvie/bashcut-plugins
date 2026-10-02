# BashCut plugins

The plugin registry for [BashCut](https://github.com/dongnguyenvie/BashCut). There is no server: BashCut reads
[`registry.json`](registry.json) from this repo, downloads plugin archives from this repo's GitHub Releases and checks
their SHA-256 before anything runs. Plugins use BashCut's out-of-process plugin API 2
([Writing plugins](https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md)).

| Plugin | What it does |
|---|---|
| [Silence Markers](plugins/silence-markers) | Adds a section marker at every quiet stretch in the selected clip |

## Layout

```text
registry.json                 catalog BashCut reads
plugins/<slug>/plugin.json    manifest (bashcut.plugin/1)
plugins/<slug>/bin/…          entrypoint and helpers
plugins/<slug>/listing.json   store listing: name and summary ({en, vi, …}), category, platforms, minAppVersion
plugins/<slug>/tests/         tests run by CI (not shipped)
scripts/package.py            zip + SHA-256 + registry entry
```

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
`signature` (ed25519 over the archive) is reserved; until BashCut checks it, the SHA-256 plus the user's Trust in the
Plugins sheet are the gate.

## Publishing

1. Change `plugins/<slug>`, bump `version` in `plugin.json`, merge to `main`.
2. Tag and push: `git tag silence-markers-v0.2.0 && git push origin silence-markers-v0.2.0`.
3. The `Release plugin` workflow tests the plugin, zips it, creates the GitHub Release with the archive and its
   `.sha256`, re-downloads and checks it, then commits the new version to `registry.json`.

A version is never re-published: bump it instead.

## Installing by hand (until BashCut has the Browse tab)

Download the zip from Releases, unzip it into `~/Library/Application Support/BashCut/Plugins/`, open **Plugins** in
BashCut and choose **Trust**. Or use **Install Plugin…** on the unzipped folder.
