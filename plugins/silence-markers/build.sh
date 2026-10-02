#!/bin/sh
# Builds bin/provider, a universal (arm64 + x86_64) binary that needs nothing beyond macOS 13.
# CI runs it before the tests and before packaging; run it locally after changing src/.
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
build="$(mktemp -d)"
trap 'rm -rf "$build"' EXIT
for arch in arm64 x86_64; do
    swiftc -O -swift-version 5 -target "$arch-apple-macos13" -o "$build/provider-$arch" "$here/src/main.swift"
done
mkdir -p "$here/bin"
lipo -create "$build/provider-arm64" "$build/provider-x86_64" -output "$here/bin/provider"
codesign --force --sign - "$here/bin/provider" 2>/dev/null || true
echo "Built $here/bin/provider ($(lipo -archs "$here/bin/provider"))"
