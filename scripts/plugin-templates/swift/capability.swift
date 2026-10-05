// {{NAME}}: provides {{CAPABILITY}} (provider {{PROVIDER_ID}}).
//
// BashCut calls `handle` with method "{{CAPABILITY}}" whenever this provider is chosen. The placeholder below
// returns a valid result so the plugin works end to end; replace it with the real work (AVFoundation, Accelerate…).
// Params and result rules: https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#capabilities
import Foundation

func handle(method: String, params: JSON, host: Host) throws -> Any? {
    guard method == "{{CAPABILITY}}" else { throw PluginError("unknown_method", "{{PLAIN_NAME}} does not handle \(method)") }
// @@ voice.synthesize
    // params: text, language, outputDirectory, takeCount, takeOffset (+ options). Placeholder: the Mac's own voice.
    guard let text = params["text"] as? String, let folder = params["outputDirectory"] as? String else {
        throw PluginError("bad_request", "text and outputDirectory are required")
    }
    let count = params["takeCount"] as? Int ?? 1
    let offset = params["takeOffset"] as? Int ?? 0
    var takes: [JSON] = []
    for index in 0..<count {
        let path = (folder as NSString).appendingPathComponent("take-\(offset + index + 1).aiff")
        host.progress(Double(index) / Double(count), "Take \(index + 1)")
        let say = Process()
        say.executableURL = URL(fileURLWithPath: "/usr/bin/say")
        say.arguments = ["-o", path, text]
        try say.run()
        say.waitUntilExit()
        guard say.terminationStatus == 0 else { throw PluginError("say_failed", "say could not make \(path)") }
        takes.append(["audioPath": path])
    }
    return ["takes": takes]
// @@ captions.transcribe
    // params: mediaPath, language, outputDirectory, optional startSeconds/endSeconds. Placeholder: one cue.
    guard let folder = params["outputDirectory"] as? String else { throw PluginError("bad_request", "No outputDirectory") }
    let start = params["startSeconds"] as? Double ?? 0
    let srt = (folder as NSString).appendingPathComponent("captions.srt")
    let cue = "1\n\(timestamp(start)) --> \(timestamp(start + 2))\nReplace this with the transcription\n"
    try cue.write(toFile: srt, atomically: true, encoding: .utf8)
    return ["srtPath": srt]
// @@ audio.beats
    // params: mediaPath. Placeholder: a steady 120 BPM grid over the first 4 seconds.
    return ["bpm": 120, "beatsSeconds": (1...8).map { Double($0) * 0.5 }]
// @@ audio.loudness
    // params: mediaPath, optional bands. Placeholder numbers; measure the file here.
    return ["integratedLUFS": -16.0, "truePeakDbTP": -1.5]
// @@ audio.sync
    // params: mediaPath, otherPath. Placeholder: no offset found.
    return ["offsetSeconds": 0.0, "correlation": 0.0]
// @@ end
}
// @@ captions.transcribe

/// SubRip time, such as 00:00:02,000.
func timestamp(_ seconds: Double) -> String {
    let millis = Int((seconds * 1000).rounded())
    return String(format: "%02d:%02d:%02d,%03d", millis / 3_600_000, millis / 60_000 % 60, millis / 1000 % 60, millis % 1000)
}
// @@ end
