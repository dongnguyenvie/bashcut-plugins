// Conversations: one JSON file per conversation in BASHCUT_PLUGIN_DATA/conversations, written after every model
// turn so an idle shutdown or a crash loses at most the turn in progress. Also the context compaction.
import type { AgentMessage } from "@earendil-works/pi-agent-core";
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, renameSync, rmSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

export interface Conversation {
    id: string;
    /** The system prompt sections as last sent, so the next turn only patches what changed. */
    sections: Record<string, string>;
    /** pi-agent-core transcript: system, user, assistant and toolResult messages. */
    messages: AgentMessage[];
}

const memory = new Map<string, Conversation>();

export function dataFolder(): string {
    return (
        process.env.BASHCUT_PLUGIN_DATA ||
        join(homedir(), "Library", "Application Support", "BashCut", "PluginData", "bashcut.director")
    );
}

/** A file name for any conversation ID: safe characters kept, anything else replaced and disambiguated by a hash. */
export function fileName(id: string): string {
    const safe = id.replace(/[^A-Za-z0-9_-]/g, "_").slice(0, 80);
    if (safe === id && safe.length > 0) return `${safe}.json`;
    const hash = createHash("sha256").update(id).digest("hex").slice(0, 16);
    return `${safe}-${hash}.json`;
}

function pathFor(id: string): string {
    return join(dataFolder(), "conversations", fileName(id));
}

export function load(id: string): Conversation {
    const cached = memory.get(id);
    if (cached) return cached;
    let conversation: Conversation = { id, sections: {}, messages: [] };
    try {
        const stored = JSON.parse(readFileSync(pathFor(id), "utf8"));
        if (stored && stored.id === id && Array.isArray(stored.messages)) {
            // Older Cut AI versions promoted editor state into system sections. Remove every
            // such section before turns or /compact can send this history to a model again.
            const { context: _legacyContext, ...sections } = stored.sections ?? {};
            const messages = stored.messages.map((message: AgentMessage) => {
                if (message.role !== "system" || !message.sections) return message;
                const { context: _context, ...safeSections } = message.sections;
                return { ...message, sections: safeSections };
            });
            conversation = { id, sections, messages };
        }
    } catch {
        // Missing or unreadable: start fresh.
    }
    memory.set(id, conversation);
    return conversation;
}

export function save(conversation: Conversation): void {
    memory.set(conversation.id, conversation);
    const path = pathFor(conversation.id);
    mkdirSync(join(dataFolder(), "conversations"), { recursive: true, mode: 0o700 });
    const temporary = `${path}.${process.pid}.tmp`;
    const body = { version: 1, id: conversation.id, savedAt: new Date().toISOString(), sections: conversation.sections, messages: conversation.messages };
    writeFileSync(temporary, JSON.stringify(body), { mode: 0o600 });
    renameSync(temporary, path);
}

export function forget(id: string): void {
    memory.delete(id);
    rmSync(pathFor(id), { force: true });
}

// MARK: - Compaction
//
// Tokens are estimated at 4 characters each and about 1,500 per image. The budget is the model's context window
// (capped at 200k tokens, so a 1M-token model does not resend a huge history on every call) minus its output
// allowance. When the estimate passes 75% of the budget, the oldest tool results — and images in older messages —
// are replaced by a one-line stub until it is under 50%; the newest 8 messages are never touched. If that is not
// enough, the oldest exchanges (from one user message to the next) are dropped. System messages are always kept.
// The compacted transcript is what gets saved, so later calls start from it.

const CHARS_PER_TOKEN = 4;
const IMAGE_TOKENS = 1_500;
const KEEP_RECENT = 8;

export function estimateTokens(messages: AgentMessage[]): number {
    let chars = 0;
    let images = 0;
    for (const message of messages as any[]) {
        if (typeof message.content === "string") chars += message.content.length;
        else if (Array.isArray(message.content)) {
            for (const block of message.content) {
                if (block.type === "image") images += 1;
                else if (block.type === "text") chars += block.text.length;
                else if (block.type === "thinking") chars += (block.thinking ?? "").length;
                else if (block.type === "toolCall") chars += JSON.stringify(block.arguments ?? {}).length + 40;
            }
        }
        if (message.role === "system") {
            chars += JSON.stringify(message.sections ?? {}).length + JSON.stringify(message.toolsAdded ?? []).length;
        }
    }
    return Math.ceil(chars / CHARS_PER_TOKEN) + images * IMAGE_TOKENS;
}

export function budget(contextWindow: number, maxTokens: number): number {
    const window = Math.min(contextWindow || 128_000, 200_000);
    return Math.max(8_000, window - Math.min(maxTokens || 8_192, Math.floor(window / 4)));
}

/** Returns the compacted transcript and how many messages were shortened or dropped (0 = unchanged). */
export function compact(messages: AgentMessage[], limit: number): { messages: AgentMessage[]; changed: number } {
    if (estimateTokens(messages) <= limit * 0.75) return { messages, changed: 0 };
    const target = limit * 0.5;
    const result = messages.slice() as any[];
    let changed = 0;
    const protectedFrom = Math.max(0, result.length - KEEP_RECENT);
    for (let i = 0; i < protectedFrom && estimateTokens(result) > target; i++) {
        const message = result[i];
        if (message.role === "toolResult" && !message.compacted) {
            const text = (message.content ?? []).filter((b: any) => b.type === "text").map((b: any) => b.text).join(" ");
            const preview = text.replace(/\s+/g, " ").slice(0, 160);
            result[i] = {
                ...message,
                compacted: true,
                content: [{ type: "text", text: `[Older tool result removed to save context. It began: ${preview}]` }],
            };
            changed += 1;
        } else if (Array.isArray(message.content) && message.content.some((b: any) => b.type === "image")) {
            result[i] = {
                ...message,
                content: message.content.map((b: any) => (b.type === "image" ? { type: "text", text: "[older image removed]" } : b)),
            };
            changed += 1;
        }
    }
    // Still too big: drop whole exchanges from the oldest user message onward, keeping system messages.
    while (estimateTokens(result) > target) {
        const firstUser = result.findIndex((m) => m.role === "user");
        if (firstUser === -1) break;
        let next = result.findIndex((m, index) => index > firstUser && m.role === "user");
        if (next === -1 || next >= result.length - 1) break;
        const dropped = result.slice(firstUser, next).filter((m) => m.role !== "system");
        const kept = result.slice(firstUser, next).filter((m) => m.role === "system");
        result.splice(firstUser, next - firstUser, ...kept);
        changed += dropped.length;
    }
    return { messages: result, changed };
}
