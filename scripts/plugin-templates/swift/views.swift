// {{NAME}}: a panel in BashCut's left rail with four views (plugin API 11).
//
// - "main" (the rail panel): a counter kept in `state`, a button that reads the timeline over the host channel while
//   the view shows progress, and buttons that open the sheet and the window.
// - "media" (a tab in the agent dock): the project's media as a list whose rows drag onto the timeline (`file`) and
//   measure their loudness with another plugin's audio.loudness (plugins.invoke, listed in "uses", then a job).
// - "form" (a sheet): a short form that closes itself with "close": true.
// - "browse" (a window): a `split` of three columns, a `nav` of media kinds, a `grid` of the media whose tiles drag
//   onto the timeline, and the selected tile's details with a button that places it at the playhead (media.place).
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
        case "browse": return try browseView(params, state, event, host)
        default: throw PluginError("unknown_view", "{{PLAIN_NAME}} has no view \(params["view"] ?? "")")
        }
    }
    if method == "plugin.action", params["action"] as? String == "{{ACTION_ID}}" {
        try showView(host, "form")
        return ["message": "Opened the form"]
    }
    throw PluginError("unknown_method", "{{PLAIN_NAME}} does not handle \(method)")
}

/// Opens one of this plugin's sheets or windows (never another plugin's).
func showView(_ host: Host, _ view: String) throws {
    _ = try host.call("plugins.show-view", ["plugin": pluginID, "view": view])
}

/// The project's media as {id, name, kind, path}; `path` is absolute when the file is on this Mac.
func loadMedia(_ host: Host) throws -> [JSON] {
    let answer = try host.call("media.list")
    let items = answer as? [JSON] ?? (answer as? JSON)?["media"] as? [JSON] ?? []
    return items.compactMap { item in
        guard let id = item["id"] as? String else { return nil }
        let path = item["absolutePath"] as? String ?? item["path"] as? String ?? ""
        return ["id": id, "name": item["name"] as? String ?? (path as NSString).lastPathComponent,
                "kind": item["kind"] as? String ?? "", "path": path]
    }
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
        try showView(host, "form")
    case "openBrowser":
        try showView(host, "browse")
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
            ["type": "row", "children": [
                ["type": "button", "id": "openForm", "title": "Open the form", "icon": "square.and.pencil"],
                ["type": "button", "id": "openBrowser", "title": "Open the browser", "icon": "macwindow"],
            ]],
            note(message),
        ] as [JSON],
    ]
}

func mediaView(_ state: JSON, _ event: JSON, _ host: Host) throws -> JSON {
    var message = state["message"] as? String ?? ""
    var media = state["media"] as? [JSON]
    if media == nil || event["node"] as? String == "refresh" { media = try loadMedia(host) }
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

let kinds: [(id: String, title: String, icon: String)] = [
    ("all", "All", "square.grid.2x2"), ("video", "Video", "film"), ("audio", "Audio", "waveform"), ("image", "Images", "photo"),
]

// A window (API 11): it stays open next to the editor and keeps its state when closed. One `split` as the whole body
// fills the window and scrolls each column on its own; narrower than 900 pt, the side columns fold into disclosures
// named by their section's `label`.
func browseView(_ params: JSON, _ state: JSON, _ event: JSON, _ host: Host) throws -> JSON {
    let node = event["node"] as? String, type = event["type"] as? String
    var media = state["media"] as? [JSON]
    var kind = state["kind"] as? String ?? "all"
    var focus = state["focus"] as? String
    var message = ""
    if media == nil || node == "refresh" { media = try loadMedia(host) }
    let all = media ?? []
    if node == "kinds", type == "select", let value = event["value"] as? String {  // a nav entry: value is its id
        kind = value
        focus = nil
    } else if node == "items", type == "select" {  // a grid tile: value is its id
        focus = event["value"] as? String
    }
    let chosen = all.first { $0["id"] as? String == focus }
    if node == "place", let chosen {
        let playhead = ((params["context"] as? JSON)?["playhead"] as? NSNumber)?.intValue ?? 0
        _ = try host.call("media.place", ["media": chosen["id"] ?? "", "atFrame": playhead, "baseRev": "last"])
        message = "Placed \(chosen["name"] ?? "") at frame \(playhead)"
    }
    func ofKind(_ key: String) -> [JSON] { all.filter { key == "all" || $0["kind"] as? String == key } }
    let nav: JSON = ["type": "nav", "id": "kinds", "value": kind, "groups": [["title": "Media", "items": kinds.map {
        ["id": $0.id, "title": $0.title, "icon": $0.icon, "count": ofKind($0.id).count] as JSON
    }]]]
    let tiles: [JSON] = ofKind(kind).map { item in
        let kindOfItem = item["kind"] as? String ?? ""
        var tile: JSON = ["id": item["id"] ?? "", "title": item["name"] ?? "", "subtitle": kindOfItem,
                          "icon": kinds.first { $0.id == kindOfItem }?.icon ?? "doc"]
        // A local file drags onto the timeline, like the dock's list rows.
        if let path = item["path"] as? String, path.hasPrefix("/") { tile["file"] = path }
        return tile
    }
    var details: [JSON] = [["type": "text", "text": "Select a tile", "style": "secondary"]]
    if let chosen {
        let kindText = (chosen["kind"] as? String).flatMap { $0.isEmpty ? nil : $0 } ?? "—"
        let pathText = (chosen["path"] as? String).flatMap { $0.isEmpty ? nil : $0 } ?? "—"
        details = [
            ["type": "text", "text": chosen["name"] ?? "", "style": "heading"],
            ["type": "keyValue", "items": [["key": "Kind", "value": kindText], ["key": "Path", "value": pathText]]],
            ["type": "button", "id": "place", "title": "Add at playhead", "icon": "plus", "style": "primary"],
        ]
    }
    let grid: JSON = ["type": "grid", "id": "items", "items": tiles, "selected": focus ?? NSNull(), "cellWidth": 140,
                      "aspect": 16.0 / 9.0, "empty": "No media of this kind"]
    return [
        "title": "Browser",
        "state": ["media": all, "kind": kind, "focus": focus ?? NSNull()] as JSON,
        "body": [["type": "split", "widths": [180, "flex", 260] as [Any], "children": [
            ["type": "section", "label": "Kinds", "children": [nav]],
            ["type": "section", "children": [
                ["type": "row", "children": [
                    ["type": "text", "text": "Drag a tile onto the timeline.", "style": "secondary"],
                    ["type": "spacer"],
                    ["type": "button", "id": "refresh", "title": "Refresh", "icon": "arrow.clockwise"],
                ]] as JSON,
                grid,
            ]],
            ["type": "section", "label": "Details", "children": details + [note(message)]],
        ] as [JSON]]] as [JSON],
    ]
}
