// Image Generation: provides image.generate (provider bashcut.image-gen.api) with the user's own key.
//
// One request is a whole batch: `prompts` [{id, prompt}], `style` {prompt?, references [paths], seed?}, `width`,
// `height`, `aspectRatio` and `outputDirectory` (rules: BashCut docs/guides/plugins.md#imagegenerate). Each scene is
// one call to the chosen service with the style text and the reference pictures; the picture is cropped to the
// asked shape, scaled to the asked size and written as <id>.png. A scene that fails goes into `failed`, so one
// refused prompt does not lose the batch.
import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

func handle(method: String, params: JSON, host: Host) throws -> Any? {
    guard method == "image.generate" else { throw PluginError("unknown_method", "Image Generation does not handle \(method)") }
    let request = try ImageRequest(params)
    let service = try Service(options: params["options"] as? JSON ?? [:])
    var images: [JSON] = []
    var failed: [JSON] = []
    for (index, scene) in request.prompts.enumerated() {
        host.progress(Double(index) / Double(request.prompts.count), "Picture \(index + 1) of \(request.prompts.count)")
        do {
            let data = try service.generate(prompt: request.text(for: scene.prompt), request: request)
            let path = (request.outputDirectory as NSString).appendingPathComponent(safeName(scene.id) + ".png")
            try fitted(data, width: request.width, height: request.height, to: path)
            var image: JSON = ["id": scene.id, "path": (path as NSString).lastPathComponent]
            if let seed = request.seed { image["seed"] = seed }
            images.append(image)
        } catch let error as PluginError where error.code == "auth" {
            throw error
        } catch let error as PluginError {
            failed.append(["id": scene.id, "message": error.message])
        } catch {
            failed.append(["id": scene.id, "message": "\(error)"])
        }
    }
    host.progress(1, "Done")
    if images.isEmpty, let first = failed.first {
        throw PluginError("failed", first["message"] as? String ?? "No picture was made")
    }
    return ["images": images, "failed": failed]
}

/// The batch BashCut asked for.
struct ImageRequest {
    let prompts: [(id: String, prompt: String)]
    let style: String?
    let references: [String]
    let seed: Int?
    let width: Int
    let height: Int
    let outputDirectory: String

    init(_ params: JSON) throws {
        let list = params["prompts"] as? [JSON] ?? []
        prompts = list.compactMap { entry in
            guard let id = entry["id"] as? String, let prompt = entry["prompt"] as? String, !prompt.isEmpty else { return nil }
            return (id, prompt)
        }
        guard !prompts.isEmpty, prompts.count == list.count else {
            throw PluginError("bad_request", "prompts must be [{id, prompt}]")
        }
        let style = params["style"] as? JSON ?? [:]
        self.style = (style["prompt"] as? String).flatMap { $0.isEmpty ? nil : $0 }
        references = style["references"] as? [String] ?? []
        seed = style["seed"] as? Int
        width = params["width"] as? Int ?? 1024
        height = params["height"] as? Int ?? 1024
        guard let folder = params["outputDirectory"] as? String, !folder.isEmpty else {
            throw PluginError("bad_request", "outputDirectory is required")
        }
        outputDirectory = folder
        for reference in references where !FileManager.default.fileExists(atPath: reference) {
            throw PluginError("bad_request", "Reference picture not found: \(reference)")
        }
    }

    /// The scene with the locked style and, with references, the ask to keep their character and look.
    func text(for prompt: String) -> String {
        var parts: [String] = []
        if let style { parts.append("Style: \(style)") }
        if !references.isEmpty {
            parts.append("Keep the same character, colours and drawing style as the reference pictures.")
        }
        parts.append(parts.isEmpty ? prompt : "Scene: \(prompt)")
        parts.append("No text, letters or watermarks in the picture.")
        return parts.joined(separator: "\n")
    }

    /// The service's nearest supported shape for the asked size.
    func nearest(_ ratios: [String]) -> String {
        let wanted = Double(width) / Double(height)
        return ratios.min { abs(log(value($0) / wanted)) < abs(log(value($1) / wanted)) } ?? "1:1"
    }

    private func value(_ ratio: String) -> Double {
        let parts = ratio.split(separator: ":").compactMap { Double($0) }
        return parts.count == 2 && parts[1] > 0 ? parts[0] / parts[1] : 1
    }
}

/// Gemini or OpenAI, with the user's key and optional model and endpoint.
struct Service {
    enum Kind: String { case gemini, openai }

    let kind: Kind
    let key: String
    let model: String
    let endpoint: String

    init(options: JSON) throws {
        kind = Kind(rawValue: options["service"] as? String ?? "gemini") ?? .gemini
        key = (options["apiKey"] as? String ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        guard !key.isEmpty else {
            throw PluginError("auth", "Add your \(kind == .gemini ? "Gemini" : "OpenAI") API key in the plugin's options (Plugins → Image Generation)")
        }
        let chosen = (options["model"] as? String ?? "").trimmingCharacters(in: .whitespaces)
        model = chosen.isEmpty ? (kind == .gemini ? "gemini-2.5-flash-image" : "gpt-image-1") : chosen
        let base = (options["endpoint"] as? String ?? "").trimmingCharacters(in: .whitespaces)
        let fallback = kind == .gemini ? "https://generativelanguage.googleapis.com" : "https://api.openai.com"
        endpoint = (base.isEmpty ? fallback : base).trimmingCharacters(in: CharacterSet(charactersIn: "/"))
    }

    /// The picture's encoded bytes (PNG, JPEG or WebP).
    func generate(prompt: String, request: ImageRequest) throws -> Data {
        switch kind {
        case .gemini: return try gemini(prompt: prompt, request: request)
        case .openai: return try openAI(prompt: prompt, request: request)
        }
    }

    private func gemini(prompt: String, request: ImageRequest) throws -> Data {
        var parts: [JSON] = [["text": prompt]]
        for reference in request.references {
            let data = try Data(contentsOf: URL(fileURLWithPath: reference))
            parts.append(["inline_data": ["mime_type": mimeType(reference), "data": data.base64EncodedString()]])
        }
        var config: JSON = [
            "responseModalities": ["IMAGE"],
            "imageConfig": ["aspectRatio": request.nearest(["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"])],
        ]
        if let seed = request.seed { config["seed"] = seed }
        let body: JSON = ["contents": [["role": "user", "parts": parts]], "generationConfig": config]
        var call = URLRequest(url: try url("/v1beta/models/\(model):generateContent"))
        call.httpMethod = "POST"
        call.setValue("application/json", forHTTPHeaderField: "Content-Type")
        call.setValue(key, forHTTPHeaderField: "x-goog-api-key")
        call.httpBody = try JSONSerialization.data(withJSONObject: body)
        let answer = try send(call)
        let candidates = answer["candidates"] as? [JSON] ?? []
        for candidate in candidates {
            for part in (candidate["content"] as? JSON)?["parts"] as? [JSON] ?? [] {
                let inline = part["inlineData"] as? JSON ?? part["inline_data"] as? JSON
                if let text = inline?["data"] as? String, let data = Data(base64Encoded: text) { return data }
            }
        }
        let reason = candidates.first?["finishReason"] as? String
            ?? (answer["promptFeedback"] as? JSON)?["blockReason"] as? String
        throw PluginError("no_image", "Gemini returned no picture" + (reason.map { " (\($0))" } ?? ""))
    }

    private func openAI(prompt: String, request: ImageRequest) throws -> Data {
        let size = ["1:1": "1024x1024", "2:3": "1024x1536", "3:2": "1536x1024"][request.nearest(["1:1", "2:3", "3:2"])] ?? "1024x1024"
        var call: URLRequest
        if request.references.isEmpty {
            call = URLRequest(url: try url("/v1/images/generations"))
            call.setValue("application/json", forHTTPHeaderField: "Content-Type")
            call.httpBody = try JSONSerialization.data(withJSONObject: ["model": model, "prompt": prompt, "size": size, "n": 1])
        } else {
            var form = Multipart()
            form.field("model", model)
            form.field("prompt", prompt)
            form.field("size", size)
            for reference in request.references {
                form.file("image[]", path: reference, type: mimeType(reference))
            }
            call = URLRequest(url: try url("/v1/images/edits"))
            call.setValue("multipart/form-data; boundary=\(form.boundary)", forHTTPHeaderField: "Content-Type")
            call.httpBody = try form.finished()
        }
        call.httpMethod = "POST"
        call.setValue("Bearer \(key)", forHTTPHeaderField: "Authorization")
        let answer = try send(call)
        guard let first = (answer["data"] as? [JSON])?.first else { throw PluginError("no_image", "OpenAI returned no picture") }
        if let text = first["b64_json"] as? String, let data = Data(base64Encoded: text) { return data }
        if let link = first["url"] as? String, let remote = URL(string: link) { return try Data(contentsOf: remote) }
        throw PluginError("no_image", "OpenAI returned no picture")
    }

    private func url(_ path: String) throws -> URL {
        guard let url = URL(string: endpoint + path), url.scheme == "https" || url.host == "127.0.0.1" || url.host == "localhost"
        else { throw PluginError("bad_endpoint", "The endpoint must be an https address (or a local server)") }
        return url
    }

    /// Sends one call and returns its JSON; a refused key stops the batch, other errors fail the scene.
    private func send(_ request: URLRequest) throws -> JSON {
        var request = request
        request.timeoutInterval = 240
        let done = DispatchSemaphore(value: 0)
        nonisolated(unsafe) var outcome: (Data?, URLResponse?, Error?)
        URLSession.shared.dataTask(with: request) { data, response, error in
            outcome = (data, response, error)
            done.signal()
        }.resume()
        done.wait()
        if let error = outcome.2 { throw PluginError("network", error.localizedDescription) }
        let status = (outcome.1 as? HTTPURLResponse)?.statusCode ?? 0
        let object = outcome.0.flatMap { try? JSONSerialization.jsonObject(with: $0) as? JSON } ?? [:]
        let message = ((object["error"] as? JSON)?["message"] as? String) ?? "HTTP \(status)"
        if status == 401 || status == 403 { throw PluginError("auth", "The service refused the key: \(message)") }
        guard (200..<300).contains(status) else { throw PluginError("http_\(status)", message) }
        return object
    }
}

/// A multipart/form-data body.
struct Multipart {
    let boundary = "bashcut-\(UUID().uuidString)"
    private var body = Data()
    private var problem: Error?

    mutating func field(_ name: String, _ value: String) {
        body.append(Data("--\(boundary)\r\nContent-Disposition: form-data; name=\"\(name)\"\r\n\r\n\(value)\r\n".utf8))
    }

    mutating func file(_ name: String, path: String, type: String) {
        do {
            let data = try Data(contentsOf: URL(fileURLWithPath: path))
            let file = (path as NSString).lastPathComponent
            body.append(Data("--\(boundary)\r\nContent-Disposition: form-data; name=\"\(name)\"; filename=\"\(file)\"\r\nContent-Type: \(type)\r\n\r\n".utf8))
            body.append(data)
            body.append(Data("\r\n".utf8))
        } catch {
            problem = error
        }
    }

    func finished() throws -> Data {
        if let problem { throw problem }
        return body + Data("--\(boundary)--\r\n".utf8)
    }
}

func mimeType(_ path: String) -> String {
    switch (path as NSString).pathExtension.lowercased() {
    case "jpg", "jpeg": return "image/jpeg"
    case "webp": return "image/webp"
    default: return "image/png"
    }
}

/// A scene ID as a file name.
func safeName(_ id: String) -> String {
    let allowed = CharacterSet.alphanumerics.union(CharacterSet(charactersIn: "-_"))
    let name = String(id.unicodeScalars.map { allowed.contains($0) ? Character($0) : "-" })
    return name.isEmpty ? "picture" : String(name.prefix(80))
}

/// Crops the picture to the asked shape around its centre, scales it to the asked size and writes a PNG.
func fitted(_ data: Data, width: Int, height: Int, to path: String) throws {
    guard let source = CGImageSourceCreateWithData(data as CFData, nil),
        let image = CGImageSourceCreateImageAtIndex(source, 0, nil)
    else { throw PluginError("bad_image", "The service's answer is not a picture") }
    let scale = max(Double(width) / Double(image.width), Double(height) / Double(image.height))
    let drawn = CGSize(width: Double(image.width) * scale, height: Double(image.height) * scale)
    guard let context = CGContext(
        data: nil, width: width, height: height, bitsPerComponent: 8, bytesPerRow: 0,
        space: CGColorSpace(name: CGColorSpace.sRGB) ?? CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)
    else { throw PluginError("bad_image", "Cannot draw a \(width)×\(height) picture") }
    context.interpolationQuality = .high
    context.draw(image, in: CGRect(
        x: (Double(width) - drawn.width) / 2, y: (Double(height) - drawn.height) / 2,
        width: drawn.width, height: drawn.height))
    guard let output = context.makeImage(),
        let destination = CGImageDestinationCreateWithURL(
            URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)
    else { throw PluginError("write_failed", "Cannot write \(path)") }
    CGImageDestinationAddImage(destination, output, nil)
    guard CGImageDestinationFinalize(destination) else { throw PluginError("write_failed", "Cannot write \(path)") }
}
