// {{NAME}}: hooks on export.finished and media.imported.
//
// BashCut calls `handle` with method "plugin.hook" after an event. Hooks are notify-only: the event already happened.
// A hook declared with "edits": true may return operations or pluginData, which BashCut applies as one undoable edit
// (or keeps for review). https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#hooks
import { basename } from "node:path";
import { PluginError } from "./bashcut-plugin.mjs";

export async function handle(method, params, host) {
    if (method !== "plugin.hook") throw new PluginError("unknown_method", `{{PLAIN_NAME}} does not handle ${method}`);
    const payload = params.payload ?? {};
    if (params.event === "export.finished") {
        // Count exports in this plugin's own project data.
        const exports = params.context?.pluginData?.exports ?? 0;
        const output = payload.output ?? "";
        return {
            label: "Remember last export",
            pluginData: { lastExport: output, exports: exports + 1 },
            message: `Exported ${basename(output)} (export ${exports + 1})`,
        };
    }
    if (params.event === "media.imported") return { message: `Imported ${(payload.media ?? []).length} media` };
    return {};
}
