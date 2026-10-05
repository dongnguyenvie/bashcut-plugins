// The BashCut plugin protocol for {{NAME}} (Node.js built-ins only). You rarely need to change this file.
//
// BashCut runs the entrypoint as `provider rpc` (one JSON request on stdin, one JSON response on stdout) or, with
// "transport": "session" in plugin.json, as `provider session` (newline-delimited JSON until it says shutdown).
// Handlers get a `host` to report progress, stream chat events and call BashCut commands. Diagnostics go to
// stderr: stdout carries only protocol lines.

/** A failure with a stable code BashCut can show, such as new PluginError("model_missing", "Install the model"). */
export class PluginError extends Error {
    constructor(code, message) {
        super(message);
        this.code = code;
    }
}

class Cancelled extends Error {}

function send(message) {
    process.stdout.write(JSON.stringify(message) + "\n");
}

/** Lines from stdin, one at a time; null at the end. */
class LineReader {
    constructor() {
        this.lines = [];
        this.waiting = null;
        this.ended = false;
        let buffer = "";
        process.stdin.setEncoding("utf8");
        process.stdin.on("data", (chunk) => {
            buffer += chunk;
            let index;
            while ((index = buffer.indexOf("\n")) >= 0) {
                const line = buffer.slice(0, index).trim();
                buffer = buffer.slice(index + 1);
                if (line) this.push(line);
            }
        });
        process.stdin.on("end", () => {
            if (buffer.trim()) this.push(buffer.trim());
            this.ended = true;
            this.push(null);
        });
    }

    push(line) {
        if (this.waiting) {
            const resolve = this.waiting;
            this.waiting = null;
            resolve(line);
        } else if (line !== null) {
            this.lines.push(line);
        }
    }

    next() {
        if (this.lines.length) return Promise.resolve(this.lines.shift());
        if (this.ended) return Promise.resolve(null);
        return new Promise((resolve) => (this.waiting = resolve));
    }

    async message() {
        const line = await this.next();
        return line === null ? null : JSON.parse(line);
    }
}

/** What a handler can do while its request runs. */
class Host {
    constructor(requestId, session) {
        this.requestId = requestId;
        this.session = session;
        this.calls = 0;
    }

    /** Shows progress on the job (session transport); keeps a long request alive. Send one at least every minute. */
    progress(fraction, message) {
        if (!this.session) {
            process.stderr.write(`progress ${fraction ?? ""} ${message ?? ""}\n`);
            return;
        }
        const line = { type: "progress", id: this.requestId };
        if (fraction !== undefined && fraction !== null) line.progress = Math.max(0, Math.min(1, fraction));
        if (message) line.message = message;
        send(line);
    }

    /** Hands a UI event to the caller, such as {kind: "text", delta: "Hi"} for a chat agent (API 4). */
    event(event) {
        if (!this.session) throw new PluginError("no_host_channel", "Events need the session transport");
        send({ type: "event", id: this.requestId, event });
    }

    /** Runs a BashCut command, such as await host.call("timeline.get"), and returns its result (API 4). */
    async call(method, params = {}) {
        if (!this.session) throw new PluginError("no_host_channel", "Calling BashCut needs the session transport");
        const callId = `${this.requestId}-c${++this.calls}`;
        send({ type: "call", id: this.requestId, callId, method, params });
        const reply = await this.session.waitForCall(callId, this.requestId);
        if (reply.error) {
            throw new PluginError(String(reply.error.code ?? "call_failed"), reply.error.message ?? "BashCut refused the call");
        }
        return reply.result;
    }
}

async function respond(request, handler, session) {
    const id = request.id;
    try {
        const result = await handler(request.method, request.params ?? {}, new Host(id, session));
        return { id, result: result ?? {} };
    } catch (error) {
        if (error instanceof Cancelled) return { id, error: { code: "cancelled", message: "Cancelled" } };
        const code = error instanceof PluginError ? error.code : "failed";
        return { id, error: { code, message: error?.message || String(error) } };
    }
}

/** The session transport, one request at a time. Messages that arrive while a handler waits for a call result are
 * kept and handled next, in order. */
class Session {
    constructor(handler, reader) {
        this.handler = handler;
        this.reader = reader;
        this.backlog = [];
    }

    async waitForCall(callId, requestId) {
        for (;;) {
            const message = await this.reader.message();
            if (message === null) throw new PluginError("host_closed", "BashCut closed the session");
            if (message.type === "callResult" && message.callId === callId) return message;
            if (message.type === "callResult") continue; // the answer to a call that was given up on
            if (message.type === "cancel" && message.id === requestId) throw new Cancelled();
            this.backlog.push(message);
        }
    }

    async run() {
        for (;;) {
            const message = this.backlog.length ? this.backlog.shift() : await this.reader.message();
            if (message === null || message.type === "shutdown") return;
            if (message.type === "hello") send({ type: "hello", apiVersion: message.apiVersion ?? 2 });
            else if (message.type === "cancel" || message.type === "callResult") continue;
            else send(await respond(message, this.handler, this));
        }
    }
}

/** Entry point: `provider rpc` or `provider session`. */
export async function run(handler) {
    const reader = new LineReader();
    if (process.argv[2] === "session") {
        await new Session(handler, reader).run();
    } else {
        const request = await reader.message();
        if (!request) throw new Error("expected one JSON request on stdin");
        send(await respond(request, handler, null));
    }
    // Stop reading and let Node exit once stdout is flushed (process.exit could cut a pipe write short on macOS).
    process.stdin.destroy();
}
