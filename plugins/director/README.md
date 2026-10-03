# Director

BashCut's own editing agent, shown as the **Director** tab in the agent dock. You chat with a model from Anthropic,
OpenAI, Google, OpenRouter, Groq, xAI or Mistral using your own API key. The model works only through BashCut's
catalogued commands, with the same checks as other agents: edit permission, approvals, History and Show Changes.
It can look at the result with `ui frame` and follow the agent kit's skills. It has no shell and cannot write files.
Design: [spec 11 — Director](https://github.com/dongnguyenvie/BashCut/blob/main/docs/specs/11-director.md).

**Requires BashCut with plugin API 4** (host channel, `secret` options and the `agent.chat` capability). Older
BashCut builds list the plugin as outdated.

The model runtime is the MIT-licensed [pi](https://github.com/earendil-works/pi) libraries
(`@earendil-works/pi-agent-core` and `@earendil-works/pi-ai` 1.0.1). pi is an implementation detail and is never
named in the UI. Licenses of everything in the bundle are in `dist/THIRD-PARTY-NOTICES.txt`.

## Settings (Settings › Plugins › Director)

| Option | Type | Default | Notes |
|---|---|---|---|
| `provider` | enum | `anthropic` | `anthropic`, `openai`, `google`, `openrouter`, `groq`, `xai`, `mistral` |
| `model` | string | empty | Empty means the provider's default (table below); otherwise a model ID from pi-ai's catalog |
| `apiKey` | secret | — | Kept in the Keychain by BashCut and sent only in the request; never logged or saved by the plugin |
| `thinking` | enum | `off` | `off`, `low`, `medium`, `high`; ignored by models without reasoning |
| `maxTurns` | integer 5–200 | 40 | Model calls per message before Director stops and says so |

| Provider | Default model |
|---|---|
| Anthropic | `claude-sonnet-5-5` |
| OpenAI | `gpt-5.5` |
| Google | `gemini-3.5-flash` |
| OpenRouter | `anthropic/claude-sonnet-5.5` |
| Groq | `openai/gpt-oss-120b` |
| xAI | `grok-4.7` |
| Mistral | `mistral-medium-latest` |

## Dependency: Node.js 22.19+

- `bin/check` (the probe) looks for `node` 22.19 or newer in `BASHCUT_PLUGIN_DATA/node/bin`, then `/opt/homebrew/bin`,
  `/usr/local/bin`, `~/.nvm/versions/node/*/bin` (newest first), `~/.volta/bin` and `PATH`. It exits 0 and prints
  `Node.js v22.x.y at <path>`, or exits 1 with the reason on stderr. `bin/provider` uses the same search
  (`bin/find-node`).
- `bin/setup` (the install recipe) downloads the newest official Node.js 22 LTS for darwin-arm64 or darwin-x64 from
  nodejs.org into `BASHCUT_PLUGIN_DATA/node`, after checking it against the release's `SHASUMS256.txt`, with
  `::progress` lines. Running it again updates the copy.

## Protocol (session transport, plugin API 4)

`bin/provider session` speaks NDJSON on stdin/stdout. It answers `hello` with `{"type":"hello","apiVersion":4}` and
handles `request` (method `agent.chat`), `callResult`, `cancel` (aborts that turn) and `shutdown`. Standard output
carries protocol lines only; logs go to standard error.

| `params.op` | Result |
|---|---|
| `turn` | `{"stopReason":"end"\|"aborted"\|"error","error"?}` — streams events and makes calls while it runs |
| `reset` | `{}` — deletes the conversation |
| `status` | `{"ready","provider","model","detail"}` — ready means a key is set and the model is in the catalog |

During a turn the plugin sends:

```json
{"type":"event","id":"<request>","event":{"kind":"text","delta":"…"}}
{"type":"event","id":"<request>","event":{"kind":"thinking","delta":"…"}}
{"type":"event","id":"<request>","event":{"kind":"tool","callId":"c1","name":"bashcut_timeline_get","summary":"timeline.get {\"tracks\":true}"}}
{"type":"call","id":"<request>","callId":"c1","method":"timeline.get","params":{"tracks":true}}
{"type":"event","id":"<request>","event":{"kind":"toolEnd","callId":"c1","ok":true,"summary":"{\"tracks\":[…]}"}}
{"type":"event","id":"<request>","event":{"kind":"message","role":"assistant","text":"…"}}
{"type":"event","id":"<request>","event":{"kind":"notice","text":"…"}}
{"type":"progress","id":"<request>"}
```

- `callId`s (`c1`, `c2`, … unique per process) are shared by the `tool`/`toolEnd` events and the `call` line, so the
  app can pair them. `read_skill` has tool events but no `call`.
- A tool's result goes to the model as compact JSON, cut at 30,000 characters with a note. An error `callResult`
  becomes a tool error the model sees. For `ui.frame` the PNG at `result.path` is also attached as an image when
  the model accepts images.
- `message` carries the final text of each assistant message (after its `text` deltas). `notice` reports
  compaction, skipped attachments and the `maxTurns` stop. A `progress` keepalive is sent every 20 seconds.
- Turn errors (no key, unknown model, provider failure) are results with `stopReason: "error"`; malformed requests
  get `{"id","error":{"code":"invalid_params"|"unknown_method","message"}}`.

The system prompt is a fixed first line plus three sections: `<instructions>` (`params.instructions`), `<skills>`
(the kit's skills, telling the model to call `read_skill` first) and `<context>` (`params.context`). Later turns add
a system message that patches only the sections that changed, so the cached prefix stays the same. `read_skill`
reads `<kit.root>/skills/<name>/SKILL.md` only; names with `/`, `\` or `..` are refused. `params.images` (PNG,
JPEG, GIF, WebP) are attached to the user message when the model accepts images.

## Conversations and compaction

Each conversation is saved as `BASHCUT_PLUGIN_DATA/conversations/<id>.json` (mode 0600) after every model turn and
reloaded when a new process starts. IDs with characters other than letters, digits, `_` and `-` get a hash suffix.

Tokens are estimated at 4 characters each and about 1,500 per image. The budget is the model's context window,
capped at 200,000 tokens, minus its output allowance. Past 75% of the budget, the oldest tool results (and images
in older messages) become a one-line stub until the estimate is under 50%; the newest 8 messages are kept intact.
If that is not enough, the oldest exchanges are dropped. System messages are always kept. The compacted
transcript is what is saved.

## Building and testing

```sh
plugins/director/build.sh                      # npm ci (locked versions) + tsc + esbuild → dist/director.mjs
cd plugins/director && npm test                # node:test, drives the bundle over the protocol; no network
scripts/dev-link.sh director                   # then Trust in BashCut's Plugins sheet
```

The bundle is built by `build.sh` (in CI and by `package.py`) and is not committed; the release archive ships it
together with `dist/THIRD-PARTY-NOTICES.txt` instead of `node_modules`, so users never run npm. Run `build.sh`
after changing `src/` or `package-lock.json`.

**Test-only:** with `BASHCUT_DIRECTOR_FAUX=<script.json>` every request uses pi-ai's faux provider, which answers
from the script (format at the top of `src/faux.ts`). BashCut gives plugins a filtered environment, so the app
can never turn this on.
