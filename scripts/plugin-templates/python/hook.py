"""{{NAME}}: hooks on export.finished and media.imported.

BashCut calls `handle` with method "plugin.hook" after an event. Hooks are notify-only: the event already happened.
A hook declared with "edits": true may return operations or pluginData, which BashCut applies as one undoable edit
(or keeps for review). https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#hooks
"""
import os

from bashcut_plugin import PluginError


def handle(method, params, host):
    if method != "plugin.hook":
        raise PluginError("unknown_method", f"{{PLAIN_NAME}} does not handle {method}")
    event, payload = params.get("event"), params.get("payload") or {}
    if event == "export.finished":
        # Count exports in this plugin's own project data.
        exports = ((params.get("context") or {}).get("pluginData") or {}).get("exports", 0)
        output = payload.get("output") or ""
        return {
            "label": "Remember last export",
            "pluginData": {"lastExport": output, "exports": exports + 1},
            "message": f"Exported {os.path.basename(output)} (export {exports + 1})",
        }
    if event == "media.imported":
        return {"message": f"Imported {len(payload.get('media') or [])} media"}
    return {}
