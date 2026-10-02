// Silence Markers: finds quiet stretches in the selected clip's audio and proposes a section marker at each one.
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

func mark(_ params: [String: Any]) throws -> [String: Any] {
    let context = params["context"] as? [String: Any] ?? [:]
    let values = params["params"] as? [String: Any] ?? [:]
    let options = params["options"] as? [String: Any] ?? [:]
    guard let item = context["selection"] as? [String: Any], let media = context["media"] as? [String: Any],
        let path = media["absolutePath"] as? String
    else { throw Failure(message: "select a clip with media") }
    let project = context["project"] as? [String: Any] ?? [:]
    let projectFPS = fps(project["fps"])
    let mediaFPS = fps(media["fps"], fallback: projectFPS)
    let speed = number(item["speed"]).flatMap { $0 > 0 ? $0 : nil } ?? 1
    let at = Int(number(item["at"]) ?? 0)
    let duration = Int(number(item["dur"]) ?? 0)
    let sourceIn = number(item["in"]) ?? 0
    let start = sourceIn / mediaFPS
    let end = start + Double(duration) / projectFPS * speed
    let thresholdDb = number(values["thresholdDb"]) ?? -40
    let minimum = (number(values["minSilenceMs"]) ?? 400) / 1000
    let ranges = silences(try decode(path, start: start, end: end), thresholdDb: thresholdDb, minimum: minimum)

    func frame(_ seconds: Double) -> Int { at + Int((seconds / speed * projectFPS).rounded()) }
    let prefix = (options["labelPrefix"] as? String).flatMap { $0.isEmpty ? nil : $0 } ?? "Silence"
    let marks: [[String: Any]] = ranges.map { from, to in
        ["start": frame(from), "end": min(at + duration, frame(to)), "seconds": ((to - from) * 100).rounded() / 100]
    }
    guard !marks.isEmpty else { return ["message": "No silence found", "data": ["silences": []]] }
    let operations: [[String: Any]] = marks.map { mark in
        let seconds = mark["seconds"] as? Double ?? 0
        return [
            "op": "upsertSection", "id": UUID().uuidString, "label": String(format: "%@ %.1fs", prefix, seconds),
            "atFrame": mark["start"] as? Int ?? at,
        ]
    }
    return [
        "label": "Mark silences", "baseRev": number(project["rev"]).map { Int($0) } as Any, "operations": operations,
        "message": "Marked \(marks.count) silences", "data": ["silences": marks],
        "pluginData": ["lastRun": ["item": item["id"] ?? "", "count": marks.count, "thresholdDb": thresholdDb]],
        "ui": ["reveal": marks[0]["start"] ?? at],
    ]
}

func handle(_ request: [String: Any]) -> [String: Any] {
    let id = request["id"] ?? ""
    do {
        guard request["method"] as? String == "plugin.action" else {
            return ["id": id, "error": ["code": "unknown_method", "message": "\(request["method"] ?? "")"]]
        }
        let params = request["params"] as? [String: Any] ?? [:]
        guard params["action"] as? String == "bashcut.silence-markers.mark" else { throw Failure(message: "unknown action") }
        return ["id": id, "result": try mark(params)]
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
