#!/bin/sh
# Builds bin/encode-alpha, a universal (arm64 + x86_64) binary that turns HyperFrames' RGBA PNG frames into a .mov
# with alpha (HEVC with alpha or ProRes 4444) with AVFoundation, so users need no FFmpeg. CI and package.py run it
# before the tests and before packaging; run it locally after changing src/.
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
build="$(mktemp -d)"
trap 'rm -rf "$build"' EXIT
for arch in arm64 x86_64; do
    swiftc -O -swift-version 5 -target "$arch-apple-macos13" -o "$build/encode-alpha-$arch" "$here/src/encode-alpha.swift"
done
mkdir -p "$here/bin"
lipo -create "$build/encode-alpha-arm64" "$build/encode-alpha-x86_64" -output "$here/bin/encode-alpha"
codesign --force --sign - "$here/bin/encode-alpha" 2>/dev/null || true
echo "Built $here/bin/encode-alpha ($(lipo -archs "$here/bin/encode-alpha"))"
