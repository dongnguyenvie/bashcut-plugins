"""{{NAME}}: a chat agent (agent.chat, provider {{PROVIDER_ID}}) that gets a tab in BashCut's agent dock.

This placeholder agent reads the timeline with a BashCut command and echoes the message. Replace `turn` with a real
model loop: send the model params["instructions"], params["context"] and params["tools"], stream its text with
host.event, and run each tool call with host.call(tool["method"], arguments).
https://github.com/dongnguyenvie/BashCut/blob/main/docs/specs/11-chat-agents.md
"""
from bashcut_plugin import PluginError


def handle(method, params, host):
    if method != "agent.chat":
        raise PluginError("unknown_method", f"{{PLAIN_NAME}} does not handle {method}")
    op = params.get("op")
    options = params.get("options") or {}
    if op == "turn":
        return turn(params, host)
    if op == "status":
        return {"ready": True, "provider": "{{PLAIN_NAME}}", "model": "echo",
                "detail": "Echoes your message and counts the timeline's layers."}
    if op == "reset":
        return {}
    if op == "commands":
        return {"commands": [{"name": "hello", "summary": "Say hello"}]}
    if op == "command":
        if params.get("name") == "hello":
            return {"text": f"{options.get('greeting') or 'Hello'} from {{PLAIN_NAME}}"}
        raise PluginError("unknown_command", f"Unknown command /{params.get('name')}")
    raise PluginError("unknown_op", f"Unknown op {op}")


def turn(params, host):
    host.event({"kind": "tool", "callId": "t1", "name": "bashcut_timeline_get", "summary": "Reading the timeline"})
    try:
        timeline = host.call("timeline.get")
    except PluginError as error:
        host.event({"kind": "toolEnd", "callId": "t1", "ok": False, "summary": error.message})
        return {"stopReason": "error", "error": error.message}
    layers = len(timeline.get("tracks") or []) if isinstance(timeline, dict) else 0
    host.event({"kind": "toolEnd", "callId": "t1", "ok": True, "summary": f"{layers} layers"})
    reply = f"You said: {params.get('text', '')}\nThe timeline has {layers} layers."
    host.event({"kind": "text", "delta": reply})
    host.event({"kind": "message", "role": "assistant", "text": reply})
    return {"stopReason": "end"}
