import Foundation
import BashCutProject
import BashCutPlugin
let manifest = try JSONDecoder().decode(PluginManifest.self, from: Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments[1])))
try manifest.validate()
let project = try JSONDecoder().decode(Project.self, from: Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments[2])))
let encoded = try JSONDecoder().decode([JSONValue].self, from: Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments[3])))
let ops = try encoded.map { try EditOperation(json: $0) }
let result = try project.applying(.group(label: "Studio scene build", author: .plugin, ops: ops), baseRevision: project.revision)
try result.project.validate()
precondition(result.project.revision == project.revision + 1)
let undone = try result.project.applying(result.inverse).project
precondition(undone.tracks == project.tracks && undone.media == project.media)
print("Native API 8 manifest and atomic scene edit validated; one undo restores all tracks and media.")
