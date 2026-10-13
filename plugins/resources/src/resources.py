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
                "logos": "fetch_logos", "facts": "fetch_facts"}
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
}
LABELS = {
    "photo": ("Photos", "Ảnh"), "video": ("Videos", "Video"), "music": ("Music", "Nhạc"),
    "sfx": ("Sound effects", "Hiệu ứng âm thanh"), "illustration": ("Illustrations", "Minh hoạ"),
    "emoji": ("Emoji", "Emoji"), "logo": ("Logos", "Logo"), "font": ("Fonts", "Phông chữ"), "lut": ("LUTs", "LUT"),
}
TEXT = {
    "title": ("Online resources", "Tài nguyên trực tuyến"),
    "search": ("Search", "Tìm"),
    "placeholder": ("coffee, whoosh, figma…", "cà phê, whoosh, figma…"),
    "library": ("In your library", "Đã có trong thư viện"),
    "results": ("Online", "Trên mạng"),
    "inLibrary": ("In library", "Đã có"),
    "download": ("Download to Library", "Tải về thư viện"),
    "more": ("Load more", "Xem thêm"),
    "empty": ("Search to see results.", "Tìm để xem kết quả."),
    "none": ("Nothing found.", "Không tìm thấy."),
    "scope.project": ("This project", "Project này"), "scope.user": ("My library (this Mac)", "Thư viện của tôi"),
    "sample": ("Sample text", "Chữ mẫu"),
    "fetchLuts": ("Fetch LUT packs", "Tải các gói LUT"),
    "orientation": ("Orientation", "Hướng"),
    "preview": ("Preview", "Nghe thử"),
    "selected": ("selected", "đã chọn"),
    "working": ("Working…", "Đang xử lý…"),
}


def tr(key, locale):
    pair = TEXT.get(key) or LABELS.get(key) or (key, key)
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
        library = library_first(host, kind, query) if query and kind not in ("lut",) else []
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
        return {"message": "Opened Online resources"}
    if action == "search":
        found = search(host, options, args.get("kind") or "photo", args.get("query"), args.get("source"),
                       args.get("page") or 1, args.get("orientation") or "any", args.get("text"))
        marked = sum(1 for i in found["items"] if i.get("inLibrary"))
        return {"message": f"{len(found['items'])} results from {found['source']} ({marked} already in the library, "
                           f"{len(found['library'])} library matches)", "data": found}
    if action == "download":
        rows = download(host, options, args.get("kind") or "photo", args.get("query"), args.get("ids"),
                        args.get("source"), args.get("scope") or "project")
        saved = sum(1 for r in rows if r.get("libraryId") or r.get("output"))
        return {"message": f"Saved {saved} of {len(rows)} to the library", "data": {"items": rows}}
    if action == "fetch":
        ran = fetch(host, options, args.get("script"), args.get("args"))
        return {"message": (ran["output"].strip().splitlines() or ["(no output)"])[-1][:300], "data": ran}
    raise PluginError("unknown_action", f"Online Resources has no action {action}")


# --- the sheet ---------------------------------------------------------------------------------------------------

def browse(params, state, values, event, host):
    locale = params.get("locale") or "en"
    options = params.get("options") or {}
    node, kind_of_event, value = event.get("node"), event.get("type"), event.get("value")
    kind = values.get("kind") or state.get("kind") or "photo"
    kind = kind if kind in KINDS else "photo"
    source = resolve_source(kind, values.get("source") or state.get("source") or "")
    query = (values.get("query") if values.get("query") is not None else state.get("query") or "").strip()
    if node == "query" and isinstance(value, str):  # Return in the field (or plugins view-event --value)
        query = value.strip()
    scope = values.get("scope") or state.get("scope") or "project"
    orientation = values.get("orientation") or state.get("orientation") or "any"
    sample = values.get("sample") or state.get("sample") or ""
    selected = list(state.get("selected") or [])
    found = state.get("found")
    message, reset = state.get("message", ""), {}

    if node == "kind" and kind != state.get("kind"):
        source, found, selected, message = KINDS[kind]["sources"][0], None, [], ""
        reset["source"] = source
    run_search = (node in ("search",) or (node == "query" and kind_of_event == "submit")
                  or (node == "kind" and query) or (node == "source" and query and found))
    try:
        if run_search or (node == "fetchLuts") or (kind == "lut" and found is None and node is None):
            if node == "fetchLuts":
                host.render(body_of(locale, kind, source, query, scope, orientation, sample, found, selected,
                                    tr("working", locale), busy=True), tr("title", locale))
                rows = download(host, options, "lut", query, [], source, "user")
                message = (rows[0].get("output") or "").splitlines()[-1:] or [""]
                message = message[0][:300]
            host.render(body_of(locale, kind, source, query, scope, orientation, sample, found, selected,
                                tr("working", locale), busy=True), tr("title", locale))
            found = search(host, options, kind, query, source, 1, orientation, sample)
            selected = []
            message = message if node == "fetchLuts" else ""
        elif node == "results" and kind_of_event == "select":
            selected = [s for s in selected if s != value] if value in selected else selected + [value]
        elif node == "results" and kind_of_event == "click" and value == "more" and found and found.get("next"):
            host.render(body_of(locale, kind, source, query, scope, orientation, sample, found, selected,
                                tr("working", locale), busy=True), tr("title", locale))
            more = search(host, options, kind, found["query"], found.get("source") or source, found["next"],
                          orientation, sample)
            found = {**found, "items": found["items"] + more["items"], "next": more["next"], "page": more["page"]}
        elif node == "results" and kind_of_event == "action" and isinstance(value, dict):
            if value.get("action") == "preview":
                row = ROWS.get(value.get("item"))
                if row and found:
                    with working(host, options, "Preview"):
                        path = audio_file(row)
                        if not path.exists():
                            path.write_bytes(module("fetch_audio").get(row["url"], timeout=120))
                    found = {**found, "items": [{**i, "audio": str(path)} if i["id"] == value.get("item") else i
                                                for i in found["items"]]}
        elif node == "download" and selected and found:
            host.render(body_of(locale, kind, source, query, scope, orientation, sample, found, selected,
                                tr("working", locale), busy=True), tr("title", locale))
            rows = download(host, options, kind, found["query"], selected, found.get("source") or source, scope)
            done = {r.get("id"): r.get("libraryId") for r in rows if r.get("libraryId")}
            if kind in ("emoji", "illustration"):  # picked by slot=n: the lines carry slot and n
                done = {f"{r.get('slot')}={r.get('n')}": r.get("libraryId") for r in rows if r.get("libraryId")}
            if kind == "logo":
                done = {r.get("slug"): r.get("libraryId") for r in rows if r.get("libraryId")}
            if kind == "font":
                done = {str(r.get("n")): r.get("libraryId") or "saved" for r in rows if not r.get("error")}
            found = {**found, "items": [{**i, "inLibrary": done.get(i["id"]) or i.get("inLibrary")}
                                        for i in found["items"]]}
            errors = [r.get("error") for r in rows if r.get("error")]
            message = (f"{len(done)} saved to the library" if not str(locale).startswith("vi")
                       else f"Đã lưu {len(done)} mục vào thư viện") + (f" · {errors[0]}" if errors else "")
            selected = []
    except PluginError as error:
        message = error.message
    state = {"kind": kind, "source": source, "query": query, "scope": scope, "orientation": orientation,
             "sample": sample, "selected": selected, "found": found, "message": message}
    answer = {"title": tr("title", locale), "state": state,
              "body": body_of(locale, kind, source, query, scope, orientation, sample, found, selected, message)}
    if reset:
        for component in answer["body"]:
            for child in component.get("children") or []:
                if child.get("id") in reset:
                    child["value"] = reset[child["id"]]
    return answer


def body_of(locale, kind, source, query, scope, orientation, sample, found, selected, message, busy=False):
    kinds = [{"value": k, "label": tr(k, locale)} for k in KINDS]
    sources = [{"value": s, "label": s} for s in KINDS[kind]["sources"]]
    controls = [
        {"type": "picker", "id": "kind", "label": "", "value": kind, "options": kinds},
        {"type": "textField", "id": "query", "placeholder": tr("placeholder", locale), "submit": True,
         **({"value": found["query"]} if found and found.get("query") else {})},
        {"type": "picker", "id": "source", "label": "", "value": source, "options": sources},
    ]
    if kind in ("photo", "video"):
        controls.append({"type": "picker", "id": "orientation", "label": "", "value": orientation,
                         "options": ["any", "portrait", "landscape", "square"]})
    controls.append({"type": "button", "id": "search", "title": tr("search", locale), "icon": "magnifyingglass",
                     "style": "primary", "disabled": busy})
    body = [{"type": "row", "children": controls}]
    if kind == "font":
        body.append({"type": "textField", "id": "sample", "label": tr("sample", locale), "value": sample or None,
                     "placeholder": "Phở bò Hà Nội, đường lên Đà Lạt"})
    if kind == "lut":
        body.append({"type": "button", "id": "fetchLuts", "title": tr("fetchLuts", locale), "icon": "arrow.down.circle",
                     "disabled": busy})
    if busy:
        body.append({"type": "progress", "label": message})
    elif message:
        body.append({"type": "text", "text": message, "style": "caption"})
    cell, aspect = KINDS[kind]["cell"], KINDS[kind]["aspect"]
    audio_kind = kind in ("music", "sfx")
    if found and found.get("library"):
        body.append({"type": "section", "title": f"{tr('library', locale)} ({len(found['library'])})", "children": [
            {"type": "grid", "id": "library", "cellWidth": cell, "aspect": aspect, "items": [
                {"id": item["id"], "title": item.get("title"), "subtitle": ", ".join(item.get("tags", [])[:4]),
                 "image": item.get("preview"), "audio": item.get("audio"), "libraryItem": item["libraryId"],
                 "icon": "waveform" if audio_kind else "photo", "badge": tr("inLibrary", locale),
                 "badgeColor": "green"} for item in found["library"]]}]})
    if found and found.get("sheet") and Path(found["sheet"]).exists():
        body.append({"type": "image", "path": found["sheet"], "height": 420})
    if found is not None:
        items = []
        for item in found.get("items") or []:
            cell_item = {"id": item["id"], "title": item.get("title"), "subtitle": item.get("subtitle"),
                         "image": item.get("preview"), "audio": item.get("audio"),
                         "icon": "waveform" if audio_kind else ("textformat" if kind == "font" else "photo")}
            if item.get("inLibrary"):
                cell_item.update(badge=tr("inLibrary", locale), badgeColor="green")
                if ":" in str(item["inLibrary"]):
                    cell_item["libraryItem"] = item["inLibrary"]
            if audio_kind and not item.get("audio"):
                cell_item["actions"] = [{"id": "preview", "title": tr("preview", locale), "icon": "play.circle"}]
            items.append({k: v for k, v in cell_item.items() if v not in (None, "")})
        grid = {"type": "grid", "id": "results", "cellWidth": cell, "aspect": aspect, "items": items,
                "selected": selected, "empty": tr("none", locale)}
        if found.get("next"):
            grid["more"] = tr("more", locale)
        body.append({"type": "section", "title": f"{tr('results', locale)} · {found.get('source')}",
                     "children": [grid]})
        if kind != "lut":
            body.append({"type": "row", "children": [
                {"type": "text", "text": f"{len(selected)} {tr('selected', locale)}", "style": "secondary"},
                {"type": "picker", "id": "scope", "label": "", "value": scope,
                 "options": [{"value": s, "label": tr(f"scope.{s}", locale)} for s in ("project", "user")]},
                {"type": "button", "id": "download", "title": f"{tr('download', locale)} ({len(selected)})",
                 "icon": "arrow.down.to.line", "style": "primary", "disabled": busy or not selected}]})
    else:
        body.append({"type": "text", "text": tr("empty", locale), "style": "secondary"})
    return body
