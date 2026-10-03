#!/bin/sh
# Bundles src/ (TypeScript) with its locked npm dependencies into dist/director.mjs, one ESM file that bin/provider
# runs with Node.js. CI and package.py run it before the tests and before packaging; run it locally after changing
# src/ or package-lock.json (scripts/dev-link.sh uses the bundle in the working tree). Needs Node.js 22.19+ and npm.
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
cd "$here"
if ! command -v npm >/dev/null 2>&1; then
    node="$(bin/find-node)" || { echo "build.sh needs Node.js 22.19+ with npm" >&2; exit 1; }
    PATH="$(dirname "$node"):$PATH"
fi
# Install exactly what package-lock.json pins, when node_modules is missing or older than the lockfile.
if [ ! -f node_modules/.package-lock.json ] || [ package-lock.json -nt node_modules/.package-lock.json ]; then
    npm ci --no-audit --no-fund --loglevel=error
fi
npx --no-install tsc -p tsconfig.json
mkdir -p dist
# The require shim lets bundled CommonJS SDK code call require() inside an ES module (pi-ai's README).
npx --no-install esbuild src/main.ts --bundle --platform=node --format=esm --target=node22 \
    --legal-comments=eof --minify --log-level=warning \
    --banner:js='import { createRequire as __directorRequire } from "node:module"; const require = __directorRequire(import.meta.url);' \
    --metafile=dist/meta.json --outfile=dist/director.mjs
# Licenses of every npm package inside the bundle (MIT, Apache-2.0…), shipped next to it.
node --input-type=module -e '
import { existsSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
const inputs = Object.keys(JSON.parse(readFileSync("dist/meta.json", "utf8")).inputs);
const roots = new Set(inputs.map((p) => p.match(/^(.*node_modules\/(?:@[^/]+\/)?[^/]+)\//)?.[1]).filter(Boolean));
const parts = ["Third-party software bundled in dist/director.mjs", ""];
for (const root of [...roots].sort()) {
    const pkg = JSON.parse(readFileSync(root + "/package.json", "utf8"));
    const file = readdirSync(root).find((f) => /^(licen[cs]e|copying|notice)/i.test(f));
    parts.push("=".repeat(78), `${pkg.name} ${pkg.version} (${pkg.license ?? "see below"})`, "");
    parts.push(file ? readFileSync(root + "/" + file, "utf8").trim() : `License: ${pkg.license}`, "");
}
writeFileSync("dist/THIRD-PARTY-NOTICES.txt", parts.join("\n"));
rmSync("dist/meta.json");
'
echo "Built $here/dist/director.mjs ($(wc -c < dist/director.mjs | tr -d ' ') bytes)"
