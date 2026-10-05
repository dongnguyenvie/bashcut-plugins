"""{{NAME}}: provides {{CAPABILITY}} (provider {{PROVIDER_ID}}).

BashCut calls `handle` with method "{{CAPABILITY}}" whenever this provider is chosen. The placeholder below returns a
valid result so the plugin works end to end; replace it with the real work. Params and result rules:
https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#capabilities
"""
# @@ voice.synthesize captions.transcribe
import os
# @@ voice.synthesize
import subprocess
# @@ voice.synthesize captions.transcribe

# @@ end
from bashcut_plugin import PluginError


def handle(method, params, host):
    if method != "{{CAPABILITY}}":
        raise PluginError("unknown_method", f"{{PLAIN_NAME}} does not handle {method}")
# @@ voice.synthesize
    # params: text, language, outputDirectory, takeCount, takeOffset (+ options). Placeholder: the Mac's own voice.
    text, folder = params["text"], params["outputDirectory"]
    takes = []
    for index in range(params.get("takeCount", 1)):
        path = os.path.join(folder, f"take-{params.get('takeOffset', 0) + index + 1}.aiff")
        host.progress(index / params.get("takeCount", 1), f"Take {index + 1}")
        subprocess.run(["say", "-o", path, text], check=True, capture_output=True)
        takes.append({"audioPath": path})
    return {"takes": takes}
# @@ captions.transcribe
    # params: mediaPath, language, outputDirectory, optional startSeconds/endSeconds. Placeholder: one cue.
    start = float(params.get("startSeconds") or 0)
    srt = os.path.join(params["outputDirectory"], "captions.srt")
    with open(srt, "w", encoding="utf-8") as out:
        out.write(f"1\n{timestamp(start)} --> {timestamp(start + 2)}\nReplace this with the transcription\n")
    return {"srtPath": srt}
# @@ audio.beats
    # params: mediaPath. Placeholder: a steady 120 BPM grid over the first 4 seconds.
    return {"bpm": 120, "beatsSeconds": [round(0.5 * beat, 3) for beat in range(1, 9)]}
# @@ audio.loudness
    # params: mediaPath, optional bands. Placeholder numbers; measure the file here.
    return {"integratedLUFS": -16.0, "truePeakDbTP": -1.5}
# @@ audio.sync
    # params: mediaPath, otherPath. Placeholder: no offset found.
    return {"offsetSeconds": 0.0, "correlation": 0.0}
# @@ end
# @@ captions.transcribe


def timestamp(seconds):
    millis = int(round(seconds * 1000))
    return f"{millis // 3600000:02}:{millis // 60000 % 60:02}:{millis // 1000 % 60:02},{millis % 1000:03}"
# @@ end
