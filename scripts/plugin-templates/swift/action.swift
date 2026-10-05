// {{NAME}}: the action {{ACTION_ID}}.
//
// BashCut calls `handle` with method "plugin.action" when someone runs the action (menu, context menu, shortcut,
// `bashcut plugins run`). The result only *proposes* operations in the `timeline apply` format; BashCut validates
// them and applies one undoable edit. https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#actions
import Foundation

func handle(method: String, params: JSON, host: Host) throws -> Any? {
    guard method == "plugin.action" else { throw PluginError("unknown_method", "{{PLAIN_NAME}} does not handle \(method)") }
    let action = params["action"] as? String ?? ""
    switch action {
    case "{{ACTION_ID}}": return try addMarker(params)
    default: throw PluginError("unknown_action", "Unknown action \(action)")
    }
}

func addMarker(_ params: JSON) throws -> JSON {
    guard let context = params["context"] as? JSON, let frame = context["playhead"] as? Int,
        let rev = (context["project"] as? JSON)?["rev"] as? Int
    else { throw PluginError("bad_request", "The request has no playhead or project revision") }
    let label = ((params["params"] as? JSON)?["label"] as? String).flatMap { $0.isEmpty ? nil : $0 } ?? "Marker"
    return [
        "label": "Add marker",
        "baseRev": rev,
        "operations": [["op": "upsertSection", "id": UUID().uuidString, "label": label, "atFrame": frame]],
        "ui": ["reveal": frame],
        "message": "Added \(label) at frame \(frame)",
    ]
}
