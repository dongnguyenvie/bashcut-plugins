// {{NAME}}: provides {{CAPABILITY}} (provider {{PROVIDER_ID}}).
//
// BashCut calls `handle` with method "{{CAPABILITY}}" whenever this provider is chosen. The placeholder below returns
// a valid result so the plugin works end to end; replace it with the real work. Params and result rules:
// https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#capabilities
// @@ voice.synthesize
import { execFileSync } from "node:child_process";
// @@ voice.synthesize captions.transcribe
import { join } from "node:path";
// @@ captions.transcribe
import { writeFileSync } from "node:fs";
// @@ end
import { PluginError } from "./bashcut-plugin.mjs";

export async function handle(method, params, host) {
    if (method !== "{{CAPABILITY}}") throw new PluginError("unknown_method", `{{PLAIN_NAME}} does not handle ${method}`);
// @@ voice.synthesize
    // params: text, language, outputDirectory, takeCount, takeOffset (+ options). Placeholder: the Mac's own voice.
    const count = params.takeCount ?? 1;
    const takes = [];
    for (let index = 0; index < count; index++) {
        const audioPath = join(params.outputDirectory, `take-${(params.takeOffset ?? 0) + index + 1}.aiff`);
        host.progress(index / count, `Take ${index + 1}`);
        execFileSync("say", ["-o", audioPath, params.text], { stdio: ["ignore", "ignore", "inherit"] });
        takes.push({ audioPath });
    }
    return { takes };
// @@ captions.transcribe
    // params: mediaPath, language, outputDirectory, optional startSeconds/endSeconds. Placeholder: one cue.
    const start = Number(params.startSeconds ?? 0);
    const srtPath = join(params.outputDirectory, "captions.srt");
    writeFileSync(srtPath, `1\n${timestamp(start)} --> ${timestamp(start + 2)}\nReplace this with the transcription\n`);
    return { srtPath };
// @@ audio.beats
    // params: mediaPath. Placeholder: a steady 120 BPM grid over the first 4 seconds.
    return { bpm: 120, beatsSeconds: [1, 2, 3, 4, 5, 6, 7, 8].map((beat) => beat * 0.5) };
// @@ audio.loudness
    // params: mediaPath, optional bands. Placeholder numbers; measure the file here.
    return { integratedLUFS: -16.0, truePeakDbTP: -1.5 };
// @@ audio.sync
    // params: mediaPath, otherPath. Placeholder: no offset found.
    return { offsetSeconds: 0, correlation: 0 };
// @@ end
}
// @@ captions.transcribe

function timestamp(seconds) {
    const millis = Math.round(seconds * 1000);
    const pad = (value, width = 2) => String(value).padStart(width, "0");
    return `${pad(Math.floor(millis / 3600000))}:${pad(Math.floor(millis / 60000) % 60)}:${pad(Math.floor(millis / 1000) % 60)},${pad(millis % 1000, 3)}`;
}
// @@ end
