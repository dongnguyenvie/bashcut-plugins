"""{{NAME}}: the action {{ACTION_ID}}.

BashCut calls `handle` with method "plugin.action" when someone runs the action (menu, context menu, shortcut,
`bashcut plugins run`). The result only *proposes* operations in the `timeline apply` format; BashCut validates them
and applies one undoable edit. https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#actions
"""
import uuid

from bashcut_plugin import PluginError


def handle(method, params, host):
    if method != "plugin.action":
        raise PluginError("unknown_method", f"{{PLAIN_NAME}} does not handle {method}")
    if params.get("action") == "{{ACTION_ID}}":
        return add_marker(params)
    raise PluginError("unknown_action", f"Unknown action {params.get('action')}")


def add_marker(params):
    context = params["context"]
    label = (params.get("params") or {}).get("label") or "Marker"
    frame = context["playhead"]
    return {
        "label": "Add marker",
        "baseRev": context["project"]["rev"],
        "operations": [{"op": "upsertSection", "id": str(uuid.uuid4()), "label": label, "atFrame": frame}],
        "ui": {"reveal": frame},
        "message": f"Added {label} at frame {frame}",
    }
