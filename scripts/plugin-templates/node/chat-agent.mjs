// {{NAME}}: a chat agent (agent.chat, provider {{PROVIDER_ID}}) that gets a tab in BashCut's agent dock.
//
// This placeholder agent reads the timeline with a BashCut command and echoes the message. Replace `turn` with a
// real model loop: send the model params.instructions, params.context and params.tools, stream its text with
// host.event, and run each tool call with await host.call(tool.method, args).
// https://github.com/dongnguyenvie/BashCut/blob/main/docs/specs/11-chat-agents.md
import { PluginError } from "./bashcut-plugin.mjs";

export async function handle(method, params, host) {
    if (method !== "agent.chat") throw new PluginError("unknown_method", `{{PLAIN_NAME}} does not handle ${method}`);
    const options = params.options ?? {};
    switch (params.op) {
        case "turn":
            return turn(params, host);
        case "status":
            return { ready: true, provider: "{{PLAIN_NAME}}", model: "echo", detail: "Echoes your message and counts the timeline's layers." };
        case "reset":
            return {};
        case "commands":
            return { commands: [{ name: "hello", summary: "Say hello" }] };
        case "command":
            if (params.name === "hello") return { text: `${options.greeting || "Hello"} from {{PLAIN_NAME}}` };
            throw new PluginError("unknown_command", `Unknown command /${params.name}`);
        default:
            throw new PluginError("unknown_op", `Unknown op ${params.op}`);
    }
}

async function turn(params, host) {
    host.event({ kind: "tool", callId: "t1", name: "bashcut_timeline_get", summary: "Reading the timeline" });
    let timeline;
    try {
        timeline = await host.call("timeline.get");
    } catch (error) {
        if (!(error instanceof PluginError)) throw error;
        host.event({ kind: "toolEnd", callId: "t1", ok: false, summary: error.message });
        return { stopReason: "error", error: error.message };
    }
    const layers = Array.isArray(timeline?.tracks) ? timeline.tracks.length : 0;
    host.event({ kind: "toolEnd", callId: "t1", ok: true, summary: `${layers} layers` });
    const reply = `You said: ${params.text ?? ""}\nThe timeline has ${layers} layers.`;
    host.event({ kind: "text", delta: reply });
    host.event({ kind: "message", role: "assistant", text: reply });
    return { stopReason: "end" };
}
