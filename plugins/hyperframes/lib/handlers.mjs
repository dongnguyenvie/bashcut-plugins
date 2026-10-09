// HyperFrames Graphics: provides graphics.render (provider bashcut.hyperframes.render).
//
// graphics.render turns a HyperFrames composition (a folder with index.html: HTML/CSS + GSAP, any design) into a
// .mov with alpha that BashCut places like any clip. HyperFrames renders RGBA PNG frames in headless Chrome and
// bin/encode-alpha writes HEVC with alpha (small) or ProRes 4444 with AVFoundation, so no FFmpeg is needed.
//
// Params: composition (absolute path to the folder, or to one .html file in it), fps (default 30), codec ("hevc" or
// "prores"), variables (object, merged over the composition's declared defaults), name (output file name without
// extension), outputDirectory (from BashCut).
// Result: path, codec, frames, fps, width, height, bytes, renderSeconds, encodeSeconds, lint {errors, warnings,
// findings}.
import { copyFileSync, existsSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, dirname, extname, isAbsolute, join, relative } from "node:path";
import { PluginError } from "./bashcut-plugin.mjs";
import { hyperframes, execute, paths, requireRuntime } from "./runtime.mjs";

export async function handle(method, params, host) {
    if (method !== "graphics.render") {
        throw new PluginError("unknown_method", `HyperFrames Graphics does not handle ${method}`);
    }
    return render(params, host);
}

function compositionOf(params) {
    const value = params.composition;
    if (typeof value !== "string" || !isAbsolute(value)) {
        throw new PluginError("invalid_params", "composition must be the absolute path of a composition folder");
    }
    if (!existsSync(value)) throw new PluginError("invalid_params", `${value} does not exist`);
    if (statSync(value).isDirectory()) {
        if (!existsSync(join(value, "index.html"))) throw new PluginError("invalid_params", `${value} has no index.html`);
        return { dir: value, file: null, name: basename(value) };
    }
    if (extname(value).toLowerCase() !== ".html") {
        throw new PluginError("invalid_params", "composition must be a folder or an .html file");
    }
    return { dir: dirname(value), file: value, name: basename(value, extname(value)) };
}

function settingsOf(params) {
    const fps = params.fps ?? 30;
    if (!Number.isInteger(fps) || fps < 1 || fps > 120) throw new PluginError("invalid_params", "fps must be 1–120");
    const codec = params.codec ?? "hevc";
    if (!["hevc", "prores"].includes(codec)) throw new PluginError("invalid_params", 'codec must be "hevc" or "prores"');
    const variables = params.variables ?? {};
    if (typeof variables !== "object" || Array.isArray(variables) || variables === null) {
        throw new PluginError("invalid_params", "variables must be a JSON object");
    }
    if (params.name !== undefined && !/^[A-Za-z0-9][A-Za-z0-9._-]{0,80}$/.test(String(params.name))) {
        throw new PluginError("invalid_params", "name may use letters, digits, '.', '_' and '-'");
    }
    const output = params.outputDirectory;
    if (typeof output !== "string" || !isAbsolute(output)) {
        throw new PluginError("invalid_params", "outputDirectory is missing (BashCut sets it)");
    }
    return { fps, codec, variables, output };
}

/** GSAP is not bundled in compositions: copy the pinned one next to a page that loads gsap.min.js locally. */
function provideGsap(composition) {
    const page = composition.file ?? join(composition.dir, "index.html");
    const html = readFileSync(page, "utf8");
    const target = join(composition.dir, "gsap.min.js");
    if (/src=["']\.?\/?gsap\.min\.js["']/.test(html) && !existsSync(target)) copyFileSync(paths.gsap, target);
}

async function lint(composition) {
    const args = ["lint", composition.dir, "--json"];
    const { stdout } = await hyperframes(args);
    try {
        const report = JSON.parse(stdout);
        const findings = (report.findings ?? []).filter((f) => !composition.file || !f.file || f.file === composition.file);
        return {
            errors: report.errorCount ?? 0,
            warnings: report.warningCount ?? 0,
            findings: findings.slice(0, 12).map((f) => ({
                severity: f.severity, code: f.code, message: f.message, fixHint: f.fixHint, line: f.line,
            })),
        };
    } catch {
        return { errors: 0, warnings: 0, findings: [], unread: stdout.slice(0, 500) };
    }
}

async function render(params, host) {
    const composition = compositionOf(params);
    const { fps, codec, variables, output } = settingsOf(params);
    requireRuntime();
    provideGsap(composition);
    const name = params.name ?? composition.name;
    const work = mkdtempSync(join(tmpdir(), "bashcut-hyperframes-"));
    try {
        host.progress(0.02, "Checking the composition");
        const lintReport = await lint(composition);
        if (params.strict && lintReport.errors > 0) {
            throw new PluginError("lint_failed", `The composition has ${lintReport.errors} lint error(s): ` +
                lintReport.findings.filter((f) => f.severity === "error").map((f) => f.message).join(" · "));
        }

        host.progress(0.05, "Rendering frames in Chrome");
        const started = Date.now();
        const variablesFile = join(work, "variables.json");
        writeFileSync(variablesFile, JSON.stringify(variables));
        const args = ["render", composition.dir, "--format", "png-sequence", "-o", join(work, "png"),
            "--fps", String(fps), "--variables-file", variablesFile, "--quiet"];
        if (composition.file) args.push("-c", relative(composition.dir, composition.file));
        const rendered = await hyperframes(args, { onTick: () => host.progress(null, "Rendering frames in Chrome") });
        if (rendered.code !== 0) {
            throw new PluginError("render_failed", `HyperFrames could not render: ${rendered.stderr.trim().slice(-1500)}`);
        }
        const renderSeconds = Math.round((Date.now() - started) / 100) / 10;

        host.progress(0.85, codec === "hevc" ? "Encoding HEVC with alpha" : "Encoding ProRes 4444");
        const path = join(output, `${name}.mov`);
        const encoded = await execute(paths.encoder, [join(work, "png"), path, "--fps", String(fps), "--codec", codec],
            { onTick: () => host.progress(null, "Encoding") });
        if (encoded.code !== 0) {
            throw new PluginError("encode_failed", `Encoding failed: ${encoded.stderr.trim().slice(-1500)}`);
        }
        const report = JSON.parse(encoded.stdout.trim().split("\n").pop());
        return {
            path,
            codec,
            frames: report.frames,
            fps,
            width: report.width,
            height: report.height,
            bytes: report.bytes,
            renderSeconds,
            encodeSeconds: report.encodeSeconds,
            lint: lintReport,
        };
    } finally {
        rmSync(work, { recursive: true, force: true });
    }
}
