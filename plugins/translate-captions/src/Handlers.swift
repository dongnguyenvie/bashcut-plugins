// Translate Captions: three actions.
//
// - bashcut.translate-captions.translate: translates every caption on the caption layers with the user's own Gemini or
//   OpenAI key and keeps its timing and look (Translate.swift). Without a key it says to ask the agent, whose skill
//   does the same through `captions export` and `timeline apply`.
// - bashcut.translate-captions.cover: finds subtitles burned into the picture in the first seconds of each video and
//   hides them under a dark band or by zooming them out of the frame (Cover.swift).
// - bashcut.translate-captions.install-preset: saves the "Vietsub TikTok" batch preset (Preset.swift).
//
// Actions return proposed operations; BashCut applies them as one undoable edit with this plugin as the author.
// https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#actions
import Foundation

func handle(method: String, params: JSON, host: Host) throws -> Any? {
    if method == "options.check" { return checkOption(params) }
    guard method == "plugin.action" else { throw PluginError("unknown_method", "Translate Captions does not handle \(method)") }
    let action = params["action"] as? String ?? ""
    switch action {
    case "bashcut.translate-captions.translate": return try translate(params, host: host)
    case "bashcut.translate-captions.cover": return try cover(params, host: host)
    case "bashcut.translate-captions.install-preset": return try installPreset(params)
    default: throw PluginError("unknown_action", "Unknown action \(action)")
    }
}

/// What every action reads from the request.
struct ActionRequest {
    let params: JSON
    let options: JSON
    let context: JSON
    let outputDirectory: String?

    init(_ request: JSON) {
        params = request["params"] as? JSON ?? [:]
        options = request["options"] as? JSON ?? [:]
        context = request["context"] as? JSON ?? [:]
        outputDirectory = request["outputDirectory"] as? String
    }

    var project: JSON { context["project"] as? JSON ?? [:] }
    var rev: Int? { project["rev"] as? Int }
    var pluginData: JSON { context["pluginData"] as? JSON ?? [:] }

    func string(_ key: String, _ fallback: String) -> String {
        (params[key] as? String).flatMap { $0.isEmpty ? nil : $0 } ?? fallback
    }

    func number(_ key: String, _ fallback: Double) -> Double {
        (params[key] as? NSNumber)?.doubleValue ?? fallback
    }

    func bool(_ key: String, _ fallback: Bool) -> Bool {
        (params[key] as? Bool) ?? fallback
    }

    /// The tracks of the `timeline` context part.
    var tracks: [JSON] { context["tracks"] as? [JSON] ?? [] }

    /// Project frames per second, from `[numerator, denominator]`.
    var fps: Double {
        let rate = project["fps"] as? [Any] ?? []
        let numbers = rate.compactMap { ($0 as? NSNumber)?.doubleValue }
        return numbers.count == 2 && numbers[1] > 0 ? numbers[0] / numbers[1] : 30
    }
}

/// This plugin's pluginData with `key` set to `value`, keeping what the other actions stored.
func mergedPluginData(_ request: ActionRequest, _ key: String, _ value: Any) -> JSON {
    var data = request.pluginData
    data[key] = value
    return data
}

/// The caption items on the caption layers, in time order.
func captionItems(_ tracks: [JSON]) -> [JSON] {
    tracks.filter { ($0["role"] as? String) == "captions" && ($0["kind"] as? String ?? "text") == "text" }
        .flatMap { $0["items"] as? [JSON] ?? [] }
        .filter { !(($0["text"] as? String) ?? "").trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
        .sorted { ($0["at"] as? Int ?? 0) < ($1["at"] as? Int ?? 0) }
}
