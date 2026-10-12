"""{{NAME}}: a panel in BashCut's left rail with three views (plugin API 8).

- "main" (the rail panel): a counter kept in `state`, a button that reads the timeline over the host channel while
  the view shows progress, and a button that opens the sheet.
- "media" (a tab in the agent dock): the project's media as a list whose rows drag onto the timeline (`file`) and
  measure their loudness with another plugin's audio.loudness (plugins.invoke, listed in "uses", then a job).
- "form" (a sheet): a short form that closes itself with "close": true.

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
        host.call("plugins.show-view", {"plugin": PLUGIN_ID, "view": "form"})
        return {"message": "Opened the form"}
    raise PluginError("unknown_method", f"{{PLAIN_NAME}} does not handle {method}")


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
        host.call("plugins.show-view", {"plugin": PLUGIN_ID, "view": "form"})
    return {
        "title": "{{PLAIN_NAME}}",
        "state": {"count": count, "message": message},
        "body": [
            {"type": "text", "text": f"Clicked **{count}** times", "markdown": True},
            {"type": "row", "children": [
                {"type": "button", "id": "add", "title": "Add one", "icon": "plus", "style": "primary"},
                {"type": "button", "id": "timeline", "title": "Read the timeline", "icon": "film"},
            ]},
            {"type": "button", "id": "openForm", "title": "Open the form", "icon": "macwindow"},
            {"type": "text", "text": message, "style": "caption"} if message else {"type": "spacer", "size": 0},
        ],
    }


def media_view(params, state, values, event, host):
    message = state.get("message", "")
    media = state.get("media")
    if media is None or event.get("node") == "refresh":
        answer = host.call("media.list")
        items = answer if isinstance(answer, list) else (answer or {}).get("media") or []
        media = [{"id": m.get("id"), "name": m.get("name") or os.path.basename(str(m.get("path", ""))),
                  "kind": m.get("kind", ""), "path": m.get("absolutePath") or m.get("path") or ""}
                 for m in items if isinstance(m, dict) and m.get("id")]
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
            {"type": "text", "text": message, "style": "caption"} if message else {"type": "spacer", "size": 0},
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
            {"type": "text", "text": problem, "style": "caption", "color": "red"} if problem else {"type": "spacer", "size": 0},
            {"type": "row", "children": [
                {"type": "button", "id": "cancel", "title": "Cancel"},
                {"type": "spacer"},
                {"type": "button", "id": "save", "title": "Save", "style": "primary"},
            ]},
        ],
    }


VIEWS = {"main": main_view, "media": media_view, "form": form_view}
