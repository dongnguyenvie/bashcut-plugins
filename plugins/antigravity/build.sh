#!/bin/sh
# Ship a native universal provider; users do not need Swift, Python or Node to run the plugin.
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
build="$(mktemp -d)"
trap 'rm -rf "$build"' EXIT
for arch in arm64 x86_64; do
    swiftc -O -swift-version 5 -target "$arch-apple-macos14" -o "$build/provider-$arch" "$here/src/main.swift"
done
mkdir -p "$here/bin"
lipo -create "$build/provider-arm64" "$build/provider-x86_64" -output "$here/bin/provider"
codesign --force --sign - "$here/bin/provider" 2>/dev/null || true
echo "Built $here/bin/provider ($(lipo -archs "$here/bin/provider"))"
