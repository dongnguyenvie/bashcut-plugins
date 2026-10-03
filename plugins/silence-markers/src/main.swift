// Silence Markers: finds quiet stretches in the selected clip's audio, and either proposes a section marker at each
// one or cuts them out of the clip.
//
// BashCut plugin API 2, one-shot transport: `provider rpc` reads one JSON request from stdin and writes one JSON
// response. Audio is decoded with AVFoundation (any format macOS plays: mp4, mov, m4a, wav, mp3…) to 16 kHz mono
// floats and measured in 10 ms windows. Nothing outside macOS is needed.
import AVFoundation
import Foundation

let sampleRate = 16_000.0
let windowSeconds = 0.01

struct Failure: Error { let message: String }

func number(_ value: Any?) -> Double? { (value as? NSNumber)?.doubleValue }

/// Frames per second from BashCut's `[numerator, denominator]` (or a plain number).
func fps(_ value: Any?, fallback: Double = 30) -> Double {
    if let pair = value as? [NSNumber], pair.count == 2, pair[1].doubleValue != 0 {
        return pair[0].doubleValue / pair[1].doubleValue
    }
    return number(value).flatMap { $0 > 0 ? $0 : nil } ?? fallback
}

/// Mono samples between `start` and `end` seconds of the file's first audio track.
func decode(_ path: String, start: Double, end: Double) throws -> [Float] {
    let asset = AVURLAsset(url: URL(fileURLWithPath: path))
    guard let track = asset.tracks(withMediaType: .audio).first else { throw Failure(message: "the clip has no audio") }
    let reader = try AVAssetReader(asset: asset)
    reader.timeRange = CMTimeRange(
        start: CMTime(seconds: max(0, start), preferredTimescale: 48_000),
        end: CMTime(seconds: end, preferredTimescale: 48_000))
    let output = AVAssetReaderTrackOutput(track: track, outputSettings: [
        AVFormatIDKey: kAudioFormatLinearPCM, AVSampleRateKey: sampleRate, AVNumberOfChannelsKey: 1,
        AVLinearPCMBitDepthKey: 32, AVLinearPCMIsFloatKey: true, AVLinearPCMIsNonInterleaved: false,
        AVLinearPCMIsBigEndianKey: false,
    ])
    reader.add(output)
    guard reader.startReading() else {
        throw Failure(message: "cannot decode audio: \(reader.error?.localizedDescription ?? "unknown error")")
    }
    var samples: [Float] = []
    while let buffer = output.copyNextSampleBuffer() {
        guard let block = CMSampleBufferGetDataBuffer(buffer) else { continue }
        let length = CMBlockBufferGetDataLength(block)
        var chunk = [Float](repeating: 0, count: length / MemoryLayout<Float>.size)
        chunk.withUnsafeMutableBytes { raw in
            _ = CMBlockBufferCopyDataBytes(block, atOffset: 0, dataLength: length, destination: raw.baseAddress!)
        }
        samples += chunk
    }
    if reader.status == .failed {
        throw Failure(message: "cannot decode audio: \(reader.error?.localizedDescription ?? "unknown error")")
    }
    return samples
}

/// `[(start, end)]` in seconds relative to the decoded range where the RMS level stays below `thresholdDb`.
func silences(_ samples: [Float], thresholdDb: Double, minimum: Double) -> [(Double, Double)] {
    let window = Int(sampleRate * windowSeconds)
    let threshold = Float(pow(10, thresholdDb / 20))
    var found: [(Double, Double)] = []
    var quietFrom: Double?
    var offset = 0
    while offset < samples.count {
        let chunk = samples[offset..<min(offset + window, samples.count)]
        let rms = (chunk.reduce(0) { $0 + $1 * $1 } / Float(chunk.count)).squareRoot()
        let now = Double(offset) / sampleRate
        if rms < threshold {
            if quietFrom == nil { quietFrom = now }
        } else if let from = quietFrom {
            if now - from >= minimum { found.append((from, now)) }
            quietFrom = nil
        }
        offset += window
    }
    let total = Double(samples.count) / sampleRate
    if let from = quietFrom, total - from >= minimum { found.append((from, total)) }
    return found
}

/// The selected clip, where its source range starts and ends, and the silences in it (seconds from its start).
struct Analysis {
    let item: [String: Any]
    let itemID: String
    let at: Int
    let duration: Int
    let speed: Double
    let projectFPS: Double
    let revision: Int?
    let thresholdDb: Double
    let ranges: [(Double, Double)]
    let length: Double

    var end: Int { at + duration }
    /// Timeline frame of a time measured from the clip's start in source seconds.
    func frame(_ seconds: Double) -> Int { at + Int((seconds / speed * projectFPS).rounded()) }
}

func analyze(_ params: [String: Any]) throws -> Analysis {
    let context = params["context"] as? [String: Any] ?? [:]
    let values = params["params"] as? [String: Any] ?? [:]
    guard let item = context["selection"] as? [String: Any], let media = context["media"] as? [String: Any],
        let path = media["absolutePath"] as? String
    else { throw Failure(message: "select a clip with media") }
    let project = context["project"] as? [String: Any] ?? [:]
    let projectFPS = fps(project["fps"])
    let mediaFPS = fps(media["fps"], fallback: projectFPS)
    let speed = number(item["speed"]).flatMap { $0 > 0 ? $0 : nil } ?? 1
    let duration = Int(number(item["dur"]) ?? 0)
    let start = (number(item["in"]) ?? 0) / mediaFPS
    let end = start + Double(duration) / projectFPS * speed
    let thresholdDb = number(values["thresholdDb"]) ?? -40
    let minimum = (number(values["minSilenceMs"]) ?? 400) / 1000
    let samples = try decode(path, start: start, end: end)
    return Analysis(
        item: item, itemID: item["id"] as? String ?? "", at: Int(number(item["at"]) ?? 0), duration: duration,
        speed: speed, projectFPS: projectFPS, revision: number(project["rev"]).map { Int($0) },
        thresholdDb: thresholdDb, ranges: silences(samples, thresholdDb: thresholdDb, minimum: minimum),
        length: end - start)
}

func mark(_ params: [String: Any]) throws -> [String: Any] {
    let analysis = try analyze(params)
    let options = params["options"] as? [String: Any] ?? [:]
    let prefix = (options["labelPrefix"] as? String).flatMap { $0.isEmpty ? nil : $0 } ?? "Silence"
    let marks: [[String: Any]] = analysis.ranges.map { from, to in
        [
            "start": analysis.frame(from), "end": min(analysis.end, analysis.frame(to)),
            "seconds": ((to - from) * 100).rounded() / 100,
        ]
    }
    guard !marks.isEmpty else { return ["message": "No silence found", "data": ["silences": []]] }
    let operations: [[String: Any]] = marks.map { mark in
        let seconds = mark["seconds"] as? Double ?? 0
        return [
            "op": "upsertSection", "id": UUID().uuidString, "label": String(format: "%@ %.1fs", prefix, seconds),
            "atFrame": mark["start"] as? Int ?? analysis.at,
        ]
    }
    return [
        "label": "Mark silences", "baseRev": analysis.revision as Any, "operations": operations,
        "message": "Marked \(marks.count) silences", "data": ["silences": marks],
        "pluginData": ["lastRun": ["item": analysis.itemID, "count": marks.count, "thresholdDb": analysis.thresholdDb]],
        "ui": ["reveal": marks[0]["start"] ?? analysis.at],
    ]
}

/// Cuts every silence out of the clip: split at both ends (keeping `paddingMs` of quiet on each side so words are
/// not clipped) and ripple-delete the middle. Cuts run right to left, so a ripple never moves a cut still to come.
/// Linked sound is split and deleted with the picture by BashCut.
func remove(_ params: [String: Any]) throws -> [String: Any] {
    let analysis = try analyze(params)
    let values = params["params"] as? [String: Any] ?? [:]
    let padding = (number(values["paddingMs"]) ?? 100) / 1000
    var cuts: [(Int, Int)] = []
    for (from, to) in analysis.ranges {
        // No padding against the clip's own edges: a silence there goes completely.
        let start = from <= 0.0001 ? analysis.at : analysis.frame(from + padding)
        let end = to >= analysis.length - 0.0001 ? analysis.end : analysis.frame(to - padding)
        if end - start >= 1 { cuts.append((max(analysis.at, start), min(analysis.end, end))) }
    }
    guard !cuts.isEmpty else { return ["message": "No silence to remove", "data": ["removed": []]] }
    if cuts.count == 1, cuts[0] == (analysis.at, analysis.end) { throw Failure(message: "the whole clip is silent") }
    var operations: [[String: Any]] = []
    var keep: String? = analysis.itemID
    for (start, end) in cuts.reversed() {
        let tail = UUID().uuidString
        if end < analysis.end {
            operations.append(["op": "split", "item": analysis.itemID, "atFrame": end, "newID": tail])
        }
        if start > analysis.at {
            let middle = UUID().uuidString
            operations.append(["op": "split", "item": analysis.itemID, "atFrame": start, "newID": middle])
            operations.append(["op": "delete", "item": middle, "ripple": true])
        } else {
            // The silence opens the clip: the clip's own left part is the silence.
            operations.append(["op": "delete", "item": analysis.itemID, "ripple": true])
            keep = end < analysis.end ? tail : nil
        }
    }
    let removedFrames = cuts.reduce(0) { $0 + $1.1 - $1.0 }
    let seconds = Double(removedFrames) / analysis.projectFPS
    var result: [String: Any] = [
        "label": "Remove silences", "baseRev": analysis.revision as Any, "operations": operations,
        "message": String(format: "Removed %d silences (%.1fs)", cuts.count, seconds),
        "data": ["removed": cuts.map { ["start": $0.0, "end": $0.1] }, "seconds": seconds],
        "pluginData": ["lastRun": ["item": analysis.itemID, "removed": cuts.count, "thresholdDb": analysis.thresholdDb]],
    ]
    if let keep { result["ui"] = ["select": keep, "seek": analysis.at] }
    return result
}

func handle(_ request: [String: Any]) -> [String: Any] {
    let id = request["id"] ?? ""
    do {
        guard request["method"] as? String == "plugin.action" else {
            return ["id": id, "error": ["code": "unknown_method", "message": "\(request["method"] ?? "")"]]
        }
        let params = request["params"] as? [String: Any] ?? [:]
        switch params["action"] as? String {
        case "bashcut.silence-markers.mark": return ["id": id, "result": try mark(params)]
        case "bashcut.silence-markers.remove": return ["id": id, "result": try remove(params)]
        default: throw Failure(message: "unknown action")
        }
    } catch let failure as Failure {
        return ["id": id, "error": ["code": "failed", "message": failure.message]]
    } catch {
        return ["id": id, "error": ["code": "failed", "message": error.localizedDescription]]
    }
}

let line = readLine(strippingNewline: true) ?? ""
let request = (try? JSONSerialization.jsonObject(with: Data(line.utf8))) as? [String: Any] ?? [:]
let response = try JSONSerialization.data(withJSONObject: handle(request))
FileHandle.standardOutput.write(response + Data([0x0A]))
