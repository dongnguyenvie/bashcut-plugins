# {{NAME}}: hooks on export.finished and media.imported.
#
# BashCut calls `handle plugin.hook` after an event; print the JSON result. Hooks are notify-only: the event already
# happened. A hook declared with "edits": true may return operations or pluginData, which BashCut applies as one
# undoable edit (or keeps for review). https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#hooks

handle() {
    [ "$1" = "plugin.hook" ] || bc_fail unknown_method "{{PLAIN_NAME}} does not handle $1"
    case "$(bc_get params.event)" in
        export.finished)
            # Count exports in this plugin's own project data.
            exports="$(bc_get params.context.pluginData.exports || echo 0)"
            output="$(bc_get params.payload.output)"
            printf '{"label":"Remember last export","pluginData":{"lastExport":%s,"exports":%s},"message":%s}' \
                "$(bc_str "$output")" "$((exports + 1))" "$(bc_str "Exported $(basename "$output") (export $((exports + 1)))")"
            ;;
        media.imported)
            printf '{"message":%s}' "$(bc_str "Imported $(bc_count params.payload.media) media")"
            ;;
        *) printf '{}' ;;
    esac
}
