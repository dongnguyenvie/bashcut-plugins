

class ChatAgentTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.session = Session(self.folder)

    def tearDown(self):
        self.session.close()

    def chat(self, request_id, params, on_call=None):
        return self.session.request(request_id, "agent.chat", {"options": {"greeting": "Xin chào"}, **params},
                                    provider="{{PROVIDER_ID}}", on_call=on_call)

    def test_turn_streams_events_and_calls_bashcut(self):
        calls = []

        def on_call(message):
            calls.append(message["method"])
            return {"result": {"tracks": [{"id": "v1"}, {"id": "a1"}]}}

        lines, reply = self.chat("t1", {"op": "turn", "conversation": "c1", "text": "Cắt đoạn đầu", "context": "",
                                        "instructions": "", "tools": [], "kit": None}, on_call)
        self.assertEqual(reply["result"]["stopReason"], "end")
        self.assertEqual(calls, ["timeline.get"])
        events = [line["event"] for line in lines if line["type"] == "event"]
        self.assertEqual([event["kind"] for event in events], ["tool", "toolEnd", "text", "message"])
        self.assertIn("Cắt đoạn đầu", events[-1]["text"])
        self.assertIn("2 layers", events[-1]["text"])

    def test_refused_call_ends_the_turn_with_an_error(self):
        _, reply = self.chat("t2", {"op": "turn", "conversation": "c1", "text": "hi"},
                             lambda _: {"error": {"code": -32602, "message": "Edits are off"}})
        self.assertEqual(reply["result"], {"stopReason": "error", "error": "Edits are off"})

    def test_status_commands_and_reset(self):
        self.assertTrue(self.chat("s", {"op": "status"})[1]["result"]["ready"])
        commands = self.chat("l", {"op": "commands"})[1]["result"]["commands"]
        self.assertEqual([c["name"] for c in commands], ["hello"])
        reply = self.chat("c", {"op": "command", "conversation": "c1", "name": "hello", "args": ""})[1]
        self.assertTrue(reply["result"]["text"].startswith("Xin chào"))
        self.assertEqual(self.chat("r", {"op": "reset", "conversation": "c1"})[1]["result"], {})
        self.assertIn("error", self.chat("x", {"op": "nope"})[1])


if __name__ == "__main__":
    unittest.main()
