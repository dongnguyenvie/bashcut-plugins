// The "Vietsub TikTok" batch preset: each English (or any language) clip becomes a portrait project with captions of
// what is said, burned-in subtitles covered, logos removed, the captions translated to Vietnamese and styled, review
// checks, and a TikTok and a Shorts export. The pipeline ships in presets/vietsub-tiktok.json; this action saves it where
// `batch presets` keeps saved pipelines, so it shows in the Batch window's presets and `batch run --preset`.
import Foundation

func installPreset(_ raw: JSON) throws -> JSON {
    let folder = ProcessInfo.processInfo.environment["BASHCUT_PLUGIN_DIR"]
        ?? URL(fileURLWithPath: CommandLine.arguments[0]).deletingLastPathComponent().deletingLastPathComponent().path
    let source = URL(fileURLWithPath: folder).appendingPathComponent("presets/vietsub-tiktok.json")
    guard let data = try? Data(contentsOf: source), (try? JSONSerialization.jsonObject(with: data)) is JSON else {
        throw PluginError("missing_preset", "The plugin's presets/vietsub-tiktok.json is missing or not JSON")
    }
    let home = ProcessInfo.processInfo.environment["HOME"] ?? NSHomeDirectory()
    let store = URL(fileURLWithPath: home).appendingPathComponent("Library/Application Support/BashCut/Batch/Presets")
    let target = store.appendingPathComponent("vietsub-tiktok.json")
    let replaced = FileManager.default.fileExists(atPath: target.path)
    do {
        try FileManager.default.createDirectory(at: store, withIntermediateDirectories: true)
        try data.write(to: target, options: .atomic)
    } catch {
        throw PluginError("write_failed", "Cannot save the preset: \(error.localizedDescription). Run `bashcut batch presets \(source.path)` instead")
    }
    return [
        "message": (replaced ? "Updated" : "Added") + " the batch preset \"Vietsub TikTok\" (File › Batch…, or `bashcut batch run --preset \"Vietsub TikTok\" --inputs <clips>`)",
        "data": ["preset": "Vietsub TikTok", "path": target.path, "replaced": replaced],
    ]
}
