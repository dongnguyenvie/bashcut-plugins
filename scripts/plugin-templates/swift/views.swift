// {{NAME}}: a panel in BashCut's left rail with three views (plugin API 8).
//
// - "main" (the rail panel): a counter kept in `state`, a button that reads the timeline over the host channel while
//   the view shows progress, and a button that opens the sheet.
// - "media" (a tab in the agent dock): the project's media as a list whose rows drag onto the timeline (`file`) and
//   measure their loudness with another plugin's audio.loudness (plugins.invoke, listed in "uses", then a job).
// - "form" (a sheet): a short form that closes itself with "close": true.
//
// Views are answers, not widgets: BashCut sends view.render (draw) or view.event (the user did something) and the
// plugin answers with the whole component tree. Keep what you need between requests in `state`.
// https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#plugin-panels-and-views
import Foundation

let pluginID = "{{ID}}"

func handle(method: String, params: JSON, host: Host) throws -> Any? {
    if method == "view.render" || method == "view.event" {
        let state = params["state"] as? JSON ?? [:]
        let values = params["values"] as? JSON ?? [:]
        let event = params["event"] as? JSON ?? [:]
        switch params["view"] as? String {
        case "main": return try mainView(state, event, host)
        case "media": return try mediaView(state, event, host)
        case "form": return try formView(values, event, host)
        default: throw PluginError("unknown_view", "{{PLAIN_NAME}} has no view \(params["view"] ?? "")")
        }
    }
    if method == "plugin.action", params["action"] as? String == "{{ACTION_ID}}" {
        _ = try host.call("plugins.show-view", ["plugin": pluginID, "view": "form"])
        return ["message": "Opened the form"]
    }
    throw PluginError("unknown_method", "{{PLAIN_NAME}} does not handle \(method)")
}

func note(_ message: String, color: String? = nil) -> JSON {
    guard !message.isEmpty else { return ["type": "spacer", "size": 0] }
    var node: JSON = ["type": "text", "text": message, "style": "caption"]
    if let color { node["color"] = color }
    return node
}

func mainView(_ state: JSON, _ event: JSON, _ host: Host) throws -> JSON {
    var count = state["count"] as? Int ?? 0
    var message = state["message"] as? String ?? ""
    switch event["node"] as? String {
    case "add":
        count += 1
    case "timeline":
        try host.render([["type": "progress", "label": "Reading the timeline…"]])
        let timeline = try host.call("timeline.get") as? JSON ?? [:]
        message = "The timeline has \((timeline["tracks"] as? [Any])?.count ?? 0) layers."
    case "openForm":
        _ = try host.call("plugins.show-view", ["plugin": pluginID, "view": "form"])
    default:
        break
    }
    return [
        "title": "{{PLAIN_NAME}}",
        "state": ["count": count, "message": message],
        "body": [
            ["type": "text", "text": "Clicked **\(count)** times", "markdown": true],
            ["type": "row", "children": [
                ["type": "button", "id": "add", "title": "Add one", "icon": "plus", "style": "primary"],
                ["type": "button", "id": "timeline", "title": "Read the timeline", "icon": "film"],
            ]],
            ["type": "button", "id": "openForm", "title": "Open the form", "icon": "macwindow"],
            note(message),
        ] as [JSON],
    ]
}

func mediaView(_ state: JSON, _ event: JSON, _ host: Host) throws -> JSON {
    var message = state["message"] as? String ?? ""
    var media = state["media"] as? [JSON]
    if media == nil || event["node"] as? String == "refresh" {
        let answer = try host.call("media.list")
        let items = answer as? [JSON] ?? (answer as? JSON)?["media"] as? [JSON] ?? []
        media = items.compactMap { item in
            guard let id = item["id"] as? String else { return nil }
            let path = item["absolutePath"] as? String ?? item["path"] as? String ?? ""
            return ["id": id, "name": item["name"] as? String ?? (path as NSString).lastPathComponent,
                    "kind": item["kind"] as? String ?? "", "path": path]
        }
    }
    let rows = media ?? []
    if event["node"] as? String == "media", event["type"] as? String == "action",
        let item = (event["value"] as? JSON)?["item"] as? String, let row = rows.first(where: { $0["id"] as? String == item })
    {
        // A capability without its own command: plugins.invoke runs as a job; waitJob polls it.
        let started = try host.call("plugins.invoke", ["capability": "audio.loudness", "params": ["mediaPath": row["path"] ?? ""]])
        let measured = try host.waitJob(started) as? JSON ?? [:]
        let name = row["name"] as? String ?? item
        if let lufs = ((measured["result"] as? JSON) ?? measured)["integratedLUFS"] {
            message = "\(name): \(lufs) LUFS"
        } else {
            message = "\(name): no loudness"
        }
    }
    let list: [JSON] = rows.map { row in
        var entry: JSON = ["id": row["id"] ?? "", "title": row["name"] ?? "", "subtitle": row["kind"] ?? "", "icon": "film",
                           "actions": [["id": "loudness", "title": "Measure loudness", "icon": "speedometer"]]]
        // An absolute path to a local file lets the row drag onto the timeline (host feature views.drag).
        if let path = row["path"] as? String, path.hasPrefix("/") { entry["file"] = path }
        return entry
    }
    return [
        "title": "Media",
        "state": ["media": rows, "message": message],
        "body": [
            ["type": "button", "id": "refresh", "title": "Refresh", "icon": "arrow.clockwise"],
            ["type": "list", "id": "media", "items": list, "empty": "No media in the project"],
            note(message),
        ] as [JSON],
    ]
}

func formView(_ values: JSON, _ event: JSON, _ host: Host) throws -> JSON {
    let node = event["node"] as? String
    if node == "cancel" { return ["body": [JSON](), "close": true, "state": JSON()] }
    var problem = ""
    let colorValue = (values["color"] as? String).flatMap { $0.isEmpty ? nil : $0 } ?? "#FF8800"
    if node == "save" || node == "title" {
        let title = (values["title"] as? String ?? "").trimmingCharacters(in: .whitespaces)
        if !title.isEmpty {
            _ = try host.call("ui.action", ["action": "notify", "target": "Saved \(title) (\(colorValue))"])
            return ["body": [JSON](), "close": true, "state": JSON(), "notify": "Saved"]
        }
        problem = "Write a title first."
    }
    // Newer components: check the hello's features and fall back to a text field in an older BashCut.
    let color: JSON = hostFeatures.contains("views.colorPicker")
        ? ["type": "colorPicker", "id": "color", "label": "Colour", "value": colorValue]
        : ["type": "textField", "id": "color", "label": "Colour (hex)", "value": colorValue]
    return [
        "title": "Form",
        "body": [
            ["type": "textField", "id": "title", "label": "Title", "placeholder": "Chapter 1", "submit": true],
            color,
            note(problem, color: "red"),
            ["type": "row", "children": [
                ["type": "button", "id": "cancel", "title": "Cancel"],
                ["type": "spacer"],
                ["type": "button", "id": "save", "title": "Save", "style": "primary"],
            ]],
        ] as [JSON],
    ]
}
