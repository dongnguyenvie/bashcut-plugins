// bin/graphic: one call that renders a HyperFrames composition and places it, and one that renders it again when its
// data or the project's brand changes, so an agent never repeats render → wait → library add → place by hand.
//
//   place D [--at-frame F] [--duration N] [--track T] [--set k=v …] [--variables JSON] [--frame JSON] [--name N]
//           [--fps N] [--codec hevc|prores] [--no-brand] [--steps-from voice|sections] [--dry-run]
//     Renders composition folder D with graphics.render (an example of this plugin is first copied to the project's
//     graphics/<name>-<id>/ and the copy rendered), waits, adds the .mov as a sticker and places it full canvas
//     (size 1 at 0.5,0.5) on the Overlay layer, then records the render inputs on the placed media
//     (media.data.graphics, setMediaData). Prints {item, media, track, atFrame, frames, path, rev, brand, …}.
//     --duration N (frames) is also the composition's length: its root data-duration is set to N while it renders, so
//     an exit timed on the end plays at the end of the span; rerender keeps that length.
//     --steps-from voice|sections (--steps-from-voice): times the `data` variable's steps (or stops) on the voice lines
//     (Voiceover layer items) or section markers from --at-frame on, one per step; without --at-frame/--duration the
//     graphic starts 0.4 s before the first and ends 0.5 s after the last. "line:N" / "section:Label" as a step's at
//     picks one (resolveSteps).
//   rerender ITEM|MEDIA|--all [--set k=v …] [--unset k …] [--variables JSON] [--frame JSON] [--fps N] [--codec C]
//            [--name N] [--brand | --no-brand] [--keep-length] [--steps-from voice|sections] [--dry-run]
//     Reads the recorded inputs, applies the changes and the current brand, renders again and, as ONE timeline
//     apply, adds the new movie and points every item that used the old one at it (setSource), keeping each item's
//     in-point. An item that played the whole old render plays the whole new one (its end moves; the result lists
//     the length change); --keep-length keeps every length (cut to the new render when it is shorter).
//
//   examples [NAME]
//     One short row per example: name, what it draws (the first sentence of its header comment), seconds and its
//     own variables as "id:type" (the brand ids left out), enough to choose. With NAME the full row: the whole
//     comment, folder, every variable {id, type, label, default}, the brand ids it declares, its known pitfalls (a
//     `<!-- Pitfalls: - … -->` comment in the page) and the active lessons tagged block:NAME in BashCut's knowledge
//     (`lessons`; skipped when BashCut cannot be reached).
//   plan [--only g1,g2] [--force] [--no-apply] [--codec C] [--dry-run]
//     Renders every plan.cut graphic that has `render` {composition, set, name, codec} and no up-to-date movie, each to
//     the span plan check gives it (the composition's data-duration is set to it while it renders, so an exit timed
//     on the end lands there), imports the movies (alpha), records the inputs on each media, writes
//     their media IDs into plan.cut and runs plan apply — the whole picture of a plan in one call. A `set` value
//     "@words" becomes the seconds from the graphic's start to where the voiceover says those words (plan check
//     --words); inside a list or object given for a string variable, every "@words" string is replaced the same way.
//     A composition path may be relative to the project folder; a bare name ("stat-counter") is this plugin's
//     example. A brand id in `set` the composition does not declare is left out with a warning. render.frame is the frame (below); "@words" work
//     in its callout.at too. Prints {rendered, kept, apply}.
//
// Frame (--frame JSON, render.frame): chrome drawn around any composition for the render only — backdrop
// ("texture" | "paper" | "plain"), fadeIn (s), drift (true), float (true), chip ("2/4"), credit ("© OpenStreetMap contributors"), callout
// ({text, at, top}, *word* in the accent), scale (0.5–2.5) — so a series of cards shares one look without editing
// their HTML (lib/frame.mjs). It is recorded with the inputs; rerender --frame changes keys (null drops one; --frame
// null drops the frame).
//
// Canvas: a composition whose root has data-fit="canvas" lays itself out for any size; it renders at the project's
// width and height (data-width/data-height set while it renders), so one example serves 9:16 and 16:9.
//
// Variables: `--set data=@file.json` reads the value from a file (JSON made compact). --set values are typed by the
// composition's declarations (number, boolean, string…); --variables takes
// a JSON object (a list or object given for a string variable is stringified). An id the composition does not
// declare is refused. Brand: the project's `brand` (bashcut project get) fills the standard ids the composition
// declares — accent, background, text, secondary (palette), headingFont, bodyFont (fonts), disclosure — and
// explicit values win. A brand font in the project's fonts folder is copied into the composition's fonts/ folder.
// A declared `logo` / `mascot` gets the brand's logo / mascot pose copied in; `--set pose=thinking` picks the pose.
// Uses $BASHCUT_CLI, else `bashcut` on PATH.
import { spawnSync } from "node:child_process";
import { createHash, randomBytes, randomUUID } from "node:crypto";
import { copyFileSync, cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, realpathSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, dirname, extname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { checkFrame, FRAME_VERSION, mergeFrame, withFrameMarkup } from "./frame.mjs";

export class UsageError extends Error {}

const BRAND_MAP = {
    accent: ["palette", "accent"], background: ["palette", "background"], text: ["palette", "text"],
    secondary: ["palette", "secondary"], headingFont: ["fonts", "heading"], bodyFont: ["fonts", "body"],
    disclosure: ["disclosure"],
};
export const BRAND_IDS = Object.keys(BRAND_MAP);
// What the brand fills besides BRAND_IDS: its logo, its mascot and the mascot's pose (`mascotPose` is the older name).
const BRAND_SLOTS = ["logo", "mascot", "pose", "mascotPose"];
const POSE_IDS = ["pose", "mascotPose"];
const FLAGS = new Set(["no-brand", "brand", "keep-length", "dry-run", "all", "force", "no-apply", "steps-from-voice"]);
const LISTS = new Set(["set", "unset"]);
const OPTIONS = new Set(["at-frame", "duration", "track", "variables", "frame", "name", "fps", "codec", "only", "steps-from"]);

/** argv (after the node script) → {command, target, options}; options.set/unset are lists. */
export function parseArgs(argv) {
    const [command, ...rest] = argv;
    if (command === "examples") return { command, target: rest.find((w) => !w.startsWith("--")), options: { set: [], unset: [] } };
    if (!["place", "rerender", "plan"].includes(command)) {
        throw new UsageError("usage: graphic place DIR [--at-frame F] [--set k=v …] | graphic rerender ITEM|MEDIA|--all [--set k=v …] | graphic plan [--only IDS]");
    }
    const options = { set: [], unset: [] };
    let target;
    for (let i = 0; i < rest.length; i += 1) {
        const word = rest[i];
        if (!word.startsWith("--")) {
            if (target !== undefined) throw new UsageError(`unexpected argument ${word}`);
            target = word;
            continue;
        }
        let name = word.slice(2);
        let value;
        const eq = name.indexOf("=");
        if (eq > 0) [name, value] = [name.slice(0, eq), name.slice(eq + 1)];
        if (FLAGS.has(name)) {
            options[name] = true;
            continue;
        }
        if (!LISTS.has(name) && !OPTIONS.has(name)) throw new UsageError(`unknown option --${name}`);
        if (value === undefined) {
            if (i + 1 >= rest.length) throw new UsageError(`--${name} needs a value`);
            value = rest[(i += 1)];
        }
        if (LISTS.has(name)) options[name].push(value);
        else options[name] = value;
    }
    for (const key of ["at-frame", "duration", "fps"]) {
        if (options[key] === undefined) continue;
        const number = Number(options[key]);
        if (!Number.isInteger(number) || number < (key === "at-frame" ? 0 : 1)) throw new UsageError(`--${key} must be a whole number`);
        options[key] = number;
    }
    if (options.codec !== undefined && !["hevc", "prores"].includes(options.codec)) throw new UsageError('--codec is "hevc" or "prores"');
    if (options.brand && options["no-brand"]) throw new UsageError("--brand and --no-brand together");
    if (options["steps-from-voice"]) {
        if (options["steps-from"] && options["steps-from"] !== "voice") throw new UsageError("--steps-from-voice and --steps-from sections together");
        options["steps-from"] = "voice";
    }
    delete options["steps-from-voice"];
    if (options["steps-from"] !== undefined && !["voice", "sections"].includes(options["steps-from"])) {
        throw new UsageError('--steps-from is "voice" (voice line starts) or "sections" (section markers)');
    }
    if (command === "plan") {
        if (target) throw new UsageError("plan takes no folder: it reads plan.cut.graphics");
        for (const key of ["all", "keep-length", "brand", "at-frame", "duration", "track", "variables", "frame", "name", "steps-from"]) {
            if (options[key] !== undefined && options[key] !== false) throw new UsageError(`--${key} is not for plan`);
        }
        if (options.set.length || options.unset.length) throw new UsageError("plan reads each graphic's render.set from plan.cut");
        return { command, target, options };
    }
    if (options.only !== undefined || options.force || options["no-apply"]) throw new UsageError("--only, --force and --no-apply are for plan");
    if (command === "place") {
        if (!target) throw new UsageError("place needs the composition folder");
        for (const key of ["all", "unset", "keep-length", "brand"]) {
            if (key === "unset" ? options.unset.length : options[key]) throw new UsageError(`--${key} is for rerender`);
        }
    } else {
        if (!target && !options.all) throw new UsageError("rerender needs an item or media id, or --all");
        if (target && options.all) throw new UsageError("give an id or --all, not both");
        for (const key of ["at-frame", "duration", "track"]) if (options[key] !== undefined) throw new UsageError(`--${key} is for place`);
    }
    if (options.variables !== undefined) {
        try {
            options.variables = JSON.parse(options.variables);
        } catch {
            throw new UsageError("--variables must be a JSON object");
        }
        if (typeof options.variables !== "object" || options.variables === null || Array.isArray(options.variables)) {
            throw new UsageError("--variables must be a JSON object");
        }
    }
    if (options.frame !== undefined) {
        let frame;
        try {
            frame = JSON.parse(options.frame);
        } catch {
            throw new UsageError("--frame must be a JSON object (or null to drop the frame)");
        }
        if (frame !== null) {
            try {
                if (command === "place") checkFrame(frame);
                else checkFrame(Object.fromEntries(Object.entries(frame).filter(([, value]) => value !== null)));
            } catch (error) {
                throw new UsageError(error.message);
            }
            if (typeof frame.callout?.at === "string" || typeof frame.callout?.top === "string") {
                throw new UsageError('"@words" in frame.callout work in graphic plan only; give seconds');
            }
        }
        options.frame = frame;
    }
    return { command, target, options };
}

/** The composition's declarations and canvas from its index.html. */
export function readComposition(dir) {
    const page = join(dir, "index.html");
    if (!existsSync(page)) throw new Error(`${dir} has no index.html`);
    const html = readFileSync(page, "utf8");
    const match = /data-composition-variables='([\s\S]*?)'/.exec(html);
    let declared = [];
    if (match) {
        try {
            declared = JSON.parse(match[1].replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&"));
        } catch (error) {
            throw new Error(`data-composition-variables in ${page} is not JSON: ${error.message}`);
        }
    }
    const number = (name) => Number(new RegExp(`data-composition-id="main"[^>]*\\bdata-${name}="([\\d.]+)"`).exec(html)?.[1]);
    // data-fit="canvas": the page lays itself out for any canvas, so it renders at the project's size.
    const fit = /data-composition-id="main"[^>]*\bdata-fit="canvas"/.test(html);
    return { declared, width: number("width"), height: number("height"), duration: number("duration"), fit };
}

/**
 * Explicit values from --set and --variables, typed by the declarations; unknown ids fail, except a brand id the
 * composition does not use (one look given to every row), which is left out with a warning when `warnings` is given.
 */
export function explicitVariables(declared, sets = [], variables = {}, warnings = null) {
    const types = Object.fromEntries(declared.map((d) => [d.id, d.type]));
    const known = () => Object.keys(types).join(", ") || "none";
    const out = {};
    const put = (id, value, fromText) => {
        // `pose` and `mascotPose` are one variable: either name reaches a composition that declares the other.
        if (!types[id] && POSE_IDS.includes(id)) id = POSE_IDS.find((p) => types[p]) ?? id;
        const type = types[id];
        if (!type && warnings && BRAND_IDS.includes(id)) {
            warnings.push(`the composition declares no ${id}; that brand value is left out`);
            return;
        }
        if (!type) throw new UsageError(`the composition declares no variable ${id} (it has: ${known()})`);
        if (type === "number") {
            const number = typeof value === "number" ? value : Number(value);
            if (!Number.isFinite(number) || (fromText && String(value).trim() === "")) throw new UsageError(`${id} must be a number`);
            out[id] = number;
        } else if (type === "boolean") {
            const text = String(value).toLowerCase();
            if (typeof value === "boolean") out[id] = value;
            else if (["true", "1", "yes", "on"].includes(text)) out[id] = true;
            else if (["false", "0", "no", "off"].includes(text)) out[id] = false;
            else throw new UsageError(`${id} must be true or false`);
        } else {
            out[id] = typeof value === "string" ? (fromText ? valueFile(id, value) : value) : JSON.stringify(value);
        }
    };
    for (const [id, value] of Object.entries(variables)) put(id, value, false);
    for (const pair of sets) {
        const eq = pair.indexOf("=");
        if (eq < 1) throw new UsageError(`--set takes key=value, got ${pair}`);
        put(pair.slice(0, eq), pair.slice(eq + 1), true);
    }
    return out;
}

/**
 * `--set data=@diagram.json`: a value naming a file is that file's text (JSON made compact), so the agent passes data
 * without quoting it. A value starting with @ that names no file is kept ("@handle"), unless it looks like a file name.
 */
export function valueFile(id, value) {
    if (!value.startsWith("@") || value.length < 2) return value;
    const path = resolve(process.cwd(), value.slice(1));
    if (!existsSync(path) || !statSync(path).isFile()) {
        if (/\.(json|txt|tex|md|csv)$/i.test(value)) throw new UsageError(`${id}=${value}: there is no file ${path}`);
        return value;
    }
    const text = readFileSync(path, "utf8").trim();
    try {
        return JSON.stringify(JSON.parse(text));
    } catch {
        return text;
    }
}

// MARK: steps from the voice

/**
 * What steps can land on: the voice lines (items on Voiceover layers, by start) and the section markers, in project
 * frames: [{at, end, id|label}].
 */
export function stepAnchors(project) {
    const items = (project.tracks ?? []).flatMap((t) => t.items ?? []);
    const projectEnd = Math.max(0, ...items.map((i) => (i.at ?? 0) + (i.dur ?? 0)));
    const lines = (project.tracks ?? []).filter((t) => t.role === "voiceover").flatMap((t) => t.items ?? [])
        .filter((i) => (i.dur ?? 0) > 0).map((i) => ({ at: i.at ?? 0, end: (i.at ?? 0) + i.dur, id: i.id }))
        .sort((a, b) => a.at - b.at);
    const marks = (project.markers ?? []).filter((m) => m.kind === "section").sort((a, b) => a.at - b.at);
    const sections = marks.map((m, i) => ({ at: m.at, end: marks[i + 1]?.at ?? projectEnd, label: m.label ?? "" }));
    return { voice: lines, sections };
}

const NAMED = /^(line|section):(.+)$/;

/** True when data (JSON text) has steps or stops naming a line or section ("line:3", "section:Intro"). */
export function namesAnchors(text) {
    try {
        const data = JSON.parse(text);
        return [...(data.steps ?? []), ...(data.stops ?? [])].some((s) => typeof s?.at === "string" && NAMED.test(s.at));
    } catch {
        return false;
    }
}

/**
 * The data's steps (or stops) timed in seconds from the graphic's start: a step without `at` gets the start of the
 * next voice line (`from` "voice") or section marker ("sections") from atFrame on, "line:N" the N-th voice line,
 * "section:Label" that marker; a number is kept. Without atFrame the graphic starts 0.4 s before the first step; without
 * duration it ends 0.5 s after the last used line or section. Returns {data (JSON text), atFrame, duration}.
 */
export function resolveSteps(text, { anchors, from, atFrame, duration, fps }) {
    let data;
    try {
        data = JSON.parse(text);
    } catch {
        throw new UsageError("data is not JSON, so its steps cannot be timed");
    }
    const key = Array.isArray(data.steps) ? "steps" : Array.isArray(data.stops) ? "stops" : null;
    if (!key) throw new UsageError("--steps-from needs data with steps (or stops for big-canvas)");
    const list = data[key];
    const sequence = from ? anchors[from] : [];
    if (from && !sequence.length) {
        throw new UsageError(from === "voice" ? "there are no voice lines on a Voiceover layer to time the steps from" : "there are no section markers to time the steps from");
    }
    let next = atFrame === undefined ? 0 : sequence.findIndex((a) => a.at >= atFrame - 1);
    if (next < 0) next = sequence.length;
    const start = next;
    const used = [];
    const frames = list.map((step) => {
        const at = step?.at;
        if (typeof at === "number") return null;
        const named = typeof at === "string" ? NAMED.exec(at) : null;
        if (named) {
            const anchor = named[1] === "line" ? anchors.voice[Number(named[2]) - 1] : anchors.sections.find((s) => s.label === named[2]);
            if (!anchor) throw new UsageError(`"${at}": no such ${named[1] === "line" ? "voice line" : "section marker"}`);
            used.push(anchor);
            return anchor.at;
        }
        if (typeof at === "string" && at) throw new UsageError(`step at "${at}" is not seconds, "line:N" or "section:Label"`);
        if (!from) return undefined;
        const anchor = sequence[next];
        if (!anchor) throw new UsageError(`${list.length} ${key} but only ${sequence.length - start} ${from === "voice" ? "voice lines" : "section markers"} from frame ${atFrame ?? 0} on`);
        next += 1;
        used.push(anchor);
        return anchor.at;
    });
    const timed = frames.filter((f) => typeof f === "number");
    if (atFrame === undefined) atFrame = timed.length ? Math.max(0, Math.min(...timed) - Math.round(0.4 * fps)) : 0;
    if (duration === undefined && used.length) duration = Math.max(1, Math.max(...used.map((a) => a.end)) + Math.round(0.5 * fps) - atFrame);
    data[key] = list.map((step, i) => {
        if (typeof frames[i] !== "number") return step;
        return { ...step, at: Math.max(0, Math.round(((frames[i] - atFrame) / fps) * 100) / 100) };
    });
    return { data: JSON.stringify(data), atFrame, duration };
}

/** New data whose steps have no `at` keeps the times the recorded data gave the same steps (a label edit). */
export function keepStepTimes(text, recordedText) {
    try {
        const data = JSON.parse(text);
        const old = JSON.parse(recordedText);
        let changed = false;
        for (const key of ["steps", "stops"]) {
            if (!Array.isArray(data[key]) || !Array.isArray(old[key])) continue;
            data[key] = data[key].map((step, i) => {
                if (step?.at !== undefined || typeof old[key][i]?.at !== "number") return step;
                changed = true;
                return { ...step, at: old[key][i].at };
            });
        }
        return changed ? JSON.stringify(data) : text;
    } catch {
        return text;
    }
}

/** The brand's values for the standard ids this composition declares. */
export function brandVariables(brand, declared) {
    if (!brand || typeof brand !== "object") return {};
    const ids = new Set(declared.map((d) => d.id));
    const out = {};
    for (const [id, path] of Object.entries(BRAND_MAP)) {
        if (!ids.has(id)) continue;
        const value = path.reduce((node, key) => (node && typeof node === "object" ? node[key] : undefined), brand);
        if (typeof value === "string" && value.trim()) out[id] = value.trim();
    }
    return out;
}

/** Inputs recorded on a placed graphic's media, merged with a rerender's changes. */
export function mergeInputs(recorded, { explicit = {}, unset = [], fps, codec, name, brand, frame } = {}) {
    const variables = { ...(recorded.variables ?? {}), ...explicit };
    for (const id of unset) delete variables[id];
    const framed = mergeFrame(recorded.frame, frame);
    return {
        composition: recorded.composition,
        variables,
        fps: fps ?? recorded.fps,
        codec: codec ?? recorded.codec ?? "hevc",
        name: name ?? recorded.name,
        brand: brand ?? recorded.brand ?? true,
        ...(recorded.seconds ? { seconds: recorded.seconds } : {}),
        ...(framed ? { frame: framed } : {}),
    };
}

function frameRate(value) {
    if (Array.isArray(value)) return value[0] / (value[1] || 1);
    return Number(value) || 30;
}

/** A file name graphics.render accepts. */
export function safeName(text) {
    const cleaned = String(text).normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/đ/g, "d").replace(/Đ/g, "D")
        .replace(/[^A-Za-z0-9._-]+/g, "-").replace(/^[^A-Za-z0-9]+/, "").slice(0, 80);
    return cleaned || "graphic";
}

/** A path BashCut stores: relative to the project when the render landed in its generated/ folder. */
export function projectPath(path) {
    const index = path.indexOf("/generated/plugins/");
    return index > 0 ? path.slice(index + 1) : path;
}

/**
 * The ops of one rerender: add the new movie (alpha), point every item of `oldMedia` at it, fix lengths, record
 * the inputs. `render` is graphics.render's result; returns {ops, items, media}.
 */
export function rerenderOps(project, oldMedia, render, inputs, { keepLength = false, mediaId = randomUUID().toUpperCase() } = {}) {
    const projectFps = frameRate(project.format?.fps);
    const toProject = (frames, fps) => Math.floor((frames / fps) * projectFps + 1e-6);
    const old = (project.media ?? []).find((m) => m.id === oldMedia);
    const oldLength = old ? toProject(old.frames ?? 0, frameRate(old.fps)) : 0;
    const newLength = toProject(render.frames, render.fps);
    const ops = [{
        op: "addMedia",
        media: {
            id: mediaId, path: projectPath(render.path), kind: "video", fps: [render.fps, 1], frames: render.frames,
            width: render.width, height: render.height, hasAudio: false, alpha: true,
        },
    }];
    const items = [];
    for (const track of project.tracks ?? []) {
        for (const item of track.items ?? []) {
            if (item.media !== oldMedia) continue;
            const at = item.at ?? 0;
            const length = item.dur ?? 0;
            const sourceIn = Math.min(item.in ?? 0, Math.max(0, newLength - 1));
            ops.push({ op: "setSource", item: item.id, media: mediaId, sourceIn });
            const playedAll = (item.in ?? 0) + length >= oldLength - 1;
            let next = length;
            if (!keepLength && playedAll) next = newLength - sourceIn;
            next = Math.max(1, Math.min(next, newLength - sourceIn));
            const entry = { item: item.id, track: track.id, frames: next };
            if (next !== length) {
                ops.push({ op: "trim", item: item.id, edge: "end", toFrame: at + next });
                entry.from = length;
            }
            items.push(entry);
        }
    }
    if (items.length === 0) throw new Error(`no timeline item uses media ${oldMedia}`);
    ops.push({ op: "setMediaData", media: mediaId, patch: { graphics: record(inputs, render) } });
    return { ops, items, media: mediaId, length: newLength };
}

function record(inputs, render) {
    return {
        composition: inputs.composition, variables: inputs.variables, fps: inputs.fps, codec: inputs.codec,
        name: inputs.name, brand: inputs.brand, frames: render.frames,
        ...(inputs.seconds ? { seconds: inputs.seconds } : {}),
        ...(inputs.frame ? { frame: inputs.frame } : {}),
    };
}

// MARK: Talking to BashCut

// Every BashCut call goes through `call`: the bashcut CLI (spawnSync) for bin/graphic, or a runner set with useRunner,
// such as the plugin's own host channel when the Inspector view renders a graphic again.
let runner = null;

/** Sends BashCut calls (`["project", "get"]`-style CLI arguments) to `fn(args)` (async) instead of the CLI. */
export function useRunner(fn) {
    runner = fn;
}

async function call(args) {
    return runner ? runner(args) : cli(args);
}

function cli(args) {
    const program = process.env.BASHCUT_CLI || "bashcut";
    const out = spawnSync(program, args, { encoding: "utf8", maxBuffer: 256 * 1024 * 1024 });
    if (out.error) throw new Error(`cannot run ${program}: ${out.error.message}`);
    if (out.status !== 0) {
        const detail = (out.stderr || out.stdout || "").trim();
        throw new Error(`bashcut ${args.slice(0, 2).join(" ")} failed: ${detail.slice(0, 1500)}`);
    }
    const text = out.stdout.trim();
    try {
        return text ? JSON.parse(text) : null;
    } catch {
        throw new Error(`bashcut ${args.slice(0, 2).join(" ")} printed something that is not JSON: ${text.slice(0, 300)}`);
    }
}

async function applyOps(ops, baseRev, label) {
    const folder = mkdtempSync(join(tmpdir(), "bashcut-graphic-"));
    try {
        const file = join(folder, "ops.json");
        writeFileSync(file, JSON.stringify(ops));
        return await call(["timeline", "apply", file, "--base-rev", String(baseRev), "--label", label]);
    } finally {
        rmSync(folder, { recursive: true, force: true });
    }
}

/** Brand fonts: a font in the project's fonts/ folder is copied next to the composition (Chrome loads it by file). */
async function resolveFonts(variables, dir, warnings) {
    const fontIds = ["headingFont", "bodyFont"].filter((id) => variables[id] && !variables[id].startsWith("System-")
        && !/\.(ttf|otf|woff2?)$/i.test(variables[id]));
    if (fontIds.length === 0) return;
    let fonts = [];
    try {
        fonts = await call(["fonts", "list", "--project"]) ?? [];
    } catch {
        return;
    }
    let root;
    for (const id of fontIds) {
        const font = fonts.find((f) => f.file && (f.name === variables[id] || f.family === variables[id]));
        if (!font) continue;
        if (/\.ttc$/i.test(font.file)) {
            warnings.push(`${variables[id]} is in a .ttc collection, which the composition cannot load; it falls back to the design font`);
            continue;
        }
        root ??= dirname((await call(["context", "get"]))?.project ?? "");
        const source = join(root, "fonts", font.file);
        if (!existsSync(source)) continue;
        mkdirSync(join(dir, "fonts"), { recursive: true });
        copyFileSync(source, join(dir, "fonts", font.file));
        variables[id] = `fonts/${font.file}`;
    }
}

/** A library item's file path from `library get` (fileURL is a file URL or a path). */
export function libraryFilePath(item) {
    const url = item?.fileURL ?? item?.file;
    if (typeof url !== "string" || !url) return null;
    return url.startsWith("file://") ? decodeURIComponent(new URL(url).pathname) : url;
}

/** Brand logo: when the composition declares `logo`, the kit's logo sticker is copied next to it as brand-logo.<ext>. */
async function resolveLogo(variables, brand, declared, dir, warnings) {
    if (!declared.some((d) => d.id === "logo") || variables.logo || typeof brand?.logo !== "string") return false;
    let source;
    try {
        source = libraryFilePath(await call(["library", "get", brand.logo]));
    } catch (error) {
        warnings.push(`brand logo ${brand.logo}: ${error.message}`);
        return false;
    }
    if (!source || !existsSync(source)) {
        warnings.push(`brand logo ${brand.logo} has no file (an emoji sticker?); the composition keeps its own`);
        return false;
    }
    const name = `brand-logo${extname(source).toLowerCase()}`;
    copyFileSync(source, join(dir, name));
    variables.logo = name;
    return true;
}

/** The pose given with --set pose=… (or the older mascotPose), else undefined. */
function askedPose(variables) {
    return variables.pose ?? variables.mascotPose;
}

/** The mascot pose a composition asks for: its `pose` (given or declared), else "default", else the first. */
export function mascotPose(poses, declared, variables) {
    const names = Object.keys(poses ?? {}).sort();
    if (names.length === 0) return null;
    const asked = askedPose(variables) ?? declared.find((d) => POSE_IDS.includes(d.id))?.default;
    if (asked && names.includes(asked)) return asked;
    return names.includes("default") ? "default" : names[0];
}

/**
 * Brand mascot: when the composition declares `mascot` (type image), the kit's pose sticker named by `pose`
 * (else "default", else the first) is copied next to it as brand-mascot-<pose>.<ext>. Without poses in the brand the
 * slot stays empty and the composition hides it.
 */
async function resolveMascot(variables, brand, declared, dir, warnings) {
    if (!declared.some((d) => d.id === "mascot") || variables.mascot) return false;
    const poses = brand?.mascot;
    const pose = mascotPose(poses, declared, variables);
    const asked = askedPose(variables);
    if (!pose) {
        if (asked) warnings.push(`the brand has no mascot poses, so pose ${asked} shows nothing (add one: bashcut library brand-pose)`);
        return false;
    }
    if (asked && asked !== pose) {
        warnings.push(`the brand has no mascot pose ${asked} (it has: ${Object.keys(poses).sort().join(", ")}); ${pose} is used`);
    }
    let source;
    try {
        source = libraryFilePath(await call(["library", "get", poses[pose]]));
    } catch (error) {
        warnings.push(`brand mascot ${pose}: ${error.message}`);
        return false;
    }
    if (!source || !existsSync(source)) {
        warnings.push(`brand mascot ${pose} has no file; the composition keeps its own`);
        return false;
    }
    const name = `brand-mascot-${safeName(pose)}${extname(source).toLowerCase()}`;
    copyFileSync(source, join(dir, name));
    variables.mascot = name;
    return true;
}

/**
 * A value that is an absolute path to a file (a lottie pick in media/lottie, a picture) is copied next to the
 * composition and becomes its file name: the render serves only the composition folder. Plugin examples are left alone.
 */
export function resolveFiles(variables, declared, dir) {
    const real = realpathSync(dir);
    if (real.startsWith(realpathSync(fileURLToPath(new URL("../", import.meta.url))) + "/")) return;
    for (const { id, type } of declared) {
        const value = variables[id];
        if (!["string", "image"].includes(type) || typeof value !== "string" || !value.startsWith("/")) continue;
        if (!existsSync(value) || !statSync(value).isFile()) continue;
        if (dirname(realpathSync(value)) !== real) copyFileSync(value, join(dir, basename(value)));
        variables[id] = basename(value);
    }
}

async function resolveVariables(inputs, project, warnings) {
    const composition = readComposition(inputs.composition);
    const fromBrand = inputs.brand ? brandVariables(project.brand, composition.declared) : {};
    const explicitIds = new Set(Object.keys(inputs.variables));
    const applied = Object.keys(fromBrand).filter((id) => !explicitIds.has(id));
    const variables = { ...fromBrand, ...inputs.variables };
    if (inputs.brand && await resolveLogo(variables, project.brand, composition.declared, inputs.composition, warnings)) {
        applied.push("logo");
    }
    if (inputs.brand && await resolveMascot(variables, project.brand, composition.declared, inputs.composition, warnings)) {
        applied.push("mascot");
    }
    await resolveFonts(variables, inputs.composition, warnings);
    resolveFiles(variables, composition.declared, inputs.composition);
    const width = project.format?.width;
    const height = project.format?.height;
    delete inputs.canvas;
    if (composition.width && width && (composition.width !== width || composition.height !== height)) {
        if (composition.fit && height) inputs.canvas = { width, height };
        else warnings.push(`the composition is ${composition.width}×${composition.height} but the project is ${width}×${height}`);
    }
    return { variables, brand: applied };
}

async function renderNow(inputs, variables, dryRun, page) {
    const params = { composition: page ?? inputs.composition, fps: inputs.fps, codec: inputs.codec, variables, name: inputs.name };
    if (dryRun) return { dryRun: params };
    const started = await call(["plugins", "invoke", "graphics.render", "--params", JSON.stringify(params)]);
    const job = started?.job;
    if (!job) throw new Error(`graphics.render did not start a job: ${JSON.stringify(started)}`);
    for (let round = 0; round < 60; round += 1) {
        const waited = await call(["jobs", "wait", job, "--done", "--timeout", "110"]);
        const state = waited?.job?.state;
        if (state === "completed") {
            const result = waited.job.result ?? {};
            const render = result.result ?? result;
            if (!render.path) throw new Error(`graphics.render finished without a file: ${JSON.stringify(result).slice(0, 500)}`);
            return render;
        }
        if (state === "failed" || state === "cancelled") throw new Error(`graphics.render ${state}: ${waited.job.error ?? "no detail"}`);
    }
    throw new Error(`graphics.render job ${job} did not finish`);
}

/**
 * Renders with the page's data-duration set to `inputs.seconds` when it has one (so the exit lands on the end) and
 * the frame drawn around it when there is one.
 */
async function renderSpan(inputs, variables, dryRun) {
    if (dryRun || (!inputs.seconds && !inputs.frame && !inputs.canvas)) {
        const render = await renderNow(inputs, variables, dryRun);
        if (render.dryRun && inputs.seconds) render.dryRun.seconds = inputs.seconds;
        if (render.dryRun && inputs.frame) render.dryRun.frame = inputs.frame;
        if (render.dryRun && inputs.canvas) render.dryRun.canvas = inputs.canvas;
        return render;
    }
    return withPage(inputs.composition, { seconds: inputs.seconds, frame: inputs.frame, canvas: inputs.canvas }, () => renderNow(inputs, variables, false));
}

function lintNote(render, out) {
    if (render.lint && (render.lint.errors || render.lint.warnings)) {
        out.lint = { errors: render.lint.errors, warnings: render.lint.warnings, findings: (render.lint.findings ?? []).slice(0, 3) };
    }
}

/**
 * A composition inside this plugin (an example) is copied into the project's graphics/ folder first: rendering writes
 * gsap.min.js, brand fonts, logos and (plan) a stretched data-duration next to the page, and the plugin's own folder
 * must not change (its trust follows its files). The copy is also what rerender finds after a plugin update.
 * `slot` names the copy; an existing copy is reused as it is (it may have been edited for this project). `projectRoot`
 * is the project folder or a function that returns it (asked only for a plugin folder).
 */
/**
 * A composition folder: `given` resolved against `base` (the project folder in plan), or the plugin's example of that
 * name ("stat-counter") when there is no such folder.
 */
export function compositionFolder(given, base) {
    const asGiven = resolve(base, given);
    if (existsSync(asGiven) || given.includes("/")) return asGiven;
    const example = fileURLToPath(new URL(`../examples/${given}/`, import.meta.url)).replace(/\/$/, "");
    return existsSync(join(example, "index.html")) ? example : asGiven;
}

export async function ownComposition(dir, projectRoot, slot) {
    const plugin = realpathSync(fileURLToPath(new URL("../", import.meta.url)));
    const real = realpathSync(dir);
    if (!real.startsWith(plugin + "/")) return dir;
    if (typeof projectRoot === "function") projectRoot = await projectRoot();
    if (!projectRoot || projectRoot === ".") return dir;
    const copy = join(projectRoot, "graphics", safeName(slot));
    if (!existsSync(join(copy, "index.html"))) {
        mkdirSync(dirname(copy), { recursive: true });
        cpSync(real, copy, { recursive: true, filter: (from) => !["gsap.min.js", "diagram.js", "katex", "lottie.min.js"].includes(basename(from)) });
    }
    return copy;
}

async function place(target, options) {
    const given = compositionFolder(target, process.cwd());
    if (!existsSync(given) || !statSync(given).isDirectory()) throw new UsageError(`${given} is not a composition folder`);
    const project = await call(["project", "get"]) ?? {};
    const name = safeName(options.name ?? basename(given));
    const dir = options["dry-run"] ? given
        : await ownComposition(given, async () => dirname((await call(["context", "get"]))?.project ?? ""), `${name}-${randomBytes(3).toString("hex")}`);
    const declared = readComposition(dir).declared;
    const warnings = [];
    const explicit = explicitVariables(declared, options.set, options.variables, warnings);
    const dataText = explicit.data ?? declared.find((d) => d.id === "data")?.default;
    if (options["steps-from"] || (typeof dataText === "string" && namesAnchors(dataText))) {
        if (typeof dataText !== "string") throw new UsageError("--steps-from needs a composition with a data variable");
        const timed = resolveSteps(dataText, {
            anchors: stepAnchors(project), from: options["steps-from"], atFrame: options["at-frame"], duration: options.duration,
            fps: frameRate(project.format?.fps),
        });
        explicit.data = timed.data;
        options["at-frame"] = timed.atFrame;
        if (timed.duration !== undefined) options.duration = timed.duration;
    }
    const inputs = {
        composition: dir, variables: explicit, name,
        fps: options.fps ?? Math.round(frameRate(project.format?.fps)), codec: options.codec ?? "hevc",
        brand: !options["no-brand"],
    };
    if (options.frame) inputs.frame = checkFrame(options.frame) ?? undefined;
    // --duration also sets the composition's length, so its exit plays at the end of the span instead of being cut.
    if (options.duration !== undefined) {
        const frames = Number(options.duration);
        if (!(frames > 0)) throw new UsageError("--duration must be a positive number of frames");
        inputs.seconds = frames / frameRate(project.format?.fps);
    }
    const { variables, brand } = await resolveVariables(inputs, project, warnings);
    const render = await renderSpan(inputs, variables, options["dry-run"]);
    if (render.dryRun) return { ...render.dryRun, brand, ...(warnings.length ? { warnings } : {}) };
    const id = `graphic-${name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || "card"}-${randomBytes(3).toString("hex")}`;
    const added = await call(["library", "add", "--kind", "sticker", "--name", name, "--file", render.path, "--id", id]);
    const libraryId = added?.id ?? id;
    const rev = (await call(["project", "get"]))?.rev;
    const args = ["library", "place", libraryId, "--size", "1", "--position", "0.5,0.5", "--base-rev", String(rev)];
    if (options["at-frame"] !== undefined) args.push("--at-frame", String(options["at-frame"]));
    if (options.duration !== undefined) args.push("--duration", String(options.duration));
    if (options.track) args.push("--track", options.track);
    const placed = cli(args);
    const out = {
        item: placed.item, media: placed.media, track: placed.track, atFrame: options["at-frame"] ?? null,
        frames: placed.duration, path: render.path, rev: placed.rev, brand,
    };
    try {
        const recorded = await applyOps([{ op: "setMediaData", media: placed.media, patch: { graphics: record(inputs, render) } }],
            placed.rev, "Record graphic inputs");
        out.rev = recorded?.rev ?? out.rev;
    } catch (error) {
        warnings.push(`placed, but the render inputs were not recorded (rerender will not find them): ${error.message}`);
    }
    if (placed.note) warnings.push(placed.note);
    lintNote(render, out);
    if (warnings.length) out.warnings = warnings;
    return out;
}

export async function rerender(target, options) {
    const project = await call(["project", "get"]) ?? {};
    const media = project.media ?? [];
    const used = new Set((project.tracks ?? []).flatMap((t) => (t.items ?? []).map((i) => i.media)).filter(Boolean));
    let targets;
    if (options.all) {
        targets = media.filter((m) => m.data?.graphics && used.has(m.id)).map((m) => m.id);
        if (targets.length === 0) throw new Error("no placed graphic has recorded inputs (place them with bin/graphic place)");
    } else {
        const item = (project.tracks ?? []).flatMap((t) => t.items ?? []).find((i) => i.id === target);
        const id = item ? item.media : target;
        const found = media.find((m) => m.id === id);
        if (!found) throw new Error(`${target} is neither a timeline item nor a media of this project`);
        if (!found.data?.graphics) throw new Error(`${target} has no recorded render inputs (it was not placed with bin/graphic place)`);
        targets = [id];
    }
    const warnings = [];
    const renders = [];
    for (const id of targets) {
        const recorded = media.find((m) => m.id === id).data.graphics;
        if (!recorded.composition || !existsSync(join(recorded.composition, "index.html"))) {
            throw new Error(`the composition of ${id} is gone: ${recorded.composition}`);
        }
        const declared = readComposition(recorded.composition).declared;
        const unknown = options.unset.filter((key) => !declared.some((d) => d.id === key));
        if (unknown.length && !options.all) throw new UsageError(`the composition declares no variable ${unknown.join(", ")}`);
        // With --all, a change applies to the graphics that declare it.
        const ids = new Set(declared.map((d) => d.id));
        if (POSE_IDS.some((id) => ids.has(id))) POSE_IDS.forEach((id) => ids.add(id));
        const sets = options.all ? options.set.filter((pair) => ids.has(pair.split("=")[0])) : options.set;
        const given = options.all && options.variables
            ? Object.fromEntries(Object.entries(options.variables).filter(([key]) => ids.has(key))) : options.variables;
        const explicit = explicitVariables(declared, sets, given, warnings);
        const dataText = explicit.data ?? recorded.variables?.data;
        if (options["steps-from"] || (explicit.data && namesAnchors(explicit.data))) {
            if (typeof dataText !== "string") throw new UsageError("--steps-from needs a composition with a data variable");
            const first = (project.tracks ?? []).flatMap((t) => t.items ?? []).filter((i) => i.media === id).sort((a, b) => (a.at ?? 0) - (b.at ?? 0))[0];
            explicit.data = resolveSteps(dataText, {
                anchors: stepAnchors(project), from: options["steps-from"], atFrame: first?.at ?? 0, duration: 1,
                fps: frameRate(project.format?.fps),
            }).data;
        } else if (explicit.data && typeof recorded.variables?.data === "string") {
            explicit.data = keepStepTimes(explicit.data, recorded.variables.data);
        }
        const inputs = mergeInputs(recorded, {
            explicit, unset: options.unset, fps: options.fps,
            codec: options.codec, name: options.name && safeName(options.name),
            brand: options.brand ? true : options["no-brand"] ? false : undefined, frame: options.frame,
        });
        const { variables, brand } = await resolveVariables(inputs, project, warnings);
        const render = await renderSpan(inputs, variables, options["dry-run"]);
        renders.push({ id, inputs, render, brand });
    }
    if (options["dry-run"]) return { graphics: renders.map((r) => ({ media: r.id, ...r.render.dryRun, brand: r.brand })) };
    const fresh = await call(["project", "get"]) ?? {};
    const ops = [];
    const graphics = [];
    for (const { id, inputs, render, brand } of renders) {
        const plan = rerenderOps(fresh, id, render, inputs, { keepLength: options["keep-length"] });
        ops.push(...plan.ops);
        const entry = { media: plan.media, replaced: id, path: render.path, frames: plan.length, items: plan.items, brand };
        const changed = plan.items.filter((i) => i.from !== undefined);
        if (changed.length) entry.note = `length changed for ${changed.map((i) => `${i.item} ${i.from}→${i.frames}`).join(", ")} frames`;
        lintNote(render, entry);
        graphics.push(entry);
    }
    const applied = await applyOps(ops, fresh.rev, graphics.length > 1 ? "Re-render graphics" : "Re-render graphic");
    const out = graphics.length === 1 && !options.all ? { ...graphics[0], rev: applied?.rev } : { graphics, rev: applied?.rev };
    if (warnings.length) out.warnings = [...new Set(warnings)];
    return out;
}

// MARK: examples

/**
 * The examples as one short row each (name, what it draws in its first sentence, seconds, its own variables as
 * "id:type"), enough to choose; with NAME the full row: every variable's label and default, the brand ids it
 * declares, its pitfalls and learned lessons.
 */
export async function examples(name) {
    const root = fileURLToPath(new URL("../examples/", import.meta.url));
    const names = readdirSync(root).filter((n) => existsSync(join(root, n, "index.html"))).sort();
    if (name && !names.includes(name)) throw new UsageError(`no example ${name} (there are: ${names.join(", ")})`);
    return Promise.all((name ? [name] : names).map(async (n) => {
        const html = readFileSync(join(root, n, "index.html"), "utf8");
        const about = (/<!--([\s\S]*?)-->/.exec(html)?.[1] ?? "").replace(/\s+/g, " ").trim();
        const { declared, duration } = readComposition(join(root, n));
        const own = declared.filter((d) => !BRAND_IDS.includes(d.id) && !BRAND_SLOTS.includes(d.id));
        if (!name) {
            const first = /^.*?[.!?](?=\s|$)/.exec(about)?.[0] ?? about;
            const brief = { name: n, about: first, seconds: duration, variables: own.map((d) => `${d.id}:${d.type}`).join(" ") };
            // A mascot slot is filled from the brand (pose by --set pose=…), so it is not one of the variables.
            if (declared.some((d) => d.id === "mascot")) brief.mascot = true;
            return brief;
        }
        const row = { name: n, about, seconds: duration, folder: join(root, n) };
        row.variables = own.map((d) => {
            const shown = typeof d.default === "string" && d.default.length > 160 ? `${d.default.slice(0, 160)}…` : d.default;
            return { id: d.id, type: d.type, label: d.label, default: shown };
        });
        row.brand = declared.filter((d) => BRAND_IDS.includes(d.id) || BRAND_SLOTS.includes(d.id)).map((d) => d.id);
        row.pitfalls = pitfalls(html);
        const learned = await blockLessons(n);
        if (learned) row.lessons = learned;
        return row;
    }));
}

/** The page's `<!-- Pitfalls: - one - two -->` comment as a list of lines; empty without one. */
export function pitfalls(html) {
    const comment = /<!--\s*Pitfalls:([\s\S]*?)-->/.exec(html)?.[1];
    if (!comment) return [];
    return comment.split(/\n\s*-\s+/).map((line) => line.replace(/^\s*-\s+/, "").replace(/\s+/g, " ").trim()).filter(Boolean);
}

/** Active lessons tagged block:NAME ({id, title, fix, check}), or null when BashCut cannot be asked. */
async function blockLessons(name) {
    try {
        const lessons = await call(["knowledge", "lessons", "--tag", `block:${name}`, "--status", "active"]) ?? [];
        return lessons.map((l) => Object.fromEntries(Object.entries({ id: l.id, title: l.title, fix: l.fix, check: l.check })
            .filter(([, value]) => value)));
    } catch {
        return null;
    }
}

// MARK: plan

/** Words as compared: lower case, letters and digits only (tone marks kept). */
function token(text) {
    return String(text).normalize("NFC").toLowerCase().replace(/[^\p{L}\p{N}]+/gu, "");
}

/** Seconds from the graphic's start to the first place `quote` is said in `words` [{text, at}]. */
export function wordTime(quote, words) {
    const wanted = String(quote).split(/\s+/).map(token).filter(Boolean);
    const heard = words.map((w) => token(w.text));
    if (wanted.length === 0) throw new UsageError(`"@" needs words after it`);
    for (let i = 0; i + wanted.length <= heard.length; i += 1) {
        if (wanted.every((w, k) => heard[i + k] === w)) return words[i].at;
    }
    const said = words.map((w) => w.text).join(" ");
    throw new UsageError(`"@${quote}" is not said during this graphic (heard: ${said.slice(0, 300) || "nothing"})`);
}

/** A value with every "@words" string turned into seconds (lists and objects walked). */
export function resolveWordTimes(value, words) {
    if (typeof value === "string" && value.startsWith("@") && value.length > 1) return wordTime(value.slice(1), words);
    if (Array.isArray(value)) return value.map((v) => resolveWordTimes(v, words));
    if (value && typeof value === "object") {
        return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, resolveWordTimes(v, words)]));
    }
    return value;
}

const BACKUP = ".index.html.plan-original";

/** Puts back an index.html a stopped render left stretched. */
export function restorePage(dir) {
    const backup = join(dir, BACKUP);
    if (existsSync(backup)) {
        copyFileSync(backup, join(dir, "index.html"));
        rmSync(backup, { force: true });
    }
}

/**
 * Runs `work` with index.html's root data-duration set to `seconds` and the frame drawn around the composition (a
 * second root file would be a lint error and a second entry point), then puts the page back.
 */
export async function withPage(dir, { seconds, frame, canvas } = {}, work) {
    restorePage(dir);
    const page = join(dir, "index.html");
    let html = readFileSync(page, "utf8");
    const root = /(data-composition-id="main"[^>]*\bdata-duration=")([\d.]+)(")/;
    if (seconds && !root.test(html)) throw new Error(`${page} has no root with data-composition-id="main" and data-duration`);
    // Rounded down to the millisecond: the renderer rounds frames up, so 110 frames at 30 fps (3.667 s) stay 110.
    if (seconds) html = html.replace(root, `$1${Math.floor(seconds * 1000) / 1000}$3`);
    if (canvas) html = withCanvas(html, canvas);
    if (frame) html = withFrameMarkup(html, frame);
    copyFileSync(page, join(dir, BACKUP));
    try {
        writeFileSync(page, html);
        return await work();
    } finally {
        restorePage(dir);
    }
}

/** The page with its root's data-width and data-height set to `canvas` (a data-fit="canvas" composition). */
export function withCanvas(html, { width, height }) {
    return html.replace(/<[^>]*data-composition-id="main"[^>]*>/, (tag) => tag.replace(/\bdata-width="[\d.]+"/, `data-width="${width}"`)
        .replace(/\bdata-height="[\d.]+"/, `data-height="${height}"`));
}

/** What an agent needs from plan apply: the outcome, the problems and the review, not the change list. */
export function briefApply(apply) {
    if (!apply || apply.error) return apply;
    const keep = ["ok", "rev", "duration", "lines", "graphics", "captions", "sections", "problems", "review"];
    const out = Object.fromEntries(keep.filter((k) => apply[k] !== undefined).map((k) => [k, apply[k]]));
    if (Array.isArray(out.problems)) out.problems = out.problems.map(({ facts, ...p }) => (p.id === "review-profile-unset" ? { ...p, unsetLimits: facts?.unsetLimits } : p));
    return out;
}

/** What a render depends on, so an unchanged graphic is not rendered again. */
export function inputsHash(dir, variables, seconds, fps, codec, frame = null, canvas = null) {
    // Every file the page can load counts (a shared chrome.js, map tiles, a logo), not only index.html: a change to
    // any of them renders again. What rendering itself writes (gsap.min.js, movies, snapshots) is skipped; large files
    // count by size and time.
    const hash = createHash("sha256").update(JSON.stringify([variables, Math.round(seconds * 100), fps, codec]));
    if (frame) hash.update(JSON.stringify([FRAME_VERSION, frame]));
    if (canvas) hash.update(JSON.stringify(canvas));
    const walk = (folder, depth) => {
        for (const name of readdirSync(folder).sort()) {
            if (name.startsWith(".") || ["node_modules", "gsap.min.js", "snapshots", "renders"].includes(name)) continue;
            const path = join(folder, name);
            const info = statSync(path);
            if (info.isDirectory()) {
                if (depth < 3) walk(path, depth + 1);
            } else if (!/\.(mov|mp4|m4v|webm)$/i.test(name)) {
                hash.update(relative(dir, path));
                hash.update(info.size > 4_000_000 ? `${info.size}:${info.mtimeMs}` : readFileSync(path));
            }
        }
    };
    walk(dir, 0);
    return hash.digest("hex").slice(0, 16);
}

async function planGraphics(options) {
    const project = await call(["project", "get"]) ?? {};
    const root = dirname((await call(["context", "get"]))?.project ?? "");
    const entries = project.plan?.cut?.graphics ?? [];
    const only = options.only ? new Set(String(options.only).split(",").map((s) => s.trim())) : null;
    if (only) {
        const unknown = [...only].filter((id) => !entries.some((e) => e.id === id));
        if (unknown.length) throw new UsageError(`plan.cut.graphics has no ${unknown.join(", ")}`);
    }
    const check = await call(["plan", "check", "--words"]) ?? {};
    const rows = Object.fromEntries((check.graphics ?? []).map((row) => [row.id, row]));
    const fps = Math.round(frameRate(project.format?.fps));
    const media = project.media ?? [];
    const rendered = [];
    const kept = [];
    const warnings = [];
    const patch = {};
    const records = [];
    for (const entry of entries) {
        if (!entry.render || (only && !only.has(entry.id))) continue;
        const row = rows[entry.id];
        if (!row || !(row.seconds > 0)) throw new Error(`plan check gives graphic ${entry.id} no span: ${JSON.stringify((check.problems ?? []).filter((p) => p.entry === entry.id))}`);
        const seconds = row.short ?? row.seconds;
        const given = entry.render.composition;
        if (typeof given !== "string" || !given) throw new UsageError(`graphic ${entry.id}: render.composition is missing`);
        const asGiven = compositionFolder(given, root);
        if (!existsSync(join(asGiven, "index.html"))) throw new UsageError(`graphic ${entry.id}: ${asGiven} has no index.html`);
        const dir = options["dry-run"] ? asGiven : await ownComposition(asGiven, root, `${entry.id}-${basename(asGiven)}`);
        const declared = readComposition(dir).declared;
        const asked = resolveWordTimes({ ...(entry.render.variables ?? {}), ...(entry.render.set ?? {}) }, row.words ?? []);
        let frame;
        try {
            frame = checkFrame(resolveWordTimes(entry.render.frame, row.words ?? []));
        } catch (error) {
            throw new UsageError(`graphic ${entry.id}: ${error.message}`);
        }
        const inputs = {
            composition: dir, variables: explicitVariables(declared, [], asked, warnings), name: safeName(entry.render.name ?? `${entry.id}-${basename(dir)}`),
            fps, codec: options.codec ?? entry.render.codec ?? "hevc", brand: entry.render.brand !== false,
            ...(frame ? { frame } : {}),
        };
        const { variables, brand } = await resolveVariables(inputs, project, warnings);
        restorePage(dir);
        const hash = inputsHash(dir, variables, seconds, fps, inputs.codec, frame, inputs.canvas);
        const current = media.find((m) => m.id === entry.media);
        if (!options.force && current?.data?.graphics?.hash === hash) {
            kept.push(entry.id);
            continue;
        }
        if (options["dry-run"]) {
            rendered.push({ id: entry.id, seconds, variables, brand, ...(frame ? { frame } : {}), ...(inputs.canvas ? { canvas: inputs.canvas } : {}) });
            continue;
        }
        const render = await withPage(dir, { seconds, frame, canvas: inputs.canvas }, () => renderNow(inputs, variables, false));
        const imported = await call(["media", "import", render.path, "--origin", "ai", "--base-rev", "last"]) ?? {};
        const id = imported.media ?? imported.files?.[0]?.media ?? imported.id;
        if (!id) throw new Error(`media import returned no media for ${render.path}: ${JSON.stringify(imported).slice(0, 300)}`);
        patch[entry.id] = { media: id };
        records.push({ op: "setMediaData", media: id, patch: { graphics: { ...record(inputs, render), seconds, hash } } });
        const out = { id: entry.id, media: id, seconds, frames: render.frames, renderSeconds: render.renderSeconds };
        lintNote(render, out);
        rendered.push(out);
    }
    const result = { rendered, kept };
    if (options["dry-run"]) return result;
    if (records.length) await applyOps(records, (await call(["project", "get"]))?.rev, "Record graphic inputs");
    if (!options["no-apply"]) {
        const args = ["plan", "apply", "--base-rev", String((await call(["project", "get"]))?.rev)];
        if (Object.keys(patch).length) args.push("--patch", JSON.stringify({ graphics: patch }));
        try {
            result.apply = briefApply(cli(args));
        } catch (error) {
            result.apply = { error: error.message };
            if (Object.keys(patch).length) {
                // Keep the rendered media IDs in plan.cut, so fixing the list does not render again.
                await saveMedia(project, patch);
            }
        }
    } else if (Object.keys(patch).length) {
        await saveMedia(project, patch);
    }
    if (warnings.length) result.warnings = [...new Set(warnings)];
    return result;
}

/** plan.cut with each patched graphic's media set. */
export function mergedCut(cut, patch) {
    return { ...cut, graphics: (cut?.graphics ?? []).map((g) => (patch[g.id] ? { ...g, ...patch[g.id] } : g)) };
}

/** Writes the rendered media IDs into plan.cut without building it. */
async function saveMedia(project, patch) {
    const folder = mkdtempSync(join(tmpdir(), "bashcut-graphic-"));
    try {
        const file = join(folder, "plan.json");
        writeFileSync(file, JSON.stringify({ cut: mergedCut(project.plan?.cut, patch) }));
        await call(["project", "set-data", "plan", file, "--merge", "--base-rev", String((await call(["project", "get"]))?.rev)]);
    } finally {
        rmSync(folder, { recursive: true, force: true });
    }
}

export async function main(argv) {
    try {
        const { command, target, options } = parseArgs(argv);
        const result = command === "examples" ? await examples(target)
            : command === "plan" ? await planGraphics(options) : command === "place" ? await place(target, options)
                : await rerender(target, options);
        process.stdout.write(JSON.stringify(result) + "\n");
        return 0;
    } catch (error) {
        process.stderr.write(JSON.stringify({ error: error.message }) + "\n");
        return error instanceof UsageError ? 2 : 1;
    }
}

// Compared as real paths: an installed plugin is often reached through a symlink, and Node resolves the module's own
// URL to the real file, so a plain comparison never matched and the script exited doing nothing.
if (process.argv[1] && realpathSync(resolve(process.argv[1])) === realpathSync(fileURLToPath(import.meta.url))) {
    process.exitCode = await main(process.argv.slice(2));
}
