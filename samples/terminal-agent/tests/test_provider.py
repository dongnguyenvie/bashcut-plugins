import json
import os
import subprocess
import tempfile
import unittest

PROVIDER = os.path.join(os.path.dirname(__file__), "..", "bin", "provider")


def call(params):
    request = {"id": "r1", "apiVersion": 5, "method": "agent.terminal", "params": params}
    out = subprocess.run([PROVIDER, "rpc"], input=json.dumps(request) + "\n", capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def launch(self, resume=""):
        return call({
            "op": "launch", "workspace": self.folder, "agentFolder": self.folder, "project": None,
            "prompt": "Use BashCut.", "resume": resume, "canEdit": True, "kit": None,
            "options": {"greeting": "Xin chào"},
            "mcp": {"name": "bashcut", "command": "/Apps/bashcut-mcp", "arguments": [],
                    "environment": ["BASHCUT_SOCKET", "BASHCUT_SESSION_TOKEN"]},
        })

    def test_launch_writes_config_without_the_token(self):
        result = self.launch()["result"]
        self.assertEqual(result["executable"], "bin/fake-agent")
        self.assertEqual(result["arguments"], [])
        self.assertEqual(result["directory"], self.folder)
        self.assertTrue(result["skillsFolder"].startswith(self.folder + "/"))
        with open(os.path.join(self.folder, "settings.json")) as handle:
            server = json.load(handle)["mcpServers"]["bashcut"]
        self.assertEqual(server["command"], "/Apps/bashcut-mcp")
        self.assertEqual(server["env"]["BASHCUT_SESSION_TOKEN"], "$BASHCUT_SESSION_TOKEN")
        with open(os.path.join(self.folder, "PROMPT.md")) as handle:
            self.assertEqual(handle.read(), "Use BashCut.")

    def test_resume_and_session(self):
        self.assertEqual(self.launch("abc")["result"]["arguments"], ["--resume", "abc"])
        session = {"op": "session", "workspace": self.folder, "agentFolder": self.folder, "project": "/p",
                   "notBefore": None, "options": {}}
        self.assertIsNone(call(session)["result"]["id"])
        with open(os.path.join(self.folder, "last-session"), "w") as handle:
            handle.write("abc\n")
        self.assertEqual(call(session)["result"]["id"], "abc")

    def test_unknown_op(self):
        self.assertEqual(call({"op": "nope"})["error"]["code"], "unknown_op")


if __name__ == "__main__":
    unittest.main()
