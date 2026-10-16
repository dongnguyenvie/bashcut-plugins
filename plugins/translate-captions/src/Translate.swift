// Translating captions: every caption's text goes to the chosen service in batches of lines with their on-screen
// time, and comes back as one line each. The caption keeps its timing, style and word style; its word timings are
// dropped (they belong to the old words), so BashCut spreads the new words over the caption by length.
import Foundation

let languageNames = [
    "vi": "Vietnamese", "en": "English", "zh": "Simplified Chinese", "ja": "Japanese", "ko": "Korean", "th": "Thai",
    "id": "Indonesian", "es": "Spanish", "fr": "French", "de": "German", "pt": "Portuguese", "ru": "Russian",
]

/// One caption to translate.
struct Line {
    /// The line's number, which the service answers with (shorter and safer than the item ID).
    let id: String
    let item: String
    let text: String
    let seconds: Double
}

func translate(_ raw: JSON, host: Host) throws -> JSON {
    let request = ActionRequest(raw)
    guard let rev = request.rev else { throw PluginError("bad_request", "The request has no project revision") }
    let target = request.string("target", "vi")
    guard let language = languageNames[target] else { throw PluginError("bad_request", "Unknown target language \(target)") }
    let items = captionItems(request.tracks)
    guard !items.isEmpty else {
        throw PluginError("no_captions", "There are no captions to translate. Make them first (Tools › Auto captions)")
    }
    let service = try Translator(options: request.options)
    let lines = items.enumerated().map { index, item in
        Line(id: "\(index + 1)", item: item["id"] as? String ?? "", text: (item["text"] as? String ?? "").replacingOccurrences(of: "\n", with: " "),
             seconds: Double(item["dur"] as? Int ?? 0) / request.fps)
    }
    let brief = projectBrief(host)
    let glossary = glossaryEntries(request.string("glossary", ""))
    let style = TranslationStyle(
        language: language, tone: request.string("tone", "natural"), maxCps: Int(request.number("maxCps", 17)),
        glossary: glossary, brief: brief)

    var translated: [String: String] = [:]
    let chunks = stride(from: 0, to: lines.count, by: 40).map { Array(lines[$0..<min($0 + 40, lines.count)]) }
    for (index, chunk) in chunks.enumerated() {
        host.progress(Double(index) / Double(chunks.count), "Translating lines \(index * 40 + 1)–\(index * 40 + chunk.count) of \(lines.count)")
        let before = lines.prefix { $0.id != chunk.first?.id }.suffix(3).map { translated[$0.id] ?? $0.text }
        var answer = try service.translate(chunk, style: style, before: Array(before))
        let missing = chunk.filter { answer[$0.id] == nil }
        if !missing.isEmpty {
            answer.merge(try service.translate(missing, style: style, before: [])) { first, _ in first }
        }
        translated.merge(answer) { _, new in new }
    }
    host.progress(1, "Done")

    var operations: [JSON] = []
    var kept: [String] = []
    for (item, line) in zip(items, lines) {
        guard let text = translated[line.id]?.trimmingCharacters(in: .whitespacesAndNewlines), !text.isEmpty else {
            kept.append(line.item)
            continue
        }
        guard text != item["text"] as? String else { continue }
        var patch: JSON = ["text": text]
        if item["words"] != nil { patch["words"] = NSNull() }
        operations.append(["op": "setProperties", "item": line.item, "patch": patch])
    }
    let tooFast = lines.filter { line in
        guard let text = translated[line.id], line.seconds > 0 else { return false }
        return Double(text.count) / line.seconds > Double(style.maxCps) * 1.25
    }.count
    var message = "Translated \(operations.count) of \(lines.count) captions to \(language) with \(service.label)"
    if !kept.isEmpty { message += "; \(kept.count) kept as they were (no translation came back)" }
    if tooFast > 0 { message += "; \(tooFast) still read faster than \(style.maxCps) characters a second" }
    return [
        "label": "Translate captions to \(language)",
        "baseRev": rev,
        "operations": operations,
        "pluginData": mergedPluginData(request, "translate", [
            "target": target, "service": service.label, "lines": lines.count, "translated": operations.count,
            "kept": kept, "at": ISO8601DateFormatter().string(from: Date()),
        ]),
        "message": message,
        "data": ["target": target, "translated": operations.count, "lines": lines.count, "kept": kept, "tooFast": tooFast],
    ]
}

/// The project brief as compact JSON (names, topic, audience help the translation), or nil when there is none.
func projectBrief(_ host: Host) -> String? {
    guard let answer = try? host.call("project.data", ["key": "brief"]) as? JSON else { return nil }
    let value = answer["value"] ?? answer["brief"]
    guard let value, !(value is NSNull), JSONSerialization.isValidJSONObject(value),
        let data = try? JSONSerialization.data(withJSONObject: value, options: [.sortedKeys, .withoutEscapingSlashes]),
        let text = String(data: data, encoding: .utf8)
    else { return nil }
    return String(text.prefix(4000))
}

/// "Tom Scott; grizzly = gấu xám" → ["Tom Scott", "grizzly = gấu xám"].
func glossaryEntries(_ text: String) -> [String] {
    text.components(separatedBy: CharacterSet(charactersIn: ";\n"))
        .map { $0.trimmingCharacters(in: .whitespaces) }
        .filter { !$0.isEmpty }
        .prefix(100).map { String($0.prefix(200)) }
}

struct TranslationStyle {
    let language: String
    let tone: String
    let maxCps: Int
    let glossary: [String]
    let brief: String?

    var instructions: String {
        let voice = [
            "casual": "casual and lively, like a native creator on social video",
            "formal": "formal and polite",
        ][tone] ?? "natural, the way a native speaker would say it"
        var text = """
            You translate the captions of a video into \(language).
            Each input line is one caption shown for `seconds`. Translate every line on its own, in order, using the \
            lines around it for meaning. The tone is \(voice).
            Keep each line readable: at most `maxChars` characters (\(maxCps) characters per second); when the meaning \
            needs more, say it shorter instead of adding words.
            Never merge, split, drop or reorder lines. Keep numbers as digits. Keep names of people, places, brands \
            and products as they are written unless the glossary says otherwise.
            Write plain caption text: no quotes around it, no notes, no speaker names, no line breaks.
            Answer with JSON only: {"lines": [{"id": "<the line's id>", "text": "<the translation>"}]} with every id.
            """
        if !glossary.isEmpty {
            text += "\nGlossary (\"term = translation\" means use that translation; a term alone means keep it as written):\n"
                + glossary.map { "- \($0)" }.joined(separator: "\n")
        }
        if let brief { text += "\nWhat the video is about (the project brief): \(brief)" }
        return text
    }

    func input(_ lines: [Line], before: [String]) throws -> String {
        var body: JSON = [
            "lines": lines.map { line in
                ["id": line.id, "seconds": (line.seconds * 10).rounded() / 10, "maxChars": max(8, Int(line.seconds * Double(maxCps))),
                 "text": line.text] as JSON
            },
        ]
        if !before.isEmpty { body["previousLinesAlreadyTranslated"] = before }
        let data = try JSONSerialization.data(withJSONObject: body, options: [.sortedKeys, .withoutEscapingSlashes])
        return String(decoding: data, as: UTF8.self)
    }
}

/// Gemini or OpenAI (or an OpenAI-compatible server), with the user's key and optional model and endpoint.
struct Translator {
    enum Kind: String { case gemini, openai }

    let kind: Kind
    let key: String
    let model: String
    let endpoint: String

    var label: String { "\(kind == .gemini ? "Gemini" : "OpenAI") (\(model))" }

    init(options: JSON) throws {
        kind = Kind(rawValue: options["service"] as? String ?? "gemini") ?? .gemini
        key = (options["apiKey"] as? String ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        let base = (options["endpoint"] as? String ?? "").trimmingCharacters(in: .whitespaces)
        // A local OpenAI-compatible server (an endpoint on this Mac) may need no key.
        let local = base.contains("://127.0.0.1") || base.contains("://localhost")
        guard !key.isEmpty || (kind == .openai && local) else {
            throw PluginError(
                "no_key",
                "Add your \(kind == .gemini ? "Gemini" : "OpenAI") API key in Plugins › Translate Captions, or ask your agent "
                    + "to \"translate the captions to Vietnamese\" (it translates them itself with the translate-captions skill)")
        }
        let fallback = kind == .gemini ? "gemini-flash-latest" : "gpt-5-mini"
        var chosen = (options["model"] as? String ?? "auto").trimmingCharacters(in: .whitespaces)
        if chosen == "custom" { chosen = (options["customModel"] as? String ?? "").trimmingCharacters(in: .whitespaces) }
        model = chosen.isEmpty || chosen == "auto" ? fallback : chosen
        // A model of the other service is a mistake in the options, unless the endpoint is a server of the user's own.
        if base.isEmpty, (kind == .gemini) != model.hasPrefix("gemini"), options["model"] as? String != "custom" {
            throw PluginError(
                "wrong_model",
                "\(model) is not a \(kind == .gemini ? "Gemini" : "OpenAI") model: choose a model of that service in Plugins › Translate Captions")
        }
        let service = kind == .gemini ? "https://generativelanguage.googleapis.com" : "https://api.openai.com"
        endpoint = (base.isEmpty ? service : base).trimmingCharacters(in: CharacterSet(charactersIn: "/"))
    }

    /// Translations by line ID; lines the service left out are missing.
    func translate(_ lines: [Line], style: TranslationStyle, before: [String]) throws -> [String: String] {
        let input = try style.input(lines, before: before)
        let text = kind == .gemini
            ? try gemini(system: style.instructions, user: input)
            : try openAI(system: style.instructions, user: input)
        return parseLines(text, ids: Set(lines.map(\.id)))
    }

    private func gemini(system: String, user: String) throws -> String {
        let body: JSON = [
            "systemInstruction": ["parts": [["text": system]]],
            "contents": [["role": "user", "parts": [["text": user]]]],
            "generationConfig": ["responseMimeType": "application/json", "temperature": 0.3],
        ]
        var call = URLRequest(url: try url("/v1beta/models/\(model):generateContent"))
        call.httpMethod = "POST"
        call.setValue("application/json", forHTTPHeaderField: "Content-Type")
        call.setValue(key, forHTTPHeaderField: "x-goog-api-key")
        call.httpBody = try JSONSerialization.data(withJSONObject: body)
        let answer = try sendForModel(call)
        let candidates = answer["candidates"] as? [JSON] ?? []
        let parts = (candidates.first?["content"] as? JSON)?["parts"] as? [JSON] ?? []
        let text = parts.compactMap { $0["text"] as? String }.joined()
        guard !text.isEmpty else {
            let reason = candidates.first?["finishReason"] as? String
                ?? (answer["promptFeedback"] as? JSON)?["blockReason"] as? String
            throw PluginError("no_answer", "Gemini returned no translation" + (reason.map { " (\($0))" } ?? ""))
        }
        return text
    }

    private func openAI(system: String, user: String) throws -> String {
        var body: JSON = [
            // No temperature: GPT-5 and other reasoning models accept only their default.
            "model": model, "response_format": ["type": "json_object"],
            "messages": [["role": "system", "content": system], ["role": "user", "content": user]],
        ]
        var call = URLRequest(url: try url("/v1/chat/completions"))
        call.httpMethod = "POST"
        call.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if !key.isEmpty { call.setValue("Bearer \(key)", forHTTPHeaderField: "Authorization") }
        call.httpBody = try JSONSerialization.data(withJSONObject: body)
        let answer: JSON
        do {
            answer = try sendForModel(call)
        } catch let error as PluginError where error.code == "http_400" && !error.message.contains(model) {
            // Some compatible servers do not know response_format; the instructions still ask for JSON.
            body["response_format"] = nil
            call.httpBody = try JSONSerialization.data(withJSONObject: body)
            answer = try sendForModel(call)
        }
        let choice = (answer["choices"] as? [JSON])?.first
        guard let text = (choice?["message"] as? JSON)?["content"] as? String, !text.isEmpty else {
            throw PluginError("no_answer", "OpenAI returned no translation")
        }
        return text
    }

    /// What is wrong with the key's shape, without showing it: a key of the other service, quotes or spaces, a short key.
    var keyHint: String {
        let trimmed = key.trimmingCharacters(in: CharacterSet(charactersIn: "\"' "))
        if kind == .gemini, key.hasPrefix("sk-") {
            return ". This looks like an OpenAI key: choose OpenAI as the service, or paste a Gemini key (it starts with AIza)"
        }
        if kind == .openai, key.hasPrefix("AIza") {
            return ". This looks like a Gemini key: choose Google Gemini as the service, or paste an OpenAI key (it starts with sk-)"
        }
        if trimmed != key || key.contains(" ") { return ". The key has quotes or spaces in it: paste only the key" }
        if kind == .gemini, !key.hasPrefix("AIza") || key.count != 39 {
            return ". A Gemini key starts with AIza and has 39 characters; this one has \(key.count): copy it again from Google AI Studio"
        }
        return ". Check the key in Settings › Plugins › Translate Captions"
    }

    /// Sends a call that names the model; when the service does not know the model, the error lists the ones it has.
    private func sendForModel(_ request: URLRequest) throws -> JSON {
        do {
            return try send(request)
        } catch let error as PluginError
            where error.code == "http_404" || (error.code == "http_400" && error.message.lowercased().contains("model"))
        {
            let names = (try? availableModels()) ?? []
            throw PluginError(
                "model_missing",
                "The service has no model \(model) for your key (\(error.message))"
                    + (names.isEmpty ? "" : ". Models it has: " + names.prefix(40).joined(separator: ", ")))
        }
    }

    /// The text models the key can use, from the service's model list.
    func availableModels() throws -> [String] {
        var call = URLRequest(url: try url(kind == .gemini ? "/v1beta/models?pageSize=1000" : "/v1/models"))
        if kind == .gemini {
            call.setValue(key, forHTTPHeaderField: "x-goog-api-key")
        } else if !key.isEmpty {
            call.setValue("Bearer \(key)", forHTTPHeaderField: "Authorization")
        }
        let answer = try send(call)
        if kind == .gemini {
            return (answer["models"] as? [JSON] ?? [])
                .filter { ($0["supportedGenerationMethods"] as? [String] ?? []).contains("generateContent") }
                .compactMap { ($0["name"] as? String)?.replacingOccurrences(of: "models/", with: "") }
                .filter { !$0.contains("image") && !$0.contains("tts") && !$0.contains("embedding") }.sorted()
        }
        return (answer["data"] as? [JSON] ?? []).compactMap { $0["id"] as? String }
            .filter { !["embedding", "whisper", "tts", "dall-e", "image", "audio", "realtime", "moderation", "transcribe"].contains(where: $0.contains) }
            .sorted()
    }

    private func url(_ path: String) throws -> URL {
        guard let url = URL(string: endpoint + path), url.scheme == "https" || url.host == "127.0.0.1" || url.host == "localhost"
        else { throw PluginError("bad_endpoint", "The endpoint must be an https address (or a local server)") }
        return url
    }

    private func send(_ request: URLRequest) throws -> JSON {
        var request = request
        request.timeoutInterval = 180
        var lastError: PluginError?
        for attempt in 0..<3 {
            if attempt > 0 { Thread.sleep(forTimeInterval: Double(attempt) * 2) }
            let done = DispatchSemaphore(value: 0)
            nonisolated(unsafe) var outcome: (Data?, URLResponse?, Error?)
            URLSession.shared.dataTask(with: request) { data, response, error in
                outcome = (data, response, error)
                done.signal()
            }.resume()
            done.wait()
            if let error = outcome.2 {
                lastError = PluginError("network", error.localizedDescription)
                continue
            }
            let status = (outcome.1 as? HTTPURLResponse)?.statusCode ?? 0
            let object = outcome.0.flatMap { try? JSONSerialization.jsonObject(with: $0) as? JSON } ?? [:]
            let message = ((object["error"] as? JSON)?["message"] as? String) ?? "HTTP \(status)"
            if status == 401 || status == 403 || (status == 400 && message.lowercased().contains("api key")) {
                throw PluginError("auth", "The service refused the key: \(message)" + keyHint)
            }
            if status == 429 || status >= 500 {
                lastError = PluginError("http_\(status)", message)
                continue
            }
            guard (200..<300).contains(status) else { throw PluginError("http_\(status)", message) }
            return object
        }
        throw lastError ?? PluginError("network", "The service did not answer")
    }
}

/// The `{"lines": [{"id", "text"}]}` answer (also inside a ```json fence, or as a bare array) as text by ID.
func parseLines(_ text: String, ids: Set<String>) -> [String: String] {
    var body = text.trimmingCharacters(in: .whitespacesAndNewlines)
    if body.hasPrefix("```") {
        body = body.components(separatedBy: "\n").dropFirst().joined(separator: "\n")
        if let fence = body.range(of: "```", options: .backwards) { body = String(body[..<fence.lowerBound]) }
    }
    guard let value = try? JSONSerialization.jsonObject(with: Data(body.utf8)) else { return [:] }
    let list = (value as? JSON)?["lines"] as? [JSON] ?? value as? [JSON] ?? []
    var result: [String: String] = [:]
    for entry in list {
        let id = entry["id"].map { "\($0)" } ?? ""
        guard ids.contains(id), let line = entry["text"] as? String else { continue }
        let clean = line.replacingOccurrences(of: "\n", with: " ").trimmingCharacters(in: .whitespacesAndNewlines)
        if !clean.isEmpty { result[id] = clean }
    }
    return result
}

/// Settings asks before saving the API key (host feature `options.check`): the key's shape for the chosen service
/// first, then the service's model list, which costs nothing and proves the key works.
func checkOption(_ params: JSON) -> JSON {
    guard params["option"] as? String == "apiKey" else { return ["ok": true] }
    var options = params["options"] as? JSON ?? [:]
    options["apiKey"] = params["value"] as? String ?? ""
    let service: Translator
    do {
        service = try Translator(options: options)
    } catch let error as PluginError {
        return ["ok": false, "message": error.code == "no_key" ? "The key is empty" : error.message]
    } catch {
        return ["ok": false, "message": "\(error)"]
    }
    let hint = service.keyHint
    if !hint.hasPrefix(". Check the key") {
        return ["ok": false, "message": String(hint.dropFirst(2))]
    }
    let name = service.kind == .gemini ? "Gemini" : "OpenAI"
    do {
        let models = try service.availableModels()
        return ["ok": true, "message": "\(name) accepts the key (\(models.count) text models)"]
    } catch let error as PluginError where error.code == "auth" {
        return ["ok": false, "message": "\(name) refused the key: " + error.message.replacingOccurrences(of: "The service refused the key: ", with: "")]
    } catch {
        return ["ok": true, "message": "Saved without a check: \(name) did not answer (\((error as? PluginError)?.message ?? "\(error)"))"]
    }
}
