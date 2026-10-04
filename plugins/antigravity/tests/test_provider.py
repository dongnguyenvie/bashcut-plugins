"""Exercises the native API-5 provider without a Google login or network access."""
import hashlib
import json
import os
import pathlib
import stat
import subprocess
import tempfile
import unittest

PLUGIN = pathlib.Path(__file__).resolve().parent.parent
PROVIDER = PLUGIN / "bin" / "provider"


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = pathlib.Path(self.scratch.name)
        self.folder = self.root / "agent-workspaces" / "bashcut.antigravity"
        self.folder.mkdir(parents=True)
        self.project = self.root / "Project" / "project.bashcut.json"
        self.project.parent.mkdir()
        self.project.write_text("{}")

    def call(self, params):
        request = {"id": "r1", "apiVersion": 5, "method": "agent.terminal", "params": params}
        environment = dict(os.environ, HOME=str(self.root))
        output = subprocess.run([str(PROVIDER), "rpc"], input=json.dumps(request) + "\n",
                                capture_output=True, text=True, check=True, env=environment)
        self.assertEqual(len(output.stdout.splitlines()), 1)
        return json.loads(output.stdout)

    def params(self, *, project=None, resume="", bypass=False):
        return {
            "op": "launch", "workspace": str(self.project.parent), "agentFolder": str(self.folder),
            "project": str(project or self.project), "prompt": "Use BashCut. Do not edit project JSON directly.",
            "resume": resume, "canEdit": True, "kit": None,
            "options": {"bypassPermissions": bypass},
            "mcp": {"name": "bashcut", "command": "/Apps/bashcut-mcp", "arguments": [],
                    "environment": ["BASHCUT_SOCKET", "BASHCUT_SESSION_TOKEN"]},
        }

    def test_launch_writes_private_config_without_token(self):
        result = self.call(self.params())["result"]
        self.assertEqual(result["executable"], "agy")
        self.assertEqual(result["arguments"], [])
        project_key = hashlib.sha256(str(self.project).encode()).hexdigest()[:16]
        self.assertEqual(pathlib.Path(result["directory"]), self.folder / "projects" / project_key)
        settings = pathlib.Path(result["directory"]) / ".agents" / "mcp_config.json"
        prompt = pathlib.Path(result["directory"]) / "AGENTS.md"
        self.assertEqual(pathlib.Path(result["skillsFolder"]), settings.parent / "skills")
        server = json.loads(settings.read_text())["mcpServers"]["bashcut"]
        self.assertEqual(server["command"], "/Apps/bashcut-mcp")
        self.assertEqual(server["env"]["BASHCUT_SESSION_TOKEN"], "$BASHCUT_SESSION_TOKEN")
        self.assertNotIn("private-session-token", settings.read_text() + prompt.read_text())
        self.assertIn("Use BashCut.", prompt.read_text())
        self.assertEqual(stat.S_IMODE(settings.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(prompt.stat().st_mode), 0o600)

    def test_bypass_is_a_plugin_option_and_resume_is_project_scoped(self):
        result = self.call(self.params(resume="old-session", bypass=True))["result"]
        self.assertEqual(result["arguments"], ["--continue", "--dangerously-skip-permissions"])
        other = self.root / "Other" / "project.bashcut.json"
        other.parent.mkdir()
        other.write_text("{}")
        fresh = self.call(self.params(project=other))["result"]
        self.assertEqual(fresh["arguments"], [])
        self.assertNotEqual(result["directory"], fresh["directory"])

    def test_session_and_unknown_operation(self):
        params = self.params()
        params["op"] = "session"
        params["notBefore"] = None
        self.assertIsNone(self.call(params)["result"]["id"])
        folder = pathlib.Path(self.call(self.params())["result"]["directory"])
        cache = self.root / ".gemini" / "antigravity-cli" / "cache"
        cache.mkdir(parents=True)
        identifier = "619b4757-f649-48db-a7d0-991a0386ab4c"
        (cache / "last_conversations.json").write_text(json.dumps({str(folder): identifier}))
        self.assertEqual(self.call(params)["result"]["id"], identifier)
        params["op"] = "unknown"
        self.assertEqual(self.call(params)["error"]["code"], "unknown_op")


if __name__ == "__main__":
    unittest.main()
