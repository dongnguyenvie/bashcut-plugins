// NDJSON session transport (BashCut plugin API 4). Standard output carries protocol lines only; everything else
// (logs, library chatter) goes to standard error.

export type JSONValue = null | boolean | number | string | JSONValue[] | { [key: string]: JSONValue };

/** UI events for the caller (spec 11 §3.3). */
export type DirectorEvent =
    | { kind: "text"; delta: string }
    | { kind: "thinking"; delta: string }
    | { kind: "tool"; callId: string; name: string; summary: string }
    | { kind: "toolEnd"; callId: string; ok: boolean; summary: string }
    | { kind: "message"; role: "assistant"; text: string }
    | { kind: "notice"; text: string };

let queue: Promise<void> = Promise.resolve();

/** Writes one protocol line. Lines are queued so a large result never interleaves with another line. */
export function send(message: Record<string, unknown>): Promise<void> {
    const line = JSON.stringify(message) + "\n";
    queue = queue.then(
        () =>
            new Promise<void>((resolve) => {
                if (process.stdout.write(line)) resolve();
                else process.stdout.once("drain", () => resolve());
            }),
    );
    return queue;
}

/** Resolves when every queued line has been handed to the OS. */
export function flushed(): Promise<void> {
    return queue;
}

export function log(...parts: unknown[]): void {
    process.stderr.write(`[director] ${parts.map((p) => (typeof p === "string" ? p : JSON.stringify(p))).join(" ")}\n`);
}

/** Library code must never write to stdout: route console output to stderr. */
export function guardStdout(): void {
    const toStderr = (...args: unknown[]) => process.stderr.write(args.map(String).join(" ") + "\n");
    console.log = toStderr;
    console.info = toStderr;
    console.debug = toStderr;
    console.warn = toStderr;
}

export function truncate(text: string, max: number): string {
    return text.length <= max ? text : text.slice(0, Math.max(0, max - 1)) + "…";
}

/** One line, at most `max` characters: for tool rows. */
export function oneLine(text: string, max = 160): string {
    return truncate(text.replace(/\s+/g, " ").trim(), max);
}
