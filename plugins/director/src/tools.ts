// The model's tools: one per BashCut catalog command the app offers (each runs in the app through a `call` line),
// plus read_skill for the agent kit. Director has no shell and no file writes.
import type { AgentTool, AgentToolResult } from "@earendil-works/pi-agent-core";
import { Type } from "@earendil-works/pi-ai";
import { readFile, realpath, stat } from "node:fs/promises";
import { join, sep } from "node:path";
import { send, oneLine, type JSONValue } from "./protocol.ts";

export interface ToolSpec {
    name: string;
    method: string;
    description?: string;
    inputSchema?: Record<string, unknown>;
}

export interface Kit {
    root: string;
    skills: { name: string; description?: string }[];
}

export const RESULT_LIMIT = 30_000;
const IMAGE_LIMIT = 8 * 1024 * 1024;
const SKILL_LIMIT = 256 * 1024;
const NAME = /^[A-Za-z0-9_-]{1,64}$/;

// MARK: - Host calls

interface Pending {
    resolve: (value: JSONValue) => void;
    reject: (error: Error) => void;
}

const pending = new Map<string, Pending>();
let nextCall = 0;

export class HostError extends Error {}

/** A `callResult` line from the app. */
export function settleCall(message: { callId?: unknown; result?: JSONValue; error?: { code?: unknown; message?: unknown } }) {
    const entry = typeof message.callId === "string" ? pending.get(message.callId) : undefined;
    if (!entry) return;
    pending.delete(message.callId as string);
    if (message.error) {
        const text = typeof message.error.message === "string" ? message.error.message : JSON.stringify(message.error);
        entry.reject(new HostError(text));
    } else {
        entry.resolve(message.result ?? null);
    }
}

export function newCallId(): string {
    nextCall += 1;
    return `c${nextCall}`;
}

/** Sends `call` inside request `requestId` and waits for its `callResult` (or the turn's cancellation). */
export function callHost(requestId: string, callId: string, method: string, params: unknown, signal?: AbortSignal): Promise<JSONValue> {
    return new Promise((resolve, reject) => {
        if (signal?.aborted) return reject(new Error("Cancelled"));
        const onAbort = () => {
            pending.delete(callId);
            reject(new Error("Cancelled"));
        };
        signal?.addEventListener("abort", onAbort, { once: true });
        pending.set(callId, {
            resolve: (value) => {
                signal?.removeEventListener("abort", onAbort);
                resolve(value);
            },
            reject: (error) => {
                signal?.removeEventListener("abort", onAbort);
                reject(error);
            },
        });
        void send({ type: "call", id: requestId, callId, method, params: params ?? {} });
    });
}

// MARK: - Tool definitions

export interface ToolContext {
    requestId: string;
    images: boolean;
    /** Host callId for each model tool call, assigned when the tool row starts. */
    callIdFor: (toolCallId: string) => string;
}

export function compactJSON(value: unknown): string {
    const text = JSON.stringify(value) ?? "null";
    if (text.length <= RESULT_LIMIT) return text;
    return (
        text.slice(0, RESULT_LIMIT) +
        `\n[Truncated: the result has ${text.length} characters and only the first ${RESULT_LIMIT} are shown. Ask for less, for example a narrower range or one item.]`
    );
}

export function hostTools(specs: unknown, context: ToolContext): { tools: AgentTool<any>[]; methods: Map<string, string> } {
    const tools: AgentTool<any>[] = [];
    const methods = new Map<string, string>();
    for (const spec of Array.isArray(specs) ? (specs as ToolSpec[]) : []) {
        if (!spec || typeof spec.name !== "string" || !NAME.test(spec.name) || typeof spec.method !== "string") continue;
        if (spec.name === "read_skill" || methods.has(spec.name)) continue;
        methods.set(spec.name, spec.method);
        const schema =
            spec.inputSchema && typeof spec.inputSchema === "object" ? spec.inputSchema : { type: "object", properties: {} };
        tools.push({
            name: spec.name,
            label: spec.method,
            description: spec.description || spec.method,
            parameters: Type.Unsafe(schema as any),
            executionMode: "sequential",
            execute: async (toolCallId, params, signal) => {
                const result = await callHost(context.requestId, context.callIdFor(toolCallId), spec.method, params, signal);
                return toolResult(spec.method, result, context.images);
            },
        });
    }
    return { tools, methods };
}

async function toolResult(method: string, result: JSONValue, images: boolean): Promise<AgentToolResult<any>> {
    const content: AgentToolResult<any>["content"] = [{ type: "text", text: compactJSON(result) }];
    // `ui frame` returns {path, frame, width, height}: show the model the picture itself when it can see.
    if (method === "ui.frame" && images && result && typeof result === "object" && !Array.isArray(result)) {
        const path = (result as Record<string, JSONValue>).path;
        if (typeof path === "string" && path.toLowerCase().endsWith(".png")) {
            try {
                const info = await stat(path);
                if (info.size <= IMAGE_LIMIT) {
                    content.push({ type: "image", data: (await readFile(path)).toString("base64"), mimeType: "image/png" });
                }
            } catch {
                // The text result still has the path.
            }
        }
    }
    return { content, details: undefined };
}

export function readSkillTool(kit: Kit | null | undefined): AgentTool<any> | null {
    if (!kit || typeof kit.root !== "string" || !kit.root) return null;
    return {
        name: "read_skill",
        label: "read_skill",
        description:
            "Read one of the agent kit's skills (its SKILL.md). Call it before following a skill listed in <skills>.",
        parameters: Type.Object({ name: Type.String({ description: "The skill's name, as listed in <skills>" }) }),
        executionMode: "parallel",
        execute: async (_id, params) => {
            const text = await readSkill(kit.root, (params as { name?: unknown })?.name);
            return { content: [{ type: "text", text }], details: undefined };
        },
    };
}

export async function readSkill(root: string, name: unknown): Promise<string> {
    if (typeof name !== "string" || !name || name.includes("/") || name.includes("\\") || name.includes("..") || name.includes("\0")) {
        throw new Error("Use a skill name from the list, without / or ..");
    }
    const skills = await realpath(join(root, "skills")).catch(() => {
        throw new Error("The agent kit has no skills folder");
    });
    const file = await realpath(join(skills, name, "SKILL.md")).catch(() => {
        throw new Error(`No skill named "${name}"`);
    });
    if (!file.startsWith(skills + sep)) throw new Error(`No skill named "${name}"`);
    const text = await readFile(file, "utf8");
    return text.length > SKILL_LIMIT ? text.slice(0, SKILL_LIMIT) + "\n[Truncated]" : text;
}

/** A short line for the tool row: the catalog method and its arguments. */
export function startSummary(method: string, args: unknown): string {
    const json = args && typeof args === "object" && Object.keys(args).length > 0 ? " " + JSON.stringify(args) : "";
    return oneLine(method + json, 160);
}

export const END_SUMMARY_LIMIT = 120;

/**
 * A short line for a finished tool row (at most 120 characters): the error message, or "ok" with what the result
 * says at a glance (its revision, how many items its lists have, its message). Never the raw result.
 */
export function endSummary(method: string, result: any, isError: boolean): string {
    const text = (result?.content ?? []).filter((b: any) => b.type === "text").map((b: any) => b.text).join(" ");
    if (isError) return oneLine(text || "Failed", END_SUMMARY_LIMIT);
    if (method === "read_skill") {
        const title = text.match(/^#\s+(.+)$/m)?.[1];
        return oneLine(`read ${text.split("\n").length} lines${title ? ` · ${title}` : ""}`, END_SUMMARY_LIMIT);
    }
    let value: unknown;
    try {
        value = JSON.parse(text);
    } catch {
        // Cut at RESULT_LIMIT, or not JSON: say how big it is.
        return text ? oneLine(`ok · ${text.length.toLocaleString("en-US")} characters`, END_SUMMARY_LIMIT) : "ok";
    }
    if (method === "ui.frame") {
        const frame = value && typeof value === "object" ? (value as Record<string, unknown>).frame : undefined;
        return typeof frame === "number" ? `frame image · frame ${frame}` : "frame image";
    }
    return oneLine(describe(value), END_SUMMARY_LIMIT);
}

function describe(value: unknown): string {
    if (value === null || value === undefined || value === true) return "ok";
    if (value === false) return "ok · false";
    if (typeof value === "string") return value ? `ok · ${value}` : "ok";
    if (typeof value === "number") return `ok · ${value}`;
    if (Array.isArray(value)) return `ok · ${value.length} ${value.length === 1 ? "item" : "items"}`;
    const object = value as Record<string, unknown>;
    const parts = ["ok"];
    for (const key of ["rev", "revision"]) {
        if (typeof object[key] === "number" || typeof object[key] === "string") {
            parts.push(`rev ${object[key]}`);
            break;
        }
    }
    for (const key of ["message", "summary", "status"]) {
        if (typeof object[key] === "string" && object[key]) {
            parts.push(oneLine(object[key] as string, 60));
            break;
        }
    }
    let lists = 0;
    for (const [key, item] of Object.entries(object)) {
        if (Array.isArray(item) && lists < 3) {
            parts.push(`${key}: ${item.length}`);
            lists += 1;
        }
    }
    if (parts.length === 1) {
        const keys = Object.keys(object);
        if (keys.length > 0) parts.push(keys.slice(0, 4).join(", ") + (keys.length > 4 ? ", …" : ""));
    }
    return parts.join(" · ");
}
