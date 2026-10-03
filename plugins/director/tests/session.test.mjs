// End-to-end tests of the built bundle (dist/director.mjs, made by build.sh) over the NDJSON session protocol, with
// pi-ai's faux provider scripting the model (BASHCUT_DIRECTOR_FAUX, test-only). No network.
import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const PLUGIN = join(dirname(fileURLToPath(import.meta.url)), "..");
const BUNDLE = join(PLUGIN, "dist", "director.mjs");
const TOOLS = [
    {
        name: "bashcut_timeline_get",
        method: "timeline.get",
        description: "Read the timeline",
        inputSchema: { type: "object", properties: { tracks: { type: "boolean" } }, additionalProperties: false },
    },
    {
        name: "bashcut_ui_frame",
        method: "ui.frame",
        description: "Render a frame",
        inputSchema: { type: "object", properties: { frame: { type: "integer", minimum: 0 } } },
    },
];
// A 1×1 PNG.
const PNG = Buffer.from(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
    "base64",
);

assert.ok(existsSync(BUNDLE), "dist/director.mjs is missing: run plugins/director/build.sh first");

function temp(prefix) {
    return mkdtempSync(join(tmpdir(), `director-${prefix}-`));
}

function script(responses, extra = {}) {
    const path = join(temp("script"), "faux.json");
    writeFileSync(path, JSON.stringify({ responses, ...extra }));
    return path;
}

function kit() {
    const root = temp("kit");
    mkdirSync(join(root, "skills", "cut-silences"), { recursive: true });
    writeFileSync(join(root, "skills", "cut-silences", "SKILL.md"), "# Cut silences\nFind pauses, then cut them.");
    writeFileSync(join(root, "secret.txt"), "outside the skills folder");
    return { root, skills: [{ name: "cut-silences", description: "Remove pauses from speech" }] };
}

/** A running plugin process: send lines, wait for lines. Every stdout line must be JSON. */
class Session {
    constructor({ data, faux, command = [process.execPath, BUNDLE, "session"], env = {} }) {
        this.messages = [];
        this.waiters = [];
        this.stderr = "";
        this.child = spawn(command[0], command.slice(1), {
            env: {
                HOME: process.env.HOME,
                PATH: "/usr/bin:/bin:/usr/sbin:/sbin",
                BASHCUT_PLUGIN_ID: "bashcut.director",
                BASHCUT_PLUGIN_DATA: data,
                ...(faux ? { BASHCUT_DIRECTOR_FAUX: faux } : {}),
                ...env,
            },
            stdio: ["pipe", "pipe", "pipe"],
        });
        this.exited = new Promise((resolve) => this.child.on("exit", (code) => resolve(code)));
        let buffer = "";
        this.child.stdout.on("data", (chunk) => {
            buffer += chunk;
            let index;
            while ((index = buffer.indexOf("\n")) >= 0) {
                const line = buffer.slice(0, index);
                buffer = buffer.slice(index + 1);
                const message = JSON.parse(line); // throws on any non-protocol output
                this.messages.push(message);
                this.waiters = this.waiters.filter((w) => !(w.match(message) && (w.resolve(message), true)));
            }
        });
        this.child.stderr.on("data", (chunk) => (this.stderr += chunk));
        this.write({ type: "hello", apiVersion: 4, host: "BashCut", pluginId: "bashcut.director" });
    }
    write(message) {
        this.child.stdin.write(JSON.stringify(message) + "\n");
    }
    next(match, timeout = 10_000) {
        const found = this.messages.find(match);
        if (found) return Promise.resolve(found);
        return new Promise((resolve, reject) => {
            const timer = setTimeout(
                () => reject(new Error(`timed out; got ${JSON.stringify(this.messages)}\nstderr: ${this.stderr}`)),
                timeout,
            );
            this.waiters.push({ match, resolve: (m) => (clearTimeout(timer), resolve(m)) });
        });
    }
    request(id, params) {
        this.write({ type: "request", id, apiVersion: 4, method: "agent.chat", provider: "bashcut.director.agent", params });
        return this.next((m) => m.id === id && !m.type && ("result" in m || "error" in m), 20_000);
    }
    events(id) {
        return this.messages.filter((m) => m.type === "event" && m.id === id).map((m) => m.event);
    }
    async close() {
        this.write({ type: "shutdown" });
        return this.exited;
    }
}

function turn(extra = {}) {
    return {
        op: "turn",
        conversation: "project-1",
        text: "Tighten the intro",
        context: "[BashCut context]\nproject: /tmp/demo.bashcut",
        instructions: "Use the BashCut tools. Keep edits undoable.",
        tools: TOOLS,
        kit: null,
        options: { provider: "anthropic", apiKey: "test-key", maxTurns: 40 },
        ...extra,
    };
}

function report(events) {
    const messages = events.filter((e) => e.kind === "message");
    return JSON.parse(messages[messages.length - 1].text);
}

test("hello, and status without a key", async () => {
    const session = new Session({ data: temp("data") });
    assert.deepEqual(await session.next((m) => m.type === "hello"), { type: "hello", apiVersion: 4 });
    const status = await session.request("s1", { op: "status", options: { provider: "openai", apiKey: "" } });
    assert.deepEqual(status.result, {
        ready: false,
        provider: "openai",
        model: "gpt-5.5",
        detail: "Add an API key in Settings › Plugins › Director",
    });
    const ready = await session.request("s2", { op: "status", options: { provider: "anthropic", apiKey: "k" } });
    assert.equal(ready.result.ready, true);
    assert.equal(ready.result.model, "claude-sonnet-5-5");
    const unknown = await session.request("s3", { op: "status", options: { provider: "groq", model: "nope", apiKey: "k" } });
    assert.equal(unknown.result.ready, false);
    assert.match(unknown.result.detail, /no model "nope"/);
    const bad = await session.request("s4", { op: "dance" });
    assert.equal(bad.error.code, "invalid_params");
    assert.equal(await session.close(), 0);
});

test("a turn without a key ends with an error the user can act on", async () => {
    const session = new Session({ data: temp("data"), faux: script([{ text: "never" }]) });
    const reply = await session.request("t1", turn({ options: { apiKey: "" } }));
    assert.deepEqual(reply.result, { stopReason: "error", error: "Add an API key in Settings › Plugins › Director" });
    await session.close();
});

test("a turn that calls a BashCut tool", async () => {
    const skills = kit();
    const session = new Session({
        data: temp("data"),
        faux: script([
            { thinking: "Read the timeline first.", text: "Let me look.", toolCalls: [{ name: "bashcut_timeline_get", arguments: { tracks: true } }] },
            { reportContext: true },
        ]),
    });
    session.write({ type: "request", id: "t1", apiVersion: 4, method: "agent.chat", params: turn({ kit: skills }) });
    const call = await session.next((m) => m.type === "call");
    assert.deepEqual(call, { type: "call", id: "t1", callId: "c1", method: "timeline.get", params: { tracks: true } });
    session.write({ type: "callResult", callId: "c1", result: { tracks: [{ id: "V1", items: 3 }] } });
    const reply = await session.next((m) => m.id === "t1" && "result" in m);
    assert.deepEqual(reply.result, { stopReason: "end" });

    const events = session.events("t1");
    const kinds = events.map((e) => e.kind);
    assert.ok(kinds.includes("thinking") && kinds.includes("text"));
    assert.equal(events.filter((e) => e.kind === "thinking").map((e) => e.delta).join(""), "Read the timeline first.");
    assert.deepEqual(events.find((e) => e.kind === "message"), { kind: "message", role: "assistant", text: "Let me look." });
    assert.deepEqual(events.find((e) => e.kind === "tool"), {
        kind: "tool",
        callId: "c1",
        name: "bashcut_timeline_get",
        summary: 'timeline.get {"tracks":true}',
    });
    const end = events.find((e) => e.kind === "toolEnd");
    assert.equal(end.callId, "c1");
    assert.equal(end.ok, true);
    assert.match(end.summary, /V1/);
    assert.ok(kinds.indexOf("tool") < kinds.indexOf("toolEnd"));

    const seen = report(events);
    assert.deepEqual(seen.toolResults, ['{"tracks":[{"id":"V1","items":3}]}']);
    assert.equal(seen.lastUser, "Tighten the intro");
    assert.match(seen.systemPrompt, /Use the BashCut tools/);
    assert.match(seen.systemPrompt, /cut-silences: Remove pauses from speech/);
    assert.match(seen.systemPrompt, /read_skill/);
    assert.match(seen.systemPrompt, /project: \/tmp\/demo.bashcut/);
    assert.deepEqual(seen.tools.sort(), ["bashcut_timeline_get", "bashcut_ui_frame", "read_skill"]);
    await session.close();
});

test("a failed tool call is shown to the model as an error", async () => {
    const session = new Session({
        data: temp("data"),
        faux: script([{ toolCalls: [{ name: "bashcut_timeline_get", arguments: {} }] }, { reportContext: true }]),
    });
    session.write({ type: "request", id: "t1", apiVersion: 4, method: "agent.chat", params: turn() });
    const call = await session.next((m) => m.type === "call");
    session.write({ type: "callResult", callId: call.callId, error: { code: -32602, message: "Edits are turned off" } });
    const reply = await session.next((m) => m.id === "t1" && "result" in m);
    assert.deepEqual(reply.result, { stopReason: "end" });
    const end = session.events("t1").find((e) => e.kind === "toolEnd");
    assert.equal(end.ok, false);
    assert.match(end.summary, /Edits are turned off/);
    assert.match(report(session.events("t1")).toolResults[0], /Edits are turned off/);
    await session.close();
});

test("read_skill reads only the kit's skills, and ui.frame sends the picture", async () => {
    const skills = kit();
    const png = join(temp("frame"), "frame.png");
    writeFileSync(png, PNG);
    const session = new Session({
        data: temp("data"),
        faux: script([
            { toolCalls: [{ name: "read_skill", arguments: { name: "cut-silences" } }] },
            { toolCalls: [{ name: "read_skill", arguments: { name: "../secret.txt" } }] },
            { toolCalls: [{ name: "bashcut_ui_frame", arguments: { frame: 12 } }] },
            { reportContext: true },
        ]),
    });
    session.write({ type: "request", id: "t1", apiVersion: 4, method: "agent.chat", params: turn({ kit: skills }) });
    const call = await session.next((m) => m.type === "call");
    assert.equal(call.method, "ui.frame");
    session.write({ type: "callResult", callId: call.callId, result: { path: png, frame: 12, width: 1, height: 1 } });
    await session.next((m) => m.id === "t1" && "result" in m);
    const ends = session.events("t1").filter((e) => e.kind === "toolEnd");
    assert.deepEqual(ends.map((e) => e.ok), [true, false, true]);
    const seen = report(session.events("t1"));
    assert.match(seen.toolResults[0], /# Cut silences/);
    assert.match(seen.toolResults[1], /without \/ or \.\./);
    assert.equal(seen.images, 1);
    await session.close();
});

test("cancel aborts a turn waiting on a tool call or on the model", async () => {
    const session = new Session({
        data: temp("data"),
        faux: script([{ toolCalls: [{ name: "bashcut_timeline_get", arguments: {} }] }, { delayMs: 30_000, text: "too late" }]),
    });
    session.write({ type: "request", id: "t1", apiVersion: 4, method: "agent.chat", params: turn() });
    await session.next((m) => m.type === "call");
    session.write({ type: "cancel", id: "t1" });
    const first = await session.next((m) => m.id === "t1" && "result" in m);
    assert.deepEqual(first.result, { stopReason: "aborted" });

    session.write({ type: "request", id: "t2", apiVersion: 4, method: "agent.chat", params: turn({ text: "again" }) });
    await new Promise((resolve) => setTimeout(resolve, 300));
    const started = Date.now();
    session.write({ type: "cancel", id: "t2" });
    const second = await session.next((m) => m.id === "t2" && "result" in m);
    assert.deepEqual(second.result, { stopReason: "aborted" });
    assert.ok(Date.now() - started < 5_000);
    await session.close();
});

test("conversations survive a restart, and reset forgets them", async () => {
    const data = temp("data");
    const first = new Session({ data, faux: script([{ text: "First answer." }]) });
    const one = await first.request("t1", turn({ text: "Hello" }));
    assert.deepEqual(one.result, { stopReason: "end" });
    assert.equal(await first.close(), 0);
    assert.deepEqual(readdirSync(join(data, "conversations")), ["project-1.json"]);
    const saved = readFileSync(join(data, "conversations", "project-1.json"), "utf8");
    assert.match(saved, /First answer/);
    assert.ok(!saved.includes("test-key") && !first.stderr.includes("test-key"), "the API key is never stored or logged");

    const second = new Session({ data, faux: script([{ reportContext: true }, { reportContext: true }]) });
    await second.request("t2", turn({ text: "And now?" }));
    const seen = report(second.events("t2"));
    assert.equal(seen.roles.user, 2);
    assert.equal(seen.roles.assistant, 1);
    assert.equal(seen.lastUser, "And now?");

    assert.deepEqual((await second.request("r1", { op: "reset", conversation: "project-1" })).result, {});
    assert.deepEqual(readdirSync(join(data, "conversations")), []);
    await second.request("t3", turn({ text: "Fresh" }));
    const fresh = report(second.events("t3"));
    assert.equal(fresh.roles.user, 1);
    assert.equal(fresh.roles.assistant, undefined);
    await second.close();
});

test("maxTurns stops a runaway tool loop with a notice", async () => {
    const loop = Array.from({ length: 8 }, () => ({ toolCalls: [{ name: "read_skill", arguments: { name: "cut-silences" } }] }));
    const session = new Session({ data: temp("data"), faux: script(loop) });
    const reply = await session.request("t1", turn({ kit: kit(), options: { apiKey: "k", maxTurns: 5 } }));
    assert.deepEqual(reply.result, { stopReason: "end" });
    const events = session.events("t1");
    assert.equal(events.filter((e) => e.kind === "tool").length, 5);
    assert.match(events.find((e) => e.kind === "notice").text, /Stopped after 5 model turns/);
    await session.close();
});

test("old tool results are compacted near the context window", async () => {
    const calls = Array.from({ length: 6 }, () => ({ toolCalls: [{ name: "bashcut_timeline_get", arguments: {} }] }));
    const session = new Session({
        data: temp("data"),
        faux: script([...calls, { reportContext: true }], { model: { contextWindow: 16_000, maxTokens: 1_000 } }),
    });
    session.write({ type: "request", id: "t1", apiVersion: 4, method: "agent.chat", params: turn() });
    for (let i = 1; i <= 6; i++) {
        await session.next((m) => m.type === "call" && m.callId === `c${i}`);
        session.write({ type: "callResult", callId: `c${i}`, result: { text: "x".repeat(12_000), n: i } });
    }
    const reply = await session.next((m) => m.id === "t1" && "result" in m);
    assert.deepEqual(reply.result, { stopReason: "end" });
    const events = session.events("t1");
    assert.ok(events.some((e) => e.kind === "notice" && /shortened/.test(e.text)));
    const results = report(events).toolResults;
    assert.equal(results.length, 6);
    assert.match(results[0], /^\[Older tool result removed/);
    assert.match(results[5], /"n":6/);
    await session.close();
});

test("a model error ends the turn with its message", async () => {
    const session = new Session({ data: temp("data"), faux: script([{ stopReason: "error", errorMessage: "Overloaded" }]) });
    const reply = await session.request("t1", turn());
    assert.equal(reply.result.stopReason, "error");
    assert.match(reply.result.error, /Overloaded/);
    await session.close();
});

test("bin/check and bin/provider find Node.js in the plugin data folder", async () => {
    const data = temp("data");
    mkdirSync(join(data, "node", "bin"), { recursive: true });
    symlinkSync(process.execPath, join(data, "node", "bin", "node"));
    const env = { HOME: temp("home"), PATH: "/usr/bin:/bin:/usr/sbin:/sbin", BASHCUT_PLUGIN_DATA: data };
    const check = spawnSync(join(PLUGIN, "bin", "check"), [], { env, encoding: "utf8" });
    assert.equal(check.status, 0, check.stderr);
    assert.match(check.stdout, new RegExp(`^Node\\.js v\\d+\\.\\d+\\.\\d+ at ${data}/node/bin/node\\n$`));

    const session = new Session({ data, command: [join(PLUGIN, "bin", "provider"), "session"], env: { HOME: env.HOME } });
    assert.deepEqual(await session.next((m) => m.type === "hello"), { type: "hello", apiVersion: 4 });
    assert.equal(await session.close(), 0);

    // With nothing installed anywhere the probe fails (skipped where Homebrew or /usr/local has a Node.js).
    if (!existsSync("/opt/homebrew/bin/node") && !existsSync("/usr/local/bin/node")) {
        const missing = spawnSync(join(PLUGIN, "bin", "check"), [], { env: { ...env, BASHCUT_PLUGIN_DATA: temp("empty") }, encoding: "utf8" });
        assert.equal(missing.status, 1);
        assert.match(missing.stderr, /22\.19 or newer was not found/);
    }
});
