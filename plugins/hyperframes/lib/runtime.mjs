// Where the HyperFrames runtime lives and how to run it: the same paths as bin/runtime.sh (bin/setup installs them).
import { spawn } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readdirSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { PluginError } from "./bashcut-plugin.mjs";

const pluginDir = process.env.BASHCUT_PLUGIN_DIR || join(dirname(fileURLToPath(import.meta.url)), "..");
const id = "bashcut.hyperframes";
const data = process.env.BASHCUT_PLUGIN_DATA || join(homedir(), "Library/Application Support/BashCut/PluginData", id);
const cache = process.env.BASHCUT_PLUGIN_CACHE || join(homedir(), "Library/Caches/BashCut/PluginData", id);

export const paths = {
    cli: join(data, "runtime/node_modules/hyperframes/bin/hyperframes.mjs"),
    gsap: join(data, "runtime/node_modules/gsap/dist/gsap.min.js"),
    katex: join(data, "runtime/node_modules/katex/dist"),
    lottie: join(data, "runtime/node_modules/lottie-web/build/player/lottie_svg.min.js"),
    chromePathFile: join(cache, "chrome/path"),
    encoder: join(pluginDir, "bin/encode-alpha"),
    diagram: join(pluginDir, "lib/diagram.js"),
    amenityMap: join(pluginDir, "lib/amenity-map.js"),
};

/** The environment HyperFrames runs in: telemetry off, the plugin's Chrome, this Node.js first on PATH. */
function environment() {
    const env = {
        ...process.env,
        HYPERFRAMES_NO_TELEMETRY: "1",
        DO_NOT_TRACK: "1",
        HF_CLI_TELEMETRY_DISABLED: "1",
        HYPERFRAMES_SKIP_SKILLS: "1",
        PATH: `${dirname(process.execPath)}:${process.env.PATH ?? "/usr/bin:/bin"}`,
    };
    if (existsSync(paths.chromePathFile)) env.HYPERFRAMES_BROWSER_PATH = readFileSync(paths.chromePathFile, "utf8").trim();
    return env;
}

export function requireRuntime() {
    if (!existsSync(paths.cli) || !existsSync(paths.chromePathFile)) {
        throw new PluginError("dependency_missing",
            "HyperFrames is not installed: choose Install Dependencies for HyperFrames Graphics in Plugins");
    }
    if (!existsSync(paths.encoder)) throw new PluginError("dependency_missing", "bin/encode-alpha is missing (run build.sh)");
}

/** Runs a program and resolves {code, stdout, stderr}; `onTick` is called every 10 s while it runs. */
export function execute(command, args, { cwd, onTick } = {}) {
    return new Promise((resolve, reject) => {
        const child = spawn(command, args, { cwd, env: environment(), stdio: ["ignore", "pipe", "pipe"] });
        let stdout = "";
        let stderr = "";
        child.stdout.on("data", (chunk) => (stdout += chunk));
        child.stderr.on("data", (chunk) => {
            stderr += chunk;
            if (stderr.length > 64_000) stderr = stderr.slice(-32_000);
        });
        const timer = onTick ? setInterval(onTick, 10_000) : null;
        child.on("error", (error) => {
            if (timer) clearInterval(timer);
            reject(error);
        });
        child.on("close", (code) => {
            if (timer) clearInterval(timer);
            resolve({ code, stdout, stderr });
        });
    });
}

/** Runs the HyperFrames CLI. */
export function hyperframes(args, options) {
    return execute(process.execPath, [paths.cli, ...args], options);
}

/**
 * GSAP, KaTeX, lottie-web and the shared scripts are not bundled in compositions: the pinned GSAP, KaTeX (script, style
 * and its woff2 fonts, into katex/), lottie-web's SVG player (as lottie.min.js), lib/diagram.js and lib/amenity-map.js
 * are copied next to a page that loads them locally, so a render needs no network.
 */
export function provideScripts(composition) {
    const page = composition.file ?? join(composition.dir, "index.html");
    const html = readFileSync(page, "utf8");
    const loads = (file) => new RegExp(`(src|href)=["']\\.?\\/?${file.replace(/[./]/g, "\\$&")}["']`).test(html);
    const target = join(composition.dir, "gsap.min.js");
    if (loads("gsap.min.js") && !existsSync(target)) copyFileSync(paths.gsap, target);
    // The shared scripts are the plugin's: a copy older than the plugin's is replaced, so a rerender gets layout fixes.
    for (const [file, from] of [["diagram.js", paths.diagram], ["amenity-map.js", paths.amenityMap]]) {
        const copy = join(composition.dir, file);
        if (loads(file) && (!existsSync(copy) || !readFileSync(copy).equals(readFileSync(from)))) copyFileSync(from, copy);
    }
    if (loads("lottie.min.js") && !existsSync(join(composition.dir, "lottie.min.js"))) {
        if (!existsSync(paths.lottie)) {
            throw new PluginError("dependency_missing", "lottie-web is not installed: choose Install Dependencies for HyperFrames Graphics in Plugins");
        }
        copyFileSync(paths.lottie, join(composition.dir, "lottie.min.js"));
    }
    if (loads("katex/katex.min.js") && !existsSync(join(composition.dir, "katex", "katex.min.js"))) {
        if (!existsSync(join(paths.katex, "katex.min.js"))) {
            throw new PluginError("dependency_missing", "KaTeX is not installed: choose Install Dependencies for HyperFrames Graphics in Plugins");
        }
        mkdirSync(join(composition.dir, "katex", "fonts"), { recursive: true });
        for (const file of ["katex.min.js", "katex.min.css"]) copyFileSync(join(paths.katex, file), join(composition.dir, "katex", file));
        for (const font of readdirSync(join(paths.katex, "fonts")).filter((f) => f.endsWith(".woff2"))) {
            copyFileSync(join(paths.katex, "fonts", font), join(composition.dir, "katex", "fonts", font));
        }
    }
}
