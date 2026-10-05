// {{NAME}}: options of every kind, read by the action {{ACTION_ID}}.
//
// BashCut draws the options in Settings › Plugins and sends their current values as params["options"] with every
// request. The secret (apiKey) comes from the Keychain: use it, never print or return it.
// https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#options
import Foundation

func handle(method: String, params: JSON, host: Host) throws -> Any? {
    guard method == "plugin.action" else { throw PluginError("unknown_method", "{{PLAIN_NAME}} does not handle \(method)") }
    let action = params["action"] as? String ?? ""
    guard action == "{{ACTION_ID}}" else { throw PluginError("unknown_action", "Unknown action \(action)") }
    let options = params["options"] as? JSON ?? [:]
    var greeting = (options["greeting"] as? String).flatMap { $0.isEmpty ? nil : $0 } ?? "Hello"
    if options["shout"] as? Bool == true { greeting = greeting.uppercased() }
    let words = Array(repeating: greeting, count: max(1, options["repeat"] as? Int ?? 1)).joined(separator: " ")
    let style = options["style"] as? String ?? "short"
    let keySet = !(options["apiKey"] as? String ?? "").isEmpty
    let detail = style == "long" ? " (style long, API key \(keySet ? "set" : "not set"))" : ""
    return ["message": words + detail, "data": ["greeting": words, "style": style, "apiKeySet": keySet]]
}
