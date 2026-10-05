// {{NAME}}: hooks on export.finished and media.imported.
//
// BashCut calls `handle` with method "plugin.hook" after an event. Hooks are notify-only: the event already happened.
// A hook declared with "edits": true may return operations or pluginData, which BashCut applies as one undoable edit
// (or keeps for review). https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#hooks
import Foundation

func handle(method: String, params: JSON, host: Host) throws -> Any? {
    guard method == "plugin.hook" else { throw PluginError("unknown_method", "{{PLAIN_NAME}} does not handle \(method)") }
    let payload = params["payload"] as? JSON ?? [:]
    switch params["event"] as? String {
    case "export.finished":
        // Count exports in this plugin's own project data.
        let pluginData = (params["context"] as? JSON)?["pluginData"] as? JSON
        let exports = (pluginData?["exports"] as? Int ?? 0) + 1
        let output = payload["output"] as? String ?? ""
        return [
            "label": "Remember last export",
            "pluginData": ["lastExport": output, "exports": exports],
            "message": "Exported \((output as NSString).lastPathComponent) (export \(exports))",
        ]
    case "media.imported":
        return ["message": "Imported \((payload["media"] as? [Any])?.count ?? 0) media"]
    default:
        return JSON()
    }
}
