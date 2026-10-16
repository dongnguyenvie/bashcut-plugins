// The BashCut plugin protocol for Translate Captions (Foundation only). You rarely need to change this file.
//
// BashCut runs the entrypoint as `provider rpc` (one JSON request on stdin, one JSON response on stdout) or, with
// "transport": "session" in plugin.json, as `provider session` (newline-delimited JSON until it says shutdown).
// Handlers.swift gets a `Host` to report progress, stream chat events and call BashCut commands. Diagnostics go to
// stderr: stdout carries only protocol lines.
import Foundation

typealias JSON = [String: Any]

/// A failure with a stable code BashCut can show, such as `PluginError("model_missing", "Install the model")`.
struct PluginError: Error {
    let code: String
    let message: String
    init(_ code: String, _ message: String) {
        self.code = code
        self.message = message
    }
}

struct Cancelled: Error {}

/// The host features the session hello listed (API 8), such as "views.colorPicker" or "overlays". Check one before
/// using what it names, so the plugin still works in an older BashCut. Empty over the one-shot transport.
var hostFeatures = Set<String>()

func send(_ message: JSON) {
    guard let data = try? JSONSerialization.data(withJSONObject: message, options: [.withoutEscapingSlashes]) else {
        FileHandle.standardError.write(Data("could not encode a response\n".utf8))
        return
    }
    FileHandle.standardOutput.write(data + Data("\n".utf8))
}

/// Redraws one of the plugin's views outside a request (session transport, host feature `viewUpdate`): `answer` is a
/// whole view answer (`body`, `title`?, `state`?, `notify`?). BashCut draws it only while the view is on screen and
/// drops updates beyond about ten a second; an older BashCut ignores the line.
func viewUpdate(_ view: String, _ answer: JSON) {
    send(answer.merging(["type": "viewUpdate", "view": view]) { _, new in new })
}

/// Replaces the plugin's marks on the timeline and viewer at any time (host feature `overlays`); `[]` clears them.
/// From a request, `host.call("plugins.set-overlays", …)` does the same and reports a bad set.
func sendOverlays(_ overlays: [JSON]) {
    send(["type": "overlays", "overlays": overlays])
}

func readMessage() -> JSON? {
    while let line = readLine(strippingNewline: true) {
        if line.trimmingCharacters(in: .whitespaces).isEmpty { continue }
        if let object = try? JSONSerialization.jsonObject(with: Data(line.utf8)) as? JSON { return object }
        FileHandle.standardError.write(Data("ignored a line that is not a JSON object\n".utf8))
    }
    return nil
}

/// What a handler can do while its request runs.
final class Host {
    let requestId: Any
    let session: Session?
    private var calls = 0

    init(requestId: Any, session: Session?) {
        self.requestId = requestId
        self.session = session
    }

    /// Shows progress on the job (session transport); keeps a long request alive. Send one at least every minute.
    func progress(_ fraction: Double?, _ message: String? = nil) {
        guard session != nil else {
            FileHandle.standardError.write(Data("progress \(fraction.map { "\($0)" } ?? "") \(message ?? "")\n".utf8))
            return
        }
        var line: JSON = ["type": "progress", "id": requestId]
        if let fraction { line["progress"] = min(1, max(0, fraction)) }
        if let message { line["message"] = message }
        send(line)
    }

    /// Hands a UI event to the caller, such as `["kind": "text", "delta": "Hi"]` for a chat agent (API 4).
    func event(_ event: JSON) throws {
        guard session != nil else { throw PluginError("no_host_channel", "Events need the session transport") }
        send(["type": "event", "id": requestId, "event": event])
    }

    /// Runs a BashCut command, such as `try host.call("timeline.get")`, and returns its result (API 4).
    func call(_ method: String, _ params: JSON = [:]) throws -> Any? {
        guard let session else { throw PluginError("no_host_channel", "Calling BashCut needs the session transport") }
        calls += 1
        let callId = "\(requestId)-c\(calls)"
        send(["type": "call", "id": requestId, "callId": callId, "method": method, "params": params])
        let reply = try session.waitForCall(callId, requestId: "\(requestId)")
        if let error = reply["error"] as? JSON {
            throw PluginError("\(error["code"] ?? "call_failed")", error["message"] as? String ?? "BashCut refused the call")
        }
        return reply["result"]
    }

    /// Redraws the view that asked while the request still works (view requests): a progress bar, partial results.
    func render(_ body: [JSON], title: String? = nil) throws {
        var event: JSON = ["kind": "render", "body": body]
        if let title { event["title"] = title }
        try self.event(event)
    }

    /// Commands that run as jobs (voice.speak, plugins.invoke, export.start …) answer `{"job": id}`: polls
    /// jobs.status until the job ends and returns its result. Other answers come back unchanged.
    func waitJob(_ started: Any?, timeout: TimeInterval = 600, interval: TimeInterval = 0.4) throws -> Any? {
        guard let job = (started as? JSON)?["job"] as? String else { return started }
        let deadline = Date().addingTimeInterval(timeout)
        while Date() < deadline {
            let answer = try call("jobs.status", ["job": job]) as? JSON ?? [:]
            let status = answer["job"] as? JSON ?? answer
            switch status["state"] as? String {
            case "completed": return status["result"]
            case let state? where state == "failed" || state == "cancelled":
                throw PluginError("job_\(state)", "\(status["error"] ?? "The job \(state)")")
            default: Thread.sleep(forTimeInterval: interval)
            }
        }
        throw PluginError("timeout", "The job \(job) did not end in \(Int(timeout)) s")
    }
}

func respond(_ request: JSON, session: Session?) -> JSON {
    let id = request["id"] ?? NSNull()
    do {
        let result = try handle(method: request["method"] as? String ?? "", params: request["params"] as? JSON ?? [:],
                                host: Host(requestId: id, session: session))
        return ["id": id, "result": result ?? JSON()]
    } catch let error as PluginError {
        return ["id": id, "error": ["code": error.code, "message": error.message]]
    } catch is Cancelled {
        return ["id": id, "error": ["code": "cancelled", "message": "Cancelled"]]
    } catch {
        return ["id": id, "error": ["code": "failed", "message": "\(error)"]]
    }
}

/// The session transport, one request at a time. Messages that arrive while a handler waits for a call result are
/// kept and handled next, in order.
final class Session {
    private var backlog: [JSON] = []

    func waitForCall(_ callId: String, requestId: String) throws -> JSON {
        while true {
            guard let message = readMessage() else { throw PluginError("host_closed", "BashCut closed the session") }
            let kind = message["type"] as? String
            if kind == "callResult" {
                if message["callId"] as? String == callId { return message }
                continue  // the answer to a call that was given up on
            }
            if kind == "cancel", "\(message["id"] ?? "")" == requestId { throw Cancelled() }
            backlog.append(message)
        }
    }

    func run() {
        while true {
            let next = backlog.isEmpty ? readMessage() : backlog.removeFirst()
            guard let message = next else { return }
            switch message["type"] as? String {
            case "hello":
                hostFeatures.formUnion((message["features"] as? [Any] ?? []).map { "\($0)" })
                send(["type": "hello", "apiVersion": message["apiVersion"] ?? 2])
            case "shutdown": return
            case "cancel", "callResult": continue
            default: send(respond(message, session: self))
            }
        }
    }
}

if CommandLine.arguments.dropFirst().first == "session" {
    Session().run()
} else if let request = readMessage() {
    send(respond(request, session: nil))
} else {
    FileHandle.standardError.write(Data("expected one JSON request on stdin\n".utf8))
    exit(2)
}
