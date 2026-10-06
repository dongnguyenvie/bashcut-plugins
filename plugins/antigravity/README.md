# Antigravity

The Antigravity plugin adds Google's `agy` CLI as a terminal in BashCut's agent dock. It uses your existing Google
login or Gemini API-key configuration, BashCut's MCP tools and editing skills, and separate conversation history for
each BashCut project. It requires BashCut plugin API 5.

Contributed by [Luan Tran](https://github.com/luantran069) ([#21](https://github.com/dongnguyenvie/bashcut-plugins/pull/21)); maintained and published by BashCut.

## Install and use

For a local checkout, run `plugins/antigravity/build.sh` and `scripts/dev-link.sh antigravity`, then reopen
**Plugins** in BashCut and choose **Trust**.
After a plugin release is published, it can be installed from Plugins › Browse. Its dependency setup can install
`agy` from Google's official installer without changing your shell profile; sign in when its terminal opens.

Open **Agent → + → Antigravity terminal**. The app supplies a token to that tab only; the plugin's config file stores
`$BASHCUT_SESSION_TOKEN` as an environment reference, never the token value. The tab receives BashCut's current
instructions and links the installed agent kit into its `.agents/skills` directory. Reopening a project continues
its latest Antigravity conversation; **New conversation** starts fresh.

## Settings (Settings → Plugins → Antigravity)

| Option | Default | Effect |
|---|---|---|
| **Bypass permission mode** | Off | Adds `--dangerously-skip-permissions` to new `agy` tabs. This skips Antigravity's prompts for shell, file, web and MCP tools; BashCut's own timeline-edit and privileged export controls still apply. |

The option belongs to this plugin, not the dock's + menu, and affects only new tabs. When off, Antigravity's own
`/permissions` rules apply. For direct access to a footage folder outside its working directory, use Antigravity's
`/add-dir <path>`.

Antigravity's login and API-key settings are managed by Antigravity, not stored in this plugin. If you use
`GEMINI_API_KEY`, Antigravity also requires `"modelProvider": "gemini"` in its settings. Prompts, project context and
tool results go to Google under your account or API configuration.

## Build and test

```sh
plugins/antigravity/build.sh
python3 -m unittest discover -s plugins/antigravity/tests
scripts/dev-link.sh antigravity
```

The release archive ships a universal native provider, so users need neither Python nor Node to run the plugin.
The tests use a fake home and no Google login or network. Live acceptance still needs an installed, authenticated
`agy`: check `/mcp`, `/skills`, project isolation, resume and the bypass option in a scratch BashCut project.
