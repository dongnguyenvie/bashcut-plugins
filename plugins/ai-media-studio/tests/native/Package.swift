// swift-tools-version: 6.0
import PackageDescription
import Foundation
let core = ProcessInfo.processInfo.environment["BASHCUT_CORE_PATH"] ?? "../../../../../BashCut/Packages/BashCutCore"
let package = Package(name: "StudioNativeValidation", platforms: [.macOS(.v14)],
    dependencies: [.package(path: core)],
    targets: [.executableTarget(name: "StudioValidation", dependencies: [
        .product(name: "BashCutProject", package: "BashCutCore"),
        .product(name: "BashCutPlugin", package: "BashCutCore")])])
