// Finding logos and watermarks that stay in place, with or without letters.
//
// A few pictures spread over the clip (`media.frames`) are shrunk to 320 pixels wide. A pixel that keeps its colour in
// every picture while the rest of the picture moves, and that has detail (an edge, or a colour unlike its
// neighbours), belongs to something laid over the picture: a channel logo, a "4K HDR" badge, a watermark. Such pixels
// near each other make one logo; only logos near an edge or a corner of the picture and no bigger than a logo count,
// so a door frame in a shot from a tripod is not one. A shot where most of the picture stands still is skipped: there
// a logo cannot be told from the scene (the text reader still finds logos with letters).
import CoreGraphics
import Foundation
import ImageIO

/// A logo's box as shares of the upright picture from the top left.
struct LogoBox: Equatable {
    var x: Double
    var y: Double
    var width: Double
    var height: Double

    var right: Double { x + width }
    var bottom: Double { y + height }

    func union(_ other: LogoBox) -> LogoBox {
        let left = min(x, other.x), top = min(y, other.y)
        return LogoBox(x: left, y: top, width: max(right, other.right) - left, height: max(bottom, other.bottom) - top)
    }

    /// Whether the two boxes overlap or are closer than `gap` (a share of the picture) apart.
    func near(_ other: LogoBox, gap: Double) -> Bool {
        x - gap <= other.right && other.x - gap <= right && y - gap <= other.bottom && other.y - gap <= bottom
    }
}

/// The logos that stand still over the pictures at `paths` (at least four); nil when the pictures cannot tell (too
/// few, or most of the picture stands still).
func findStillLogos(_ paths: [String]) -> [LogoBox]? {
    let width = 320
    var pictures: [[UInt8]] = []
    var height = 0
    for path in paths {
        guard let source = CGImageSourceCreateWithURL(URL(fileURLWithPath: path) as CFURL, nil),
            let image = CGImageSourceCreateImageAtIndex(source, 0, nil), image.width > 0
        else { continue }
        let rows = max(1, Int((Double(image.height) * Double(width) / Double(image.width)).rounded()))
        if height == 0 { height = rows }
        guard rows == height else { continue }
        var pixels = [UInt8](repeating: 0, count: width * rows * 4)
        let drawn = pixels.withUnsafeMutableBytes { buffer -> Bool in
            guard let context = CGContext(
                data: buffer.baseAddress, width: width, height: rows, bitsPerComponent: 8, bytesPerRow: width * 4,
                space: CGColorSpace(name: CGColorSpace.sRGB) ?? CGColorSpaceCreateDeviceRGB(),
                bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)
            else { return false }
            context.interpolationQuality = .medium
            context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: rows))
            return true
        }
        if drawn { pictures.append(pixels) }
    }
    return stillLogos(pictures, width: width, height: height)
}

/// The still logos in `pictures` (RGBA, `width` × `height`, top row first), or nil when they cannot tell.
func stillLogos(_ pictures: [[UInt8]], width: Int, height: Int) -> [LogoBox]? {
    guard pictures.count >= 4, width > 8, height > 8 else { return nil }
    let count = width * height
    var still = [Bool](repeating: false, count: count)
    var mean = [Double](repeating: 0, count: count)
    for pixel in 0..<count {
        var range = 0
        for channel in 0..<3 {
            var low = 255, high = 0
            for picture in pictures {
                let value = Int(picture[pixel * 4 + channel])
                low = min(low, value)
                high = max(high, value)
            }
            range = max(range, high - low)
        }
        still[pixel] = range < 28
        mean[pixel] = pictures.reduce(0) { sum, picture in
            sum + (Double(picture[pixel * 4]) + Double(picture[pixel * 4 + 1]) + Double(picture[pixel * 4 + 2])) / 3
        } / Double(pictures.count)
    }
    // Most of the picture stands still: a tripod shot or a still image, where a logo cannot be told from the scene.
    guard Double(still.filter { $0 }.count) / Double(count) < 0.5 else { return nil }

    // Detail: an edge, or a colour unlike the 5 × 5 pixels around it, so flat bars and a still sky do not count.
    var marked = [Bool](repeating: false, count: count)
    for y in 0..<height {
        for x in 0..<width where still[y * width + x] {
            let here = mean[y * width + x]
            let edge = max(x > 0 ? abs(here - mean[y * width + x - 1]) : 0, y > 0 ? abs(here - mean[(y - 1) * width + x]) : 0)
            var sum = 0.0, cells = 0.0
            for dy in -2...2 {
                for dx in -2...2 {
                    let nx = min(width - 1, max(0, x + dx)), ny = min(height - 1, max(0, y + dy))
                    sum += mean[ny * width + nx]
                    cells += 1
                }
            }
            marked[y * width + x] = edge > 18 || abs(here - sum / cells) > 10
        }
    }

    // Marked pixels within three pixels of each other make one logo.
    let reach = 3
    var group = [Int](repeating: -1, count: count)
    var boxes: [(left: Int, top: Int, right: Int, bottom: Int, pixels: Int)] = []
    for start in 0..<count where marked[start] && group[start] < 0 {
        var queue = [start]
        group[start] = boxes.count
        var box = (left: width, top: height, right: 0, bottom: 0, pixels: 0)
        while let pixel = queue.popLast() {
            let x = pixel % width, y = pixel / width
            box = (min(box.left, x), min(box.top, y), max(box.right, x), max(box.bottom, y), box.pixels + 1)
            for ny in max(0, y - reach)...min(height - 1, y + reach) {
                for nx in max(0, x - reach)...min(width - 1, x + reach) {
                    let next = ny * width + nx
                    if marked[next], group[next] < 0 {
                        group[next] = boxes.count
                        queue.append(next)
                    }
                }
            }
        }
        boxes.append(box)
    }

    var logos: [LogoBox] = boxes.compactMap { box in
        let logo = LogoBox(
            x: Double(box.left) / Double(width), y: Double(box.top) / Double(height),
            width: Double(box.right - box.left + 1) / Double(width), height: Double(box.bottom - box.top + 1) / Double(height))
        let centreX = logo.x + logo.width / 2, centreY = logo.y + logo.height / 2
        let nearEdge = centreX < 0.3 || centreX > 0.7 || centreY < 0.2 || centreY > 0.8
        guard box.pixels >= 6, nearEdge, logo.width <= 0.4, logo.height <= 0.2, max(logo.width, logo.height) >= 0.015
        else { return nil }
        return logo
    }
    // Parts of one logo (an icon beside its name) close together become one box.
    var merged = true
    while merged {
        merged = false
        outer: for i in logos.indices {
            for j in logos.indices where j > i && logos[i].near(logos[j], gap: 0.02) {
                logos[i] = logos[i].union(logos[j])
                logos.remove(at: j)
                merged = true
                break outer
            }
        }
    }
    return logos.filter { $0.width <= 0.45 && $0.height <= 0.25 }.sorted { ($0.y, $0.x) < ($1.y, $1.x) }
}

/// The logos found both ways, as one list: a still logo and the text read inside or beside it become one box. Text
/// that stays the same but does not stand still (a name on a shirt in a talking head) is not a logo, so where the
/// pictures could tell (`still` not nil), text away from a still logo counts only in a corner of the picture.
func mergeLogos(still: [LogoBox]?, read: [SeenText]) -> [LogoBox] {
    var logos = still ?? []
    for text in read {
        let box = LogoBox(x: text.x, y: text.y, width: text.width, height: text.height)
        if let index = logos.firstIndex(where: { $0.near(box, gap: 0.02) }) {
            logos[index] = logos[index].union(box)
            continue
        }
        let centreX = box.x + box.width / 2, centreY = box.y + box.height / 2
        let corner = (centreX < 0.25 || centreX > 0.75) && (centreY < 0.2 || centreY > 0.8)
        if still == nil || corner { logos.append(box) }
    }
    return logos
}
