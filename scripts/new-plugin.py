#!/usr/bin/env python3
"""Creates a new BashCut plugin from a template, ready to test, dev-link and trust.

    scripts/new-plugin.py <slug> --template <template> [--name "My Plugin"] [--name-vi "…"] [--id author.my-plugin]
                          [--lang swift|shell|node|python] [--capability <id>] [--category <id>]
                          [--out <dir>] [--private]

Templates:
    capability   a provider for a capability (--capability voice.synthesize, captions.transcribe, audio.beats,
                 audio.loudness or audio.sync), with the request and result already wired
    action       a contributes.actions command that proposes a timeline edit (a marker at the playhead)
    hook         contributes.hooks subscribers (export.finished with pluginData, media.imported)
    options      options of every type, including a secret, read by an action
    chat-agent   an agent.chat session plugin: a tab in the agent dock that streams events and calls BashCut

Languages (--lang):
    swift   compiled by build.sh into a universal binary; nothing to install on users' Macs (default)
    shell   POSIX sh and macOS built-ins (plutil reads the JSON); one-shot templates only, not chat-agent
    node    plain ES modules; Node.js is found on the Mac or downloaded by the install recipe (bin/setup)
    python  standard library only; needs a python3, which the registry refuses (see "Rules for users who are
            not developers" in README.md): fine for private plugins, bring your own Python with uv to publish

By default the plugin goes to plugins/<slug> with listing.json and an empty versions.json, ready for the registry.
--private, or --out outside this repo's plugins/ folder, makes a standalone plugin in <out>/<slug> (default: the
current folder) for people who keep their plugin to themselves. Every manifest is checked before anything is written
(scripts/plugin_manifest.py), and an existing folder is never overwritten.
"""
import argparse
import json
import os
import pathlib
import re
import shutil
import stat
import sys
import tempfile

from plugin_manifest import API_CURRENT, CATEGORIES, manifest_problems

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = pathlib.Path(__file__).resolve().parent / "plugin-templates"
REPO_URL = "https://github.com/dongnguyenvie/bashcut-plugins"

TEMPLATE_NAMES = ("capability", "action", "hook", "options", "chat-agent")
LANGUAGES = {"swift": "Swift", "shell": "POSIX sh", "node": "JavaScript (Node.js)", "python": "Python"}
PROVIDED_CAPABILITIES = ("voice.synthesize", "captions.transcribe", "audio.beats", "audio.loudness", "audio.sync")
SESSION_TEMPLATES = {"chat-agent"}
SLUG_PATTERN = r"[a-z0-9]+(?:-[a-z0-9]+)*"
# Names end up inside generated string literals of every language, so they stay plain.
NAME_PATTERN = r"[^\"'\\`$\n\r\t{}]{1,80}"

SUMMARIES = {
    "capability": ("Provides {capability} for BashCut.", "Cung cấp {capability} cho BashCut."),
    "action": ("Adds a marker at the playhead.", "Thêm mốc tại playhead."),
    "hook": ("Remembers each export and announces imported media.", "Ghi nhớ mỗi lần xuất và báo khi nhập media."),
    "options": ("Shows how plugin options work, including a secret API key.",
                "Minh hoạ các loại tuỳ chọn của plugin, kể cả khoá API bí mật."),
    "chat-agent": ("A chat agent in BashCut's agent dock.", "Trợ lý trò chuyện trong agent dock của BashCut."),
}
DEFAULT_CATEGORIES = {"voice.synthesize": "voice", "captions.transcribe": "captions", "chat-agent": "agents",
                      "audio.beats": "audio", "audio.loudness": "audio", "audio.sync": "audio"}


def fail(message):
    sys.exit(f"error: {message}")


def title_from_slug(slug):
    return " ".join(part.capitalize() for part in slug.split("-"))


def text(en, vi=None):
    return {"en": en, "vi": vi} if vi else en


# --- plugin.json -------------------------------------------------------------------------------------------------

def dependencies_for(lang):
    if lang == "python":
        return [{"id": "python", "name": "Python 3", "kind": "executable",
                 "probe": {"executable": "python3", "arguments": ["--version"]}}]
    if lang == "node":
        return [{
            "id": "node", "name": "Node.js 22", "kind": "executable",
            "probe": {"executable": "bin/check", "arguments": []},
            "install": {"summary": "Download the official Node.js 22 LTS for this Mac from nodejs.org (about 50 MB) "
                                   "into the plugin's data folder, checked against its published SHA-256. A Node.js "
                                   "22 or newer already on this Mac is used instead.",
                        "command": {"executable": "bin/setup", "arguments": []}},
            "estimatedBytes": 200000000,
        }]
    return []


def contribution_for(template, plugin_id, name, capability):
    """The template-specific part of the manifest: capabilities, providers, transport, options, contributes."""
    action_id = f"{plugin_id}.add-marker" if template == "action" else f"{plugin_id}.show-options"
    if template == "capability":
        provider = f"{plugin_id}.{capability.split('.')[-1]}"
        return 2, {"capabilities": [capability],
                   "providers": [{"id": provider, "capability": capability, "name": name, "priority": 10}]}
    if template == "action":
        return 2, {"capabilities": [], "contributes": {"actions": [{
            "id": action_id,
            "title": text("Add marker at playhead…", "Thêm mốc tại playhead…"),
            "icon": "flag",
            "placements": ["menu.plugins", "timeline.context"],
            "when": "project && timeline",
            "params": [{"id": "label", "title": text("Label", "Nhãn"), "type": "string", "default": "Marker"}],
        }]}}
    if template == "hook":
        return 2, {"capabilities": [], "contributes": {"hooks": [{"event": "export.finished", "edits": True},
                                                                 "media.imported"]}}
    if template == "options":
        # A plugin with a secret keeps every option on this Mac (user scope).
        return 4, {"capabilities": [], "options": [
            {"id": "greeting", "title": text("Greeting", "Lời chào"), "type": "string", "default": "Hello",
             "maxLength": 200, "scope": "user"},
            {"id": "style", "title": text("Style", "Kiểu"), "type": "enum", "choices": ["short", "long"],
             "default": "short", "scope": "user",
             "choiceLabels": {"short": text("Short", "Ngắn"), "long": text("Long", "Dài")}},
            {"id": "repeat", "title": text("Repeat", "Lặp lại"), "type": "integer", "minimum": 1, "maximum": 5,
             "default": 1, "scope": "user"},
            {"id": "shout", "title": text("Shout", "Viết hoa"), "type": "bool", "default": False, "scope": "user"},
            {"id": "apiKey", "title": text("API key", "Khoá API"), "type": "secret", "scope": "user",
             "help": text("Kept in the macOS Keychain and sent only to this plugin.",
                          "Lưu trong Keychain của macOS và chỉ gửi cho plugin này.")},
        ], "contributes": {"actions": [{
            "id": action_id, "title": text("Show options", "Xem tuỳ chọn"), "icon": "slider.horizontal.3",
            "placements": ["menu.plugins"],
        }]}}
    if template == "chat-agent":
        provider = f"{plugin_id}.chat"
        return 4, {"transport": "session", "capabilities": ["agent.chat"],
                   "providers": [{"id": provider, "capability": "agent.chat", "name": name, "priority": 10,
                                  "timeoutSeconds": 300}],
                   "options": [{"id": "greeting", "title": text("Greeting", "Lời chào"), "type": "string",
                                "default": "Hello", "scope": "user"}]}
    raise ValueError(template)


def build_manifest(args):
    minimum, part = contribution_for(args.template, args.id, args.name, args.capability)
    manifest = {"schema": "bashcut.plugin/1", "id": args.id, "name": text(args.name, args.name_vi),
                "version": "0.0.1", "apiVersion": API_CURRENT, "minApiVersion": minimum, "entrypoint": "bin/provider",
                "category": args.category}
    if "transport" in part:
        manifest["transport"] = part.pop("transport")
    manifest["capabilities"] = part.pop("capabilities")
    manifest.update({k: part.pop(k) for k in ("providers",) if k in part})
    manifest["dependencies"] = dependencies_for(args.lang)
    manifest.update(part)
    return manifest


# --- source files ------------------------------------------------------------------------------------------------

MARKER = re.compile(r"^\s*(?:#|//)\s*@@\s+(.+?)\s*$")


def keep_blocks(source, key):
    """Drops `@@ <keys>` … blocks that are not for `key`; `@@ end` closes a block. Marker lines go away."""
    lines, keeping = [], True
    for line in source.splitlines(keepends=True):
        match = MARKER.match(line)
        if match:
            keys = match.group(1).split()
            keeping = keys == ["end"] or key in keys
            continue
        if keeping:
            lines.append(line)
    return "".join(lines)


def render(source, values):
    for key, value in values.items():
        source = source.replace("{{" + key + "}}", value)
    leftover = re.search(r"\{\{[A-Z_]+\}\}", source)
    if leftover:
        raise ValueError(f"unfilled placeholder {leftover.group(0)}")
    return source


def source_files(lang, template):
    """(destination, template file, executable) for the language runtime and the template's handlers."""
    files = {
        "python": [("bin/provider", "python/provider", True), ("bin/bashcut_plugin.py", "python/bashcut_plugin.py", False),
                   ("bin/handlers.py", f"python/{template}.py", False)],
        "node": [("bin/provider", "node/provider", True), ("bin/find-node", "node/find-node", True),
                 ("bin/check", "node/check", True), ("bin/setup", "node/setup", True),
                 ("lib/main.mjs", "node/main.mjs", False), ("lib/bashcut-plugin.mjs", "node/bashcut-plugin.mjs", False),
                 ("lib/handlers.mjs", f"node/{template}.mjs", False)],
        "shell": [("bin/provider", "shell/provider", True), ("bin/bashcut-plugin.sh", "shell/bashcut-plugin.sh", False),
                  ("bin/handlers.sh", f"shell/{template}.sh", False)],
        "swift": [("build.sh", "swift/build.sh", True), ("src/main.swift", "swift/main.swift", False),
                  ("src/Handlers.swift", f"swift/{template}.swift", False)],
    }[lang]
    return files + [("tests/test_plugin.py", None, False)]


FILE_NOTES = {
    "plugin.json": "manifest (`bashcut.plugin/1`): id, API version, capabilities, options, contributions",
    "listing.json": "store listing for the registry: name, summary, category, platforms",
    "versions.json": "published versions; `scripts/package.py --register` fills it at release",
    "bin/provider": "the entrypoint BashCut runs (`provider rpc` or `provider session`)",
    "bin/handlers.py": "**your code**", "lib/handlers.mjs": "**your code**", "bin/handlers.sh": "**your code**",
    "src/Handlers.swift": "**your code**",
    "bin/bashcut_plugin.py": "the protocol (requests, responses, progress, host calls)",
    "lib/bashcut-plugin.mjs": "the protocol (requests, responses, progress, host calls)",
    "bin/bashcut-plugin.sh": "the protocol and JSON helpers (`bc_get`, `bc_str`, `bc_fail`…)",
    "src/main.swift": "the protocol (requests, responses, progress, host calls)",
    "lib/main.mjs": "starts the protocol with your handlers",
    "bin/find-node": "finds Node.js 22+ (plugin data folder, Homebrew, nvm, Volta, PATH)",
    "bin/check": "dependency probe: is Node.js there?",
    "bin/setup": "install recipe: downloads Node.js after the user approves",
    "build.sh": "builds `bin/provider` (universal binary) from `src/`; not shipped",
    "bin/provider (built)": "the entrypoint BashCut runs, built by `build.sh` (not in git)",
    "tests/test_plugin.py": "smoke tests that run the entrypoint like BashCut; not shipped",
}


def readme(args, files, registry):
    rel = f"plugins/{args.slug}" if registry else str(args.folder)
    build = "./build.sh\n" if args.lang == "swift" else ""
    tests = f"cd {rel}\n{build}python3 -m unittest discover -s tests -v"
    if registry:
        try_it = f"From the repo root:\n\n```sh\nscripts/dev-link.sh {args.slug}            # link into BashCut's " \
                 f"plugin folder\nscripts/dev-link.sh {args.slug} --remove   # unlink\n```"
        publish = (f"\n## Publish\n\nWrite a real summary in `listing.json`, then follow [Publishing]({REPO_URL}#publishing):"
                   f" merge to `main`, then tag `{args.slug}-v<version>`. Versions stay `0.0.x` while plugins are in beta.\n")
    else:
        try_it = (f"Link the folder into BashCut's plugin folder (with a `bashcut-plugins` checkout, "
                  f"`scripts/dev-link.sh {args.folder}` does the same):\n\n```sh\n"
                  f"ln -sfn \"{args.folder}\" \"$HOME/Library/Application Support/BashCut/Plugins/{args.id}\"\n```\n\n"
                  "Or copy the folder there, or use **Add plugin…** in BashCut once it is available.")
        publish = ""
    after = ""
    if args.lang == "node":
        after = "\nWithout a Node.js 22 on the Mac, BashCut shows **Install Dependencies…**, which runs `bin/setup`.\n"
    if args.lang == "python" and registry:
        after = ("\nThe registry refuses a `python3` dependency (users' Macs may not have one): before publishing, bring a "
                 "Python with `uv` like `plugins/vieneu-tts`, or switch to Swift, shell or Node.\n")
    if args.lang == "swift":
        files = set(files) | {"bin/provider (built)"}
    lines = [f"- `{path.split(' ')[0]}`: {FILE_NOTES[path]}" for path in sorted(files) if path in FILE_NOTES]
    page = render((TEMPLATES / "README.md").read_text(), {
        "PLAIN_NAME": args.name, "SUMMARY": args.summary, "ID": args.id, "TEMPLATE": args.template,
        "LANG_NAME": LANGUAGES[args.lang], "FILES": "\n".join(lines), "TEST_COMMANDS": tests, "TRY_IT": try_it,
        "TRY_IT_AFTER": after, "PUBLISH": publish,
    })
    return re.sub(r"\n{3,}", "\n\n", page).rstrip("\n") + "\n"


def generate(args, registry, staging):
    """Writes every file into `staging`; returns the manifest."""
    manifest = build_manifest(args)
    problems = manifest_problems(manifest)
    if problems:
        fail("the generated manifest is invalid:\n  " + "\n  ".join(problems))
    providers = manifest.get("providers", [])
    actions = manifest.get("contributes", {}).get("actions", [])
    values = {
        "ID": args.id, "NAME": args.name, "PLAIN_NAME": args.name, "CAPABILITY": args.capability or "",
        "PROVIDER_ID": providers[0]["id"] if providers else "", "ACTION_ID": actions[0]["id"] if actions else "",
    }
    block_key = args.capability or args.template
    written = {}

    def write(path, content, executable=False):
        target = staging / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        if executable:
            target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        written[path] = target

    write("plugin.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    for destination, source, executable in source_files(args.lang, args.template):
        if source is None:  # the smoke tests: shared harness + the template's tests
            content = (TEMPLATES / "tests/harness.py").read_text() + (TEMPLATES / f"tests/{args.template}.py").read_text()
        else:
            content = (TEMPLATES / source).read_text()
        write(destination, render(keep_blocks(content, block_key), values), executable)
    if registry:
        en, vi = SUMMARIES[args.template]
        listing = {
            "name": {"en": args.name, "vi": args.name_vi or args.name},
            "summary": {"en": en.format(capability=args.capability), "vi": vi.format(capability=args.capability)},
            "publisher": "bashcut",
            "category": args.category,
            "homepage": f"{REPO_URL}/tree/main/plugins/{args.slug}",
            "minAppVersion": "0.0.1",
            "platforms": ["macos-arm64", "macos-x86_64"],
        }
        write("listing.json", json.dumps(listing, indent=2, ensure_ascii=False) + "\n")
        write("versions.json", json.dumps({"id": args.id, "listing": {}, "versions": []}, indent=2) + "\n")
    write("README.md", readme(args, set(written) | {"README.md"}, registry))
    return manifest


# --- checks and main ---------------------------------------------------------------------------------------------

def ids_in_repo():
    ids = set()
    for path in list(ROOT.glob("plugins/*/plugin.json")) + list(ROOT.glob("samples/*/plugin.json")):
        try:
            ids.add(json.loads(path.read_text()).get("id"))
        except ValueError:
            pass
    registry = ROOT / "registry.json"
    if registry.is_file():
        ids.update(entry["id"] for entry in json.loads(registry.read_text()).get("plugins", []))
    return ids


def ignore_build_output(slug):
    """Swift plugins build bin/provider; keep it out of git like the other compiled plugins."""
    path = ROOT / ".gitignore"
    line = f"plugins/{slug}/bin/provider"
    lines = path.read_text().splitlines() if path.is_file() else []
    if line not in lines:
        path.write_text("\n".join(lines + [line]) + "\n")


def parse(argv):
    parser = argparse.ArgumentParser(description="Create a new BashCut plugin from a template.",
                                     formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__.split("\n\n", 2)[2])
    parser.add_argument("slug", help="folder name: lowercase letters, digits and dashes, such as my-plugin")
    parser.add_argument("--template", required=True, choices=TEMPLATE_NAMES)
    parser.add_argument("--name", help="display name (default: from the slug)")
    parser.add_argument("--name-vi", help="Vietnamese display name (default: the same as --name)")
    parser.add_argument("--id", help="plugin id (default: bashcut.<slug> in the registry, local.<slug> when private)")
    parser.add_argument("--lang", choices=tuple(LANGUAGES), default="swift")
    parser.add_argument("--capability", choices=PROVIDED_CAPABILITIES,
                        help="for --template capability (default: audio.beats)")
    parser.add_argument("--category", choices=CATEGORIES, help="category in plugin.json and listing.json")
    parser.add_argument("--out", help="parent folder of the new plugin (default: plugins/ in this repo)")
    parser.add_argument("--private", action="store_true", help="a standalone plugin, outside the registry layout")
    args = parser.parse_args(argv)

    if not re.fullmatch(SLUG_PATTERN, args.slug):
        parser.error("the slug must be lowercase letters and digits joined by dashes, such as my-plugin")
    if args.template == "capability":
        args.capability = args.capability or "audio.beats"
    elif args.capability:
        parser.error("--capability is only for --template capability")
    if args.lang == "shell" and args.template in SESSION_TEMPLATES:
        parser.error(f"--template {args.template} needs the session transport; use --lang swift, node or python")
    args.name = args.name or title_from_slug(args.slug)
    for value in (args.name, args.name_vi):
        if value is not None and not re.fullmatch(NAME_PATTERN, value):
            parser.error("names are up to 80 characters without quotes, backslashes, $, braces or line breaks")
    plugins = (ROOT / "plugins").resolve()
    parent = pathlib.Path(args.out).expanduser().resolve() if args.out else (pathlib.Path.cwd() if args.private else plugins)
    args.registry = not args.private and parent == plugins
    args.folder = parent / args.slug
    args.id = args.id or (f"bashcut.{args.slug}" if args.registry else f"local.{args.slug}")
    args.category = args.category or DEFAULT_CATEGORIES.get(args.capability or args.template, "utilities")
    en, _ = SUMMARIES[args.template]
    args.summary = en.format(capability=args.capability)
    return args


def next_steps(args):
    rel = f"plugins/{args.slug}" if args.registry else str(args.folder)
    steps = []
    if args.lang == "swift":
        steps.append(f"{rel}/build.sh                                  # build bin/provider")
    steps.append(f"python3 -m unittest discover -s {rel}/tests -v    # run the smoke tests")
    steps.append(f"scripts/dev-link.sh {args.slug if args.registry else rel}" + "   # link it into BashCut")
    steps.append("open Plugins in BashCut and choose Trust")
    if args.registry:
        steps.append(f"edit {rel}/listing.json (summary), then merge and tag {args.slug}-v0.0.1 to publish")
    return steps


def main(argv=None):
    args = parse(argv)
    if args.folder.exists():
        fail(f"{args.folder} already exists; choose another slug or remove it")
    if args.id in ids_in_repo():
        fail(f"the id {args.id} is already used by a plugin in this repo or the registry; pass --id")
    args.folder.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.folder.parent, prefix=f".{args.slug}.") as staging:
        generate(args, args.registry, pathlib.Path(staging))
        shutil.move(staging, args.folder)
        # TemporaryDirectory cleans up a path that no longer exists; recreate it so the exit does not fail.
        os.makedirs(staging, exist_ok=True)
    args.folder.chmod(0o755)
    if args.registry and args.lang == "swift":
        ignore_build_output(args.slug)
    print(f"Created {args.id} ({args.template}, {LANGUAGES[args.lang]}) in {args.folder}")
    if args.lang == "python" and args.registry:
        print("note: the registry refuses a python3 dependency; bring a Python with uv (plugins/vieneu-tts) before "
              "publishing, or use --lang swift, shell or node", file=sys.stderr)
    print("\nNext:")
    for number, step in enumerate(next_steps(args), 1):
        print(f"  {number}. {step}")


if __name__ == "__main__":
    main()
