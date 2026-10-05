# The BashCut plugin protocol for {{NAME}} (POSIX sh and macOS built-ins only). You rarely need to change this file.
#
# BashCut runs `bin/provider rpc`, writes one JSON request to stdin and reads one JSON response from stdout. The
# provider saves the request to "$BC_REQUEST" and calls `handle <method>` from handlers.sh, which prints the JSON
# result. Helpers for handlers:
#   bc_get <key.path>       a value from the request, such as `bc_get params.context.playhead` (exit 1 when missing)
#   bc_json <key.path>      the same value as JSON (objects and arrays)
#   bc_count <key.path>     how many items an array has (0 when missing)
#   bc_str <text>           <text> as a JSON string, quotes included
#   bc_progress <0…1> <msg> a progress note on stderr (the one-shot transport has no progress channel)
#   bc_fail <code> <msg>    fail the request with a stable code and a message
# Only diagnostics go to stderr; stdout carries the response.

# plutil prints its errors on stdout, so a value is printed only when the extraction worked.
bc_get() {
    bc_value="$(plutil -extract "$1" raw -o - "$BC_REQUEST" 2>/dev/null)" || return 1
    printf '%s' "$bc_value"
}

bc_json() {
    bc_value="$(plutil -extract "$1" json -o - "$BC_REQUEST" 2>/dev/null)" || return 1
    printf '%s' "$bc_value"
}

bc_count() {
    count=0
    while plutil -extract "$1.$count" json -o /dev/null "$BC_REQUEST" >/dev/null 2>&1; do
        count=$((count + 1))
    done
    echo "$count"
}

bc_str() {
    printf '%s' "$1" | awk 'BEGIN { ORS = ""; printf "\"" }
        { if (NR > 1) printf "\\n"; gsub(/\\/, "\\\\"); gsub(/"/, "\\\""); gsub(/\t/, "\\t"); gsub(/\r/, "\\r"); print }
        END { printf "\"" }'
}

bc_progress() {
    echo "progress $1 ${2:-}" >&2
}

bc_fail() {
    printf '%s' "$1" > "$BC_WORK/error-code"
    printf '%s' "$2" > "$BC_WORK/error-message"
    exit 1
}

bc_run() {
    BC_WORK="$(mktemp -d "${TMPDIR:-/tmp}/bashcut-plugin.XXXXXX")"
    trap 'rm -rf "$BC_WORK"' EXIT
    BC_REQUEST="$BC_WORK/request.json"
    if [ "${1:-rpc}" != "rpc" ]; then
        echo "This plugin speaks only the one-shot transport (bin/provider rpc)" >&2
        exit 2
    fi
    IFS= read -r line || [ -n "$line" ] || { echo "expected one JSON request on stdin" >&2; exit 2; }
    printf '%s\n' "$line" > "$BC_REQUEST"
    id="$(bc_get id)" || { echo "the request has no id" >&2; exit 2; }
    method="$(bc_get method)"
    if result="$(handle "$method")"; then
        [ -n "$result" ] || result='{}'
        printf '{"id":%s,"result":%s}\n' "$(bc_str "$id")" "$result"
    else
        code="$(cat "$BC_WORK/error-code" 2>/dev/null || echo failed)"
        message="$(cat "$BC_WORK/error-message" 2>/dev/null || echo "$method failed")"
        printf '{"id":%s,"error":{"code":%s,"message":%s}}\n' "$(bc_str "$id")" "$(bc_str "$code")" "$(bc_str "$message")"
    fi
}
