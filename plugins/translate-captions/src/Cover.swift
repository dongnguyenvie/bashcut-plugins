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
        shownShare: Double(shown) / Double(pictures), examples: examples, fixedText: fixedList), fixedList, fixedBoxes)
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

    // Look at each video once, from its first clip.
    var found: [String: Subtitles] = [:]
    var logos: [String: [SeenText]] = [:]
    var report: [JSON] = []
    var order: [String] = []
    for clip in clips where !order.contains(clip["media"] as? String ?? "") { order.append(clip["media"] as? String ?? "") }
    for (index, media) in order.prefix(12).enumerated() {
        host.progress(Double(index) / Double(min(order.count, 12)), "Looking for subtitles in video \(index + 1) of \(min(order.count, 12))")
        guard let first = clips.first(where: { $0["media"] as? String == media }) else { continue }
        let from = Double(first["in"] as? Int ?? 0) / fps
        let length = min(seconds, Double(first["dur"] as? Int ?? 0) / fps)
        let started = try host.call("media.ocr", [
            "media": media, "from": from, "to": from + max(1, length), "step": length > 20 ? 1 : 0.5,
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

    // Plan each clip: the area over its subtitles (tight: what the text reader saw plus a little), and how it is covered.
    struct Plan {
        let clip: JSON
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
        var area: CGRect?, band: CGRect?, blurCopy: JSON?
        if let subtitles = found[media] {
            // A quarter line above and below, two thirds of a line at the sides (all as picture shares).
            let pad = subtitles.lineHeight * 0.25
            let side = subtitles.lineHeight * 0.66 * placement.height / max(1, placement.width)
            let above = pad + extraAbove * subtitles.lineHeight * 1.3
            let top = max(0, subtitles.top - above), bottom = min(1, subtitles.bottom + pad)
            let left = max(0, subtitles.left - side), right = min(1, subtitles.right + side)
            if style == "zoom", boxes.isEmpty, (subtitles.top + subtitles.bottom) / 2 >= 0.5,
                let zoom = placement.zoomOut(below: top), zoom.zoom <= 1.2
            {
                var transform = placement.transform
                transform["zoom"] = (zoom.zoom * 1000).rounded() / 1000
                transform["tilt"] = zoom.tilt
                zoomOps.append(["op": "setProperties", "item": id, "patch": ["transform": transform]])
                zoomed += 1
                continue
            }
            switch style {
            case "band", "zoom":
                band = onCanvas(0, top, 1, bottom - top)
                area = band
            case "blur":
                area = onCanvas(left, top, right - left, bottom - top)
                blurCopy = blurredCopy(of: clip, crop: (left, top, right, bottom), blur: blur)
            default:
                let box = onCanvas(left, top, right - left, bottom - top)
                boxes.insert(box, at: 0)
                area = box
            }
        }
        if area?.isEmpty == true { area = nil }
        if band != nil || !boxes.isEmpty || blurCopy != nil {
            plans.append(Plan(clip: clip, area: area, band: band, boxes: boxes, blurCopy: blurCopy))
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

    // Covers go on layers of their own, in front of the other video layers: "Subtitle cover", and "Subtitle cover 2"
    // for the picture when a clip has both a blurred copy and a picture (logos).
    var operations: [JSON] = earlier.filter(existing.contains).map { ["op": "delete", "item": $0] }
    let trackIDs = Set(freshTracks.compactMap { $0["id"] as? String })
    func layer(_ id: String, _ name: String) -> String {
        if !trackIDs.contains(id), !operations.contains(where: { ($0["track"] as? JSON)?["id"] as? String == id }) {
            operations.append(["op": "addTrack", "track": ["id": id, "kind": "video", "name": name, "role": "overlay"]])
        }
        return id
    }
    var coverItems: [String] = []
    for plan in plans {
        let at = plan.clip["at"] as? Int ?? 0, dur = plan.clip["dur"] as? Int ?? 1
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
    let covered = plans.filter { $0.area != nil }.count
    if covered > 0 {
        let verb = ["blur": "blurred on", "box": "a box over them on", "band": "a band over them on"][style] ?? "covered on"
        how.append("\(verb) \(covered) clip(s)")
    }
    if zoomed > 0 { how.append("zoomed \(zoomed) clip(s)") }
    let logoClips = plans.filter { $0.boxes.count > ($0.area != nil && style == "box" ? 1 : 0) }.count
    if logoClips > 0 { how.append("fixed text or logos covered on \(logoClips) clip(s)") }
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
/// the picture), blurred by `blur` (a share of the picture's short side) and a little darker so new captions stand
/// out; muted, since the clip below already plays its sound.
func blurredCopy(of clip: JSON, crop: (Double, Double, Double, Double), blur: Double) -> JSON {
    var copy: JSON = [:]
    for key in ["media", "at", "dur", "in", "speed", "speedCurve", "reverse", "transform", "fill", "keyframes"] {
        if let value = clip[key] { copy[key] = value }
    }
    copy["crop"] = [
        "left": round3(min(0.95, crop.0)), "top": round3(min(0.95, crop.1)),
        "right": round3(min(0.95, 1 - crop.2)), "bottom": round3(min(0.95, 1 - crop.3)), "radius": 0.02,
    ]
    copy["blur"] = round3(blur)
    copy["color"] = ["exposure": -0.6]
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
