"""{{NAME}}: options of every kind, read by the action {{ACTION_ID}}.

BashCut draws the options in Settings › Plugins and sends their current values as params["options"] with every
request. The secret (apiKey) comes from the Keychain: use it, never print or return it.
https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#options
"""
from bashcut_plugin import PluginError


def handle(method, params, host):
    if method != "plugin.action":
        raise PluginError("unknown_method", f"{{PLAIN_NAME}} does not handle {method}")
    if params.get("action") != "{{ACTION_ID}}":
        raise PluginError("unknown_action", f"Unknown action {params.get('action')}")
    options = params.get("options") or {}
    greeting = options.get("greeting") or "Hello"
    if options.get("shout"):
        greeting = greeting.upper()
    words = " ".join([greeting] * int(options.get("repeat") or 1))
    key_set = bool(options.get("apiKey"))
    summary = {
        "greeting": words,
        "style": options.get("style", "short"),
        "apiKeySet": key_set,
    }
    detail = f" (style {summary['style']}, API key {'set' if key_set else 'not set'})" if summary["style"] == "long" else ""
    return {"message": words + detail, "data": summary}
