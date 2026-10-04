import CryptoKit
import Foundation

private struct ProviderFailure: Error {
    let code: String
    let message: String
    init(_ code: String, _ message: String) {
        self.code = code
        self.message = message
    }
}

private func requiredString(_ key: String, in object: [String: Any]) throws -> String {
    guard let value = object[key] as? String, !value.isEmpty else {
        throw ProviderFailure("invalid_params", "Missing \(key)")
    }
    return value
}

private func canonical(_ path: String) -> String {
    URL(fileURLWithPath: path).standardizedFileURL.resolvingSymlinksInPath().path
}

private func workingFolder(_ params: [String: Any]) throws -> URL {
    let rootPath = try requiredString("agentFolder", in: params)
    guard rootPath.hasPrefix("/") else { throw ProviderFailure("invalid_params", "agentFolder must be absolute") }
    let project = params["project"] as? String
    let key: String
    if let project, !project.isEmpty {
        let digest = SHA256.hash(data: Data(canonical(project).utf8))
        key = digest.prefix(8).map { String(format: "%02x", $0) }.joined()
    } else {
        key = "no-project"
    }
    return URL(fileURLWithPath: rootPath, isDirectory: true)
        .appendingPathComponent("projects/\(key)", isDirectory: true)
}

private func writePrivate(_ data: Data, to url: URL) throws {
    try data.write(to: url, options: .atomic)
    try FileManager.default.setAttributes([.posixPermissions: 0o600], ofItemAtPath: url.path)
}

private func launch(_ params: [String: Any]) throws -> [String: Any] {
    let folder = try workingFolder(params)
    let agents = folder.appendingPathComponent(".agents", isDirectory: true)
    let manager = FileManager.default
    try manager.createDirectory(at: agents, withIntermediateDirectories: true,
                                attributes: [.posixPermissions: 0o700])
    try manager.setAttributes([.posixPermissions: 0o700], ofItemAtPath: folder.path)
    try manager.setAttributes([.posixPermissions: 0o700], ofItemAtPath: agents.path)

    guard let mcp = params["mcp"] as? [String: Any],
          let name = mcp["name"] as? String,
          let command = mcp["command"] as? String,
          let arguments = mcp["arguments"] as? [String],
          let names = mcp["environment"] as? [String]
    else { throw ProviderFailure("invalid_params", "Missing MCP launch configuration") }
    let environment = Dictionary(uniqueKeysWithValues: names.map { ($0, "$" + $0) })
    let config: [String: Any] = [
        "mcpServers": [name: ["command": command, "args": arguments, "env": environment]],
    ]
    let configData = try JSONSerialization.data(withJSONObject: config, options: [.sortedKeys])
    try writePrivate(configData, to: agents.appendingPathComponent("mcp_config.json"))

    let prompt = try requiredString("prompt", in: params)
    let workspace = try requiredString("workspace", in: params)
    let notes = """
        # BashCut editing agent

        \(prompt)

        Use the BashCut MCP server to inspect and edit the open project. The footage workspace is
        \(workspace). Ask for access before reading files outside this working folder.
        Use the bashcut-* skills when a task matches them.
        """
    try writePrivate(Data(notes.utf8), to: folder.appendingPathComponent("AGENTS.md"))

    let options = params["options"] as? [String: Any] ?? [:]
    let resume = params["resume"] as? String ?? ""
    let bypass = options["bypassPermissions"] as? Bool ?? false
    let argv = (resume.isEmpty ? [] : ["--continue"])
        + (bypass ? ["--dangerously-skip-permissions"] : [])
    return [
        "executable": "agy", "arguments": argv, "directory": folder.path,
        "skillsFolder": agents.appendingPathComponent("skills", isDirectory: true).path,
    ]
}

private func session(_ params: [String: Any]) throws -> [String: Any] {
    let folder = try workingFolder(params)
    let home = ProcessInfo.processInfo.environment["HOME"]
        .map { URL(fileURLWithPath: $0, isDirectory: true) }
        ?? FileManager.default.homeDirectoryForCurrentUser
    let cache = home
        .appendingPathComponent(".gemini/antigravity-cli/cache/last_conversations.json")
    if let earliest = params["notBefore"] as? Double {
        guard let modified = try? cache.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate,
              modified.timeIntervalSince1970 >= earliest - 2
        else { return ["id": NSNull()] }
    }
    guard let data = try? Data(contentsOf: cache), data.count <= 2_000_000,
          let values = try? JSONDecoder().decode([String: String].self, from: data),
          let id = values[canonical(folder.path)], UUID(uuidString: id) != nil
    else { return ["id": NSNull()] }
    return ["id": id.lowercased()]
}

private func respond(_ value: [String: Any]) {
    guard let data = try? JSONSerialization.data(withJSONObject: value) else { return }
    FileHandle.standardOutput.write(data + Data([0x0A]))
}

do {
    guard let line = readLine(), let data = line.data(using: .utf8),
          let request = try JSONSerialization.jsonObject(with: data) as? [String: Any],
          let id = request["id"] as? String,
          let params = request["params"] as? [String: Any]
    else { throw ProviderFailure("invalid_params", "Invalid agent.terminal request") }
    do {
        let result: [String: Any]
        switch params["op"] as? String {
        case "launch": result = try launch(params)
        case "session": result = try session(params)
        default: throw ProviderFailure("unknown_op", "Unknown terminal operation")
        }
        respond(["id": id, "result": result])
    } catch let failure as ProviderFailure {
        respond(["id": id, "error": ["code": failure.code, "message": failure.message]])
    } catch {
        respond(["id": id, "error": ["code": "failed", "message": error.localizedDescription]])
    }
} catch {
    respond(["id": "", "error": ["code": "invalid_params", "message": "Invalid agent.terminal request"]])
}
