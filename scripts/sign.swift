// Signs archive digests with the BashCut publisher key (ed25519, CryptoKit — the same code BashCut verifies with).
//
//     BASHCUT_SIGNING_KEY=<base64 raw 32-byte private key> swift scripts/sign.swift <sha256-hex>...
//
// Prints one `ed25519:BASE64` signature per digest, over the digest's 32 raw bytes. `--public-key` prints the
// public key instead.
import CryptoKit
import Foundation

func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data("error: \(message)\n".utf8))
    exit(1)
}

guard let encoded = ProcessInfo.processInfo.environment["BASHCUT_SIGNING_KEY"], let raw = Data(base64Encoded: encoded),
    let key = try? Curve25519.Signing.PrivateKey(rawRepresentation: raw)
else { fail("BASHCUT_SIGNING_KEY must hold a base64 ed25519 private key") }

let arguments = Array(CommandLine.arguments.dropFirst())
if arguments == ["--public-key"] {
    print("ed25519:" + key.publicKey.rawRepresentation.base64EncodedString())
    exit(0)
}
for digest in arguments {
    let characters = Array(digest)
    guard characters.count == 64 else { fail("\(digest) is not a SHA-256 hex digest") }
    let bytes = stride(from: 0, to: 64, by: 2).compactMap { UInt8(String(characters[$0...$0 + 1]), radix: 16) }
    guard bytes.count == 32, let signature = try? key.signature(for: Data(bytes)) else { fail("cannot sign \(digest)") }
    print("ed25519:" + signature.base64EncodedString())
}
