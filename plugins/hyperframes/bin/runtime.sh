# Sourced by bin/hf, bin/check and bin/setup (after setting `here`): where the HyperFrames runtime lives and how it
# runs. lib/runtime.mjs keeps the same paths for the provider. The folders are fixed, so agents that run bin/hf
# without BashCut's variables find the same install.
data="${BASHCUT_PLUGIN_DATA:-$HOME/Library/Application Support/BashCut/PluginData/bashcut.hyperframes}"
cache="${BASHCUT_PLUGIN_CACHE:-$HOME/Library/Caches/BashCut/PluginData/bashcut.hyperframes}"
# npm ci of runtime/package.template.json (HyperFrames, GSAP, KaTeX and lottie-web at pinned versions): kept across
# plugin updates.
runtime="$data/runtime"
cli="$runtime/node_modules/hyperframes/bin/hyperframes.mjs"
gsap="$runtime/node_modules/gsap/dist/gsap.min.js"
# KaTeX typesets the formula example's LaTeX at render time (copied next to the page, no network).
katex="$runtime/node_modules/katex/dist/katex.min.js"
# lottie-web (SVG player with expressions) plays the lottie example's animation, copied next to the page as lottie.min.js.
lottie="$runtime/node_modules/lottie-web/build/player/lottie_svg.min.js"
# Chrome headless shell for rendering: can be downloaded again, so it lives in the cache folder. HyperFrames keeps
# it under $HOME/.cache, so setup runs `browser ensure` with HOME set here and saves the path it printed.
chrome_home="$cache/chrome"
chrome_path_file="$cache/chrome/path"
# No telemetry, no skills check against GitHub.
export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 HF_CLI_TELEMETRY_DISABLED=1 HYPERFRAMES_SKIP_SKILLS=1
if [ -f "$chrome_path_file" ]; then
    HYPERFRAMES_BROWSER_PATH="$(cat "$chrome_path_file")"
    export HYPERFRAMES_BROWSER_PATH
fi
