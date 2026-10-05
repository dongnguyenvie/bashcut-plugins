# {{NAME}}: options of every kind, read by the action {{ACTION_ID}}.
#
# BashCut draws the options in Settings › Plugins and sends their current values as params.options with every
# request. The secret (apiKey) comes from the Keychain: use it, never print or return it.
# https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#options

handle() {
    [ "$1" = "plugin.action" ] || bc_fail unknown_method "{{PLAIN_NAME}} does not handle $1"
    action="$(bc_get params.action)"
    [ "$action" = "{{ACTION_ID}}" ] || bc_fail unknown_action "Unknown action $action"
    greeting="$(bc_get params.options.greeting)"
    [ -n "$greeting" ] || greeting="Hello"
    [ "$(bc_get params.options.shout)" = "true" ] && greeting="$(printf '%s' "$greeting" | tr '[:lower:]' '[:upper:]')"
    repeat="$(bc_get params.options.repeat || echo 1)"
    words="$greeting"
    while [ "$repeat" -gt 1 ]; do
        words="$words $greeting"
        repeat=$((repeat - 1))
    done
    style="$(bc_get params.options.style || echo short)"
    key_set=false
    [ -n "$(bc_get params.options.apiKey)" ] && key_set=true
    message="$words"
    if [ "$style" = "long" ]; then
        state="not set"
        [ "$key_set" = true ] && state="set"
        message="$words (style long, API key $state)"
    fi
    printf '{"message":%s,"data":{"greeting":%s,"style":%s,"apiKeySet":%s}}' \
        "$(bc_str "$message")" "$(bc_str "$words")" "$(bc_str "$style")" "$key_set"
}
