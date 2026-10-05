// {{NAME}}: options of every kind, read by the action {{ACTION_ID}}.
//
// BashCut draws the options in Settings › Plugins and sends their current values as params.options with every
// request. The secret (apiKey) comes from the Keychain: use it, never print or return it.
// https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#options
import { PluginError } from "./bashcut-plugin.mjs";

export async function handle(method, params, host) {
    if (method !== "plugin.action") throw new PluginError("unknown_method", `{{PLAIN_NAME}} does not handle ${method}`);
    if (params.action !== "{{ACTION_ID}}") throw new PluginError("unknown_action", `Unknown action ${params.action}`);
    const options = params.options ?? {};
    let greeting = options.greeting || "Hello";
    if (options.shout) greeting = greeting.toUpperCase();
    const words = Array(Number(options.repeat || 1)).fill(greeting).join(" ");
    const summary = { greeting: words, style: options.style ?? "short", apiKeySet: Boolean(options.apiKey) };
    const detail = summary.style === "long" ? ` (style long, API key ${summary.apiKeySet ? "set" : "not set"})` : "";
    return { message: words + detail, data: summary };
}
