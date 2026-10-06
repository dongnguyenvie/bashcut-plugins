"""Checks a plugin.json against the rules BashCut applies when it loads a plugin (PluginManifest.validate in the app).

    from plugin_manifest import manifest_problems, skill_problems
    problems = manifest_problems(json.load(open("plugin.json")))   # [] when the manifest is valid
    problems += skill_problems(folder, manifest)                     # the SKILL.md files contributes.skills names

`scripts/new-plugin.py` checks every manifest it writes, and its CI test checks every template, so templates never
drift from the API. The app stays the authority: this mirrors its rules, it does not replace them.
"""
import pathlib
import re

SCHEMA = "bashcut.plugin/1"
API_MINIMUM = 1
API_CURRENT = 8
# Capabilities BashCut wires today (docs/guides/plugins.md › Capabilities).
CAPABILITIES = ("voice.synthesize", "captions.transcribe", "audio.beats", "audio.loudness", "audio.sync",
                "agent.chat", "agent.terminal")
# Plugin categories, in BashCut's display order (PluginCategory in the app). listing.json and plugin.json may only
# name one of these; scripts/build-registry.py --check rejects anything else.
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
SKILL_NAME_PATTERN = r"[a-z0-9]+(?:-[a-z0-9]+)*"
# contributes.skills limits (PluginSkillContribution in the app).
MAX_SKILLS, MAX_SKILL_TEXT, MAX_SKILL_FOLDER = 16, 64 * 1024, 2 * 1024 * 1024
MAX_SKILL_NAME, MAX_SKILL_DESCRIPTION = 64, 1024
# Plugin API 8 (PluginComposition.swift in the app): the rail panel, views, requires, uses and host features.
MAX_VIEWS, MAX_REQUIRES, MAX_USES, MAX_FEATURES = 8, 16, 32, 32
SYMBOL_PATTERN = r"[a-z0-9]+(?:\.[a-z0-9]+)*"
VERSION_RANGE_PATTERN = r"\*|(?:(?:\^|~|>=|<=|>|<|=)?[0-9]+(?:\.[0-9]+){0,2}(?:-[A-Za-z0-9.-]+)?)(?: +(?:(?:\^|~|>=|<=|>|<|=)?[0-9]+(?:\.[0-9]+){0,2}(?:-[A-Za-z0-9.-]+)?))*"
VIEW_LOCATIONS = ("panel", "dock", "sheet")
FEATURE_PATTERN = r"[a-z][a-zA-Z0-9]*(?:[.-][a-zA-Z0-9]+)*"


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
    if "category" in manifest and manifest["category"] not in CATEGORIES:
        problems.append(f"category must be one of {', '.join(CATEGORIES)}")

    capabilities = manifest.get("capabilities")
    contributes = manifest.get("contributes") or {}
    actions, hooks = contributes.get("actions", []), contributes.get("hooks", [])
    library, skills = contributes.get("library", []), contributes.get("skills", [])
    if not isinstance(capabilities, list):
        problems.append("capabilities is required (it may be [] when the plugin contributes something)")
        capabilities = []
    container, views = contributes.get("container"), contributes.get("views", [])
    if not capabilities and not actions and not hooks and not library and not skills and not container and not views:
        problems.append("a plugin needs a capability, an action, a hook, a library pack, a skill or a panel")
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
    if library and api < 6:
        problems.append("contributes.library needs apiVersion 6")
    if skills and api < 7:
        problems.append("contributes.skills needs apiVersion 7")
    skill_paths = [s.get("path") if isinstance(s, dict) else None for s in skills]
    if len(skills) > MAX_SKILLS or len({str(p).rstrip("/") for p in skill_paths}) != len(skills):
        problems.append(f"contributes.skills lists at most {MAX_SKILLS} different skill folders")
    for path in skill_paths:
        if not relative_path_ok(path) or path.startswith("~"):
            problems.append(f"skill path {path} must stay inside the plugin folder")

    problems += composition_problems(manifest, api, transport, container, views)

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


def composition_problems(manifest, api, transport, container, views):
    """contributes.container and views, requires, uses and features (plugin API 8)."""
    problems = []
    requires, uses, features = manifest.get("requires"), manifest.get("uses"), manifest.get("features")
    if container is None and not views and requires is None and uses is None and features is None:
        return problems
    if api < 8:
        problems.append("contributes.container, contributes.views, requires, uses and features need apiVersion 8")
    if container is not None:
        if not re.fullmatch(SYMBOL_PATTERN, str(container.get("icon", ""))) or len(str(container.get("icon"))) > 64:
            problems.append("contributes.container.icon must be an SF Symbol name")
        if "title" in container and not text_ok(container["title"], limit=24):
            problems.append("contributes.container.title needs at most 24 characters per language")
    if views:
        if container is None and any(v.get("location", "panel") == "panel" for v in views):
            problems.append("panel views need contributes.container (dock and sheet views do not)")
        if transport != "session":
            problems.append('contributes.views needs "transport": "session"')
    if len(views) > MAX_VIEWS or len({v.get("id") for v in views}) != len(views):
        problems.append(f"view ids must be unique (at most {MAX_VIEWS})")
    for view in views:
        if not re.fullmatch(OPTION_ID_PATTERN, str(view.get("id", ""))):
            problems.append(f'view {view.get("id")}: id must be a short key')
        if not text_ok(view.get("title"), limit=40):
            problems.append(f'view {view.get("id")}: title is required, up to 40 characters')
        if view.get("location", "panel") not in VIEW_LOCATIONS:
            problems.append(f'view {view.get("id")}: location must be one of {", ".join(VIEW_LOCATIONS)}')
        if "icon" in view and not re.fullmatch(SYMBOL_PATTERN, str(view["icon"])):
            problems.append(f'view {view.get("id")}: icon must be an SF Symbol name')
    requires = requires or []
    if len(requires) > MAX_REQUIRES or len({r.get("id") for r in requires}) != len(requires):
        problems.append(f"requires lists at most {MAX_REQUIRES} different plugins")
    for requirement in requires:
        if not re.fullmatch(ID_PATTERN, str(requirement.get("id", ""))) or requirement.get("id") == manifest.get("id"):
            problems.append(f'requires: {requirement.get("id")} must be another plugin\'s id')
        if not re.fullmatch(VERSION_RANGE_PATTERN, str(requirement.get("version", "*")).strip()):
            problems.append(f'requires {requirement.get("id")}: invalid version range {requirement.get("version")}')
    uses = uses or []
    if len(uses) > MAX_USES or len(set(uses)) != len(uses) \
            or not all(re.fullmatch(CAPABILITY_PATTERN, str(c)) for c in uses):
        problems.append(f"uses lists at most {MAX_USES} different capability ids")
    if {"agent.chat", "agent.terminal"} & set(uses):
        problems.append("uses cannot name agent.chat or agent.terminal")
    features = features or []
    if len(features) > MAX_FEATURES or len(set(features)) != len(features) \
            or not all(re.fullmatch(FEATURE_PATTERN, str(f)) for f in features):
        problems.append(f"features lists at most {MAX_FEATURES} different feature names")
    return problems


def front_matter(text):
    """The `key: value` lines between the first two `---` lines of a SKILL.md, quotes removed."""
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
                value = value[1:-1]
            fields.setdefault(key.strip(), value)
    return {}


def skill_problems(folder, manifest):
    """What BashCut would refuse in the skill folders `contributes.skills` names (PluginSkills.read in the app):
    each resolves inside the plugin, has a SKILL.md whose front matter `name` is the folder name and has a
    `description`, and stays within the size limits. BashCut leaves such a skill out; publishing refuses it."""
    folder = pathlib.Path(folder)
    base = folder.resolve()
    problems = []
    for entry in (manifest.get("contributes") or {}).get("skills", []):
        path = entry.get("path") if isinstance(entry, dict) else None
        where = f"skill {path}"
        if not relative_path_ok(path):
            continue  # manifest_problems reports it
        skill = (folder / path).resolve()
        if base not in skill.parents:
            problems.append(f"{where}: the folder is outside the plugin")
            continue
        text_file = skill / "SKILL.md"
        if not text_file.is_file() or base not in text_file.resolve().parents:
            problems.append(f"{where}: the folder has no SKILL.md")
            continue
        total = 0
        for item in skill.rglob("*"):
            if item.is_symlink() and base not in item.resolve().parents:
                problems.append(f"{where}: {item.name} links outside the plugin")
            if item.is_file():
                total += item.stat().st_size
        if total > MAX_SKILL_FOLDER:
            problems.append(f"{where}: the folder is larger than {MAX_SKILL_FOLDER // 1024 // 1024} MB")
        data = text_file.read_bytes()
        if len(data) > MAX_SKILL_TEXT:
            problems.append(f"{where}: SKILL.md is larger than {MAX_SKILL_TEXT // 1024} KB")
            continue
        fields = front_matter(data.decode("utf-8", errors="replace"))
        name, description = fields.get("name", ""), fields.get("description", "")
        if not re.fullmatch(SKILL_NAME_PATTERN, name) or len(name) > MAX_SKILL_NAME:
            problems.append(f"{where}: front matter name must be lowercase words joined by - (at most {MAX_SKILL_NAME})")
        elif name != skill.name:
            problems.append(f"{where}: front matter name {name} must match the folder {skill.name}")
        if not description or len(description) > MAX_SKILL_DESCRIPTION:
            problems.append(f"{where}: front matter needs a description of at most {MAX_SKILL_DESCRIPTION} characters")
    return problems
