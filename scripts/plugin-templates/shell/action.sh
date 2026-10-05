# {{NAME}}: the action {{ACTION_ID}}.
#
# BashCut calls `handle plugin.action` when someone runs the action (menu, context menu, shortcut,
# `bashcut plugins run`); print the JSON result. It only *proposes* operations in the `timeline apply` format;
# BashCut validates them and applies one undoable edit.
# https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#actions

handle() {
    [ "$1" = "plugin.action" ] || bc_fail unknown_method "{{PLAIN_NAME}} does not handle $1"
    action="$(bc_get params.action)"
    case "$action" in
        {{ACTION_ID}}) add_marker ;;
        *) bc_fail unknown_action "Unknown action $action" ;;
    esac
}

add_marker() {
    label="$(bc_get params.params.label)"
    [ -n "$label" ] || label="Marker"
    frame="$(bc_get params.context.playhead)" || bc_fail bad_request "No playhead"
    rev="$(bc_get params.context.project.rev)" || bc_fail bad_request "No project revision"
    id="$(uuidgen)"
    printf '{"label":"Add marker","baseRev":%s,"operations":[{"op":"upsertSection","id":"%s","label":%s,"atFrame":%s}],"ui":{"reveal":%s},"message":%s}' \
        "$rev" "$id" "$(bc_str "$label")" "$frame" "$frame" "$(bc_str "Added $label at frame $frame")"
}
