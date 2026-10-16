"""{{NAME}}: a panel in BashCut's left rail with four views (plugin API 11).

- "main" (the rail panel): a counter kept in `state`, a button that reads the timeline over the host channel while
  the view shows progress, and buttons that open the sheet and the window.
- "media" (a tab in the agent dock): the project's media as a list whose rows drag onto the timeline (`file`) and
  measure their loudness with another plugin's audio.loudness (plugins.invoke, listed in "uses", then a job).
- "form" (a sheet): a short form that closes itself with "close": true.
- "browse" (a window): a `split` of three columns, a `nav` of media kinds, a `grid` of the media whose tiles drag
  onto the timeline, and the selected tile's details with a button that places it at the playhead (media.place).

Views are answers, not widgets: BashCut sends view.render (draw) or view.event (the user did something) and the
plugin answers with the whole component tree. Keep what you need between requests in `state`.
https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#plugin-panels-and-views
"""
import os

from bashcut_plugin import HOST_FEATURES, PluginError

PLUGIN_ID = "{{ID}}"


def handle(method, params, host):
    if method in ("view.render", "view.event"):
        view = VIEWS.get(params.get("view"))
        if view is None:
            raise PluginError("unknown_view", f"{{PLAIN_NAME}} has no view {params.get('view')}")
        return view(params, params.get("state") or {}, params.get("values") or {}, params.get("event") or {}, host)
    if method == "plugin.action" and params.get("action") == "{{ACTION_ID}}":
        show_view(host, "form")
        return {"message": "Opened the form"}
    raise PluginError("unknown_method", f"{{PLAIN_NAME}} does not handle {method}")


def show_view(host, view):
    """Opens one of this plugin's sheets or windows (never another plugin's)."""
    host.call("plugins.show-view", {"plugin": PLUGIN_ID, "view": view})


def note(message, **extra):
    return {"type": "text", "text": message, "style": "caption", **extra} if message else {"type": "spacer", "size": 0}


def load_media(host):
    """The project's media as {id, name, kind, path}; `path` is absolute when the file is on this Mac."""
    answer = host.call("media.list")
    items = answer if isinstance(answer, list) else (answer or {}).get("media") or []
    return [{"id": m.get("id"), "name": m.get("name") or os.path.basename(str(m.get("path", ""))),
             "kind": m.get("kind", ""), "path": m.get("absolutePath") or m.get("path") or ""}
            for m in items if isinstance(m, dict) and m.get("id")]


def main_view(params, state, values, event, host):
    count, message = state.get("count", 0), state.get("message", "")
    node = event.get("node")
    if node == "add":
        count += 1
    elif node == "timeline":
        host.render([{"type": "progress", "label": "Reading the timeline…"}])
        timeline = host.call("timeline.get") or {}
        message = f"The timeline has {len(timeline.get('tracks') or [])} layers."
    elif node == "openForm":
        show_view(host, "form")
    elif node == "openBrowser":
        show_view(host, "browse")
    return {
        "title": "{{PLAIN_NAME}}",
        "state": {"count": count, "message": message},
        "body": [
            {"type": "text", "text": f"Clicked **{count}** times", "markdown": True},
            {"type": "row", "children": [
                {"type": "button", "id": "add", "title": "Add one", "icon": "plus", "style": "primary"},
                {"type": "button", "id": "timeline", "title": "Read the timeline", "icon": "film"},
            ]},
            {"type": "row", "children": [
                {"type": "button", "id": "openForm", "title": "Open the form", "icon": "square.and.pencil"},
                {"type": "button", "id": "openBrowser", "title": "Open the browser", "icon": "macwindow"},
            ]},
            note(message),
        ],
    }


def media_view(params, state, values, event, host):
    message = state.get("message", "")
    media = state.get("media")
    if media is None or event.get("node") == "refresh":
        media = load_media(host)
    if event.get("node") == "media" and event.get("type") == "action":
        row = next((m for m in media if m["id"] == (event.get("value") or {}).get("item")), None)
        if row:
            # A capability without its own command: plugins.invoke runs as a job; wait_job polls it.
            measured = host.wait_job(host.call("plugins.invoke", {
                "capability": "audio.loudness", "params": {"mediaPath": row["path"]}})) or {}
            lufs = (measured.get("result") or measured).get("integratedLUFS")
            message = f"{row['name']}: {lufs} LUFS" if lufs is not None else f"{row['name']}: no loudness"
    rows = [{"id": m["id"], "title": m["name"], "subtitle": m["kind"], "icon": "film",
             # An absolute path to a local file lets the row drag onto the timeline (host feature views.drag).
             **({"file": m["path"]} if os.path.isabs(m["path"]) else {}),
             "actions": [{"id": "loudness", "title": "Measure loudness", "icon": "speedometer"}]} for m in media]
    return {
        "title": "Media",
        "state": {"media": media, "message": message},
        "body": [
            {"type": "button", "id": "refresh", "title": "Refresh", "icon": "arrow.clockwise"},
            {"type": "list", "id": "media", "items": rows, "empty": "No media in the project"},
            note(message),
        ],
    }


def form_view(params, state, values, event, host):
    node = event.get("node")
    if node == "cancel":
        return {"body": [], "close": True, "state": {}}
    problem = ""
    if node in ("save", "title"):
        title = str(values.get("title") or "").strip()
        if title:
            host.call("ui.action", {"action": "notify", "target": f"Saved {title} ({values.get('color', '')})"})
            return {"body": [], "close": True, "state": {}, "notify": "Saved"}
        problem = "Write a title first."
    # Newer components: check the hello's features and fall back to a text field in an older BashCut.
    color = ({"type": "colorPicker", "id": "color", "label": "Colour", "value": values.get("color") or "#FF8800"}
             if "views.colorPicker" in HOST_FEATURES else
             {"type": "textField", "id": "color", "label": "Colour (hex)", "value": values.get("color") or "#FF8800"})
    return {
        "title": "Form",
        "body": [
            {"type": "textField", "id": "title", "label": "Title", "placeholder": "Chapter 1", "submit": True},
            color,
            note(problem, color="red"),
            {"type": "row", "children": [
                {"type": "button", "id": "cancel", "title": "Cancel"},
                {"type": "spacer"},
                {"type": "button", "id": "save", "title": "Save", "style": "primary"},
            ]},
        ],
    }


KINDS = [("all", "All", "square.grid.2x2"), ("video", "Video", "film"), ("audio", "Audio", "waveform"),
         ("image", "Images", "photo")]


def browse_view(params, state, values, event, host):
    """A window (API 11): it stays open next to the editor and keeps its state when closed. One `split` as the whole
    body fills the window and scrolls each column on its own; narrower than 900 pt, the side columns fold into
    disclosures named by their section's `label`."""
    node, kind_of_event, value = event.get("node"), event.get("type"), event.get("value")
    media, kind, focus, message = state.get("media"), state.get("kind", "all"), state.get("focus"), ""
    if media is None or node == "refresh":
        media = load_media(host)
    if node == "kinds" and kind_of_event == "select":  # a nav entry: value is its id
        kind, focus = value, None
    elif node == "items" and kind_of_event == "select":  # a grid tile: value is its id
        focus = value
    chosen = next((m for m in media if m["id"] == focus), None)
    if node == "place" and chosen:
        playhead = int((params.get("context") or {}).get("playhead") or 0)
        host.call("media.place", {"media": chosen["id"], "atFrame": playhead, "baseRev": "last"})
        message = f"Placed {chosen['name']} at frame {playhead}"
    icons = {key: icon for key, _, icon in KINDS}
    shown = [m for m in media if kind == "all" or m["kind"] == kind]
    nav = {"type": "nav", "id": "kinds", "value": kind, "groups": [{"title": "Media", "items": [
        {"id": key, "title": title, "icon": icon, "count": len([m for m in media if key == "all" or m["kind"] == key])}
        for key, title, icon in KINDS]}]}
    tiles = [{"id": m["id"], "title": m["name"], "subtitle": m["kind"], "icon": icons.get(m["kind"], "doc"),
              # A local file drags onto the timeline, like the dock's list rows.
              **({"file": m["path"]} if os.path.isabs(m["path"]) else {})} for m in shown]
    details = [{"type": "text", "text": "Select a tile", "style": "secondary"}]
    if chosen:
        details = [
            {"type": "text", "text": chosen["name"], "style": "heading"},
            {"type": "keyValue", "items": [{"key": "Kind", "value": chosen["kind"] or "—"},
                                           {"key": "Path", "value": chosen["path"] or "—"}]},
            {"type": "button", "id": "place", "title": "Add at playhead", "icon": "plus", "style": "primary"},
        ]
    return {
        "title": "Browser",
        "state": {"media": media, "kind": kind, "focus": focus},
        "body": [{"type": "split", "widths": [180, "flex", 260], "children": [
            {"type": "section", "label": "Kinds", "children": [nav]},
            {"type": "section", "children": [
                {"type": "row", "children": [
                    {"type": "text", "text": "Drag a tile onto the timeline.", "style": "secondary"},
                    {"type": "spacer"},
                    {"type": "button", "id": "refresh", "title": "Refresh", "icon": "arrow.clockwise"},
                ]},
                {"type": "grid", "id": "items", "items": tiles, "selected": focus, "cellWidth": 140,
                 "aspect": 16 / 9, "empty": "No media of this kind"},
            ]},
            {"type": "section", "label": "Details", "children": [*details, note(message)]},
        ]}],
    }


VIEWS = {"main": main_view, "media": media_view, "form": form_view, "browse": browse_view}
