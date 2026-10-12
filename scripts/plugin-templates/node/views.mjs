// {{NAME}}: a panel in BashCut's left rail with three views (plugin API 8).
//
// - "main" (the rail panel): a counter kept in `state`, a button that reads the timeline over the host channel while
//   the view shows progress, and a button that opens the sheet.
// - "media" (a tab in the agent dock): the project's media as a list whose rows drag onto the timeline (`file`) and
//   measure their loudness with another plugin's audio.loudness (plugins.invoke, listed in "uses", then a job).
// - "form" (a sheet): a short form that closes itself with "close": true.
//
// Views are answers, not widgets: BashCut sends view.render (draw) or view.event (the user did something) and the
// plugin answers with the whole component tree. Keep what you need between requests in `state`.
// https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#plugin-panels-and-views
import { basename, isAbsolute } from "node:path";
import { hostFeatures, PluginError } from "./bashcut-plugin.mjs";

const PLUGIN_ID = "{{ID}}";

export async function handle(method, params, host) {
    if (method === "view.render" || method === "view.event") {
        const view = VIEWS[params.view];
        if (!view) throw new PluginError("unknown_view", `{{PLAIN_NAME}} has no view ${params.view}`);
        return view(params, params.state ?? {}, params.values ?? {}, params.event ?? {}, host);
    }
    if (method === "plugin.action" && params.action === "{{ACTION_ID}}") {
        await host.call("plugins.show-view", { plugin: PLUGIN_ID, view: "form" });
        return { message: "Opened the form" };
    }
    throw new PluginError("unknown_method", `{{PLAIN_NAME}} does not handle ${method}`);
}

const note = (message, extra = {}) => (message ? { type: "text", text: message, style: "caption", ...extra } : { type: "spacer", size: 0 });

async function mainView(params, state, values, event, host) {
    let count = state.count ?? 0;
    let message = state.message ?? "";
    if (event.node === "add") count += 1;
    if (event.node === "timeline") {
        host.render([{ type: "progress", label: "Reading the timeline…" }]);
        const timeline = (await host.call("timeline.get")) ?? {};
        message = `The timeline has ${(timeline.tracks ?? []).length} layers.`;
    }
    if (event.node === "openForm") await host.call("plugins.show-view", { plugin: PLUGIN_ID, view: "form" });
    return {
        title: "{{PLAIN_NAME}}",
        state: { count, message },
        body: [
            { type: "text", text: `Clicked **${count}** times`, markdown: true },
            { type: "row", children: [
                { type: "button", id: "add", title: "Add one", icon: "plus", style: "primary" },
                { type: "button", id: "timeline", title: "Read the timeline", icon: "film" },
            ] },
            { type: "button", id: "openForm", title: "Open the form", icon: "macwindow" },
            note(message),
        ],
    };
}

async function mediaView(params, state, values, event, host) {
    let message = state.message ?? "";
    let media = state.media;
    if (!media || event.node === "refresh") {
        const answer = await host.call("media.list");
        const items = Array.isArray(answer) ? answer : (answer?.media ?? []);
        media = items.filter((m) => m && m.id).map((m) => ({
            id: m.id, name: m.name ?? basename(String(m.path ?? "")), kind: m.kind ?? "", path: m.absolutePath ?? m.path ?? "",
        }));
    }
    if (event.node === "media" && event.type === "action") {
        const row = media.find((m) => m.id === event.value?.item);
        if (row) {
            // A capability without its own command: plugins.invoke runs as a job; waitJob polls it.
            const measured = (await host.waitJob(await host.call("plugins.invoke", {
                capability: "audio.loudness", params: { mediaPath: row.path },
            }))) ?? {};
            const lufs = (measured.result ?? measured).integratedLUFS;
            message = lufs === undefined ? `${row.name}: no loudness` : `${row.name}: ${lufs} LUFS`;
        }
    }
    const rows = media.map((m) => ({
        id: m.id, title: m.name, subtitle: m.kind, icon: "film",
        // An absolute path to a local file lets the row drag onto the timeline (host feature views.drag).
        ...(isAbsolute(m.path) ? { file: m.path } : {}),
        actions: [{ id: "loudness", title: "Measure loudness", icon: "speedometer" }],
    }));
    return {
        title: "Media",
        state: { media, message },
        body: [
            { type: "button", id: "refresh", title: "Refresh", icon: "arrow.clockwise" },
            { type: "list", id: "media", items: rows, empty: "No media in the project" },
            note(message),
        ],
    };
}

async function formView(params, state, values, event, host) {
    if (event.node === "cancel") return { body: [], close: true, state: {} };
    let problem = "";
    if (event.node === "save" || event.node === "title") {
        const title = String(values.title ?? "").trim();
        if (title) {
            await host.call("ui.action", { action: "notify", target: `Saved ${title} (${values.color ?? ""})` });
            return { body: [], close: true, state: {}, notify: "Saved" };
        }
        problem = "Write a title first.";
    }
    // Newer components: check the hello's features and fall back to a text field in an older BashCut.
    const color = hostFeatures.has("views.colorPicker")
        ? { type: "colorPicker", id: "color", label: "Colour", value: values.color || "#FF8800" }
        : { type: "textField", id: "color", label: "Colour (hex)", value: values.color || "#FF8800" };
    return {
        title: "Form",
        body: [
            { type: "textField", id: "title", label: "Title", placeholder: "Chapter 1", submit: true },
            color,
            note(problem, { color: "red" }),
            { type: "row", children: [
                { type: "button", id: "cancel", title: "Cancel" },
                { type: "spacer" },
                { type: "button", id: "save", title: "Save", style: "primary" },
            ] },
        ],
    };
}

const VIEWS = { main: mainView, media: mediaView, form: formView };
