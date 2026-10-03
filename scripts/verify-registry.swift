// Checks every signature in registry.json against its publisher's keys, as BashCut does before installing.
//
//     swift scripts/verify-registry.swift registry.json
//
// `bashcut` versions must be signed (with a key listed under publishers.bashcut.keys, which mirrors the key compiled
// into BashCut); other publishers' signatures, when present, must match their listed keys.
import CryptoKit
import Foundation

func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data("error: \(message)\n".utf8))
    exit(1)
}

func decode(_ text: String) -> Data? {
    text.hasPrefix("ed25519:") ? Data(base64Encoded: String(text.dropFirst(8))) : nil
}

let path = CommandLine.arguments.dropFirst().first ?? "registry.json"
guard let data = FileManager.default.contents(atPath: path),
    let registry = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
else { fail("cannot read \(path)") }
let publishers = registry["publishers"] as? [String: [String: Any]] ?? [:]
var checked = 0
for plugin in registry["plugins"] as? [[String: Any]] ?? [] {
    let id = plugin["id"] as? String ?? "?"
    let publisher = plugin["publisher"] as? String ?? ""
    let keys = (publishers[publisher]?["keys"] as? [String] ?? []).compactMap(decode)
        .compactMap { try? Curve25519.Signing.PublicKey(rawRepresentation: $0) }
    for version in plugin["versions"] as? [[String: Any]] ?? [] {
        let name = "\(id) \(version["version"] as? String ?? "?")"
        guard let signature = version["signature"] as? String else {
            if publisher == "bashcut" { fail("\(name) is not signed") }
            continue
        }
        let hex = Array(version["sha256"] as? String ?? "")
        let digest = Data(stride(from: 0, to: hex.count - 1, by: 2).compactMap { UInt8(String(hex[$0...$0 + 1]), radix: 16) })
        guard digest.count == 32, let bytes = decode(signature), keys.contains(where: { $0.isValidSignature(bytes, for: digest) })
        else { fail("\(name): the signature does not match \(publisher)'s keys") }
        checked += 1
    }
}
print("\(checked) signatures verified")
