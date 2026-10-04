# Sample terminal agent (`agent.terminal`)

A starting point for adding an agent CLI (Gemini CLI, Qwen Code, opencode, aider…) to BashCut's agent dock as a
terminal tab, next to Claude, Codex and Shell. It needs BashCut with plugin API 5. The full protocol is in
[BashCut's spec 12 — Terminal agents](https://github.com/dongnguyenvie/BashCut/blob/main/docs/specs/12-terminal-agents.md).

This sample is **not published**: the registry only lists `plugins/*`, so it never shows in BashCut's Browse tab.
Its CLI is `bin/fake-agent`, a stand-in that starts the BashCut MCP server the way a real CLI would, calls
`bashcut_context_get`, and prints what it saw.

## Try it

```sh
scripts/dev-link.sh samples/terminal-agent
```

1. In BashCut, open **Plugins**, find *Sample Terminal Agent* and choose **Trust**.
2. Open a project and choose **+ › Sample Terminal Agent terminal** in the agent dock, or run
   `bashcut agent open example.terminal-agent`.
3. The tab prints a report: the MCP server, the number of tools, `contextOK`, the linked skills and `tokenSet`.
4. Open it again: it continues the same session (`bashcut agent terminals` shows `canContinue`). Use
   `bashcut agent open example.terminal-agent --new` to start a fresh one.
5. Remove it with `scripts/dev-link.sh samples/terminal-agent --remove`.

`python3 -m unittest discover -s samples/terminal-agent/tests` tests the provider without BashCut.

## Files

| File | What it is |
|---|---|
| `plugin.json` | Manifest: capability `agent.terminal`, one provider, and `terminal` (tab icon, the variables the CLI inherits) |
| `bin/provider` | Answers BashCut's `launch` and `session` requests |
| `bin/fake-agent` | The stand-in CLI. A real plugin starts the real CLI instead |
| `tests/` | Provider tests |

## What BashCut sends and expects

**`launch`** gets `workspace`, `agentFolder` (a folder BashCut owns for this plugin's tabs), `project`, `prompt`
(BashCut's instructions and the project context), `mcp` (`{name, command, arguments, environment}`), `kit`, `resume`,
`canEdit` and `options`. It answers:

```json
{"executable": "gemini", "arguments": ["--resume", "…"], "directory": "<agentFolder>",
 "environment": {"NAME": "value"}, "skillsFolder": "<agentFolder>/.gemini/skills"}
```

- `executable`: a name on the terminal's PATH, an absolute path, or a path inside the plugin. Arguments are argv,
  never a shell string.
- `environment` cannot set `PATH`, `HOME`, `TERM`, `COLORTERM` or `BASHCUT_*`.
- The plugin process never gets the session token. The terminal has it in `BASHCUT_SESSION_TOKEN` (and the socket in
  `BASHCUT_SOCKET`): configure the CLI to pass the variables named in `mcp.environment` to the MCP server, and never
  write their values to a file.

**`session`** (optional) gets `workspace`, `agentFolder`, `project` and `notBefore`, and answers `{"id": "…"}` or
`{"id": null}`.

**Skills stay in BashCut.** Do not copy the agent kit into the plugin. Return `skillsFolder` (inside `agentFolder`)
and BashCut links the kit's skills there. For a CLI without skills, use `kit.root` and `kit.skills` to tell the
model where they are, in the prompt.

## Turning it into a Gemini CLI plugin

Check each point against `gemini --help` and Gemini CLI's docs for the version you target.

1. **Manifest:** a new `id` (yours, reverse-domain), the name *Gemini*, `"environment": ["GEMINI_*", "GOOGLE_*"]`,
   and a dependency whose probe finds `gemini` (and whose install recipe runs `npm install -g @google/gemini-cli`).
2. **`write_config`:** write `<agentFolder>/.gemini/settings.json` with the `mcpServers` entry (Gemini expands `$VAR`
   in settings), and the prompt to `<agentFolder>/GEMINI.md`, the context file Gemini reads from its working folder.
   Gemini may ask the user to trust that folder the first time.
3. **`command_line`:** `"executable": "gemini"`, `"arguments": ["--resume", resume]` when resuming,
   `"directory": agentFolder`, `"skillsFolder": agentFolder + "/.gemini/skills"`.
4. **`latest_session`:** find the newest session Gemini saved for that folder (under `~/.gemini/`), or leave the op
   out to always start fresh.
5. Delete `bin/fake-agent`, move the plugin to `plugins/<slug>` with a `listing.json` and `versions.json`, and
   publish it as described in the repository README.
