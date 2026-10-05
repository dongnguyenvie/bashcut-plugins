// {{NAME}}: a chat agent (agent.chat, provider {{PROVIDER_ID}}) that gets a tab in BashCut's agent dock.
//
// This placeholder agent reads the timeline with a BashCut command and echoes the message. Replace `turn` with a
// real model loop: send the model params["instructions"], params["context"] and params["tools"], stream its text
// with host.event, and run each tool call with host.call(tool method, arguments).
// https://github.com/dongnguyenvie/BashCut/blob/main/docs/specs/11-chat-agents.md
import Foundation

func handle(method: String, params: JSON, host: Host) throws -> Any? {
    guard method == "agent.chat" else { throw PluginError("unknown_method", "{{PLAIN_NAME}} does not handle \(method)") }
    let options = params["options"] as? JSON ?? [:]
    let op = params["op"] as? String ?? ""
    switch op {
    case "turn":
        return try turn(params, host: host)
    case "status":
        return ["ready": true, "provider": "{{PLAIN_NAME}}", "model": "echo",
                "detail": "Echoes your message and counts the timeline's layers."]
    case "reset":
        return JSON()
    case "commands":
        return ["commands": [["name": "hello", "summary": "Say hello"]]]
    case "command":
        let name = params["name"] as? String ?? ""
        guard name == "hello" else { throw PluginError("unknown_command", "Unknown command /\(name)") }
        let greeting = (options["greeting"] as? String).flatMap { $0.isEmpty ? nil : $0 } ?? "Hello"
        return ["text": "\(greeting) from {{PLAIN_NAME}}"]
    default:
        throw PluginError("unknown_op", "Unknown op \(op)")
    }
}

func turn(_ params: JSON, host: Host) throws -> JSON {
    try host.event(["kind": "tool", "callId": "t1", "name": "bashcut_timeline_get", "summary": "Reading the timeline"])
    let timeline: Any?
    do {
        timeline = try host.call("timeline.get")
    } catch let error as PluginError {
        try host.event(["kind": "toolEnd", "callId": "t1", "ok": false, "summary": error.message])
        return ["stopReason": "error", "error": error.message]
    }
    let layers = ((timeline as? JSON)?["tracks"] as? [Any])?.count ?? 0
    try host.event(["kind": "toolEnd", "callId": "t1", "ok": true, "summary": "\(layers) layers"])
    let reply = "You said: \(params["text"] as? String ?? "")\nThe timeline has \(layers) layers."
    try host.event(["kind": "text", "delta": reply])
    try host.event(["kind": "message", "role": "assistant", "text": reply])
    return ["stopReason": "end"]
}
