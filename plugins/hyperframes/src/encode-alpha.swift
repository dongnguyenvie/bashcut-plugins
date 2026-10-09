// encode-alpha: an RGBA PNG sequence → a .mov with alpha (HEVC with alpha or ProRes 4444), with AVAssetWriter.
// No FFmpeg. Usage: encode-alpha <frames-dir> <out.mov> [--fps 30] [--codec hevc|prores] [--quality 0.0–1.0]
import AVFoundation
import CoreImage
import Foundation
import ImageIO
import VideoToolbox

struct Options {
    var input: URL
    var output: URL
    var fps: Int32 = 30
    var codec = "hevc"
    var quality = 0.8
}

func parse() -> Options {
    var args = Array(CommandLine.arguments.dropFirst())
    guard args.count >= 2 else {
        FileHandle.standardError.write(Data("usage: encode-alpha <frames-dir> <out.mov> [--fps N] [--codec hevc|prores] [--quality Q]\n".utf8))
        exit(2)
    }
    var options = Options(input: URL(fileURLWithPath: args.removeFirst()), output: URL(fileURLWithPath: args.removeFirst()))
    while let flag = args.first {
        args.removeFirst()
        let value = args.isEmpty ? "" : args.removeFirst()
        switch flag {
        case "--fps": options.fps = Int32(value) ?? 30
        case "--codec": options.codec = value
        case "--quality": options.quality = Double(value) ?? 0.8
        default: FileHandle.standardError.write(Data("unknown option \(flag)\n".utf8)); exit(2)
        }
    }
    return options
}

func image(_ url: URL) -> CGImage? {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil) else { return nil }
    return CGImageSourceCreateImageAtIndex(source, 0, nil)
}

/// Draws `image` into a BGRA buffer with premultiplied alpha (what the encoders take).
func fill(_ buffer: CVPixelBuffer, with image: CGImage) {
    CVPixelBufferLockBaseAddress(buffer, [])
    defer { CVPixelBufferUnlockBaseAddress(buffer, []) }
    let width = CVPixelBufferGetWidth(buffer), height = CVPixelBufferGetHeight(buffer)
    let context = CGContext(
        data: CVPixelBufferGetBaseAddress(buffer), width: width, height: height, bitsPerComponent: 8,
        bytesPerRow: CVPixelBufferGetBytesPerRow(buffer), space: CGColorSpace(name: CGColorSpace.sRGB)!,
        bitmapInfo: CGImageAlphaInfo.premultipliedFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue)!
    context.clear(CGRect(x: 0, y: 0, width: width, height: height))
    context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
}

let options = parse()
let frames = (try FileManager.default.contentsOfDirectory(at: options.input, includingPropertiesForKeys: nil))
    .filter { $0.pathExtension.lowercased() == "png" }.sorted { $0.lastPathComponent < $1.lastPathComponent }
guard let first = frames.first.flatMap(image) else { fatalError("no PNG frames in \(options.input.path)") }
let width = first.width, height = first.height
try? FileManager.default.removeItem(at: options.output)

let started = Date()
let writer = try AVAssetWriter(outputURL: options.output, fileType: .mov)
var settings: [String: Any] = [AVVideoWidthKey: width, AVVideoHeightKey: height]
if options.codec == "prores" {
    settings[AVVideoCodecKey] = AVVideoCodecType.proRes4444
} else {
    settings[AVVideoCodecKey] = AVVideoCodecType.hevcWithAlpha
    settings[AVVideoCompressionPropertiesKey] = [
        AVVideoQualityKey: options.quality,
        kVTCompressionPropertyKey_TargetQualityForAlpha as String: options.quality,
    ]
}
let input = AVAssetWriterInput(mediaType: .video, outputSettings: settings)
input.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
    kCVPixelBufferWidthKey as String: width, kCVPixelBufferHeightKey as String: height,
])
writer.add(input)
guard writer.startWriting() else { fatalError("cannot start writing: \(String(describing: writer.error))") }
writer.startSession(atSourceTime: .zero)

for (index, url) in frames.enumerated() {
    guard let picture = image(url), picture.width == width, picture.height == height else {
        fatalError("\(url.lastPathComponent) is unreadable or not \(width)×\(height)")
    }
    while !input.isReadyForMoreMediaData { usleep(1_000) }
    var buffer: CVPixelBuffer?
    CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &buffer)
    guard let buffer else { fatalError("no pixel buffer") }
    fill(buffer, with: picture)
    guard adaptor.append(buffer, withPresentationTime: CMTime(value: CMTimeValue(index), timescale: options.fps)) else {
        fatalError("append failed at frame \(index): \(String(describing: writer.error))")
    }
}
input.markAsFinished()
let done = DispatchSemaphore(value: 0)
writer.finishWriting { done.signal() }
done.wait()
guard writer.status == .completed else { fatalError("write failed: \(String(describing: writer.error))") }

let bytes = (try FileManager.default.attributesOfItem(atPath: options.output.path)[.size] as? Int) ?? 0
var usage = rusage()
getrusage(RUSAGE_SELF, &usage)
let seconds = Date().timeIntervalSince(started)
let report: [String: Any] = [
    "output": options.output.path, "codec": options.codec, "frames": frames.count, "fps": options.fps,
    "width": width, "height": height, "bytes": bytes, "encodeSeconds": (seconds * 100).rounded() / 100,
    "encodeFps": (Double(frames.count) / seconds * 10).rounded() / 10, "peakRSSMB": usage.ru_maxrss / 1_048_576,
]
print(String(data: try JSONSerialization.data(withJSONObject: report, options: [.sortedKeys]), encoding: .utf8)!)
