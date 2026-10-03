// Director: BashCut's in-app editing agent (plugin `bashcut.director`, capability `agent.chat`, plugin API 4).
// BashCut starts `bin/provider session` and talks NDJSON over stdin/stdout; see README.md for the protocol.
import { createInterface } from "node:readline";
import { flushed, guardStdout, log, send } from "./protocol.ts";
import { settleCall } from "./tools.ts";
import { CommandError, list as listCommands, run as runCommand } from "./commands.ts";
import { busy, cancel, cancelAll, hold, reset, status, turn } from "./turn.ts";

const API_VERSION = 4;

guardStdout();

const inFlight = new Set<Promise<unknown>>();
let closing = false;

function track(work: Promise<unknown>) {
    inFlight.add(work);
    work.finally(() => inFlight.delete(work));
}

async function exit(code: number): Promise<never> {
    closing = true;
    await cancelAll();
    await Promise.allSettled([...inFlight]);
    await flushed();
    process.exit(code);
}

function fail(id: string, code: string, message: string) {
    return send({ id, error: { code, message } });
}

async function handleRequest(message: Record<string, any>): Promise<void> {
    const id = typeof message.id === "string" ? message.id : String(message.id ?? "");
    try {
        if (message.method !== "agent.chat") return void (await fail(id, "unknown_method", `Unknown method ${message.method}`));
        const params = (message.params ?? {}) as Record<string, any>;
        switch (params.op) {
            case "turn": {
                if (typeof params.conversation !== "string" || !params.conversation) {
                    return void (await fail(id, "invalid_params", "turn needs a conversation id"));
                }
                if (typeof params.text !== "string") return void (await fail(id, "invalid_params", "turn needs text"));
                const result = await turn(id, params);
                return void (await send({ id, result }));
            }
            case "reset":
                if (typeof params.conversation !== "string" || !params.conversation) {
                    return void (await fail(id, "invalid_params", "reset needs a conversation id"));
                }
                return void (await send({ id, result: await reset(params.conversation) }));
            case "status":
                return void (await send({ id, result: status(params.options, params.conversation) }));
            case "commands":
                return void (await send({ id, result: listCommands(params.options) }));
            case "command": {
                if (typeof params.name !== "string" || !params.name) return void (await fail(id, "invalid_params", "command needs a name"));
                try {
                    return void (await send({ id, result: await runCommand(id, params, { busy, hold }) }));
                } catch (error) {
                    if (error instanceof CommandError) return void (await fail(id, error.code, error.message));
                    throw error;
                }
            }
            default:
                return void (await fail(id, "invalid_params", `Unknown agent.chat op ${params.op}`));
        }
    } catch (error) {
        log("request failed:", error instanceof Error ? error.stack ?? error.message : String(error));
        await fail(id, "failed", error instanceof Error ? error.message : String(error));
    }
}

function handleLine(line: string) {
    if (!line.trim()) return;
    let message: Record<string, any>;
    try {
        message = JSON.parse(line);
    } catch {
        log("ignored a line that is not JSON");
        return;
    }
    switch (message.type) {
        case "hello":
            void send({ type: "hello", apiVersion: API_VERSION });
            break;
        case "request":
            if (!closing) track(handleRequest(message));
            break;
        case "callResult":
            settleCall(message);
            break;
        case "cancel":
            if (typeof message.id === "string") cancel(message.id);
            break;
        case "shutdown":
            void exit(0);
            break;
        default:
            log("ignored message type", String(message.type));
    }
}

process.on("unhandledRejection", (error) => log("unhandled rejection:", error instanceof Error ? error.message : String(error)));
process.on("SIGTERM", () => void exit(0));

const input = createInterface({ input: process.stdin, crlfDelay: Infinity });
input.on("line", handleLine);
// The app closed our stdin: stop running turns (their calls can no longer be answered), finish replies, exit.
input.on("close", () => void exit(0));
