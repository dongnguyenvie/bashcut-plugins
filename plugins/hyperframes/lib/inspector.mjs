// The Inspector view "graphic" (plugin view location inspector): for a selected item whose media this plugin rendered
// (media.data.graphics, recorded by bin/graphic), its composition's variables as fields and a button that renders it
// again with the edited values and points every use at the new movie as one undoable edit — what
// `bin/graphic rerender ITEM --variables …` does, without an agent. Other items get an empty view (no room taken).
//
// The view's request handles the whole re-render: bin/graphic's calls go over the host channel (useRunner), and the
// render runs here in this process (the session handles one request at a time, so a plugins.invoke of our own
// graphics.render would wait behind this request for good).
import { randomUUID } from "node:crypto";
import { mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { hostFeatures } from "./bashcut-plugin.mjs";
import { BRAND_IDS, readComposition, rerender, useRunner } from "./graphic.mjs";

export const VIEW = "graphic";

const WORDS = {
    en: { title: "Graphic", unreadable: "Its composition cannot be read:", nothing: "Nothing changed.", rendering: "Rendering…",
          rendered: (n) => `Rendered again (${n} frames).`, look: "Look (empty keeps the brand)", render: "Render again" },
    vi: { title: "Đồ hoạ", unreadable: "Không đọc được composition:", nothing: "Chưa có gì thay đổi.", rendering: "Đang render…",
          rendered: (n) => `Đã render lại (${n} frame).`, look: "Giao diện (để trống thì theo brand)", render: "Render lại" },
};

/** view.render / view.event for the Inspector view. */
export async function graphicView(params, host, renderHere) {
    const words = String(params.locale ?? "").startsWith("vi") ? WORDS.vi : WORDS.en;
    const context = params.context ?? {};
    const item = context.selection;
    const recorded = context.media?.data?.graphics;
    if (!item?.id || !recorded?.composition) return { body: [] };
    let declared;
    try {
        declared = readComposition(recorded.composition).declared;
    } catch (error) {
        return { title: words.title, body: [{ type: "text", text: `${words.unreadable} ${error.message}`, style: "caption", color: "orange" }] };
    }
    const values = params.values ?? {};
    const event = params.event;
    let notice = null;
    if (event?.node === "render" && event.type === "click") {
        const changed = changedVariables(declared, recorded.variables ?? {}, values);
        if (Object.keys(changed).length === 0) {
            notice = { type: "text", text: words.nothing, style: "caption" };
        } else {
            host.event({ kind: "render", title: words.title, body: [{ type: "progress", label: words.rendering }] });
            try {
                const result = await rerenderWithHost(host, item.id, changed, renderHere, context);
                notice = { type: "text", text: words.rendered(result.frames ?? "?"), style: "caption", color: "green" };
            } catch (error) {
                notice = { type: "text", text: error.message, style: "caption", color: "red" };
            }
        }
    }
    return { title: words.title, body: fields(declared, recorded, values, notice, words, hostFeatures) };
}

/** The variables whose field differs from what the graphic was rendered with, typed by their declarations. */
export function changedVariables(declared, recordedVariables, values) {
    const changed = {};
    for (const d of declared) {
        if (!(d.id in values)) continue;
        const now = typed(d, values[d.id]);
        if (now === undefined) continue;
        const before = d.id in recordedVariables ? recordedVariables[d.id] : d.default;
        if (JSON.stringify(comparable(d, now)) !== JSON.stringify(comparable(d, before))) changed[d.id] = now;
    }
    return changed;
}

function typed(declaration, value) {
    if (declaration.type === "number") {
        const n = Number(value);
        return value === "" || Number.isNaN(n) ? undefined : n;
    }
    if (declaration.type === "boolean") return value === true || value === "true";
    return value == null ? "" : String(value);
}

/** The colour picker answers `#AABBCC` in upper case: "#aabbcc" and "#abc" recorded earlier are the same colour. */
function comparable(declaration, value) {
    if (declaration.type !== "color" || typeof value !== "string") return value;
    return hexColor(value)?.toUpperCase() ?? value;
}

/** `#RRGGBB` or `#RRGGBBAA` (3- and 4-digit forms widened) for a hex colour; null for anything else (rgba(), names). */
export function hexColor(value) {
    const match = /^#([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})$/i.exec(String(value ?? "").trim());
    if (!match) return null;
    const digits = match[1].length <= 4 ? [...match[1]].map((c) => c + c).join("") : match[1];
    return `#${digits}`;
}

function shown(declaration, recordedVariables, values) {
    if (declaration.id in values) return values[declaration.id];
    const value = declaration.id in recordedVariables ? recordedVariables[declaration.id] : declaration.default;
    if (declaration.type === "boolean") return Boolean(value);
    return value == null ? "" : String(value);
}

/**
 * The view's components. Colours get a colour well and fonts a font menu (by family: the composition sets CSS
 * font-family) when the host lists `views.colorPicker` / `views.fontPicker` in its hello; an older BashCut gets text
 * fields, so those features stay out of plugin.json `features` (that would make it refuse the whole plugin). A
 * colour that is not hex (rgba(), a name) keeps a text field too: the colour well only takes hex.
 */
export function fields(declared, recorded, values, notice, words, features = new Set()) {
    const own = declared.filter((d) => !BRAND_IDS.includes(d.id) && d.id !== "logo" && d.id !== "mascot");
    const look = declared.filter((d) => BRAND_IDS.includes(d.id));
    const node = (d) => {
        const label = d.label ?? d.id;
        const value = shown(d, recorded.variables ?? {}, values);
        if (d.type === "boolean") return { type: "toggle", id: d.id, label, value };
        if (d.type === "color" && features.has("views.colorPicker")) {
            const hex = hexColor(value);
            if (hex) return { type: "colorPicker", id: d.id, label, value: hex, ...(hex.length === 9 ? { alpha: true } : {}) };
        }
        if (d.type === "font" && features.has("views.fontPicker")) return { type: "fontPicker", id: d.id, label, value, by: "family" };
        if (d.type === "string" && String(value).length > 40) return { type: "textArea", id: d.id, label, value, height: 60 };
        return { type: "textField", id: d.id, label, value };
    };
    const body = [{ type: "text", text: recorded.name ?? "", style: "caption" }, ...own.map(node)];
    if (look.length) body.push({ type: "section", title: words.look, children: look.map(node) });
    body.push({ type: "button", id: "render", title: words.render, icon: "arrow.clockwise", style: "primary" });
    if (notice) body.push(notice);
    return body;
}

/**
 * bin/graphic's rerender over the host channel: its CLI-style calls become host commands, and the render runs here
 * through `renderHere(params, host)` (handlers.mjs render) into the project's generated/plugins folder.
 */
async function rerenderWithHost(host, itemId, variables, renderHere, context) {
    const projectFile = context.project?.path ?? (await host.call("context.get"))?.project;
    const jobs = new Map();
    useRunner(async (args) => {
        const [group, command, ...rest] = args;
        const option = (name) => (rest.includes(name) ? rest[rest.indexOf(name) + 1] : undefined);
        const key = `${group} ${command}`;
        if (key === "project get") return host.call("project.get");
        if (key === "context get") return host.call("context.get");
        if (key === "fonts list") return host.call("fonts.list", { project: rest.includes("--project") });
        if (key === "library get") return host.call("library.get", { id: rest[0] });
        if (key === "plugins invoke" && rest[0] === "graphics.render") {
            if (!projectFile) throw new Error("save the project first: the render goes into its generated folder");
            const outputDirectory = join(dirname(projectFile), "generated/plugins/bashcut.hyperframes/inspector", randomUUID());
            mkdirSync(outputDirectory, { recursive: true });
            const job = `inspector-${jobs.size + 1}`;
            jobs.set(job, renderHere({ ...JSON.parse(option("--params")), outputDirectory }, host));
            return { job, state: "running" };
        }
        if (key === "jobs wait" && jobs.has(rest[0])) {
            try {
                return { job: { state: "completed", result: await jobs.get(rest[0]) } };
            } catch (error) {
                return { job: { state: "failed", error: error.message } };
            }
        }
        if (key === "timeline apply") {
            const { readFileSync } = await import("node:fs");
            return host.call("timeline.apply", {
                ops: JSON.parse(readFileSync(rest[0], "utf8")), baseRev: Number(option("--base-rev")), label: option("--label"),
            });
        }
        throw new Error(`the Inspector cannot run bashcut ${key}`);
    });
    try {
        return await rerender(itemId, { set: [], unset: [], variables });
    } finally {
        useRunner(null);
    }
}
