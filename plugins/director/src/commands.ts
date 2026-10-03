// agent.chat ops `commands` and `command` (spec 11 §3.3–3.4): Director's own slash commands, /compact, /model,
// /thinking and /session. A command answers with a notice `text` and, for /model and /thinking, an `options` patch
// that the app stores like a Settings change. Secret options (the API key) are never part of a patch.
import type { AgentMessage } from "@earendil-works/pi-agent-core";
import type { AssistantMessage } from "@earendil-works/pi-ai";
import * as store from "./conversation.ts";
import { FAUX_PROVIDER, fauxFromEnvironment } from "./faux.ts";
import { API_KEY_MISSING, COMPATIBLE, DEFAULT_MODELS, models, PROVIDER_NAMES, resolve, thinkingLevel, type Options } from "./models.ts";
import { log, truncate } from "./protocol.ts";

export interface CommandInfo {
    name: string;
    args?: string;
    summary: string;
    choices?: string[];
}

export type CommandResult = { text?: string; options?: Record<string, string> };

/** A protocol error for the request (`{"id","error":{code,message}}`), as opposed to a notice for the user. */
export class CommandError extends Error {
    constructor(
        readonly code: string,
        message: string,
    ) {
        super(message);
    }
}

const THINKING_LEVELS = ["off", "low", "medium", "high"];

/** The provider the options select (the faux provider when the test hook is on). */
function providerOf(options: Options | undefined): string {
    if (fauxFromEnvironment()) return FAUX_PROVIDER;
    return typeof options?.provider === "string" && options.provider ? options.provider : "anthropic";
}

/** Model IDs of the provider in pi-ai's catalog, its default first. Empty for `compatible` and unknown providers. */
export function catalogIds(provider: string): string[] {
    if (provider === COMPATIBLE) return [];
    if (provider !== FAUX_PROVIDER && !(provider in DEFAULT_MODELS)) return [];
    const ids = models().getModels(provider).map((m) => m.id);
    const preferred = DEFAULT_MODELS[provider];
    return preferred && ids.includes(preferred) ? [preferred, ...ids.filter((id) => id !== preferred)] : ids;
}

export function list(options: Options | undefined): { commands: CommandInfo[] } {
    return {
        commands: [
            { name: "compact", args: "[instructions]", summary: "Summarize older messages to free context" },
            { name: "model", args: "[model id]", summary: "Show or change the model", choices: catalogIds(providerOf(options)) },
            {
                name: "thinking",
                args: "[off|low|medium|high]",
                summary: "Show or change how much the model reasons",
                choices: THINKING_LEVELS.slice(),
            },
            { name: "session", summary: "Model, messages and context use of this conversation" },
        ],
    };
}

export interface CommandHooks {
    /** Whether a turn (or a compaction) is running in the conversation. */
    busy: (conversation: string) => boolean;
    /** Marks the conversation busy while `work` runs, and lets `cancel` abort it. */
    hold: <T>(conversation: string, requestId: string, work: (signal: AbortSignal) => Promise<T>) => Promise<T>;
}

export async function run(requestId: string, params: Record<string, any>, hooks: CommandHooks): Promise<CommandResult> {
    const name = typeof params.name === "string" ? params.name.replace(/^\//, "").trim() : "";
    const args = typeof params.args === "string" ? params.args.trim() : "";
    const options = (params.options ?? {}) as Options;
    const conversation = typeof params.conversation === "string" ? params.conversation : "";
    switch (name) {
        case "model":
            return modelCommand(args, options);
        case "thinking":
            return thinkingCommand(args, options);
        case "session":
            if (!conversation) throw new CommandError("invalid_params", "session needs a conversation id");
            return { text: sessionText(conversation, options) };
        case "compact":
            if (!conversation) throw new CommandError("invalid_params", "compact needs a conversation id");
            if (hooks.busy(conversation)) {
                throw new CommandError("busy", "Director is answering in this conversation; stop it or wait, then compact.");
            }
            return hooks.hold(conversation, requestId, (signal) => compactCommand(conversation, args, options, signal));
        default:
            throw new CommandError("unknown_command", `Director has no command "${name}"`);
    }
}

// MARK: - /model and /thinking

function modelCommand(args: string, options: Options): CommandResult {
    const provider = providerOf(options);
    const providerName = PROVIDER_NAMES[provider] ?? provider;
    const ids = catalogIds(provider);
    if (!args) {
        const resolved = resolve(options);
        const current = resolved.modelId || "(not set)";
        const lines = [`Model: ${providerName} · ${current}`];
        if (resolved.problem) lines.push(resolved.problem);
        const others = ids.filter((id) => id !== resolved.modelId);
        if (others.length > 0) {
            const shown = others.slice(0, 10).join(", ");
            lines.push(`Also available: ${shown}${others.length > 10 ? `, and ${others.length - 10} more` : ""}`);
        } else if (provider === COMPATIBLE) {
            lines.push("Any model ID your endpoint serves can be set with /model <id>.");
        }
        return { text: lines.join("\n") };
    }
    if (/\s/.test(args) || args.length > 200) return { text: `"${truncate(args, 60)}" is not a model ID: use one word, such as ${ids[0] ?? "gpt-5.5"}.` };
    if (provider === COMPATIBLE) return { options: { model: args }, text: `Model set to ${args}` };
    if (args === "default" && DEFAULT_MODELS[provider]) {
        return { options: { model: "" }, text: `Model set to the default (${DEFAULT_MODELS[provider]})` };
    }
    if (!ids.includes(args)) {
        const close = ids.filter((id) => id.includes(args) || args.includes(id)).slice(0, 5);
        const hint = close.length > 0 ? `Did you mean ${close.join(", ")}?` : `Known models: ${ids.slice(0, 10).join(", ")}${ids.length > 10 ? ", …" : ""}`;
        return { text: `${providerName} has no model "${args}" in Director's catalog. ${hint}` };
    }
    return { options: { model: args }, text: `Model set to ${args}` };
}

function thinkingCommand(args: string, options: Options): CommandResult {
    const level = args.toLowerCase();
    if (!level) {
        const current = THINKING_LEVELS.includes(options.thinking as string) ? (options.thinking as string) : "off";
        const resolved = resolve(options);
        const note = resolved.model && !resolved.model.reasoning && current !== "off" ? " (this model does not reason, so it is ignored)" : "";
        return { text: `Thinking: ${current}${note}` };
    }
    if (!THINKING_LEVELS.includes(level)) return { text: `Thinking can be ${THINKING_LEVELS.join(", ")}; "${truncate(args, 40)}" is not one of them.` };
    return { options: { thinking: level }, text: `Thinking: ${level}` };
}

// MARK: - /session and status

function tokensLabel(tokens: number): string {
    if (tokens < 1_000) return String(tokens);
    if (tokens < 10_000) return `${(tokens / 1_000).toFixed(1).replace(/\.0$/, "")}k`;
    return `${Math.round(tokens / 1_000)}k`;
}

/** Messages shown in the transcript: everything but the system prompt messages. */
function chatMessages(messages: AgentMessage[]): AgentMessage[] {
    return messages.filter((m) => m.role !== "system");
}

export function contextUse(conversation: string): number {
    return store.estimateTokens(store.load(conversation).messages);
}

function sessionText(conversation: string, options: Options): string {
    const resolved = resolve(options);
    const providerName = PROVIDER_NAMES[resolved.provider] ?? resolved.provider;
    const messages = store.load(conversation).messages;
    const tokens = store.estimateTokens(messages);
    const window = resolved.model?.contextWindow ?? 0;
    const thinking = resolved.model ? thinkingLevel(options.thinking, resolved.model) : "off";
    const lines = [
        `Model: ${providerName} · ${resolved.modelId || "(not set)"}`,
        `Thinking: ${thinking}${resolved.model && !resolved.model.reasoning ? " (not supported by this model)" : ""}`,
        `Messages: ${chatMessages(messages).length}`,
        window > 0
            ? `Context: ~${tokensLabel(tokens)} tokens (${Math.round((tokens / window) * 100)}% of ${tokensLabel(window)})`
            : `Context: ~${tokensLabel(tokens)} tokens`,
        `Conversation: ${conversation}`,
    ];
    if (resolved.problem) lines.push(resolved.problem);
    return lines.join("\n");
}

// MARK: - /compact
//
// Like pi's compaction: the older messages are serialized to plain text (so the model does not continue the
// conversation) and summarized in a structured checkpoint format; the summary replaces them as one user message.
// The newest messages stay verbatim: at least the last user message and everything after it, and at least
// KEEP_MESSAGES messages, cut only before a user or assistant message so a tool call never loses its result.

const KEEP_MESSAGES = 6;
const MIN_SUMMARIZED = 2;
const TOOL_RESULT_CHARS = 2_000;
export const SUMMARY_PREFIX = "Summary of the earlier conversation:\n";

const SUMMARY_SYSTEM_PROMPT =
    "You are a context summarization assistant. Your task is to read a conversation between a user and an AI " +
    "video-editing assistant (Director, inside the BashCut video editor), then produce a structured summary " +
    "following the exact format specified.\n\nDo NOT continue the conversation. Do NOT respond to any questions " +
    "in the conversation. ONLY output the structured summary.";

const SUMMARY_PROMPT = `The messages above are a conversation to summarize. Create a structured context checkpoint summary that another LLM will use to continue the work.

Use this EXACT format:

## Goal
[What is the user trying to accomplish? Can be multiple items if the session covers different tasks.]

## Constraints & Preferences
- [Any constraints, preferences, or requirements mentioned by user]
- [Or "(none)" if none were mentioned]

## Progress
### Done
- [x] [Completed edits/changes]

### In Progress
- [ ] [Current work]

### Blocked
- [Issues preventing progress, if any]

## Key Decisions
- **[Decision]**: [Brief rationale]

## Next Steps
1. [Ordered list of what should happen next]

## Critical Context
- [Any data needed to continue: clip and track IDs, timecodes, frame numbers, file paths, exact error messages]
- [Or "(none)" if not applicable]

Keep each section concise. If <previous-summary> is given, merge it: keep its information and add the new messages.`;

function textOf(content: any): string {
    if (typeof content === "string") return content;
    if (!Array.isArray(content)) return "";
    return content
        .map((b: any) => (b.type === "text" ? b.text : b.type === "image" ? "[image]" : ""))
        .filter(Boolean)
        .join("\n");
}

/** pi's serializeConversation, for Director's messages. */
export function serialize(messages: AgentMessage[]): string {
    const parts: string[] = [];
    for (const message of messages as any[]) {
        if (message.role === "user") {
            const text = textOf(message.content);
            if (text) parts.push(`[User]: ${text}`);
        } else if (message.role === "assistant") {
            const blocks = Array.isArray(message.content) ? message.content : [];
            const thinking = blocks.filter((b: any) => b.type === "thinking").map((b: any) => b.thinking).join("\n");
            const text = blocks.filter((b: any) => b.type === "text").map((b: any) => b.text).join("\n");
            const calls = blocks
                .filter((b: any) => b.type === "toolCall")
                .map((b: any) => `${b.name}(${JSON.stringify(b.arguments ?? {})})`)
                .join("; ");
            if (thinking) parts.push(`[Assistant thinking]: ${thinking}`);
            if (text) parts.push(`[Assistant]: ${text}`);
            if (calls) parts.push(`[Assistant tool calls]: ${calls}`);
        } else if (message.role === "toolResult") {
            let text = textOf(message.content);
            if (text.length > TOOL_RESULT_CHARS) {
                text = `${text.slice(0, TOOL_RESULT_CHARS)}\n[… ${text.length - TOOL_RESULT_CHARS} more characters truncated]`;
            }
            parts.push(`[Tool result${message.isError ? " (error)" : ""}]: ${text}`);
        }
    }
    return parts.join("\n\n");
}

function isSummary(message: any): boolean {
    return message?.role === "user" && typeof message.content === "string" && message.content.startsWith(SUMMARY_PREFIX);
}

/**
 * Where the kept tail starts (an index into `messages`), or -1 when there is too little to summarize. The tail
 * includes the last user message and at least KEEP_MESSAGES conversation messages, and starts at a user or
 * assistant message.
 */
export function cutPoint(messages: AgentMessage[]): number {
    const positions = messages.map((m, i) => ({ m, i })).filter(({ m }) => m.role !== "system");
    if (positions.length === 0) return -1;
    let lastUser = -1;
    for (const { m, i } of positions) if (m.role === "user") lastUser = i;
    const byCount = positions[Math.max(0, positions.length - KEEP_MESSAGES)].i;
    let cut = lastUser === -1 ? byCount : Math.min(lastUser, byCount);
    while (cut > 0 && !(messages[cut].role === "user" || messages[cut].role === "assistant")) cut -= 1;
    const summarized = positions.filter(({ i }) => i < cut);
    // A lone previous summary (or one message) is not worth another model call.
    if (summarized.length < MIN_SUMMARIZED) return -1;
    return cut;
}

async function compactCommand(conversationId: string, instructions: string, options: Options, signal: AbortSignal): Promise<CommandResult> {
    const conversation = store.load(conversationId);
    const messages = conversation.messages;
    const cut = cutPoint(messages);
    if (cut === -1) return { text: "Nothing to compact yet" };

    const resolved = resolve(options);
    if (resolved.problem || !resolved.model) return { text: `Cannot compact: ${resolved.problem ?? "unknown model"}` };
    if (!resolved.apiKey) return { text: `Cannot compact: ${API_KEY_MISSING}` };
    const model = resolved.model;

    const older = messages.slice(0, cut);
    const systems = older.filter((m) => m.role === "system");
    const toSummarize = older.filter((m) => m.role !== "system");
    const previous = toSummarize.length > 0 && isSummary(toSummarize[0]) ? (toSummarize[0] as any).content.slice(SUMMARY_PREFIX.length) : "";
    const body = previous ? toSummarize.slice(1) : toSummarize;

    let prompt = `<conversation>\n${serialize(body)}\n</conversation>\n\n`;
    if (previous) prompt += `<previous-summary>\n${previous}\n</previous-summary>\n\n`;
    prompt += SUMMARY_PROMPT;
    if (instructions) prompt += `\n\nAdditional focus from the user: ${instructions}`;

    let response: AssistantMessage;
    try {
        response = await models().completeSimple(
            model,
            { systemPrompt: SUMMARY_SYSTEM_PROMPT, messages: [{ role: "user", content: [{ type: "text", text: prompt }], timestamp: Date.now() }] },
            {
                apiKey: resolved.apiKey,
                maxTokens: Math.min(model.maxTokens > 0 ? model.maxTokens : 8_192, 13_000),
                signal,
                cacheRetention: "none",
                sessionId: conversationId,
            },
        );
    } catch (error) {
        log("compaction failed:", error instanceof Error ? error.message : String(error));
        return { text: `Compaction failed: ${error instanceof Error ? error.message : String(error)}` };
    }
    if (signal.aborted || response.stopReason === "aborted") return { text: "Compaction stopped; the conversation is unchanged." };
    if (response.stopReason === "error") return { text: `Compaction failed: ${response.errorMessage || "the model request failed"}` };
    if (response.stopReason === "length") return { text: "Compaction failed: the summary hit the model's output limit. The conversation is unchanged." };
    const summary = response.content.filter((b) => b.type === "text").map((b: any) => b.text).join("").trim();
    if (!summary) return { text: "Compaction failed: the model returned an empty summary. The conversation is unchanged." };

    // A turn may have started meanwhile only if it bypassed the hold; the transcript we summarized is still ours.
    const kept = messages.slice(cut);
    const summaryMessage = { role: "user", content: SUMMARY_PREFIX + summary, timestamp: Date.now() } as AgentMessage;
    const next = [...systems, summaryMessage, ...kept];
    const before = store.estimateTokens(messages);
    const after = store.estimateTokens(next);
    conversation.messages = next;
    store.save(conversation);
    return { text: `Compacted ${toSummarize.length} messages (~${tokensLabel(before)} → ~${tokensLabel(after)} tokens)` };
}
