// {{NAME}}: the action {{ACTION_ID}}.
//
// BashCut calls `handle` with method "plugin.action" when someone runs the action (menu, context menu, shortcut,
// `bashcut plugins run`). The result only *proposes* operations in the `timeline apply` format; BashCut validates
// them and applies one undoable edit. https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#actions
import { randomUUID } from "node:crypto";
import { PluginError } from "./bashcut-plugin.mjs";

export async function handle(method, params, host) {
    if (method !== "plugin.action") throw new PluginError("unknown_method", `{{PLAIN_NAME}} does not handle ${method}`);
    if (params.action === "{{ACTION_ID}}") return addMarker(params);
    throw new PluginError("unknown_action", `Unknown action ${params.action}`);
}

function addMarker(params) {
    const { context } = params;
    const label = params.params?.label || "Marker";
    const frame = context.playhead;
    return {
        label: "Add marker",
        baseRev: context.project.rev,
        operations: [{ op: "upsertSection", id: randomUUID(), label, atFrame: frame }],
        ui: { reveal: frame },
        message: `Added ${label} at frame ${frame}`,
    };
}
