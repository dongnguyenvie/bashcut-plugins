"""Checks a plugin.json against the rules BashCut applies when it loads a plugin (PluginManifest.validate in the app).

    from plugin_manifest import manifest_problems
    problems = manifest_problems(json.load(open("plugin.json")))   # [] when the manifest is valid

`scripts/new-plugin.py` checks every manifest it writes, and its CI test checks every template, so templates never
drift from the API. The app stays the authority: this mirrors its rules, it does not replace them.
"""
import re

SCHEMA = "bashcut.plugin/1"
API_MINIMUM = 1
API_CURRENT = 5
# Capabilities BashCut wires today (docs/guides/plugins.md › Capabilities).
CAPABILITIES = ("voice.synthesize", "captions.transcribe", "audio.beats", "audio.loudness", "audio.sync",
                "agent.chat", "agent.terminal")
# Store categories for listing.json. One list for the registry, the scaffold and (#63) the app's category filter.
CATEGORIES = ("agents", "captions", "voice", "audio", "color", "effects", "export", "utilities")
OPTION_TYPES = ("string", "enum", "number", "integer", "bool", "file", "secret")
PLACEMENTS = {
    "menu.plugins", "toolbar", "clip.context", "track.context", "timeline.context", "media.context",
    "panel.media", "panel.audio", "panel.text", "panel.stickers", "panel.effects", "panel.transitions",
    "panel.filters", "panel.voice",
    "inspector.video", "inspector.audio", "inspector.text", "inspector.color", "inspector.speed",
}
CONTEXT_PARTS = {"timeline", "media", "project"}
HOOK_EVENTS = {
    "app.launched", "project.created", "project.opened", "project.saved", "project.closed",
    "edit.committed", "edit.undone", "edit.redone", "selection.changed", "playback.stopped",
    "media.imported", "captions.generated", "beats.detected", "voice.generated",
    "export.started", "export.finished", "export.failed", "job.finished", "plugin.action.finished",
}
FREQUENT_EVENTS = {"edit.committed", "edit.undone", "edit.redone", "selection.changed", "playback.stopped"}

ID_PATTERN = r"[a-z0-9]+(?:[.-][a-z0-9]+)+"
CAPABILITY_PATTERN = r"[a-z0-9]+(?:[.-][a-z0-9]+)*"
VERSION_PATTERN = r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?"
OPTION_ID_PATTERN = r"[A-Za-z][A-Za-z0-9_-]{0,63}"
LANGUAGE_PATTERN = r"[a-z]{2,3}(-[A-Za-z0-9]{2,8})?"


def text_ok(value, limit=None):
    """Display text: a nonempty string (English) or a language map that includes "en" when it has several keys."""
    values = [value] if isinstance(value, str) else list(value.values()) if isinstance(value, dict) else None
    if not values or not all(isinstance(v, str) and v.strip() for v in values):
        return False
    if isinstance(value, dict):
        if len(value) > 1 and "en" not in value:
            return False
        if not all(re.fullmatch(LANGUAGE_PATTERN, key) for key in value):
            return False
    return limit is None or all(len(v) <= limit for v in values)


def relative_path_ok(path):
    return isinstance(path, str) and path and not path.startswith("/") and ".." not in path.split("/")


def option_problems(option, where, is_param=False):
    problems = []
    option_id, kind = option.get("id", ""), option.get("type")
    if not re.fullmatch(OPTION_ID_PATTERN, str(option_id)):
        problems.append(f"{where}: id must be a letter then up to 63 letters, digits, _ or -")
    if not text_ok(option.get("title")):
        problems.append(f"{where}: title is required (a string or a language map with \"en\")")
    for field in ("help",):
        if field in option and not text_ok(option[field]):
            problems.append(f"{where}: {field} must be a string or a language map with \"en\"")
    if any(key.endswith("Vi") for key in option):
        problems.append(f'{where}: use {{"en": …, "vi": …}} instead of *Vi fields')
    if kind not in OPTION_TYPES:
        problems.append(f"{where}: type must be one of {', '.join(OPTION_TYPES)}")
    if kind == "enum":
        choices = option.get("choices") or []
        if not 1 <= len(choices) <= 100 or len(set(choices)) != len(choices):
            problems.append(f"{where}: enum needs 1–100 unique choices")
        if "default" in option and option["default"] not in choices:
            problems.append(f"{where}: default must be one of the choices")
    if kind == "secret":
        if is_param:
            problems.append(f"{where}: action parameters cannot be secrets")
        if option.get("scope", "user") != "user" or "default" in option:
            problems.append(f"{where}: a secret needs user scope and no default")
    if option.get("scope", "user") not in ("user", "project"):
        problems.append(f"{where}: scope must be user or project")
    if option.get("bindsSecrets") and kind in ("secret", "file"):
        problems.append(f"{where}: bindsSecrets is not allowed on {kind} options")
    return problems


def manifest_problems(manifest):
    """Every rule the manifest breaks, as readable sentences; an empty list means BashCut will load it."""
    problems = []
    if manifest.get("schema") != SCHEMA:
        problems.append(f"schema must be {SCHEMA}")
    plugin_id = manifest.get("id", "")
    if not re.fullmatch(ID_PATTERN, str(plugin_id)):
        problems.append("id must be reverse-domain style, such as author.my-plugin")
    if not text_ok(manifest.get("name"), limit=80):
        problems.append("name is required, up to 80 characters")
    if not re.fullmatch(VERSION_PATTERN, str(manifest.get("version", ""))):
        problems.append("version must be semantic, such as 0.0.1")
    api = manifest.get("apiVersion")
    minimum = manifest.get("minApiVersion", api)
    if not isinstance(api, int) or not isinstance(minimum, int) or not API_MINIMUM <= minimum <= api:
        problems.append(f"apiVersion must be {API_MINIMUM}–{API_CURRENT} and minApiVersion no higher than it")
        api = minimum = API_CURRENT
    if not relative_path_ok(manifest.get("entrypoint")):
        problems.append("entrypoint must be a relative path inside the plugin folder")

    capabilities = manifest.get("capabilities")
    contributes = manifest.get("contributes") or {}
    actions, hooks = contributes.get("actions", []), contributes.get("hooks", [])
    if not isinstance(capabilities, list):
        problems.append("capabilities is required (it may be [] when the plugin contributes actions or hooks)")
        capabilities = []
    if not capabilities and not actions and not hooks:
        problems.append("a plugin needs a capability, an action or a hook")
    if len(set(capabilities)) != len(capabilities) or not all(re.fullmatch(CAPABILITY_PATTERN, c) for c in capabilities):
        problems.append("capabilities must be unique lowercase identifiers")
    providers = manifest.get("providers", [])
    if len({p.get("id") for p in providers}) != len(providers):
        problems.append("provider ids must be unique")
    for provider in providers:
        if provider.get("capability") not in capabilities:
            problems.append(f'provider {provider.get("id")}: its capability must be listed in capabilities')
        if not provider.get("name"):
            problems.append(f'provider {provider.get("id")}: name is required')
        if not 10 <= provider.get("timeoutSeconds", 120) <= 3600:
            problems.append(f'provider {provider.get("id")}: timeoutSeconds must be 10–3600')

    dependency_ids = [d.get("id") for d in manifest.get("dependencies", [])]
    if len(set(dependency_ids)) != len(dependency_ids):
        problems.append("dependency ids must be unique")
    for dependency in manifest.get("dependencies", []):
        commands = [dependency.get("probe", {})] + ([dependency["install"].get("command", {})]
                                                    if dependency.get("install") else [])
        for command in commands:
            executable = command.get("executable", "")
            if not executable or ("/" in executable and not relative_path_ok(executable)):
                problems.append(f'dependency {dependency.get("id")}: commands must stay inside the plugin folder')

    transport = manifest.get("transport", "oneshot")
    options = manifest.get("options", [])
    if transport not in ("oneshot", "session"):
        problems.append("transport must be oneshot or session")
    if (options or contributes or transport == "session") and api < 2:
        problems.append("options, contributes and the session transport need apiVersion 2")
    params = [p for a in actions for p in a.get("params", [])]
    if any(o.get("type") == "file" or "choiceLabels" in o for o in options + params) and api < 3:
        problems.append("file options and choiceLabels need apiVersion 3")
    if (any(o.get("type") == "secret" for o in options) or "agent.chat" in capabilities) and api < 4:
        problems.append("secret options and agent.chat need apiVersion 4")
    if "agent.chat" in capabilities and transport != "session":
        problems.append("agent.chat needs \"transport\": \"session\"")
    if ("agent.terminal" in capabilities) != ("terminal" in manifest):
        problems.append("agent.terminal and the terminal object go together")
    if "agent.terminal" in capabilities and api < 5:
        problems.append("agent.terminal needs apiVersion 5")

    if len({o.get("id") for o in options}) != len(options) or len(options) > 64:
        problems.append("option ids must be unique (at most 64)")
    for option in options:
        problems += option_problems(option, f'option {option.get("id")}')

    if len({a.get("id") for a in actions}) != len(actions) or len(actions) > 64:
        problems.append("action ids must be unique (at most 64)")
    for action in actions:
        where = f'action {action.get("id")}'
        if not str(action.get("id", "")).startswith(f"{plugin_id}."):
            problems.append(f"{where}: id must start with the plugin id and a dot")
        if not text_ok(action.get("title"), limit=80):
            problems.append(f"{where}: title is required, up to 80 characters")
        if "confirm" in action and not text_ok(action["confirm"]):
            problems.append(f"{where}: confirm must be a string or a language map with \"en\"")
        placements = action.get("placements") or []
        if not placements or not set(placements) <= PLACEMENTS:
            problems.append(f"{where}: placements must be one or more of the documented placements")
        if not set(action.get("context", [])) <= CONTEXT_PARTS:
            problems.append(f"{where}: context parts are timeline, media and project")
        if len(action.get("params", [])) > 32:
            problems.append(f"{where}: at most 32 params")
        for param in action.get("params", []):
            problems += option_problems(param, f'{where} param {param.get("id")}', is_param=True)

    events = [h if isinstance(h, str) else h.get("event") for h in hooks]
    if len(set(events)) != len(events):
        problems.append("each hook event may appear once")
    for hook in hooks:
        event = hook if isinstance(hook, str) else hook.get("event")
        if event not in HOOK_EVENTS:
            problems.append(f"unknown hook event {event}")
        elif event in FREQUENT_EVENTS and transport != "session":
            problems.append(f'hook {event} fires often and needs "transport": "session"')
        if isinstance(hook, dict) and not 0 <= hook.get("debounceMs", 0) <= 60000:
            problems.append(f"hook {event}: debounceMs must be 0–60000")
    return problems
