#!/usr/bin/env swift
// Draws the pack's PNG and animated GIF stickers (badges, bursts, speech bubbles, arrows, symbols) with Core
// Graphics; nothing is downloaded. Usage:
//   swift plugins/stickers/src/sticker-pack.swift [folder] [--sheet contact.png]
// The folder defaults to plugins/stickers/stickers. The images are committed, so run this after changing the lists
// below and bump the plugin version. Files with the same names are replaced.
import AppKit
import ImageIO
import UniformTypeIdentifiers

// Stickers are drawn in a 512-point square with the origin at its center, y up.
let unit: CGFloat = 512
let space = CGColorSpace(name: CGColorSpace.sRGB)!
typealias Draw = (CGContext) -> Void

func rgb(_ hex: UInt32, _ alpha: CGFloat = 1) -> CGColor {
    CGColor(
        srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255,
        blue: CGFloat(hex & 255) / 255, alpha: alpha)
}
let red = rgb(0xFF3B30), orange = rgb(0xFF9500), yellow = rgb(0xFFCC00), green = rgb(0x34C759)
let blue = rgb(0x007AFF), purple = rgb(0xAF52DE), pink = rgb(0xFF2D55), ink = rgb(0x111111), white = rgb(0xFFFFFF)

// MARK: Paths

func font(_ size: CGFloat) -> NSFont {
    let base = NSFont.systemFont(ofSize: size, weight: .black)
    guard let rounded = base.fontDescriptor.withDesign(.rounded) else { return base }
    return NSFont(descriptor: rounded, size: size) ?? base
}

/// One line of text as an outline centered on the origin.
func linePath(_ string: String) -> CGPath {
    let line = CTLineCreateWithAttributedString(NSAttributedString(string: string, attributes: [.font: font(100)]))
    let path = CGMutablePath()
    for run in CTLineGetGlyphRuns(line) as? [CTRun] ?? [] {
        let attributes = CTRunGetAttributes(run) as NSDictionary
        guard let value = attributes[kCTFontAttributeName as String] else { continue }
        // swiftlint:disable:next force_cast
        let runFont = value as! CTFont
        let count = CTRunGetGlyphCount(run)
        var glyphs = [CGGlyph](repeating: 0, count: count)
        var positions = [CGPoint](repeating: .zero, count: count)
        CTRunGetGlyphs(run, CFRange(), &glyphs)
        CTRunGetPositions(run, CFRange(), &positions)
        for index in 0..<count {
            guard let glyph = CTFontCreatePathForGlyph(runFont, glyphs[index], nil) else { continue }
            path.addPath(glyph, transform: CGAffineTransform(translationX: positions[index].x, y: positions[index].y))
        }
    }
    let bounds = path.boundingBoxOfPath
    var center = CGAffineTransform(translationX: -bounds.midX, y: -bounds.midY)
    return path.copy(using: &center) ?? path
}

/// Text (lines split at "\n") scaled to fit a box, centered on the origin.
func textPath(_ string: String, width: CGFloat, height: CGFloat) -> CGPath {
    let lines = string.split(separator: "\n").map { linePath(String($0)) }
    let tallest = lines.map(\.boundingBoxOfPath.height).max() ?? 1
    let widest = lines.map(\.boundingBoxOfPath.width).max() ?? 1
    let count = CGFloat(lines.count)
    let scale = min(width / widest, height / (tallest * (1 + 1.3 * (count - 1))))
    let step = tallest * scale * 1.3
    let block = CGMutablePath()
    for (index, line) in lines.enumerated() {
        let offset = ((count - 1) / 2 - CGFloat(index)) * step
        block.addPath(line, transform: CGAffineTransform(translationX: 0, y: offset).scaledBy(x: scale, y: scale))
    }
    return block
}

func polygon(_ points: [(CGFloat, CGFloat)]) -> CGPath {
    let path = CGMutablePath()
    path.addLines(between: points.map { CGPoint(x: $0.0, y: $0.1) })
    path.closeSubpath()
    return path
}

func star(points: Int, outer: CGFloat, inner: CGFloat) -> CGPath {
    polygon((0..<points * 2).map { index in
        let radius = index.isMultiple(of: 2) ? outer : inner
        let angle = CGFloat.pi / 2 + CGFloat(index) * .pi / CGFloat(points)
        return (radius * cos(angle), radius * sin(angle))
    })
}

func heartPath() -> CGPath {
    let path = CGMutablePath()
    path.move(to: CGPoint(x: 0, y: -190))
    path.addCurve(to: CGPoint(x: -205, y: 55), control1: CGPoint(x: -70, y: -135), control2: CGPoint(x: -205, y: -60))
    path.addCurve(to: CGPoint(x: 0, y: 105), control1: CGPoint(x: -205, y: 185), control2: CGPoint(x: -45, y: 205))
    path.addCurve(to: CGPoint(x: 205, y: 55), control1: CGPoint(x: 45, y: 205), control2: CGPoint(x: 205, y: 185))
    path.addCurve(to: CGPoint(x: 0, y: -190), control1: CGPoint(x: 205, y: -60), control2: CGPoint(x: 70, y: -135))
    path.closeSubpath()
    return path
}

/// A four-point sparkle with curved sides.
func sparklePath(_ radius: CGFloat) -> CGPath {
    let path = CGMutablePath()
    let tips = [(0, radius), (radius, 0), (0, -radius), (-radius, 0)].map { CGPoint(x: $0.0, y: $0.1) }
    path.move(to: tips[3])
    for tip in tips { path.addQuadCurve(to: tip, control: .zero) }
    path.closeSubpath()
    return path
}

/// A hand-drawn ring: a little more than one turn of an ellipse that spirals inwards. `progress` 0…1 draws part.
func ringPath(progress: CGFloat = 1) -> CGPath {
    let path = CGMutablePath()
    let steps = max(2, Int(120 * progress))
    for step in 0...steps {
        let turn = CGFloat(step) / 120 * 1.1
        let shrink = 1 - 0.07 * turn
        let angle = CGFloat.pi * 0.6 - turn * 2 * .pi
        let point = CGPoint(x: 215 * shrink * cos(angle), y: 140 * shrink * sin(angle))
        if step == 0 { path.move(to: point) } else { path.addLine(to: point) }
    }
    return path
}

func roundedRect(width: CGFloat, height: CGFloat, radius: CGFloat, y: CGFloat = 0) -> CGPath {
    CGPath(
        roundedRect: CGRect(x: -width / 2, y: y - height / 2, width: width, height: height),
        cornerWidth: radius, cornerHeight: radius, transform: nil)
}

// MARK: Drawing

func outline(_ context: CGContext, _ path: CGPath, _ color: CGColor, _ width: CGFloat) {
    context.addPath(path)
    context.setStrokeColor(color)
    context.setLineWidth(width)
    context.setLineJoin(.round)
    context.setLineCap(.round)
    context.strokePath()
}

/// Fills a shape over an outline twice `border` wide, so `border` shows outside the shape.
func shape(_ context: CGContext, _ path: CGPath, fill: CGColor, border: CGFloat = 12, borderColor: CGColor = white) {
    if border > 0 { outline(context, path, borderColor, border * 2) }
    context.addPath(path)
    context.setFillColor(fill)
    context.fillPath()
}

func rotated(_ degrees: CGFloat, _ draw: @escaping Draw) -> Draw {
    { context in
        context.saveGState()
        context.rotate(by: degrees * .pi / 180)
        draw(context)
        context.restoreGState()
    }
}

func pill(_ text: String, _ background: CGColor, _ foreground: CGColor = white, tilt: CGFloat = -6) -> Draw {
    rotated(tilt) { context in
        let label = textPath(text, width: 360, height: 130)
        let bounds = label.boundingBoxOfPath
        let height = bounds.height + 90
        shape(context, roundedRect(width: bounds.width + 100, height: height, radius: height / 2), fill: background)
        shape(context, label, fill: foreground, border: 0)
    }
}

func burst(_ text: String, _ background: CGColor, _ foreground: CGColor = white, spikes: Int = 14) -> Draw {
    { context in
        shape(context, star(points: spikes, outer: 236, inner: 188), fill: background)
        context.saveGState()
        context.rotate(by: -8 * .pi / 180)
        shape(context, textPath(text, width: 270, height: 190), fill: foreground, border: 0)
        context.restoreGState()
    }
}

func bubble(_ text: String, _ foreground: CGColor = ink) -> Draw {
    { context in
        let body = CGMutablePath()
        body.addPath(roundedRect(width: 440, height: 290, radius: 80, y: 40))
        body.addPath(polygon([(-150, -90), (-175, -215), (-30, -100)]))
        outline(context, body, ink, 30)
        context.addPath(body)
        context.setFillColor(white)
        context.fillPath()
        context.translateBy(x: 0, y: 40)
        shape(context, textPath(text, width: 350, height: 190), fill: foreground, border: 0)
        context.translateBy(x: 0, y: -40)
    }
}

func arrow(_ degrees: CGFloat, _ color: CGColor) -> Draw {
    rotated(degrees) { context in
        let path = polygon([(-215, 52), (40, 52), (40, 140), (220, 0), (40, -140), (40, -52), (-215, -52)])
        shape(context, path, fill: color, border: 14)
    }
}

func strokeMark(_ path: CGPath, _ color: CGColor, width: CGFloat = 64) -> Draw {
    { context in
        outline(context, path, white, width + 30)
        outline(context, path, color, width)
    }
}

func linesPath(_ segments: [[(CGFloat, CGFloat)]]) -> CGPath {
    let path = CGMutablePath()
    for segment in segments { path.addLines(between: segment.map { CGPoint(x: $0.0, y: $0.1) }) }
    return path
}

let heart: Draw = { shape($0, heartPath(), fill: pink) }
let goldStar: Draw = { shape($0, star(points: 5, outer: 232, inner: 98), fill: yellow) }
let check = strokeMark(linesPath([[(-150, -10), (-50, -115), (160, 125)]]), green)
let cross = strokeMark(linesPath([[(-130, -130), (130, 130)], [(-130, 130), (130, -130)]]), red)
let ring: Draw = { outline($0, ringPath(), red, 24) }

let underline: Draw = { context in
    let path = CGMutablePath()
    for step in 0...60 {
        let along = CGFloat(step) / 60
        let point = CGPoint(x: -225 + 450 * along, y: 26 * sin(along * 3 * .pi) - 30 * along)
        if step == 0 { path.move(to: point) } else { path.addLine(to: point) }
    }
    outline(context, path, yellow, 34)
}

let pin: Draw = { context in
    let path = CGMutablePath()
    path.move(to: CGPoint(x: 0, y: -215))
    path.addCurve(to: CGPoint(x: -135, y: 70), control1: CGPoint(x: -45, y: -110), control2: CGPoint(x: -135, y: -25))
    path.addArc(center: CGPoint(x: 0, y: 70), radius: 135, startAngle: .pi, endAngle: 0, clockwise: true)
    path.addCurve(to: CGPoint(x: 0, y: -215), control1: CGPoint(x: 135, y: -25), control2: CGPoint(x: 45, y: -110))
    path.closeSubpath()
    shape(context, path, fill: red)
    context.setFillColor(white)
    context.fillEllipse(in: CGRect(x: -52, y: 18, width: 104, height: 104))
}

let play: Draw = { context in
    shape(context, roundedRect(width: 420, height: 290, radius: 80), fill: red)
    shape(context, polygon([(-55, 85), (-55, -85), (95, 0)]), fill: white, border: 0)
}

func rec(dot: Bool) -> Draw {
    { context in
        shape(context, roundedRect(width: 440, height: 190, radius: 50), fill: rgb(0x111111, 0.85), border: 0)
        if dot {
            context.setFillColor(red)
            context.fillEllipse(in: CGRect(x: -180, y: -50, width: 100, height: 100))
        }
        context.translateBy(x: 65, y: 0)
        shape(context, textPath("REC", width: 220, height: 90), fill: white, border: 0)
        context.translateBy(x: -65, y: 0)
    }
}

let viewfinder: Draw = { context in
    let corner: [(CGFloat, CGFloat)] = [(-215, 100), (-215, 215), (-100, 215)]
    let corners = [(1, 1), (-1, 1), (1, -1), (-1, -1)].map { flip in
        corner.map { ($0.0 * CGFloat(flip.0), $0.1 * CGFloat(flip.1)) }
    }
    outline(context, linesPath(corners), ink, 40)
    outline(context, linesPath(corners), white, 24)
}

let bolt: Draw = {
    shape($0, polygon([(55, 225), (-135, -25), (-20, -25), (-75, -225), (140, 45), (20, 45)]), fill: yellow, borderColor: ink)
}

let crown: Draw = { context in
    let path = polygon([(-190, -130), (190, -130), (225, 120), (105, 5), (0, 160), (-105, 5), (-225, 120)])
    shape(context, path, fill: yellow)
    context.setFillColor(red)
    for x in [-225.0, 0, 225] {
        context.fillEllipse(in: CGRect(x: x - 26, y: (x == 0 ? 160 : 120) - 26, width: 52, height: 52))
    }
}

func sparkles(_ scales: [CGFloat]) -> Draw {
    { context in
        let spots: [(CGFloat, CGFloat, CGFloat)] = [(-60, 30, 190), (150, 150, 85), (140, -150, 110)]
        for (spot, scale) in zip(spots, scales) {
            context.saveGState()
            context.translateBy(x: spot.0, y: spot.1)
            shape(context, sparklePath(spot.2 * scale), fill: yellow, border: 10)
            context.restoreGState()
        }
    }
}

func number(_ value: Int, _ color: CGColor) -> Draw {
    { context in
        shape(context, CGPath(ellipseIn: CGRect(x: -205, y: -205, width: 410, height: 410), transform: nil), fill: color)
        shape(context, textPath(String(value), width: 220, height: 250), fill: white, border: 0)
    }
}

func typing(_ lifted: Int?) -> Draw {
    { context in
        bubble(" ")(context)
        context.setFillColor(rgb(0x8E8E93))
        for index in 0..<3 {
            let y: CGFloat = index == lifted ? 70 : 40
            context.fillEllipse(in: CGRect(x: CGFloat(index - 1) * 110 - 32, y: y - 32, width: 64, height: 64))
        }
    }
}

// MARK: The pack

let stills: [(String, Draw)] = [
    ("badge-wow", pill("WOW!", yellow, ink)), ("badge-omg", pill("OMG", pink)), ("badge-lol", pill("LOL", orange)),
    ("badge-hot", pill("HOT", red)), ("badge-new", pill("NEW", green)), ("badge-top-1", pill("TOP 1", yellow, ink)),
    ("badge-best", pill("BEST", blue)), ("badge-free", pill("FREE", green)), ("badge-tip", pill("TIP", purple)),
    ("badge-review", pill("REVIEW", ink)), ("badge-like", pill("LIKE", blue)), ("badge-follow", pill("FOLLOW", pink)),
    ("badge-subscribe", pill("SUBSCRIBE", red, tilt: 0)), ("badge-live", pill("LIVE", red, tilt: 0)),
    ("badge-yummy", pill("YUMMY", orange)), ("badge-ngon", pill("NGON!", orange)),
    ("badge-dinh", pill("ĐỈNH", purple)), ("badge-xin", pill("XỊN", blue)), ("badge-qua-da", pill("QUÁ ĐÃ", pink)),
    ("badge-xem-ngay", pill("XEM NGAY", red, tilt: 0)), ("badge-meo-hay", pill("MẸO HAY", green)),
    ("burst-sale", burst("SALE", red)), ("burst-50", burst("-50%", yellow, ink)), ("burst-new", burst("NEW", green)),
    ("burst-hot-deal", burst("HOT\nDEAL", orange)), ("burst-vs", burst("VS", purple, spikes: 10)),
    ("burst-giam-gia", burst("GIẢM\nGIÁ", red)), ("burst-wow", burst("WOW", blue, spikes: 10)),
    ("bubble-empty", bubble(" ")), ("bubble-question", bubble("?", blue)), ("bubble-exclaim", bubble("!", red)),
    ("bubble-hello", bubble("HELLO")), ("bubble-xin-chao", bubble("XIN\nCHÀO")), ("bubble-haha", bubble("HAHA", orange)),
    ("arrow-right-red", arrow(0, red)), ("arrow-left-red", arrow(180, red)), ("arrow-up-red", arrow(90, red)),
    ("arrow-down-red", arrow(-90, red)), ("arrow-right-yellow", arrow(0, yellow)),
    ("arrow-left-yellow", arrow(180, yellow)), ("arrow-up-yellow", arrow(90, yellow)),
    ("arrow-down-yellow", arrow(-90, yellow)), ("arrow-diagonal-white", arrow(-45, white)),
    ("mark-heart", heart), ("mark-star", goldStar), ("mark-check", check), ("mark-cross", cross),
    ("mark-ring", rotated(-6, ring)), ("mark-underline", underline), ("mark-pin", pin), ("mark-play", play),
    ("mark-rec", rec(dot: true)), ("mark-viewfinder", viewfinder), ("mark-bolt", bolt), ("mark-crown", crown),
    ("mark-sparkles", sparkles([1, 1, 1])),
    ("number-1", number(1, red)), ("number-2", number(2, orange)), ("number-3", number(3, green)),
    ("number-4", number(4, blue)), ("number-5", number(5, purple)),
]

func wave(_ time: CGFloat) -> CGFloat { sin(time * 2 * .pi) }

func scaled(_ scale: CGFloat, _ draw: Draw, _ context: CGContext) {
    context.saveGState()
    context.scaleBy(x: scale, y: scale)
    draw(context)
    context.restoreGState()
}

func pulse(_ draw: @escaping Draw) -> (CGContext, CGFloat) -> Void {
    { context, time in scaled(0.9 + 0.1 * wave(time), draw, context) }
}

func wiggle(_ draw: @escaping Draw) -> (CGContext, CGFloat) -> Void {
    { context, time in scaled(0.9, rotated(9 * wave(time), draw), context) }
}

func bounce(_ dx: CGFloat, _ dy: CGFloat, _ draw: @escaping Draw) -> (CGContext, CGFloat) -> Void {
    { context, time in
        context.saveGState()
        context.translateBy(x: dx * wave(time), y: dy * wave(time))
        scaled(0.84, draw, context)
        context.restoreGState()
    }
}

/// Grows past full size, settles and holds.
func pop(_ draw: @escaping Draw) -> (CGContext, CGFloat) -> Void {
    { context, time in
        let scale: CGFloat = time < 0.3 ? 1.0 * time / 0.3 : time < 0.45 ? 1.0 - 0.12 * (time - 0.3) / 0.15 : 0.88
        if scale > 0.02 { scaled(scale, draw, context) }
    }
}

let animations: [(String, (CGContext, CGFloat) -> Void)] = [
    ("anim-heart", pulse(heart)),
    ("anim-star", { context, time in scaled(0.92, rotated(-72 * time, goldStar), context) }),
    ("anim-arrow-down", bounce(0, 38, arrow(-90, red))),
    ("anim-arrow-right", bounce(38, 0, arrow(0, yellow))),
    ("anim-arrow-left", bounce(38, 0, arrow(180, yellow))),
    ("anim-rec", { context, time in rec(dot: time < 0.5)(context) }),
    ("anim-live", pulse(pill("LIVE", red, tilt: 0))),
    ("anim-subscribe", pulse(pill("SUBSCRIBE", red, tilt: 0))),
    ("anim-follow", pulse(pill("FOLLOW", pink, tilt: 0))),
    ("anim-xem-ngay", pulse(pill("XEM NGAY", red, tilt: 0))),
    ("anim-wow", wiggle(pill("WOW!", yellow, ink, tilt: 0))),
    ("anim-ngon", wiggle(pill("NGON!", orange, tilt: 0))),
    ("anim-dinh", wiggle(pill("ĐỈNH", purple, tilt: 0))),
    ("anim-sale", { context, time in
        scaled(0.95, { inner in
            rotated(-360 / 14 * time) { shape($0, star(points: 14, outer: 236, inner: 188), fill: red) }(inner)
            rotated(-8) { shape($0, textPath("SALE", width: 270, height: 190), fill: white, border: 0) }(inner)
        }, context)
    }),
    ("anim-new", { context, time in scaled(0.95, burst("NEW", time < 0.5 ? green : orange), context) }),
    ("anim-sparkles", { context, time in
        scaled(0.9, sparkles((0..<3).map { 0.75 + 0.25 * wave(time + CGFloat($0) / 3) }), context)
    }),
    ("anim-ring", { context, time in
        scaled(0.95, rotated(-6) { outline($0, ringPath(progress: min(1, time / 0.6)), red, 24) }, context)
    }),
    ("anim-check", pop(check)),
    ("anim-typing", { context, time in scaled(0.95, typing(time < 0.75 ? Int(time * 4) : nil), context) }),
    ("anim-bolt", { context, time in if Int(time * 4) != 1 { scaled(0.95, bolt, context) } }),
]

// MARK: Output

/// Renders a 512-point drawing into a `side`-pixel RGBA bitmap (premultiplied, top row first).
func render(side: Int, _ draw: (CGContext) -> Void) -> CGContext {
    let context = CGContext(
        data: nil, width: side, height: side, bitsPerComponent: 8, bytesPerRow: side * 4, space: space,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    context.clear(CGRect(x: 0, y: 0, width: side, height: side))
    context.translateBy(x: CGFloat(side) / 2, y: CGFloat(side) / 2)
    context.scaleBy(x: CGFloat(side) / unit, y: CGFloat(side) / unit)
    draw(context)
    return context
}

/// GIF has one transparent color, so soft edges would come out with a dark fringe: makes each pixel either
/// clear or opaque.
func hardenAlpha(_ context: CGContext) {
    guard let data = context.data else { return }
    let pixels = data.assumingMemoryBound(to: UInt8.self)
    for offset in stride(from: 0, to: context.height * context.bytesPerRow, by: 4) {
        let alpha = Int(pixels[offset + 3])
        if alpha < 128 {
            for channel in 0..<4 { pixels[offset + channel] = 0 }
        } else {
            for channel in 0..<3 { pixels[offset + channel] = UInt8(min(255, Int(pixels[offset + channel]) * 255 / alpha)) }
            pixels[offset + 3] = 255
        }
    }
}

func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data((message + "\n").utf8))
    exit(1)
}

var arguments = Array(CommandLine.arguments.dropFirst())
var sheet: URL?
if let flag = arguments.firstIndex(of: "--sheet"), flag + 1 < arguments.count {
    sheet = URL(fileURLWithPath: arguments[flag + 1])
    arguments.removeSubrange(flag...flag + 1)
}
let folder = arguments.first.map { URL(fileURLWithPath: $0, isDirectory: true) }
    ?? URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
        .appendingPathComponent("stickers", isDirectory: true)
try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)

var previews: [CGImage] = []
for (name, draw) in stills {
    guard let image = render(side: 512, draw).makeImage(),
        let destination = CGImageDestinationCreateWithURL(
            folder.appendingPathComponent(name + ".png") as CFURL, UTType.png.identifier as CFString, 1, nil)
    else { fail("Cannot write \(name).png") }
    CGImageDestinationAddImage(destination, image, nil)
    guard CGImageDestinationFinalize(destination) else { fail("Cannot write \(name).png") }
    previews.append(image)
}

let frameCount = 16
for (name, draw) in animations {
    let url = folder.appendingPathComponent(name + ".gif")
    guard let destination = CGImageDestinationCreateWithURL(url as CFURL, UTType.gif.identifier as CFString, frameCount, nil)
    else { fail("Cannot write \(name).gif") }
    CGImageDestinationSetProperties(
        destination, [kCGImagePropertyGIFDictionary: [kCGImagePropertyGIFLoopCount: 0]] as CFDictionary)
    var frames: [CGContext] = []
    for index in 0..<frameCount {
        let frame = render(side: 320) { draw($0, CGFloat(index) / CGFloat(frameCount)) }
        hardenAlpha(frame)
        guard let image = frame.makeImage() else { fail("Cannot draw \(name).gif") }
        CGImageDestinationAddImage(
            destination, image,
            [kCGImagePropertyGIFDictionary: [kCGImagePropertyGIFDelayTime: 0.08]] as CFDictionary)
        frames.append(frame)
    }
    guard CGImageDestinationFinalize(destination) else { fail("Cannot write \(name).gif") }

    // Read the file back: every frame must decode alone, without pixels left over from the frame before it.
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil), CGImageSourceGetCount(source) == frameCount
    else { fail("\(name).gif does not read back as \(frameCount) frames") }
    for index in 0..<frameCount {
        guard let decoded = CGImageSourceCreateImageAtIndex(source, index, nil) else { fail("\(name).gif frame \(index)") }
        let copy = render(side: 320) { $0.draw(decoded, in: CGRect(x: -unit / 2, y: -unit / 2, width: unit, height: unit)) }
        guard let expected = frames[index].data?.assumingMemoryBound(to: UInt8.self),
            let actual = copy.data?.assumingMemoryBound(to: UInt8.self)
        else { fail("\(name).gif frame \(index)") }
        var wrong = 0
        for pixel in 0..<320 * 320 where (expected[pixel * 4 + 3] > 127) != (actual[pixel * 4 + 3] > 127) { wrong += 1 }
        if wrong > 320 * 320 / 200 { fail("\(name).gif frame \(index): \(wrong) pixels differ in transparency") }
    }
    if let middle = frames[frameCount / 4].makeImage() { previews.append(middle) }
}

if let sheet {
    // A contact sheet over gray, to look at the whole pack at once.
    let columns = 10, cell = 160
    let rows = (previews.count + columns - 1) / columns
    let context = CGContext(
        data: nil, width: columns * cell, height: rows * cell, bitsPerComponent: 8, bytesPerRow: 0, space: space,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    context.setFillColor(rgb(0x3A4A5A))
    context.fill(CGRect(x: 0, y: 0, width: columns * cell, height: rows * cell))
    for (index, image) in previews.enumerated() {
        let rect = CGRect(x: index % columns * cell + 8, y: (rows - 1 - index / columns) * cell + 8, width: cell - 16, height: cell - 16)
        context.draw(image, in: rect)
    }
    if let image = context.makeImage(),
        let destination = CGImageDestinationCreateWithURL(sheet as CFURL, UTType.png.identifier as CFString, 1, nil) {
        CGImageDestinationAddImage(destination, image, nil)
        CGImageDestinationFinalize(destination)
    }
}
print("\(stills.count) PNG and \(animations.count) GIF stickers in \(folder.path)")
