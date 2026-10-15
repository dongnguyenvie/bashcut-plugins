"""Online Resources (bashcut.resources): the Online resources sheet and its actions over the kit's fetch scripts.

One implementation for the user and the agent: the fetchers in ../scripts are the files the agent kit runs (its
skills keep thin shims that run these), and every button of the sheet is an action with a CommandSpec:

    bashcut plugins run bashcut.resources.search   --params '{"kind": "photo", "query": "coffee"}'
    bashcut plugins run bashcut.resources.download --params '{"kind": "photo", "query": "coffee", "ids": "…"}'
    bashcut plugins run bashcut.resources.fetch    --params '{"script": "stock", "args": "--query coffee"}'

The scripts call `bashcut …` as in a terminal; inside the plugin bin/bridge/bashcut forwards those words to this
session, which runs them as the host call `cli`. Downloads and previews go to BASHCUT_SHARED_CACHE/resources
(`library add` copies files into the library); the scripts' indexes stay where they keep them (BASHCUT_SHARED_DATA).
A search lists what the library already holds first and marks results that are already in it.
"""
import concurrent.futures
import contextlib
import hashlib
import importlib
import io
import json
import math
import os
import re
import shlex
import socket
import sys
import tempfile
import threading
from pathlib import Path

from bashcut_plugin import PluginError

PLUGIN_ID = "bashcut.resources"
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
PAGE = 24
MAX_RESULTS = 200
SCRIPT_NAMES = {"stock": "fetch_stock", "audio": "fetch_audio", "luts": "fetch_luts", "fonts": "fetch_fonts",
                "font": "fetch_font", "illustrations": "fetch_illustrations", "emoji": "fetch_emoji",
                "logos": "fetch_logos", "facts": "fetch_facts", "lottie": "fetch_lottie"}
KEYS = {"pexelsKey": "PEXELS_API_KEY", "pixabayKey": "PIXABAY_API_KEY", "freesoundKey": "FREESOUND_API_KEY"}

# kind → library kind, sources (the first is the default), grid cell shape
KINDS = {
    "photo": {"library": "clip", "sources": ["auto", "free", "wikimedia", "openverse", "nasa", "archive",
                                             "documentary", "pexels", "pixabay"], "cell": 130, "aspect": 1.3},
    "video": {"library": "clip", "sources": ["auto", "pexels", "pixabay", "nasa", "archive", "documentary"],
              "cell": 150, "aspect": 1.6},
    "music": {"library": "audio", "sources": ["openverse"], "cell": 170, "aspect": 3},
    "sfx": {"library": "audio", "sources": ["auto", "freesound", "mixkit", "openverse"], "cell": 170, "aspect": 3},
    "illustration": {"library": "sticker", "sources": ["auto", "open-peeps", "open-doodles", "humaaans", "undraw"],
                     "cell": 120, "aspect": 1},
    "emoji": {"library": "sticker", "sources": ["both", "noto", "openmoji"], "cell": 80, "aspect": 1},
    "logo": {"library": "sticker", "sources": ["simple-icons"], "cell": 90, "aspect": 1},
    "font": {"library": "text-preset", "sources": ["fontsource"], "cell": 170, "aspect": 3},
    "lut": {"library": "look", "sources": ["gmic,rawtherapee", "gmic", "rawtherapee"], "cell": 170, "aspect": 3},
    # The library refuses Lottie stickers: a download is a project file for the HyperFrames lottie widget.
    "lottie": {"library": None, "sources": ["all", "useanimations", "noto", "lottiefiles"], "cell": 120,
               "aspect": 1},
}
LABELS = {
    "photo": ("Photos", "Ảnh"), "video": ("Videos", "Video"), "music": ("Music", "Nhạc"),
    "sfx": ("Sound effects", "Hiệu ứng âm thanh"), "illustration": ("Illustrations", "Minh hoạ"),
    "emoji": ("Emoji", "Emoji"), "logo": ("Logos", "Logo"), "font": ("Fonts", "Phông chữ"), "lut": ("LUTs", "LUT"),
    "lottie": ("Lottie", "Lottie"),
}
TEXT = {
    "search": ("Search", "Tìm"),
    "placeholder": ("coffee, whoosh, figma…", "cà phê, whoosh, figma…"),
    "library": ("In your library", "Đã có trong thư viện"),
    "results": ("Online", "Trên mạng"),
    "inLibrary": ("In library", "Đã có"),
    "download": ("Download to Library", "Tải về thư viện"),
    "more": ("Load more", "Xem thêm"),
    "empty": ("Search free photos, videos, music, sound effects, stickers and fonts.",
              "Tìm ảnh, video, nhạc, hiệu ứng âm thanh, sticker và phông chữ miễn phí."),
    "try": ("Try:", "Thử:"),
    "type": ("Type", "Loại"),
    "source": ("Source", "Nguồn"),
    "scope": ("Save to", "Lưu vào"),
    "none": ("Nothing found.", "Không tìm thấy."),
    "scope.project": ("This project", "Project này"), "scope.user": ("My library (this Mac)", "Thư viện của tôi"),
    "sample": ("Sample text", "Chữ mẫu"),
    "fetchLuts": ("Fetch LUT packs", "Tải các gói LUT"),
    "orientation": ("Orientation", "Hướng"),
    "orientation.any": ("Any orientation", "Mọi hướng"), "orientation.portrait": ("Portrait", "Dọc"),
    "orientation.landscape": ("Landscape", "Ngang"), "orientation.square": ("Square", "Vuông"),
    "preview": ("Preview", "Nghe thử"),
    "selected": ("selected", "đã chọn"),
    "working": ("Working…", "Đang xử lý…"),
}


# Readable names for the source picker; a source without one shows its id.
SOURCE_NAMES = {
    "auto": ("Any free source", "Mọi nguồn miễn phí"), "free": ("Free (no key)", "Miễn phí (không cần key)"),
    "both": ("Noto + OpenMoji", "Noto + OpenMoji"), "all": ("All sources", "Mọi nguồn"),
    "gmic,rawtherapee": ("G'MIC + RawTherapee", "G'MIC + RawTherapee"), "wikimedia": ("Wikimedia Commons",) * 2,
    "openverse": ("Openverse",) * 2, "nasa": ("NASA",) * 2, "archive": ("Internet Archive",) * 2,
    "documentary": ("Documentary archives", "Kho tư liệu"), "pexels": ("Pexels",) * 2, "pixabay": ("Pixabay",) * 2,
    "freesound": ("Freesound",) * 2, "mixkit": ("Mixkit",) * 2, "open-peeps": ("Open Peeps",) * 2,
    "open-doodles": ("Open Doodles",) * 2, "humaaans": ("Humaaans",) * 2, "undraw": ("unDraw",) * 2,
    "noto": ("Noto",) * 2, "openmoji": ("OpenMoji",) * 2, "simple-icons": ("Simple Icons",) * 2,
    "fontsource": ("Fontsource",) * 2, "gmic": ("G'MIC",) * 2, "rawtherapee": ("RawTherapee",) * 2,
    "useanimations": ("useAnimations",) * 2, "lottiefiles": ("LottieFiles",) * 2,
}
SKELETON_TILES = 12  # placeholder tiles while a search runs
# Searches the empty sheet offers as buttons, per kind (search words stay English: the sources are).
EXAMPLES = {
    "photo": ["coffee", "city at night", "mountains"], "video": ["ocean waves", "street food", "timelapse"],
    "music": ["lofi", "upbeat", "piano"], "sfx": ["whoosh", "click", "pop"],
    "illustration": ["person", "working", "celebrate"], "emoji": ["fire", "heart", "laugh"],
    "logo": ["figma", "youtube", "github"], "font": ["serif", "handwriting", "display"], "lut": [],
    "lottie": ["loading", "check", "arrow"],
}


def tr(key, locale):
    pair = TEXT.get(key) or LABELS.get(key) or (key, key)
    return pair[1] if str(locale or "").startswith("vi") else pair[0]


def source_name(source, locale):
    pair = SOURCE_NAMES.get(source) or (source, source)
    return pair[1] if str(locale or "").startswith("vi") else pair[0]


def cache_dir(*parts):
    root = os.environ.get("BASHCUT_SHARED_CACHE") or str(Path.home() / "Library/Caches/BashCut/PluginData/_shared")
    folder = Path(root, "resources", *parts)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def module(name):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    return importlib.import_module(name)


def slug(text):
    return module("fetch_stock").slug(text)


def digest(text, n=10):
    return hashlib.sha1(str(text).encode()).hexdigest()[:n]


# --- the bridge: `bashcut` of the scripts → host call `cli` of the running request ------------------------------

class Bridge:
    def __init__(self):
        self.folder = tempfile.mkdtemp(prefix="bcres-")
        self.path = os.path.join(self.folder, "s")
        self.host = None
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.path)
        self.server.listen(16)
        threading.Thread(target=self.accept, daemon=True).start()

    def accept(self):
        while True:
            try:
                connection, _ = self.server.accept()
            except OSError:
                return
            threading.Thread(target=self.serve, args=(connection,), daemon=True).start()

    def serve(self, connection):
        with connection:
            data = b""
            while not data.endswith(b"\n"):
                chunk = connection.recv(1 << 16)
                if not chunk:
                    break
                data += chunk
            try:
                argv = json.loads(data or b"{}").get("argv") or []
                host = self.host
                if host is None:
                    raise PluginError("-32603", "No request is running")
                reply = {"result": host.call("cli", {"argv": [str(word) for word in argv]})}
            except PluginError as error:
                reply = {"error": {"code": int(error.code) if str(error.code).lstrip("-").isdigit() else error.code,
                                   "message": error.message}}
            except Exception as error:  # noqa: BLE001 - the script gets the failure as bashcut's error
                reply = {"error": {"code": -32603, "message": str(error) or type(error).__name__}}
            connection.sendall(json.dumps(reply, ensure_ascii=False).encode())


BRIDGE = None
_WORK = threading.RLock()


def start():
    """Puts bin/bridge first on PATH so the scripts' `bashcut` reaches this session."""
    global BRIDGE
    BRIDGE = Bridge()
    os.environ["PATH"] = str(ROOT / "bin" / "bridge") + os.pathsep + os.environ.get("PATH", "")
    os.environ["BASHCUT_RESOURCES_BRIDGE"] = BRIDGE.path
    os.environ["BASHCUT_RESOURCES_PYTHON"] = sys.executable
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


@contextlib.contextmanager
def working(host, options, label=None):
    """One fetch at a time: the bridge answers for this request, API keys come from the plugin's secret options,
    and a heartbeat keeps a long download from hitting the request's silence timeout."""
    with _WORK:
        saved = {env: os.environ.get(env) for env in KEYS.values()}
        for option, env in KEYS.items():
            value = (options or {}).get(option)
            if isinstance(value, str) and value.strip():
                os.environ[env] = value.strip()
            else:
                os.environ.pop(env, None)
        if BRIDGE is not None:
            BRIDGE.host = host
        stop = threading.Event()

        def beat():
            while not stop.wait(20):
                with contextlib.suppress(Exception):
                    host.progress(None, label)
        threading.Thread(target=beat, daemon=True).start()
        try:
            yield
        finally:
            stop.set()
            if BRIDGE is not None:
                BRIDGE.host = None
            for env, value in saved.items():
                if value is None:
                    os.environ.pop(env, None)
                else:
                    os.environ[env] = value


def run_script(name, argv):
    """Runs a script's main(argv) in this process; returns (stdout, stderr, exit status)."""
    script = module(name)
    out, err, status = io.StringIO(), io.StringIO(), 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            script.main([str(a) for a in argv])
        except SystemExit as stop:
            if isinstance(stop.code, str):
                err.write(stop.code + "\n")
                status = 1
            else:
                status = stop.code or 0
    return out.getvalue(), err.getvalue(), status


def json_lines(text):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("{"):
            with contextlib.suppress(ValueError):
                rows.append(json.loads(line))
    return rows


def fail_from(err, fallback):
    lines = [line for line in err.strip().splitlines() if line.strip()]
    return PluginError("fetch_failed", (lines[-1] if lines else fallback)[:300])


def small(url):
    """A grid cell needs about 320 px: Wikimedia's thumbnails are made at any width in the URL."""
    if "upload.wikimedia.org" in url and "/thumb/" in url:
        return re.sub(r"/\d{2,4}px-", "/320px-", url)
    return url


def fetch_previews(urls):
    """url → local file in the shared cache (downloaded once, in parallel); a failed one is left out."""
    folder = cache_dir("previews")
    get = module("fetch_stock").get

    def one(url):
        fetch_url = small(url)
        path = folder / f"{digest(url, 16)}{Path(url.split('?')[0]).suffix[:5] or '.jpg'}"
        if not path.exists() or path.stat().st_size == 0:
            try:
                path.write_bytes(get(fetch_url, timeout=30))
            except OSError:
                return url, None
        return url, str(path)
    wanted = [u for u in dict.fromkeys(urls) if u]
    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        return dict(pool.map(one, wanted))


# --- the library: what is there first, and which results it already holds ---------------------------------------

def library_items(host, kind, query=None, tag=None, limit=500):
    if not KINDS[kind]["library"]:
        return []
    params = {"kind": KINDS[kind]["library"], "limit": limit, "offset": 0}
    if query:
        params["query"] = query
    if tag:
        params["tag"] = tag
    try:
        answer = host.call("library.list", params)
    except PluginError:
        return []
    items = answer.get("items") if isinstance(answer, dict) else answer
    return [item for item in items or [] if isinstance(item, dict)]


def reference(item):
    ref = item.get("reference")
    if ref:
        return ref
    return f"{item.get('scope') or 'project'}:{item.get('id')}"


def library_index(host, kind):
    """library item id → reference, for every item of the kind (project, this Mac, packs)."""
    return {str(item.get("id")): reference(item) for item in library_items(host, kind)}


def library_preview(item):
    for key in ("preview", "thumbnail", "file", "path"):
        value = item.get(key)
        if isinstance(value, str) and value.startswith("/") and Path(value).suffix.lower() in (
                ".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".tif", ".tiff"):
            return value
    for value in (item.get("files") or {}).values() if isinstance(item.get("files"), dict) else []:
        if isinstance(value, str) and Path(value).suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            return value
    return None


def library_audio(item):
    for key in ("file", "path", "preview"):
        value = item.get(key)
        if isinstance(value, str) and value.startswith("/") and Path(value).suffix.lower() in (
                ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".aif", ".aiff"):
            return value
    return None


def library_first(host, kind, query):
    out = []
    for item in library_items(host, kind, query=query, limit=PAGE):
        if not (library_preview(item) or library_audio(item)) and item.get("id"):
            with contextlib.suppress(PluginError):  # list gives library-relative files; get gives fileURL
                got = host.call("library.get", {"id": item["id"], "scope": item.get("scope") or "project"}) or {}
                got = got.get("item", got) if isinstance(got, dict) else {}
                item = {**item, "file": got.get("fileURL") or item.get("file"), "preview": got.get("previewURL")}
        row = {"id": reference(item), "title": item.get("name") or item.get("id"),
               "tags": item.get("tags") or [], "libraryId": reference(item)}
        if library_preview(item):
            row["preview"] = library_preview(item)
        if library_audio(item):
            row["audio"] = library_audio(item)
        out.append(row)
    return out


# --- search per kind ---------------------------------------------------------------------------------------------

ROWS = {}  # item id → the script's full candidate row (url, licence …), for a download after the search


def resolve_source(kind, source):
    choices = KINDS[kind]["sources"]
    return source if source in choices else choices[0]


def search_stock(host, kind, query, source, page, orientation):
    stock = module("fetch_stock")
    try:
        name = stock.pick_source(None if source == "auto" else source, kind)
    except SystemExit as stop:
        raise PluginError("needs_key", f"{stop.code} (Plugins › Online Resources › Options)") from None
    count = min(page * PAGE, MAX_RESULTS)
    try:
        rows = stock.SEARCH[name](query, kind, orientation or "any", count, 1080)
    except (OSError, ValueError) as error:
        raise PluginError("search_failed", f"{name}: {error}"[:300]) from None
    rows = [r for r in rows if r.get("id")]
    shown = rows[(page - 1) * PAGE: page * PAGE]
    previews = fetch_previews([r.get("preview") or (r.get("frames") or [None])[0] for r in shown])
    known = library_index(host, kind)
    items = []
    for row in shown:
        key = f"{row['source']}-{row['id']}"
        ROWS[key] = {**row, "kind": kind}
        bits = [row["source"], row.get("size"), f"{row['seconds']} s" if row.get("seconds") else None]
        items.append({"id": key, "title": (row.get("tags") or key)[:80],
                      "subtitle": " · ".join(str(b) for b in bits if b),
                      "preview": previews.get(row.get("preview") or (row.get("frames") or [None])[0]),
                      "license": row.get("license"), "author": row.get("author"), "page": row.get("page"),
                      "inLibrary": known.get(stock.slug(key))})
    return name, items, (page + 1 if len(rows) >= count and count < MAX_RESULTS else None)


def audio_file(row):
    return cache_dir("audio", digest(row["url"])) / f"{row['stem']}{row['suffix']}"


def search_audio(host, kind, query, source, page):
    audio = module("fetch_audio")
    count = 6 if kind == "music" else 12  # Openverse gives 20 hits a request without a key: one page
    try:
        if kind == "music":
            rows, error = audio.music_candidates(query, count, 30), None
        else:
            rows, error = audio.sfx_candidates(query, source, 5, count)
    except (OSError, ValueError) as failure:
        raise PluginError("search_failed", str(failure)[:300]) from None
    if rows is None:
        raise PluginError("needs_key", f"{error} (Plugins › Online Resources › Options)")
    rows = rows[:count]
    shown = rows
    if kind == "sfx":  # effects are a few kB: fetch them now so every cell plays at once
        def one(row):
            path = audio_file(row)
            if not path.exists():
                with contextlib.suppress(OSError):
                    path.write_bytes(audio.get(row["url"], timeout=60))
        with concurrent.futures.ThreadPoolExecutor(8) as pool:
            list(pool.map(one, shown))
    known = library_index(host, kind)
    items = []
    for row in shown:
        key = digest(row["url"])
        ROWS[key] = {**row, "kind": kind}
        mark = "-" + key[:6]
        bits = [row.get("from") or "openverse", f"{row['seconds']} s" if row.get("seconds") else None,
                row.get("license")]
        path = audio_file(row)
        title = row.get("title") or query
        if title == query and row.get("url"):  # Mixkit has no titles: its file names say what the effect is
            stem = Path(row["url"].split("?")[0]).stem
            number = re.fullmatch(r"(\d+)-preview", stem)
            title = f"{query} {number.group(1)}" if number else (
                re.sub(r"^mixkit-|-\d+$", "", stem).replace("-", " ") or title)
        items.append({"id": key, "title": title[:80],
                      "subtitle": " · ".join(str(b) for b in bits if b),
                      "audio": str(path) if path.exists() else None, "license": row.get("license"),
                      "author": row.get("author"), "page": row.get("source"),
                      "inLibrary": next((ref for item_id, ref in known.items() if item_id.endswith(mark)), None)})
    return source, items, None


def search_emoji(host, query, source):
    dest = cache_dir("emoji", slug(query))
    out, err, status = run_script("fetch_emoji", ["--words", query, "--dest", dest, "--count", PAGE,
                                                  "--set", source])
    if status:
        raise fail_from(err, "emoji search failed")
    rows = json.loads((dest / "emoji.json").read_text())
    known = library_index(host, "emoji")
    items = []
    for row in rows:
        if not row.get("n"):
            continue
        wanted = (f"emoji-noto-{row['noto'].replace('_', '-')}" if row.get("set") == "noto"
                  else f"emoji-openmoji-{str(row.get('openmoji')).lower()}")
        path = row.get("file") or ""
        path = path if os.path.isabs(path) else str(dest / path)
        items.append({"id": f"{row['slot']}={row['n']}", "title": f"{row.get('emoji') or ''} {row.get('name') or ''}"
                      .strip(), "subtitle": "animated" if row.get("set") == "noto" else "OpenMoji",
                      "preview": path if Path(path).exists() else None, "inLibrary": known.get(wanted)})
    return source, items, None


def project_folder(host, *parts):
    """A folder of the open project (beside its file, as HyperFrames' graphics/), or None without a project."""
    with contextlib.suppress(PluginError):
        context = host.call("cli", {"argv": ["context", "get"]}) or {}
        project = context.get("project") if isinstance(context, dict) else None
        if isinstance(project, str) and project.startswith("/"):
            return Path(project).parent.joinpath(*parts)
    return None


def search_lottie(host, query, source):
    dest = cache_dir("lottie", slug(query))
    out, err, status = run_script("fetch_lottie", ["--words", query, "--dest", dest, "--count", PAGE,
                                                   "--source", source])
    if status:
        raise fail_from(err, "lottie search failed")
    rows = json.loads((dest / "lottie.json").read_text())
    saved = project_folder(host, "media", "lottie")
    items = []
    for row in rows:
        if not row.get("n"):
            continue
        short = module("fetch_lottie").SOURCES[row["source"]]["short"]
        there = saved / f"{row['slot']}-{short}-{slug(row['id'])}.json" if saved else None
        path = str(dest / row["file"]) if row.get("file") else ""
        bits = [row["source"], f"{row['seconds']} s" if row.get("seconds") else None, row.get("license")]
        items.append({"id": f"{row['slot']}={row['n']}", "title": row.get("name"),
                      "subtitle": " · ".join(str(b) for b in bits if b),
                      "preview": path if Path(path).exists() else None,
                      "license": row.get("license"), "author": row.get("author"), "page": row.get("page"),
                      "inLibrary": str(there) if there and there.exists() else None})
    return source, items, None


def search_illustrations(host, query, source):
    dest = cache_dir("illustrations", slug(query))
    slots = dest / "slots.txt"
    slots.write_text(f"{slug(query)}: {query}\n")
    argv = ["--slots", slots, "--dest", dest, "--count", PAGE]
    if source != "auto":
        argv += ["--set", source]
    out, err, status = run_script("fetch_illustrations", argv)
    if status:
        raise fail_from(err, "illustration search failed")
    rows = json.loads((dest / "illustrations.json").read_text()).get("rows") or []
    known = library_index(host, "illustration")
    items = []
    for row in rows:
        if not row.get("n"):
            continue
        prefix = slug(f"{row.get('set')}-{row.get('id')}-")
        path = row.get("file") or ""
        path = path if os.path.isabs(path) else str(dest / path)
        items.append({"id": f"{row['slot']}={row['n']}", "title": str(row.get("id")), "subtitle": row.get("set"),
                      "preview": path if Path(path).exists() else None,
                      "inLibrary": next((ref for item_id, ref in known.items() if item_id.startswith(prefix)), None)})
    return source, items, None


def search_logos(host, query):
    logos = module("fetch_logos")
    icons, _ = logos.ingest(False)
    folder = logos.shared_dir() / "simple-icons" / "icons"
    thumbs = cache_dir("logos", "thumbs")
    known = library_index(host, "logo")
    items, seen = [], set()
    for name in [n.strip() for n in query.replace(";", ",").split(",") if n.strip()]:
        exact, close = logos.match(name, icons)
        for icon in ([exact] if exact else []) + close:
            if icon["slug"] in seen:
                continue
            seen.add(icon["slug"])
            thumb = thumbs / f"{icon['slug']}.png"
            if not thumb.exists():
                with contextlib.suppress(OSError, ValueError):
                    svg = (folder / f"{icon['slug']}.svg").read_text()
                    logos.render_png(logos.tinted(svg, f"#{icon['hex']}"), 200, logos.svg_shape(svg), thumb)
            items.append({"id": icon["slug"], "title": icon["title"], "subtitle": f"#{icon['hex']}",
                          "preview": str(thumb) if thumb.exists() else None,
                          "inLibrary": next((ref for item_id, ref in known.items()
                                             if item_id.startswith(f"logo-{icon['slug']}-")), None)})
    return "simple-icons", items, None


def search_fonts(query, text):
    argv = ["--candidates", "--n", 12, "--text", text or "Phở bò Hà Nội, đường lên Đà Lạt"]
    if query:
        argv += ["--target", query]
    out, err, status = run_script("fetch_fonts", argv)
    if status:
        raise fail_from(err, "font search failed")
    rows, items, sheet = json_lines(out), [], None
    for row in rows:
        sheet = sheet or row.get("sheet")
        if row.get("n") is None:
            continue
        tags = row.get("tags") or []
        items.append({"id": str(row["n"]), "title": f"{row['n']}. {row.get('family') or ''}".strip(),
                      "subtitle": ", ".join(tags[:4]) if isinstance(tags, list) else str(tags)})
    return "fontsource", items, None, sheet


def search_luts(host, query):
    items = []
    for item in library_items(host, "lut", query=query or None, tag="lut", limit=PAGE * 4):
        tags = [t for t in item.get("tags") or [] if t != "lut"]
        items.append({"id": reference(item), "title": item.get("name") or item.get("id"),
                      "subtitle": ", ".join(tags[:5]), "inLibrary": reference(item)})
    return "library", items, None


def search(host, options, kind, query, source=None, page=1, orientation="any", text=None):
    """The Online resources search: the library first, then the online candidates of one page."""
    if kind not in KINDS:
        raise PluginError("bad_kind", f"kind must be one of {', '.join(KINDS)}")
    query = (query or "").strip()
    if not query and kind not in ("lut", "font"):
        raise PluginError("bad_query", "Type what to look for")
    source = resolve_source(kind, source or "")
    page = max(1, int(page or 1))
    with working(host, options, "Searching"):
        library = library_first(host, kind, query) if query and kind not in ("lut", "lottie") else []
        sheet = None
        if kind in ("photo", "video"):
            used, items, more = search_stock(host, kind, query, source, page, orientation)
        elif kind in ("music", "sfx"):
            used, items, more = search_audio(host, kind, query, source, page)
        elif kind == "emoji":
            used, items, more = search_emoji(host, query, source)
        elif kind == "illustration":
            used, items, more = search_illustrations(host, query, source)
        elif kind == "logo":
            used, items, more = search_logos(host, query)
        elif kind == "lottie":
            used, items, more = search_lottie(host, query, source)
        elif kind == "font":
            used, items, more, sheet = search_fonts(query, text)
        else:
            used, items, more = search_luts(host, query)
    result = {"kind": kind, "query": query, "source": used, "page": page, "next": more,
              "library": library, "items": [{k: v for k, v in i.items() if v not in (None, "")} for i in items]}
    if sheet:
        result["sheet"] = sheet
    return result


# --- download → library ------------------------------------------------------------------------------------------

def download(host, options, kind, query, ids, source=None, scope="project", orientation="any"):
    """Downloads the chosen results into the library with the scripts' own tags, IDs and measurements."""
    if kind not in KINDS:
        raise PluginError("bad_kind", f"kind must be one of {', '.join(KINDS)}")
    ids = [i.strip() for i in (ids if isinstance(ids, list) else str(ids or "").split(",")) if str(i).strip()]
    if not ids and kind != "lut":
        raise PluginError("bad_ids", "Give the ids of the results to download (comma separated)")
    query = (query or "").strip()
    scope = scope if scope in ("project", "user") else "project"
    with working(host, options, "Downloading"):
        if kind in ("photo", "video"):
            return download_stock(kind, query, ids, scope)
        if kind in ("music", "sfx"):
            return download_audio(host, options, kind, query, ids, source, scope)
        if kind == "lut":
            argv = ["--source", resolve_source(kind, source or ""), "--limit", 40, "--scope", scope]
            out, err, status = run_script("fetch_luts", argv)
            if status:
                raise fail_from(err, "fetching LUTs failed")
            return [{"output": out.strip()[-500:]}]
        if kind == "font":
            out, err, status = run_script("fetch_fonts", ["--pick", ",".join(ids), "--scope", scope])
        elif kind == "lottie":
            folder = project_folder(host, "media", "lottie") or cache_dir("lottie", "picked")
            out, err, status = run_script("fetch_lottie", ["--dest", cache_dir("lottie", slug(query)), "--pick",
                                                           ";".join(ids), "--save-to", folder])
        elif kind == "logo":
            out, err, status = run_script("fetch_logos", ["--brands", ",".join(ids), "--scope", scope,
                                                          "--dest", cache_dir("logos", "png")])
        else:
            script, folder = ("fetch_emoji", "emoji") if kind == "emoji" else ("fetch_illustrations", "illustrations")
            out, err, status = run_script(script, ["--dest", cache_dir(folder, slug(query)), "--pick", ";".join(ids),
                                                   "--scope", scope])
        if status:
            raise fail_from(err, "download failed")
        return [{**row, "libraryId": row.get("id") if ":" in str(row.get("id")) else None} for row in json_lines(out)]


def download_stock(kind, query, ids, scope):
    stock = module("fetch_stock")
    dest = cache_dir("stock")
    out = []
    for n, key in enumerate(ids, 1):
        source, _, item = key.partition("-")
        try:
            row = ROWS.get(key) or stock.BY_ID[source](item, kind, 1080)
            if not row or not row.get("url"):
                raise LookupError("not found")
            row = {**row, "slot": stock.slug(query) or "stock", "words": query, "n": n}
            row["file"] = stock.download(row, dest)
            stock.library_add(row, dest, scope)
            line = {"id": key, "libraryId": row.get("libraryId"), "file": str(dest / row["file"])}
            if row.get("libraryError"):
                line["error"] = row["libraryError"]
        except (OSError, LookupError, ValueError, KeyError) as error:
            line = {"id": key, "error": str(error)[:120]}
        out.append(line)
    return out


def download_audio(host, options, kind, query, ids, source, scope):
    audio = module("fetch_audio")
    out = []
    missing = [key for key in ids if key not in ROWS]
    if missing:  # a new session: search again to find the rows
        source = resolve_source(kind, source or "")
        for page in range(1, 6):
            search_audio(host, kind, query, source, page)
            if all(key in ROWS for key in missing):
                break
    for key in ids:
        row = ROWS.get(key)
        if row is None:
            out.append({"id": key, "error": "not in the last search: search again"})
            continue
        path = audio_file(row)
        try:
            if not path.exists():
                path.write_bytes(audio.get(row["url"], timeout=300))
        except OSError as error:
            out.append({"id": key, "error": str(error)[:120]})
            continue
        item = {k: v for k, v in row.items() if k not in ("stem", "suffix")}
        item.update(file=path.name, slot=slug(query) or kind, words=query, n=1)
        audio.to_library([item], path.parent, scope)
        line = {"id": key, "libraryId": item.get("id") if ":" in str(item.get("id")) else None,
                "file": str(path), "seconds": item.get("seconds"), "lufs": item.get("lufs")}
        if item.get("error"):
            line["error"] = item["error"]
        out.append({k: v for k, v in line.items() if v is not None})
    return out


# --- the scripts as they are, for the agent and the command line -------------------------------------------------

def fetch(host, options, script, args):
    """Runs one of the kit's fetch scripts with its own flags; data.output is what it prints in a terminal."""
    name = SCRIPT_NAMES.get(script)
    if not name:
        raise PluginError("bad_script", f"script must be one of {', '.join(SCRIPT_NAMES)}")
    argv = shlex.split(args or "") if isinstance(args, str) else [str(a) for a in args or []]
    with working(host, options, f"Running {name}.py"):
        out, err, status = run_script(name, argv)
    if status and not out.strip():
        raise fail_from(err, f"{name}.py exited with {status}")
    return {"output": out, "exitStatus": status, **({"stderr": err.strip()[-2000:]} if status else {})}


# --- requests ----------------------------------------------------------------------------------------------------

def handle(method, params, host):
    if method in ("view.render", "view.event"):
        if params.get("view") != "browse":
            raise PluginError("unknown_view", f"Online Resources has no view {params.get('view')}")
        return browse(params, params.get("state") or {}, params.get("values") or {}, params.get("event") or {}, host)
    if method != "plugin.action":
        raise PluginError("unknown_method", f"Online Resources does not handle {method}")
    action = str(params.get("action") or "").removeprefix(PLUGIN_ID + ".")
    args, options = params.get("params") or {}, params.get("options") or {}
    if action == "open":
        host.call("plugins.show-view", {"plugin": PLUGIN_ID, "view": "browse"})
        return {}  # the sheet opening is the answer; a status message would stay in the status bar
    if action == "search":
        found = search(host, options, args.get("kind") or "photo", args.get("query"), args.get("source"),
                       args.get("page") or 1, args.get("orientation") or "any", args.get("text"))
        marked = sum(1 for i in found["items"] if i.get("inLibrary"))
        return {"message": f"{len(found['items'])} results from {found['source']} ({marked} already in the library, "
                           f"{len(found['library'])} library matches)", "data": found}
    if action == "download":
        rows = download(host, options, args.get("kind") or "photo", args.get("query"), args.get("ids"),
                        args.get("source"), args.get("scope") or "project")
        lottie = args.get("kind") == "lottie"  # project files: the library refuses Lottie
        saved = sum(1 for r in rows if r.get("libraryId") or r.get("output") or (lottie and r.get("file")))
        where = "the project (media/lottie)" if lottie else "the library"
        return {"message": f"Saved {saved} of {len(rows)} to {where}", "data": {"items": rows}}
    if action == "fetch":
        ran = fetch(host, options, args.get("script"), args.get("args"))
        return {"message": (ran["output"].strip().splitlines() or ["(no output)"])[-1][:300], "data": ran}
    raise PluginError("unknown_action", f"Online Resources has no action {action}")


# --- the browser -------------------------------------------------------------------------------------------------
#
# A window of its own (plugin API 11, `location: window`): one split of three columns. Left, a nav of the types and
# of the current type's sources; middle, the search field, labelled filters, recent searches and the results grid
# (tiles drag onto the timeline and download when dropped); right, an inspector with a big preview, licence, author,
# size and fit, and Add to timeline / Add to project / Save to library. The window keeps its state when it closes, so
# the query, results and recent searches are still there next time.

KIND_ORDER = ["photo", "video", "music", "sfx", "font", "lut", "illustration", "emoji", "logo", "lottie"]
KIND_ICONS = {"photo": "photo", "video": "film", "music": "music.note", "sfx": "speaker.wave.2",
              "font": "textformat", "lut": "camera.filters", "illustration": "paintbrush", "emoji": "face.smiling",
              "logo": "seal", "lottie": "sparkles"}
MAX_RECENT = 6
TEXT.update({
    "types": ("Types", "Loại"), "sources": ("Sources", "Nguồn"), "details": ("Details", "Chi tiết"), "recent": ("Recent:", "Gần đây:"),
    "pick": ("Select a result to see its licence and add it.", "Chọn một kết quả để xem giấy phép và thêm vào."),
    "license": ("Licence", "Giấy phép"), "author": ("Author", "Tác giả"), "size": ("Size", "Kích thước"),
    "fit": ("Fit", "Khớp khung"), "page": ("Page", "Trang gốc"), "unknown": ("Not given: check the source page",
                                                                            "Không ghi: xem trang gốc"),
    "addTimeline": ("Add to timeline", "Thêm vào timeline"), "addProject": ("Add to project", "Thêm vào project"),
    "saveLibrary": ("Save to library", "Lưu vào thư viện"),
    "dragHint": ("Drag a result onto the timeline, or select it and choose Add to timeline.",
                 "Kéo kết quả vào timeline, hoặc chọn rồi bấm Thêm vào timeline."),
    "added": ("Added to the timeline", "Đã thêm vào timeline"), "savedProject": ("Saved to this project",
                                                                                   "Đã lưu vào project này"),
    "savedUser": ("Saved to My library", "Đã lưu vào Thư viện của tôi"),
    "noTimeline": ("This kind cannot go on the timeline; it was saved", "Loại này không đặt lên timeline được; đã lưu"),
    "fits": ("Fits the {0} project", "Vừa khung project {0}"), "crops": ("Cropped to fill a {0} frame",
                                                                          "Bị cắt cho đầy khung {0}"),
})


def browse(params, state, values, event, host):
    locale = params.get("locale") or "en"
    options = params.get("options") or {}
    node, kind_of_event, value = event.get("node"), event.get("type"), event.get("value")
    kind = state.get("kind") or values.get("kind") or "photo"
    kind = kind if kind in KINDS else "photo"
    source = resolve_source(kind, state.get("source") or values.get("source") or "")
    query = (values.get("query") if values.get("query") is not None else state.get("query") or "").strip()
    if node == "query" and isinstance(value, str):  # Return in the field (or plugins view-event --value)
        query = value.strip()
    orientation = values.get("orientation") or state.get("orientation") or project_orientation(params)
    sample = values.get("sample") or state.get("sample") or ""
    focus = state.get("focus")
    found = state.get("found")
    recent = list(state.get("recent") or [])
    message, reset, answer = state.get("message", ""), {}, {}

    if node == "kind" and kind_of_event == "select" and value in KINDS and value != kind:
        kind, source, found, focus, message = value, KINDS[value]["sources"][0], None, None, ""
    if node == "source" and kind_of_event == "select" and value in KINDS[kind]["sources"]:
        source = value
    if isinstance(node, str) and node.startswith(("example.", "recent.")) and node.split(".")[1].isdigit():
        index = int(node.split(".")[1])
        picks = ([{"kind": kind, "query": q} for q in EXAMPLES.get(kind) or []] if node.startswith("example.")
                 else recent)
        if index < len(picks) and picks[index].get("kind") in KINDS:
            if picks[index]["kind"] != kind:
                kind, source = picks[index]["kind"], KINDS[picks[index]["kind"]]["sources"][0]
            query = picks[index]["query"]
            reset["query"] = query
            node = "search"
    run_search = (node == "search" or (node == "query" and kind_of_event == "submit")
                  or (node == "kind" and query) or (node in ("source", "orientation") and query and found))
    draw = lambda text, **flags: body_of(locale, kind, source, query, orientation, sample, found, focus,  # noqa: E731
                                         recent, text, params, **flags)
    try:
        if run_search or node == "fetchLuts" or (kind == "lut" and found is None and node is None):
            if node == "fetchLuts":
                host.render(draw(tr("working", locale), busy=True))
                rows = download(host, options, "lut", query, [], source, "user")
                message = ((rows[0].get("output") or "").splitlines()[-1:] or [""])[0][:300]
            # A new search: placeholder tiles where the results will be, not the old results.
            host.render(body_of(locale, kind, source, query, orientation, sample, None, None, recent,
                                tr("working", locale), params, busy=True, skeleton=True))
            found = search(host, options, kind, query, source, 1, orientation, sample)
            focus = None
            message = message if node == "fetchLuts" else ""
            if query:
                recent = ([{"kind": kind, "query": query}]
                          + [r for r in recent if (r.get("kind"), r.get("query")) != (kind, query)])[:MAX_RECENT]
        elif node in ("results", "library") and kind_of_event == "select":
            focus = None if value == focus else value
        elif node == "results" and kind_of_event == "click" and value == "more" and found and found.get("next"):
            host.render(draw(tr("working", locale), busy=True))
            more = search(host, options, kind, found["query"], found.get("source") or source, found["next"],
                          orientation, sample)
            found = {**found, "items": found["items"] + more["items"], "next": more["next"], "page": more["page"]}
        elif node == "results" and kind_of_event == "action" and isinstance(value, dict):
            if value.get("action") == "preview":
                found = with_audio_preview(host, options, found, value.get("item"))
        elif node in ("results", "library") and kind_of_event == "drag" and isinstance(value, dict) and found:
            # Dropped on the timeline: BashCut places the item it gets back where the tile landed.
            reference, found = save_result(host, options, kind, found, str(value.get("item")), source, "project")
            answer["libraryItem"] = reference
            message = tr("savedProject", locale)
        elif node in ("addTimeline", "addProject", "saveLibrary") and focus and found:
            host.render(draw(tr("working", locale), busy=True))
            scope = "user" if node == "saveLibrary" else "project"
            reference, found = save_result(host, options, kind, found, focus, source, scope)
            if node == "addTimeline":
                if ":" not in str(reference) or not KINDS[kind]["library"]:
                    message = tr("noTimeline", locale)
                else:
                    host.call("library.place", place_params(reference, params))
                    message = tr("added", locale)
            else:
                message = tr("savedUser" if scope == "user" else "savedProject", locale)
    except PluginError as error:
        message = error.message
    state = {"kind": kind, "source": source, "query": query, "orientation": orientation, "sample": sample,
             "focus": focus, "found": found, "message": message, "recent": recent}
    # No title of its own: the window header already says "Online resources".
    body = draw(message)
    if reset:
        set_values(body, reset)
    return {"state": state, "body": body, **answer}


def place_params(reference, params):
    """library.place at the playhead the request saw (a free layer when the main one is taken there)."""
    placed = {"id": reference, "baseRev": "last"}
    playhead = (params.get("context") or {}).get("playhead")
    if isinstance(playhead, int) and playhead >= 0:
        placed["atFrame"] = playhead
    return placed


def set_values(nodes, values):
    for component in nodes:
        if component.get("id") in values:
            component["value"] = values[component["id"]]
        set_values(component.get("children") or [], values)


def with_audio_preview(host, options, found, item_id):
    row = ROWS.get(item_id)
    if not (row and found):
        return found
    with working(host, options, "Preview"):
        path = audio_file(row)
        if not path.exists():
            path.write_bytes(module("fetch_audio").get(row["url"], timeout=120))
    return {**found, "items": [{**i, "audio": str(path)} if i["id"] == item_id else i for i in found["items"]]}


def saved_ids(kind, rows):
    """Result id → what a download saved (a library reference, or the project file of a Lottie)."""
    if kind in ("emoji", "illustration"):  # picked by slot=n: the lines carry slot and n
        return {f"{r.get('slot')}={r.get('n')}": r.get("libraryId") for r in rows if r.get("libraryId")}
    if kind == "logo":
        return {r.get("slug"): r.get("libraryId") for r in rows if r.get("libraryId")}
    if kind == "lottie":
        return {f"{r.get('slot')}={r.get('n')}": r.get("file") for r in rows if r.get("file")}
    if kind == "font":
        return {str(r.get("n")): r.get("libraryId") or "saved" for r in rows if not r.get("error")}
    return {r.get("id"): r.get("libraryId") for r in rows if r.get("libraryId")}


def save_result(host, options, kind, found, item_id, source, scope):
    """One result in the library (downloaded now unless it is there already); returns (reference, found) with the
    result marked as in the library."""
    mine = next((i for i in found.get("library") or [] if i["id"] == item_id), None)
    if mine:
        return mine["libraryId"], found
    item = next((i for i in found.get("items") or [] if i["id"] == item_id), None)
    if item is None:
        raise PluginError("unknown_item", f"{item_id} is not in the results: search again")
    there = str(item.get("inLibrary") or "")
    if ":" in there and (scope == "project" or there.startswith(scope + ":")):
        return there, found
    rows = download(host, options, kind, found["query"], [item_id], found.get("source") or source, scope)
    reference = saved_ids(kind, rows).get(item_id)
    if not reference:
        errors = [r.get("error") for r in rows if r.get("error")]
        raise PluginError("download_failed", (errors[0] if errors else f"{item_id} was not saved")[:300])
    found = {**found, "items": [{**i, "inLibrary": reference} if i["id"] == item_id else i for i in found["items"]]}
    return reference, found


def body_of(locale, kind, source, query, orientation, sample, found, focus, recent, message, params, busy=False,
            skeleton=False):
    """The three columns: types and sources, the search and results, the inspector."""
    count = len((found or {}).get("items") or []) if found else None
    nav = [
        {"type": "nav", "id": "kind", "value": kind, "groups": [{"title": tr("types", locale), "items": [
            {"id": k, "title": tr(k, locale), "icon": KIND_ICONS[k], **({"count": count} if k == kind and count else {})}
            for k in KIND_ORDER]}]},
        {"type": "nav", "id": "source", "value": source, "groups": [{"title": tr("sources", locale), "items": [
            {"id": s, "title": source_name(s, locale), "icon": "globe"} for s in KINDS[kind]["sources"]]}]},
    ]
    middle = search_column(locale, kind, query, orientation, sample, found, focus, recent, message, busy, skeleton)
    inspector = inspector_column(locale, kind, found, focus, params, busy)
    # `label` names a side column where a narrow window folds it into a disclosure.
    return [{"type": "split", "widths": [200, "flex", 300], "children": [
        {"type": "section", "label": tr("types", locale), "children": nav},
        {"type": "section", "children": middle},
        {"type": "section", "label": tr("details", locale), "children": inspector},
    ]}]


def search_column(locale, kind, query, orientation, sample, found, focus, recent, message, busy, skeleton):
    body = [{"type": "row", "children": [
        {"type": "textField", "id": "query", "placeholder": tr("placeholder", locale), "submit": True,
         **({"value": query} if query else {})},
        {"type": "button", "id": "search", "title": tr("search", locale), "icon": "magnifyingglass",
         "style": "primary", "disabled": busy}]}]
    filters = []
    if kind in ("photo", "video"):
        filters.append({"type": "picker", "id": "orientation", "label": tr("orientation", locale),
                        "value": orientation, "options": [{"value": o, "label": tr(f"orientation.{o}", locale)}
                                                          for o in ("any", "portrait", "landscape", "square")]})
    if kind == "font":
        filters.append({"type": "textField", "id": "sample", "label": tr("sample", locale), "value": sample or None,
                        "placeholder": "Phở bò Hà Nội, đường lên Đà Lạt"})
    if kind == "lut":
        filters.append({"type": "button", "id": "fetchLuts", "title": tr("fetchLuts", locale),
                        "icon": "arrow.down.circle", "disabled": busy})
    if filters:
        body.append({"type": "row", "children": filters})
    if recent:
        body.append({"type": "row", "children": [{"type": "text", "text": tr("recent", locale), "style": "caption"}]
                     + [{"type": "button", "id": f"recent.{n}", "title": r["query"], "style": "link", "disabled": busy}
                        for n, r in enumerate(recent)]})
    if busy:
        body.append({"type": "progress", "label": message})
    elif message:
        body.append({"type": "text", "text": message, "style": "caption"})
    cell, aspect = KINDS[kind]["cell"], KINDS[kind]["aspect"]
    audio_kind = kind in ("music", "sfx")
    icon = "waveform" if audio_kind else ("textformat" if kind == "font" else "photo")
    if skeleton:
        body.append({"type": "grid", "id": "loading", "cellWidth": cell, "aspect": aspect,
                     "items": [{"id": f"loading-{n}", "icon": icon, "title": "…"} for n in range(SKELETON_TILES)]})
        return body
    placeable = bool(KINDS[kind]["library"])
    if found and found.get("library"):
        body.append({"type": "section", "title": f"{tr('library', locale)} ({len(found['library'])})", "children": [
            {"type": "grid", "id": "library", "cellWidth": cell, "aspect": aspect, "selected": focus, "items": [
                {"id": item["id"], "title": item.get("title"), "subtitle": ", ".join(item.get("tags", [])[:4]),
                 "image": item.get("preview"), "audio": item.get("audio"), "libraryItem": item["libraryId"],
                 "icon": icon, "badge": tr("inLibrary", locale), "badgeColor": "green"} for item in found["library"]]}]})
    if found and found.get("sheet") and Path(found["sheet"]).exists():
        body.append({"type": "image", "path": found["sheet"], "height": 420})
    if found is None:
        body.append({"type": "text", "text": tr("empty", locale), "style": "secondary"})
        examples = EXAMPLES.get(kind) or []
        if examples:
            body.append({"type": "row", "children": [{"type": "text", "text": tr("try", locale), "style": "secondary"}]
                         + [{"type": "button", "id": f"example.{n}", "title": text, "icon": "magnifyingglass",
                             "disabled": busy} for n, text in enumerate(examples)]})
        return body
    items = []
    for item in found.get("items") or []:
        cell_item = {"id": item["id"], "title": item.get("title"), "subtitle": item.get("subtitle"),
                     "image": item.get("preview"), "audio": item.get("audio"), "icon": icon}
        if item.get("inLibrary"):
            cell_item.update(badge=tr("inLibrary", locale), badgeColor="green")
            if ":" in str(item["inLibrary"]):
                cell_item["libraryItem"] = item["inLibrary"]
        if audio_kind and not item.get("audio"):
            cell_item["actions"] = [{"id": "preview", "title": tr("preview", locale), "icon": "play.circle"}]
        items.append({k: v for k, v in cell_item.items() if v not in (None, "")})
    grid = {"type": "grid", "id": "results", "cellWidth": cell, "aspect": aspect, "items": items,
            "selected": focus, "empty": tr("none", locale)}
    if placeable:
        grid["drag"] = "download"
    if found.get("next"):
        grid["more"] = tr("more", locale)
    body.append({"type": "section", "title": f"{tr('results', locale)} · {source_name(found.get('source'), locale)}",
                 "children": [grid]})
    if placeable and items:
        body.append({"type": "text", "text": tr("dragHint", locale), "style": "caption"})
    return body


def inspector_column(locale, kind, found, focus, params, busy):
    item = next((i for i in (found or {}).get("items") or [] if i["id"] == focus), None)
    mine = next((i for i in (found or {}).get("library") or [] if i["id"] == focus), None)
    if not (item or mine):
        return [{"type": "text", "text": tr("pick", locale), "style": "secondary"}]
    item = item or {"title": mine.get("title"), "preview": mine.get("preview"), "audio": mine.get("audio"),
                    "inLibrary": mine["libraryId"]}
    body = []
    if item.get("preview"):
        body.append({"type": "image", "path": item["preview"], "height": 220,
                     **({"libraryItem": item["inLibrary"]} if ":" in str(item.get("inLibrary") or "") else {})})
    if item.get("audio"):
        body.append({"type": "audio", "path": item["audio"], "title": tr("preview", locale)})
    body.append({"type": "text", "text": str(item.get("title") or focus), "style": "heading"})
    if item.get("inLibrary"):
        body.append({"type": "badge", "text": tr("inLibrary", locale), "color": "green"})
    facts = [{"key": tr("license", locale), "value": item.get("license") or tr("unknown", locale)}]
    if item.get("author"):
        facts.append({"key": tr("author", locale), "value": str(item["author"])})
    if item.get("subtitle"):
        facts.append({"key": tr("source", locale), "value": str(item["subtitle"])})
    size = size_of(item.get("subtitle"))
    if size:
        facts.append({"key": tr("size", locale), "value": f"{size[0]}×{size[1]}"})
        fit = fit_text(size, params, locale)
        if fit:
            facts.append({"key": tr("fit", locale), "value": fit})
    if item.get("page"):
        facts.append({"key": tr("page", locale), "value": str(item["page"])})
    body.append({"type": "keyValue", "items": facts})
    placeable = bool(KINDS[kind]["library"])
    body.append({"type": "button", "id": "addTimeline", "title": tr("addTimeline", locale), "icon": "plus.rectangle",
                 "style": "primary", "wide": True, "disabled": busy or not placeable})
    body.append({"type": "button", "id": "addProject", "title": tr("addProject", locale), "icon": "folder.badge.plus",
                 "wide": True, "disabled": busy})
    if placeable:
        body.append({"type": "button", "id": "saveLibrary", "title": tr("saveLibrary", locale),
                     "icon": "tray.and.arrow.down", "wide": True, "disabled": busy})
    return body


def size_of(subtitle):
    match = re.search(r"(\d{2,5})x(\d{2,5})", str(subtitle or ""))
    return (int(match.group(1)), int(match.group(2))) if match else None


def fit_text(size, params, locale):
    """Whether a picture of `size` fills the project frame as it is or is cropped to fill it."""
    project = ((params.get("context") or {}).get("project") or {})
    width, height = project.get("width"), project.get("height")
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        return None
    divisor = math.gcd(width, height)
    ratio = f"{width // divisor}:{height // divisor}"
    same = abs(size[0] / size[1] - width / height) < 0.02
    return tr("fits" if same else "crops", locale).format(ratio)


def project_orientation(params):
    """The first orientation of a photo or video search: the project's shape (portrait for 9:16), else any."""
    project = ((params.get("context") or {}).get("project") or {})
    width, height = project.get("width"), project.get("height")
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        return "any"
    return "portrait" if height > width else "landscape" if width > height else "square"
