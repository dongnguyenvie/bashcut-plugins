// Covering subtitles burned into the picture, so new captions read clearly.
//
// For each video on the Main layer, BashCut's on-screen text reader (`media.ocr`, Apple Vision by default) looks at
// one picture a second over the first seconds of its first clip. Lines near the horizontal centre whose text changes
// from picture to picture are subtitles; text that stays the same (a logo, a sign, a channel name) is not. Their
// boxes give the subtitle area (tight: a quarter line above and below) and line height. Then, for each clip:
// - blur (auto, when BashCut has host feature clip.blur): a copy of the clip cropped to that area and blurred, on a
//   "Subtitle cover" layer;
// - box (auto on an older BashCut): a rounded opaque box over the area;
// - band: a full-width opaque band;
// - zoom: the clip is zoomed (at most 1.2x) and moved down just enough that the area leaves the bottom of the frame.
// The captions move onto the covered area.
import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

/// One line of on-screen text in one sampled picture; the box is a share of the upright picture from the top left.
struct SeenText {
    let seconds: Double
    let x: Double
    let y: Double
    let width: Double
    let height: Double
    let string: String
}

/// Subtitles found in a video: their area as a share of the picture, the usual line height and how often they show.
struct Subtitles {
    let top: Double
    let bottom: Double
    let left: Double
    let right: Double
    let lineHeight: Double
    let lines: Int
    let shownShare: Double
    let examples: [String]
    let fixedText: [String]
    /// The subtitle lines read in each picture (empty when it showed none), for covers that follow each subtitle.
    var pictures: [(seconds: Double, lines: [SeenText])] = []

    var json: JSON {
        [
            "box": [round3(left), round3(top), round3(right - left), round3(bottom - top)], "lineHeight": round3(lineHeight),
            "lines": lines, "shownShare": round3(shownShare), "examples": examples, "fixedText": fixedText,
        ]
    }
}

func round3(_ value: Double) -> Double { (value * 1000).rounded() / 1000 }

/// The subtitles in the sampled pictures, or nil (with the fixed text seen) when there are none.
func findSubtitles(_ frames: [(seconds: Double, texts: [SeenText])]) -> (Subtitles?, fixed: [String], fixedBoxes: [SeenText]) {
    let pictures = max(1, frames.count)
    func key(_ string: String) -> String {
        String(string.lowercased().unicodeScalars.filter { CharacterSet.alphanumerics.contains($0) }.map(Character.init))
    }
    // Text in most pictures at the same place is part of the picture (a logo, a sign), not a subtitle.
    var seen: [String: Int] = [:]
    for frame in frames {
        for text in Set(frame.texts.map { key($0.string) }) where !text.isEmpty { seen[text, default: 0] += 1 }
    }
    let fixed = Set(seen.filter { frames.count >= 4 && Double($0.value) >= Double(pictures) * 0.6 }.keys)
    let fixedText = frames.flatMap(\.texts).filter { fixed.contains(key($0.string)) }.map(\.string)
    let fixedList = Array(Set(fixedText)).sorted().prefix(8).map { String($0.prefix(60)) }
    // Each fixed text's usual box (the median of where it was read), for covering a logo or channel name.
    let fixedBoxes: [SeenText] = fixed.sorted().prefix(8).compactMap { name in
        let boxes = frames.flatMap(\.texts).filter { key($0.string) == name }
        guard !boxes.isEmpty else { return nil }
        func median(_ values: [Double]) -> Double { values.sorted()[values.count / 2] }
        return SeenText(
            seconds: 0, x: median(boxes.map(\.x)), y: median(boxes.map(\.y)), width: median(boxes.map(\.width)),
            height: median(boxes.map(\.height)), string: boxes[0].string)
    }

    // Subtitles sit centred, low (or, rarely, high) in the picture, one to three lines.
    let candidates = frames.map { frame in
        frame.texts.filter { text in
            let centre = text.x + text.width / 2
            let middle = text.y + text.height / 2
            return !fixed.contains(key(text.string)) && key(text.string).count >= 2 && abs(centre - 0.5) <= 0.15
                && text.height <= 0.15 && text.width >= 0.03 && (middle >= 0.55 || middle <= 0.3)
        }
    }
    // The bottom or the top, whichever has more.
    let low = candidates.map { $0.filter { $0.y + $0.height / 2 >= 0.55 } }
    let high = candidates.map { $0.filter { $0.y + $0.height / 2 <= 0.3 } }
    let zone = low.filter { !$0.isEmpty }.count >= high.filter { !$0.isEmpty }.count ? low : high
    let shown = zone.filter { !$0.isEmpty }.count
    let distinct = Set(zone.flatMap { $0.map { key($0.string) } }).count
    guard shown >= max(2, Int((Double(pictures) * 0.15).rounded(.up))), distinct >= 2 else { return (nil, fixedList, fixedBoxes) }

    let lines = zone.flatMap { $0 }
    func percentile(_ values: [Double], _ share: Double) -> Double {
        let sorted = values.sorted()
        return sorted[min(sorted.count - 1, max(0, Int((Double(sorted.count - 1) * share).rounded())))]
    }
    var examples: [String] = []
    for frame in zone {
        let text = frame.map(\.string).joined(separator: " ")
        if !text.isEmpty, !examples.contains(text) { examples.append(String(text.prefix(80))) }
        if examples.count == 3 { break }
    }
    return (Subtitles(
        top: percentile(lines.map(\.y), 0.05), bottom: percentile(lines.map { $0.y + $0.height }, 0.95),
        left: percentile(lines.map(\.x), 0.05), right: percentile(lines.map { $0.x + $0.width }, 0.95),
        lineHeight: percentile(lines.map(\.height), 0.5), lines: zone.map(\.count).max() ?? 1,
        shownShare: Double(shown) / Double(pictures), examples: examples, fixedText: fixedList,
        pictures: zip(frames, zone).map { (seconds: $0.0.seconds, lines: $0.1) }), fixedList, fixedBoxes)
}

/// One subtitle on screen: from `start` to `end` (source seconds) inside `box` (left, top, right, bottom as shares of
/// the picture, the union of its lines in every picture it was read in).
struct SubtitleSpan: Equatable {
    var start: Double
    var end: Double
    var box: (left: Double, top: Double, right: Double, bottom: Double)

    static func == (a: SubtitleSpan, b: SubtitleSpan) -> Bool {
        a.start == b.start && a.end == b.end && a.box == b.box
    }
}

/// The subtitles one after another, from pictures read every `step` seconds: pictures in a row with the same text
/// (allowing the text reader's slips) make one span. A span reaches a whole `step` past its first and last picture,
/// since the subtitle may change anywhere between two pictures; spans that meet split the time between them.
func subtitleSpans(_ subtitles: Subtitles, step: Double) -> [SubtitleSpan] {
    func key(_ lines: [SeenText]) -> String {
        String(lines.map(\.string).joined().lowercased().unicodeScalars
            .filter { CharacterSet.alphanumerics.contains($0) }.map(Character.init))
    }
    func similar(_ a: String, _ b: String) -> Bool {
        guard !a.isEmpty, !b.isEmpty else { return false }
        if a == b { return true }
        func pairs(_ text: String) -> Set<String> {
            let characters = Array(text)
            return Set(zip(characters, characters.dropFirst()).map { "\($0)\($1)" })
        }
        let left = pairs(a), right = pairs(b)
        return Double(left.intersection(right).count) / Double(max(1, left.union(right).count)) >= 0.6
    }
    var spans: [SubtitleSpan] = []
    var lastKey = ""
    var lastSeconds = -Double.infinity
    for picture in subtitles.pictures {
        guard !picture.lines.isEmpty else {
            lastKey = ""
            continue
        }
        let text = key(picture.lines)
        let box = (
            left: picture.lines.map(\.x).min() ?? 0, top: picture.lines.map(\.y).min() ?? 0,
            right: picture.lines.map { $0.x + $0.width }.max() ?? 1, bottom: picture.lines.map { $0.y + $0.height }.max() ?? 1)
        if similar(text, lastKey), picture.seconds - lastSeconds <= step * 1.5, var span = spans.popLast() {
            span.end = picture.seconds + step
            span.box = (min(span.box.left, box.left), min(span.box.top, box.top),
                        max(span.box.right, box.right), max(span.box.bottom, box.bottom))
            spans.append(span)
        } else {
            let start = picture.seconds - step
            if var previous = spans.popLast() {
                // Two spans that overlap meet halfway between their pictures.
                if previous.end > start {
                    let middle = (previous.end - step + picture.seconds) / 2
                    previous.end = middle
                    spans.append(previous)
                    spans.append(SubtitleSpan(start: middle, end: picture.seconds + step, box: box))
                } else {
                    spans.append(previous)
                    spans.append(SubtitleSpan(start: start, end: picture.seconds + step, box: box))
                }
            } else {
                spans.append(SubtitleSpan(start: max(0, start), end: picture.seconds + step, box: box))
            }
        }
        lastKey = text
        lastSeconds = picture.seconds
    }
    return spans
}

/// Where a clip's picture lands on the canvas, in canvas pixels.
struct Placement {
    let left: Double
    let top: Double
    let width: Double
    let height: Double
    let canvasWidth: Double
    let canvasHeight: Double
    let transform: JSON

    var fillsFrame: Bool {
        left <= 0.5 && top <= 0.5 && left + width >= canvasWidth - 0.5 && top + height >= canvasHeight - 0.5
    }
    var plain: Bool {
        ((transform["zoom"] as? NSNumber)?.doubleValue ?? 1) == 1 && ((transform["pan"] as? NSNumber)?.doubleValue ?? 0) == 0
            && ((transform["tilt"] as? NSNumber)?.doubleValue ?? 0) == 0
    }

    /// The zoom and tilt (output pixels, up) that put picture share `cut` (from the top) at the bottom of the frame,
    /// so everything below it leaves the frame, zooming only as much as needed: a picture already taller than the
    /// frame just moves down. Nil when the picture does not fill the frame or already has a zoom, pan or tilt.
    func zoomOut(below cut: Double) -> (zoom: Double, tilt: Double)? {
        guard fillsFrame, plain, cut > 0.5 else { return nil }
        let zoom = max(1, canvasHeight / (cut * height))
        let shownHeight = height * zoom
        let shownTop = canvasHeight - cut * shownHeight
        return (zoom, (canvasHeight / 2 - (shownTop + shownHeight / 2)).rounded())
    }
}

func cover(_ raw: JSON, host: Host) throws -> JSON {
    let request = ActionRequest(raw)
    let mode = request.string("mode", "auto")
    let seconds = min(120, max(5, request.number("seconds", 30)))
    let opacity = min(1, max(0.5, request.number("opacity", 1)))
    let moveCaptions = request.bool("moveCaptions", true)
    let coverLogos = request.bool("coverLogos", false)
    let extraAbove = min(4, max(0, request.number("extraLinesAbove", 0)))
    // follow: a cover per subtitle, sized to its lines (the whole clip is read); fixed: one area for the whole clip.
    let follow = request.string("fit", "follow") == "follow"
    guard let outputDirectory = request.outputDirectory else { throw PluginError("bad_request", "outputDirectory is required") }

    let timeline = try host.call("timeline.get") as? JSON ?? [:]
    let tracks = timeline["tracks"] as? [JSON] ?? []
    let format = timeline["format"] as? JSON ?? [:]
    let canvasWidth = (format["width"] as? NSNumber)?.doubleValue ?? 1080
    let canvasHeight = (format["height"] as? NSNumber)?.doubleValue ?? 1920
    let rate = (format["fps"] as? [NSNumber])?.map(\.doubleValue) ?? [30, 1]
    let fps = rate.count == 2 && rate[1] > 0 ? rate[0] / rate[1] : 30
    let scales = timeline["scale"] as? JSON ?? [:]
    let videoMedia = Set((timeline["media"] as? [JSON] ?? []).filter { $0["kind"] as? String == "video" }.compactMap { $0["id"] as? String })
    let clips = tracks.filter { $0["role"] as? String == "main" }.flatMap { $0["items"] as? [JSON] ?? [] }
        .filter { videoMedia.contains($0["media"] as? String ?? "") }
    guard !clips.isEmpty else { throw PluginError("no_video", "There is no video on the Main layer to look at") }

    // Look at each video once: the first seconds of its first clip, or (follow) all of its clips every half second.
    var found: [String: Subtitles] = [:]
    var steps: [String: Double] = [:]
    var logos: [String: [SeenText]] = [:]
    var report: [JSON] = []
    var order: [String] = []
    for clip in clips where !order.contains(clip["media"] as? String ?? "") { order.append(clip["media"] as? String ?? "") }
    for (index, media) in order.prefix(12).enumerated() {
        host.progress(Double(index) / Double(min(order.count, 12)), "Looking for subtitles in video \(index + 1) of \(min(order.count, 12))")
        let used = clips.filter { $0["media"] as? String == media }
        guard let first = used.first else { continue }
        var from = Double(first["in"] as? Int ?? 0) / fps
        var length = min(seconds, Double(first["dur"] as? Int ?? 0) / fps)
        var step = length > 20 ? 1.0 : 0.5
        if follow {
            from = used.map { Double($0["in"] as? Int ?? 0) / fps }.min() ?? from
            let to = used.map { Double(($0["in"] as? Int ?? 0) + ($0["dur"] as? Int ?? 0)) / fps }.max() ?? from + length
            length = max(1, to - from)
            step = max(0.5, (length / 3000 * 10).rounded(.up) / 10)
        }
        steps[media] = step
        let started = try host.call("media.ocr", [
            "media": media, "from": from, "to": from + max(1, length), "step": step,
        ])
        let result = try host.waitJob(started, timeout: 900, interval: 0.5) as? JSON ?? [:]
        let frames = (result["frames"] as? [JSON] ?? []).map { frame in
            let at = (frame["seconds"] as? NSNumber)?.doubleValue ?? 0
            let texts = (frame["text"] as? [JSON] ?? []).compactMap { text -> SeenText? in
                guard let box = (text["box"] as? [NSNumber])?.map(\.doubleValue), box.count == 4,
                    let string = text["string"] as? String
                else { return nil }
                return SeenText(seconds: at, x: box[0], y: box[1], width: box[2], height: box[3], string: string)
            }
            return (seconds: at, texts: texts)
        }
        let (subtitles, fixed, fixedBoxes) = findSubtitles(frames)
        var entry: JSON = ["media": media, "pictures": frames.count, "subtitles": subtitles?.json ?? NSNull()]
        if !fixed.isEmpty { entry["fixedText"] = fixed }
        report.append(entry)
        if let subtitles { found[media] = subtitles }
        if coverLogos, !fixedBoxes.isEmpty { logos[media] = fixedBoxes }
    }
    host.progress(0.9, "Covering")

    let detection: JSON = ["at": ISO8601DateFormatter().string(from: Date()), "videos": report]
    let earlier = (request.pluginData["cover"] as? JSON)?["items"] as? [String] ?? []
    let existing = Set(tracks.flatMap { $0["items"] as? [JSON] ?? [] }.compactMap { $0["id"] as? String })
    guard !found.isEmpty || !logos.isEmpty, mode != "detect" else {
        let message = found.isEmpty
            ? "No burned-in subtitles found in the first \(Int(seconds)) s of \(order.count) video(s)"
            : "Found burned-in subtitles in \(found.count) of \(order.count) video(s); nothing changed (detect only)"
        return [
            "message": message, "pluginData": mergedPluginData(request, "detect", detection),
            "data": ["videos": report, "covered": 0],
        ]
    }

    // How to hide them: a blurred copy of the clip cropped to the subtitles (C) where this BashCut can blur a clip,
    // else a rounded box hugging them (B); a full-width band and a zoom are there when asked for.
    let blurAvailable = hostFeatures.contains("clip.blur")
    var style = mode == "auto" ? (blurAvailable ? "blur" : "box") : mode
    var note: String?
    if style == "blur", !blurAvailable {
        style = "box"
        note = "this BashCut cannot blur a clip (update it), so a box covers them"
    }
    let blur = min(0.2, max(0.01, request.number("blur", 0.05)))
    let tint = request.string("tint", "natural")
    // mosaic: square cells with soft edges, like the usual pixelated subtitle (needs clip.mosaic); smooth: a blur.
    let mosaic = request.string("look", "mosaic") == "mosaic" && hostFeatures.contains("clip.mosaic")

    // Plan each clip: the area over its subtitles (tight: what the text reader saw plus a little), and how it is covered.
    struct Plan {
        let clip: JSON
        /// Where this cover sits (timeline frames) and the source frame it starts at.
        let at: Int
        let dur: Int
        let sourceIn: Int
        /// The covered area on the canvas, where the captions go.
        let area: CGRect?
        /// Drawn into the cover picture: a full-width band, and rounded boxes (the subtitles in style box, logos).
        let band: CGRect?
        let boxes: [CGRect]
        /// A blurred copy of the clip cropped to the subtitles (style blur).
        let blurCopy: JSON?
    }
    var plans: [Plan] = []
    var zoomOps: [JSON] = []
    var zoomed = 0
    for clip in clips {
        guard let media = clip["media"] as? String, let id = clip["id"] as? String, let scale = scales[id] as? JSON,
            found[media] != nil || logos[media] != nil
        else { continue }
        let placement = place(clip, scale: scale, canvasWidth: canvasWidth, canvasHeight: canvasHeight)
        let canvas = CGRect(x: 0, y: 0, width: canvasWidth, height: canvasHeight)
        func onCanvas(_ x: Double, _ y: Double, _ width: Double, _ height: Double) -> CGRect {
            CGRect(x: placement.left + x * placement.width, y: placement.top + y * placement.height,
                   width: width * placement.width, height: height * placement.height).intersection(canvas).integral
        }
        var boxes = (logos[media] ?? []).map { text in
            let pad = text.height * 0.35
            return onCanvas(text.x - pad, text.y - pad, text.width + 2 * pad, text.height + 2 * pad)
        }.filter { !$0.isEmpty }
        let clipAt = clip["at"] as? Int ?? 0, clipDur = clip["dur"] as? Int ?? 1, clipIn = clip["in"] as? Int ?? 0
        guard let subtitles = found[media] else {
            if !boxes.isEmpty {
                plans.append(Plan(clip: clip, at: clipAt, dur: clipDur, sourceIn: 0, area: nil, band: nil, boxes: boxes, blurCopy: nil))
            }
            continue
        }
        // A quarter line above and below, half a line at the sides (as picture shares): text right at a blurred
        // crop's edge stays readable, since the blur repeats the edge.
        // A mosaic's edges fade out, so its area reaches a little further to keep the text under the opaque middle.
        let pad = subtitles.lineHeight * (mosaic && style == "blur" ? 0.55 : 0.25)
        let side = subtitles.lineHeight * (mosaic && style == "blur" ? 0.8 : 0.5) * placement.height / max(1, placement.width)
        // The picture's height as a share of its short side, to size mosaic cells from the line height.
        let heightShare = placement.height / max(1, min(placement.width, placement.height))
        let above = pad + extraAbove * subtitles.lineHeight * 1.3
        func padded(_ box: (left: Double, top: Double, right: Double, bottom: Double)) -> (Double, Double, Double, Double) {
            // At least 6 % each way (a crop keeps at least 5 %): a one-word subtitle grows around its centre.
            func span(_ low: Double, _ high: Double) -> (Double, Double) {
                guard high - low < 0.06 else { return (max(0, low), min(1, high)) }
                let centre = min(0.97, max(0.03, (low + high) / 2))
                return (centre - 0.03, centre + 0.03)
            }
            let (left, right) = span(box.left - side, box.right + side)
            let (top, bottom) = span(box.top - above, box.bottom + pad)
            return (left, top, right, bottom)
        }
        let whole = padded((subtitles.left, subtitles.top, subtitles.right, subtitles.bottom))
        if style == "zoom", boxes.isEmpty, (subtitles.top + subtitles.bottom) / 2 >= 0.5,
            let zoom = placement.zoomOut(below: whole.1), zoom.zoom <= 1.2
        {
            var transform = placement.transform
            transform["zoom"] = (zoom.zoom * 1000).rounded() / 1000
            transform["tilt"] = zoom.tilt
            zoomOps.append(["op": "setProperties", "item": id, "patch": ["transform": transform]])
            zoomed += 1
            continue
        }
        let captionArea = style == "band" || style == "zoom"
            ? onCanvas(0, whole.1, 1, whole.3 - whole.1) : onCanvas(whole.0, whole.1, whole.2 - whole.0, whole.3 - whole.1)
        // Pieces: each subtitle span inside the clip (a speed change keeps one piece for the whole clip).
        var pieces: [(at: Int, dur: Int, offset: Int, box: (Double, Double, Double, Double))] = []
        let plainSpeed = ((clip["speed"] as? NSNumber)?.doubleValue ?? 1) == 1 && clip["speedCurve"] == nil && clip["reverse"] == nil
        if follow, plainSpeed, style != "band" {
            let clipStart = Double(clipIn) / fps, clipEnd = Double(clipIn + clipDur) / fps
            for span in subtitleSpans(subtitles, step: steps[media] ?? 0.5) where span.end > clipStart && span.start < clipEnd {
                let first = Int((max(span.start, clipStart) * fps).rounded()) - clipIn
                let last = Int((min(span.end, clipEnd) * fps).rounded()) - clipIn
                guard last > first else { continue }
                pieces.append((clipAt + first, last - first, first, padded(span.box)))
            }
        } else {
            pieces.append((clipAt, clipDur, 0, whole))
        }
        if pieces.count > 1, !boxes.isEmpty {
            plans.append(Plan(clip: clip, at: clipAt, dur: clipDur, sourceIn: 0, area: nil, band: nil, boxes: boxes, blurCopy: nil))
            boxes = []
        }
        for (index, piece) in pieces.enumerated() {
            let (left, top, right, bottom) = piece.box
            var band: CGRect?, blurCopy: JSON?
            var pieceBoxes = index == 0 ? boxes : []
            switch style {
            case "band", "zoom": band = onCanvas(0, top, 1, bottom - top)
            case "blur":
                var copy = blurredCopy(of: clip, crop: (left, top, right, bottom), blur: blur, tint: tint)
                if mosaic {
                    // Cells about half a line tall, softened a little, edges fading over a third of the area.
                    let cell = min(0.1, max(0.008, subtitles.lineHeight * 0.5 * heightShare))
                    copy["pixelate"] = round3(cell)
                    copy["blur"] = round3(cell * 0.35)
                    copy["feather"] = 0.35
                    var crop = copy["crop"] as? JSON ?? [:]
                    crop["radius"] = nil
                    copy["crop"] = crop
                }
                copy["at"] = piece.at
                copy["dur"] = piece.dur
                copy["in"] = clipIn + piece.offset
                blurCopy = copy
            default: pieceBoxes.insert(onCanvas(left, top, right - left, bottom - top), at: 0)
            }
            plans.append(Plan(
                clip: clip, at: piece.at, dur: piece.dur, sourceIn: piece.offset,
                area: captionArea.isEmpty ? nil : captionArea, band: band, boxes: pieceBoxes, blurCopy: blurCopy))
        }
    }

    // One cover picture per distinct set of rectangles, imported once.
    var coverMedia: [String: String] = [:]
    var written: [String] = []
    func coverKey(_ band: CGRect?, _ boxes: [CGRect]) -> String {
        ([band].compactMap { $0 } + boxes).map { "\(Int($0.minX)),\(Int($0.minY)),\(Int($0.width)),\(Int($0.height))" }
            .joined(separator: ";")
    }
    for plan in plans where plan.band != nil || !plan.boxes.isEmpty {
        let key = coverKey(plan.band, plan.boxes)
        guard coverMedia[key] == nil else { continue }
        let name = "subtitle-cover-\(coverMedia.count + 1)-\(UUID().uuidString.prefix(6).lowercased()).png"
        let path = (outputDirectory as NSString).appendingPathComponent(name)
        try drawCover(band: plan.band, boxes: plan.boxes, canvasWidth: Int(canvasWidth), canvasHeight: Int(canvasHeight),
                      opacity: opacity, to: path)
        written.append(path)
        let imported = try host.call("media.import", ["path": path, "kind": "image", "origin": "built-in", "baseRev": "last"]) as? JSON ?? [:]
        guard let media = imported["media"] as? String ?? (imported["files"] as? [JSON])?.first?["media"] as? String else {
            throw PluginError("import_failed", "BashCut did not import the cover picture")
        }
        coverMedia[key] = media
    }
    // An import changed the project: plan the edit against the new revision.
    let fresh = written.isEmpty ? timeline : (try host.call("timeline.get") as? JSON ?? [:])
    guard let rev = fresh["rev"] as? Int else { throw PluginError("bad_answer", "timeline.get returned no revision") }
    let freshTracks = fresh["tracks"] as? [JSON] ?? tracks

    // Covers go on layers of their own, above the other video layers and below the text layers (captions, titles):
    // "Subtitle cover", and "Subtitle cover 2" for the picture when a clip has both a blurred copy and a picture.
    var operations: [JSON] = earlier.filter(existing.contains).map { ["op": "delete", "item": $0] }
    let trackIDs = freshTracks.compactMap { $0["id"] as? String }
    let firstText = freshTracks.firstIndex { $0["kind"] as? String == "text" }
    func layer(_ id: String, _ name: String) -> String {
        let added = operations.filter { $0["op"] as? String == "addTrack" }.count
        if let index = trackIDs.firstIndex(of: id) {
            // An earlier run's layer above the text layers moves below them.
            if let firstText, index > firstText, !operations.contains(where: { $0["track"] as? String == id && $0["op"] as? String == "moveTrack" }) {
                operations.append(["op": "moveTrack", "track": id, "toIndex": firstText])
            }
        } else if !operations.contains(where: { ($0["track"] as? JSON)?["id"] as? String == id }) {
            var op: JSON = ["op": "addTrack", "track": ["id": id, "kind": "video", "name": name, "role": "overlay"]]
            if let firstText { op["atIndex"] = firstText + added }
            operations.append(op)
        }
        return id
    }
    var coverItems: [String] = []
    for plan in plans {
        let at = plan.at, dur = plan.dur
        if var copy = plan.blurCopy {
            let id = "subtitle-cover-\(UUID().uuidString.prefix(8).lowercased())"
            copy["id"] = id
            operations.append(["op": "insert", "track": layer("subtitle-cover", "Subtitle cover"), "item": copy])
            coverItems.append(id)
        }
        if plan.band != nil || !plan.boxes.isEmpty, let media = coverMedia[coverKey(plan.band, plan.boxes)] {
            let id = "subtitle-cover-\(UUID().uuidString.prefix(8).lowercased())"
            let track = plan.blurCopy == nil
                ? layer("subtitle-cover", "Subtitle cover") : layer("subtitle-cover-2", "Subtitle cover 2")
            operations.append(["op": "insert", "track": track, "item": ["id": id, "media": media, "at": at, "dur": dur, "in": 0] as JSON])
            coverItems.append(id)
        }
    }
    operations += zoomOps

    // Captions over the covered clips go onto the covered area.
    var moved = 0
    let areas = plans.compactMap { plan in plan.area.map { (clip: plan.clip, rect: $0) } }
    if moveCaptions, !areas.isEmpty {
        for item in captionItems(freshTracks) {
            let at = item["at"] as? Int ?? 0
            guard let id = item["id"] as? String,
                let area = areas.first(where: { at >= ($0.clip["at"] as? Int ?? 0) && at < ($0.clip["at"] as? Int ?? 0) + ($0.clip["dur"] as? Int ?? 0) })
            else { continue }
            var style = item["textStyle"] as? JSON ?? [:]
            // Baseline (from the bottom) two fifths of the way up the area: one line sits about its middle, two fill it.
            style["positionY"] = round3((canvasHeight - area.rect.maxY + area.rect.height * 0.4) / canvasHeight)
            operations.append(["op": "setProperties", "item": id, "patch": ["textStyle": style]])
            moved += 1
        }
    }

    var message = found.isEmpty
        ? "No burned-in subtitles in \(order.count) video(s)"
        : "Covered burned-in subtitles in \(found.count) of \(order.count) video(s)"
    var how: [String] = []
    let covered = Set(plans.filter { $0.area != nil }.compactMap { $0.clip["id"] as? String }).count
    if covered > 0 {
        let verb = ["blur": "blurred on", "box": "a box over them on", "band": "a band over them on"][style] ?? "covered on"
        how.append("\(verb) \(covered) clip(s)")
    }
    if zoomed > 0 { how.append("zoomed \(zoomed) clip(s)") }
    let logoClips = plans.filter { $0.boxes.count > ($0.area != nil && style == "box" ? 1 : 0) }.count
    if logoClips > 0 { how.append("fixed text or logos covered on \(logoClips) clip(s)") }
    let pieces = plans.filter { $0.area != nil }.count
    if follow, pieces > covered { how.append("\(pieces) covers following the subtitles") }
    if !how.isEmpty { message += ": " + how.joined(separator: ", ") }
    if moved > 0 { message += "; moved \(moved) caption(s) onto the cover" }
    if let note { message += " (\(note))" }
    var stored = detection
    stored["items"] = coverItems
    stored["style"] = style
    return [
        "label": "Cover burned-in subtitles",
        "baseRev": rev,
        "operations": operations,
        "pluginData": mergedPluginData(request, "cover", stored),
        "files": written,
        "message": message,
        "data": [
            "videos": report, "style": style, "covered": covered + zoomed, "items": coverItems, "zoomed": zoomed,
            "captionsMoved": moved,
        ],
    ]
}

/// A copy of `clip` (same media, time, speed and framing) cropped to `crop` (left, top, right, bottom as shares of
/// the picture), blurred by `blur` (a share of the picture's short side) and tinted: `natural` keeps the picture's own
/// colours, `dark` darkens it so white captions stand out, `light` makes it a pale frosted glass; muted, since the
/// clip below already plays its sound.
func blurredCopy(of clip: JSON, crop: (Double, Double, Double, Double), blur: Double, tint: String = "natural") -> JSON {
    var copy: JSON = [:]
    for key in ["media", "at", "dur", "in", "speed", "speedCurve", "reverse", "transform", "fill", "keyframes"] {
        if let value = clip[key] { copy[key] = value }
    }
    copy["crop"] = [
        "left": round3(min(0.95, crop.0)), "top": round3(min(0.95, crop.1)),
        "right": round3(min(0.95, 1 - crop.2)), "bottom": round3(min(0.95, 1 - crop.3)), "radius": 0.02,
    ]
    copy["blur"] = round3(blur)
    switch tint {
    case "dark": copy["color"] = ["exposure": -0.6]
    case "light": copy["color"] = ["exposure": 0.9, "saturation": 0.5]
    default: break
    }
    copy["muted"] = true
    return copy
}

/// Where the clip's picture is on the canvas: its fitted or filled size (timeline.get `scale`) times its zoom, moved
/// by pan (right) and tilt (up). Keyframed motion is not followed.
func place(_ clip: JSON, scale: JSON, canvasWidth: Double, canvasHeight: Double) -> Placement {
    let transform = clip["transform"] as? JSON ?? [:]
    let zoom = (transform["zoom"] as? NSNumber)?.doubleValue ?? 1
    let pan = (transform["pan"] as? NSNumber)?.doubleValue ?? 0
    let tilt = (transform["tilt"] as? NSNumber)?.doubleValue ?? 0
    let base = (scale["baseScale"] as? NSNumber)?.doubleValue ?? 1
    let width = ((scale["sourceWidth"] as? NSNumber)?.doubleValue ?? canvasWidth) * base * zoom
    let height = ((scale["sourceHeight"] as? NSNumber)?.doubleValue ?? canvasHeight) * base * zoom
    return Placement(
        left: canvasWidth / 2 + pan - width / 2, top: canvasHeight / 2 - tilt - height / 2, width: width, height: height,
        canvasWidth: canvasWidth, canvasHeight: canvasHeight, transform: transform)
}

/// A transparent canvas-sized PNG with a dark band over `band` and a rounded dark box over each of `boxes` (canvas
/// pixels from the top left). The band's top and bottom edges fade over a few pixels so it does not look cut out.
func drawCover(band rect: CGRect?, boxes: [CGRect], canvasWidth: Int, canvasHeight: Int, opacity: Double, to path: String) throws {
    guard let context = CGContext(
        data: nil, width: canvasWidth, height: canvasHeight, bitsPerComponent: 8, bytesPerRow: 0,
        space: CGColorSpace(name: CGColorSpace.sRGB) ?? CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)
    else { throw PluginError("draw_failed", "Cannot draw a \(canvasWidth)×\(canvasHeight) picture") }
    // CoreGraphics counts from the bottom.
    func flipped(_ rect: CGRect) -> CGRect {
        CGRect(x: rect.minX, y: Double(canvasHeight) - rect.maxY, width: rect.width, height: rect.height)
    }
    if let rect {
        let band = flipped(rect)
        let steps = Int(max(2, min(rect.height * 0.12, 24)))
        for step in 0..<steps {
            let alpha = opacity * Double(step + 1) / Double(steps + 1)
            context.setFillColor(CGColor(srgbRed: 0, green: 0, blue: 0, alpha: alpha))
            context.fill(CGRect(x: band.minX, y: band.minY + Double(step), width: band.width, height: 1))
            context.fill(CGRect(x: band.minX, y: band.maxY - Double(step) - 1, width: band.width, height: 1))
        }
        context.setFillColor(CGColor(srgbRed: 0, green: 0, blue: 0, alpha: opacity))
        context.fill(band.insetBy(dx: 0, dy: Double(steps)))
    }
    context.setFillColor(CGColor(srgbRed: 0, green: 0, blue: 0, alpha: opacity))
    for box in boxes.map(flipped) {
        let radius = min(box.width, box.height) * 0.25
        context.addPath(CGPath(roundedRect: box, cornerWidth: radius, cornerHeight: radius, transform: nil))
        context.fillPath()
    }
    guard let image = context.makeImage(),
        let destination = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)
    else { throw PluginError("write_failed", "Cannot write \(path)") }
    CGImageDestinationAddImage(destination, image, nil)
    guard CGImageDestinationFinalize(destination) else { throw PluginError("write_failed", "Cannot write \(path)") }
}
