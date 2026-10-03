// TEST-ONLY hook. When BASHCUT_DIRECTOR_FAUX names a JSON script, every request uses pi-ai's faux provider, which
// answers from the script instead of a network model. BashCut never sets this variable (plugins get a filtered
// environment), so it cannot be turned on in the app. Script format:
//
//   {
//     "model": {"id": "faux-director", "input": ["text", "image"], "contextWindow": 200000, "reasoning": false},
//     "tokensPerSecond": 0,                       // optional pacing of streamed chunks
//     "responses": [                              // consumed in order, one per model call, across the process
//       {"thinking": "…", "text": "…", "toolCalls": [{"name": "bashcut_timeline_get", "arguments": {}}]},
//       {"delayMs": 5000, "text": "slow"},        // waits first (cancel aborts the wait)
//       {"reportContext": true},                  // replies with a JSON summary of what the model was sent
//       {"stopReason": "error", "errorMessage": "Overloaded"}
//     ]
//   }
import {
    fauxAssistantMessage,
    fauxProvider,
    fauxText,
    fauxThinking,
    fauxToolCall,
    getCurrentSystemPrompt,
    getCurrentTools,
    type FauxContentBlock,
    type FauxProviderHandle,
    type FauxResponseStep,
} from "@earendil-works/pi-ai";
import { readFileSync } from "node:fs";

export const FAUX_PROVIDER = "faux";

interface ScriptStep {
    text?: string;
    thinking?: string;
    toolCalls?: { name: string; arguments?: Record<string, any>; id?: string }[];
    stopReason?: "stop" | "length" | "toolUse" | "error" | "aborted";
    errorMessage?: string;
    delayMs?: number;
    reportContext?: boolean;
}

interface Script {
    model?: { id?: string; input?: ("text" | "image")[]; contextWindow?: number; maxTokens?: number; reasoning?: boolean };
    tokensPerSecond?: number;
    responses?: ScriptStep[];
}

let handle: FauxProviderHandle | null | undefined;

export function fauxFromEnvironment(): FauxProviderHandle | null {
    if (handle !== undefined) return handle;
    const path = process.env.BASHCUT_DIRECTOR_FAUX;
    if (!path) return (handle = null);
    const script = JSON.parse(readFileSync(path, "utf8")) as Script;
    handle = fauxProvider({
        provider: FAUX_PROVIDER,
        models: [
            {
                id: script.model?.id ?? "faux-director",
                input: script.model?.input ?? ["text", "image"],
                contextWindow: script.model?.contextWindow ?? 200_000,
                maxTokens: script.model?.maxTokens ?? 8_192,
                reasoning: script.model?.reasoning ?? false,
            },
        ],
        ...(script.tokensPerSecond ? { tokensPerSecond: script.tokensPerSecond } : {}),
    });
    handle.setResponses((script.responses ?? []).map(toStep));
    return handle;
}

function toStep(step: ScriptStep): FauxResponseStep {
    return async (context, options) => {
        if (step.delayMs) {
            const aborted = await sleep(step.delayMs, options?.signal);
            if (aborted) return fauxAssistantMessage([], { stopReason: "aborted", errorMessage: "Request was aborted" });
        }
        const blocks: FauxContentBlock[] = [];
        if (step.thinking) blocks.push(fauxThinking(step.thinking));
        if (step.reportContext) blocks.push(fauxText(JSON.stringify(report(context.messages))));
        if (step.text) blocks.push(fauxText(step.text));
        for (const call of step.toolCalls ?? []) {
            blocks.push(fauxToolCall(call.name, (call.arguments ?? {}) as any, call.id ? { id: call.id } : undefined));
        }
        const stopReason = step.stopReason ?? (step.toolCalls?.length ? "toolUse" : "stop");
        return fauxAssistantMessage(blocks, {
            stopReason,
            ...(step.errorMessage ? { errorMessage: step.errorMessage } : {}),
        });
    };
}

function report(messages: any[]) {
    const roles: Record<string, number> = {};
    let images = 0;
    let lastUser = "";
    const toolResults: string[] = [];
    const userTexts: string[] = [];
    for (const message of messages) {
        roles[message.role] = (roles[message.role] ?? 0) + 1;
        const content = Array.isArray(message.content) ? message.content : [];
        images += content.filter((block: any) => block.type === "image").length;
        if (message.role === "user") {
            lastUser =
                typeof message.content === "string"
                    ? message.content
                    : content.filter((b: any) => b.type === "text").at(-1)?.text ?? "";
            userTexts.push(typeof message.content === "string" ? message.content :
                content.filter((b: any) => b.type === "text").map((b: any) => b.text).join("\n"));
        }
        if (message.role === "toolResult") {
            toolResults.push(content.filter((b: any) => b.type === "text").map((b: any) => b.text).join("\n"));
        }
    }
    return {
        roles,
        images,
        lastUser,
        userTexts,
        toolResults,
        systemPrompt: getCurrentSystemPrompt(messages),
        tools: getCurrentTools(messages).map((tool) => tool.name),
    };
}

function sleep(ms: number, signal?: AbortSignal): Promise<boolean> {
    return new Promise((resolve) => {
        if (signal?.aborted) return resolve(true);
        const timer = setTimeout(() => resolve(false), ms);
        signal?.addEventListener("abort", () => {
            clearTimeout(timer);
            resolve(true);
        });
    });
}
