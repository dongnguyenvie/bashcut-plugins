// Silence Markers: finds quiet stretches in the selected clip's audio, and either proposes a section marker at each
// one or cuts them out of the clip.
//
// Two ways to find them. With BashCut's speech map (`media speech-map`, plugin API 8 session host channel) the gaps
// come from the media's calibrated record: quiet and sound are split by the measured floor, and a clip whose noise
// does not separate from its speech reports that instead of made-up silences. Otherwise (`detect: level`, an older
// BashCut, or media not analysed yet) audio is decoded with AVFoundation (any format macOS plays) to 16 kHz mono
// floats and measured in 10 ms windows against `thresholdDb`. Nothing outside macOS is needed.
//
// `provider rpc` answers one request (no host channel); `provider session` serves newline-delimited JSON.
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

/// How the silences were found, for the result's `detection` field.
struct Detection {
    var method: String
    var speechMap: [String: Any]

    var json: [String: Any] { ["method": method, "speechMap": speechMap] }
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
    /// Source seconds where the clip starts, to report spans in the media's own time.
    let sourceStart: Double
    let detection: Detection

    var end: Int { at + duration }
    /// Timeline frame of a time measured from the clip's start in source seconds.
    func frame(_ seconds: Double) -> Int { at + Int((seconds / speed * projectFPS).rounded()) }
}

/// Gaps from BashCut's speech map, clipped to `start…end` source seconds and measured from `start`; nil with the
/// reason when the map is unavailable or does not separate speech from the floor.
func speechMapGaps(
    _ host: Host?, media: [String: Any], start: Double, end: Double, minimum: Double
) -> (ranges: [(Double, Double)]?, report: [String: Any]) {
    guard let host else { return (nil, ["used": false, "reason": "this BashCut cannot call the speech map"]) }
    guard let id = media["id"] as? String else { return (nil, ["used": false, "reason": "the media has no ID"]) }
    let map: [String: Any]
    do { map = try host.call("media.speech-map", ["media": id]) } catch let failure as Failure {
        return (nil, ["used": false, "reason": failure.message])
    } catch { return (nil, ["used": false, "reason": error.localizedDescription]) }
    let calibration = map["calibration"] as? [String: Any] ?? [:]
    guard let gaps = map["gaps"] as? [[String: Any]] else {
        let reason = map["reason"] as? String ?? "speech and floor do not separate"
        return (nil, ["used": false, "reason": reason, "calibration": calibration])
    }
    let ranges: [(Double, Double)] = gaps.compactMap { gap in
        guard let from = number(gap["start"]), let to = number(gap["end"]) else { return nil }
        let clipped = (max(from, start), min(to, end))
        guard clipped.1 - clipped.0 >= minimum else { return nil }
        return (clipped.0 - start, clipped.1 - start)
    }
    return (ranges, ["used": true, "calibration": calibration])
}

func analyze(_ params: [String: Any], host: Host?) throws -> Analysis {
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
    let detect = values["detect"] as? String ?? "auto"
    var ranges: [(Double, Double)]?
    var detection = Detection(method: "level", speechMap: ["used": false, "reason": "detect is level"])
    if detect != "level" {
        let found = speechMapGaps(host, media: media, start: start, end: end, minimum: minimum)
        ranges = found.ranges
        detection = Detection(method: found.ranges == nil ? "level" : "speechMap", speechMap: found.report)
        if ranges == nil, detect == "speechMap" {
            throw Failure(message: "no speech map: \(found.report["reason"] as? String ?? "unavailable")")
        }
    }
    if ranges == nil {
        ranges = silences(try decode(path, start: start, end: end), thresholdDb: thresholdDb, minimum: minimum)
    }
    return Analysis(
        item: item, itemID: item["id"] as? String ?? "", at: Int(number(item["at"]) ?? 0), duration: duration,
        speed: speed, projectFPS: projectFPS, revision: number(project["rev"]).map { Int($0) },
        thresholdDb: thresholdDb, ranges: ranges ?? [], length: end - start, sourceStart: start,
        detection: detection)
}

/// Rounds seconds to hundredths for reports.
func hundredths(_ value: Double) -> Double { (value * 100).rounded() / 100 }

func mark(_ params: [String: Any], host: Host?) throws -> [String: Any] {
    let analysis = try analyze(params, host: host)
    let options = params["options"] as? [String: Any] ?? [:]
    let prefix = (options["labelPrefix"] as? String).flatMap { $0.isEmpty ? nil : $0 } ?? "Silence"
    let marks: [[String: Any]] = analysis.ranges.map { from, to in
        [
            "start": analysis.frame(from), "end": min(analysis.end, analysis.frame(to)),
            "seconds": hundredths(to - from),
            "sourceStart": hundredths(analysis.sourceStart + from), "sourceEnd": hundredths(analysis.sourceStart + to),
        ]
    }
    guard !marks.isEmpty else {
        return ["message": "No silence found", "data": ["silences": [], "detection": analysis.detection.json]]
    }
    let operations: [[String: Any]] = marks.map { mark in
        let seconds = mark["seconds"] as? Double ?? 0
        return [
            "op": "upsertSection", "id": UUID().uuidString, "label": String(format: "%@ %.1fs", prefix, seconds),
            "atFrame": mark["start"] as? Int ?? analysis.at,
        ]
    }
    return [
        "label": "Mark silences", "baseRev": analysis.revision as Any, "operations": operations,
        "message": "Marked \(marks.count) silences", "data": ["silences": marks, "detection": analysis.detection.json],
        "pluginData": ["lastRun": [
            "item": analysis.itemID, "count": marks.count, "thresholdDb": analysis.thresholdDb,
            "method": analysis.detection.method,
        ]],
        "ui": ["reveal": marks[0]["start"] ?? analysis.at],
    ]
}

/// Cuts every silence out of the clip: split at both ends (keeping `paddingMs` of quiet on each side so words are
/// not clipped) and ripple-delete the middle. Cuts run right to left, so a ripple never moves a cut still to come.
/// Linked sound is split and deleted with the picture by BashCut. The result lists every removed span longest first,
/// so long speechless lifts can be looked at before keeping the edit.
func remove(_ params: [String: Any], host: Host?) throws -> [String: Any] {
    let analysis = try analyze(params, host: host)
    let values = params["params"] as? [String: Any] ?? [:]
    let padding = (number(values["paddingMs"]) ?? 100) / 1000
    var cuts: [(Int, Int)] = []
    for (from, to) in analysis.ranges {
        // No padding against the clip's own edges: a silence there goes completely.
        let start = from <= 0.0001 ? analysis.at : analysis.frame(from + padding)
        let end = to >= analysis.length - 0.0001 ? analysis.end : analysis.frame(to - padding)
        if end - start >= 1 { cuts.append((max(analysis.at, start), min(analysis.end, end))) }
    }
    guard !cuts.isEmpty else {
        return ["message": "No silence to remove", "data": ["removed": [], "detection": analysis.detection.json]]
    }
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
    // Timeline frames are those before any cut; source seconds follow the clip's speed.
    let removed: [[String: Any]] = cuts.sorted { $0.1 - $0.0 > $1.1 - $1.0 }.map { start, end in
        let source = { (frame: Int) in
            hundredths(analysis.sourceStart + Double(frame - analysis.at) / analysis.projectFPS * analysis.speed)
        }
        return [
            "start": start, "end": end, "seconds": hundredths(Double(end - start) / analysis.projectFPS),
            "sourceStart": source(start), "sourceEnd": source(end),
        ]
    }
    var result: [String: Any] = [
        "label": "Remove silences", "baseRev": analysis.revision as Any, "operations": operations,
        "message": String(format: "Removed %d silences (%.1fs, longest %.1fs)", cuts.count, seconds,
                          removed.first?["seconds"] as? Double ?? 0),
        "data": ["removed": removed, "seconds": hundredths(seconds), "detection": analysis.detection.json],
        "pluginData": ["lastRun": [
            "item": analysis.itemID, "removed": cuts.count, "thresholdDb": analysis.thresholdDb,
            "method": analysis.detection.method,
        ]],
    ]
    if let keep { result["ui"] = ["select": keep, "seek": analysis.at] }
    return result
}

/// Writes one JSON line to BashCut.
func send(_ object: [String: Any]) {
    guard let data = try? JSONSerialization.data(withJSONObject: object) else { return }
    FileHandle.standardOutput.write(data + Data([0x0A]))
}

/// Reads one JSON line from BashCut; nil at the end of input.
func receive() -> [String: Any]? {
    while let line = readLine(strippingNewline: true) {
        if let object = (try? JSONSerialization.jsonObject(with: Data(line.utf8))) as? [String: Any] { return object }
    }
    return nil
}

/// The session host channel of one request (API 8): runs BashCut commands while the request is open. Requests that
/// arrive meanwhile wait in `queued`.
final class Host {
    let requestID: Any
    var queued: [[String: Any]] = []
    var cancelled = false
    private var next = 0

    init(requestID: Any) { self.requestID = requestID }

    func call(_ method: String, _ params: [String: Any]) throws -> [String: Any] {
        next += 1
        let callID = "c\(next)"
        send(["type": "call", "id": requestID, "callId": callID, "method": method, "params": params])
        while let message = receive() {
            switch message["type"] as? String {
            case "callResult" where message["callId"] as? String == callID:
                if let error = message["error"] as? [String: Any] {
                    throw Failure(message: error["message"] as? String ?? "\(method) failed")
                }
                return message["result"] as? [String: Any] ?? [:]
            case "cancel" where "\(message["id"] ?? "")" == "\(requestID)":
                cancelled = true
                throw Failure(message: "cancelled")
            case "shutdown": exit(0)
            case "request": queued.append(message)
            default: continue
            }
        }
        exit(0)
    }
}

func handle(_ request: [String: Any], host: Host?) -> [String: Any] {
    let id = request["id"] ?? ""
    do {
        guard request["method"] as? String == "plugin.action" else {
            return ["id": id, "error": ["code": "unknown_method", "message": "\(request["method"] ?? "")"]]
        }
        let params = request["params"] as? [String: Any] ?? [:]
        switch params["action"] as? String {
        case "bashcut.silence-markers.mark": return ["id": id, "result": try mark(params, host: host)]
        case "bashcut.silence-markers.remove": return ["id": id, "result": try remove(params, host: host)]
        default: throw Failure(message: "unknown action")
        }
    } catch let failure as Failure {
        return ["id": id, "error": ["code": "failed", "message": failure.message]]
    } catch {
        return ["id": id, "error": ["code": "failed", "message": error.localizedDescription]]
    }
}

if CommandLine.arguments.dropFirst().first == "session" {
    var pending: [[String: Any]] = []
    while let message = pending.isEmpty ? receive() : pending.removeFirst() {
        switch message["type"] as? String {
        case "hello": send(["type": "hello", "apiVersion": 8])
        case "shutdown": exit(0)
        case "request":
            // Only API 8 hosts give plugin actions a host channel.
            let version = number(message["apiVersion"]) ?? 0
            let host = version >= 8 ? Host(requestID: message["id"] ?? "") : nil
            let response = handle(message, host: host)
            if host?.cancelled != true { send(response) }
            pending += host?.queued ?? []
        default: continue
        }
    }
} else {
    send(handle(receive() ?? [:], host: nil))
}
