# {{NAME}}: provides {{CAPABILITY}} (provider {{PROVIDER_ID}}).
#
# BashCut calls `handle "{{CAPABILITY}}"` whenever this provider is chosen; print the JSON result. The placeholder
# below returns a valid result so the plugin works end to end; replace it with the real work. Params and result
# rules: https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#capabilities

handle() {
    [ "$1" = "{{CAPABILITY}}" ] || bc_fail unknown_method "{{PLAIN_NAME}} does not handle $1"
# @@ voice.synthesize
    # params: text, language, outputDirectory, takeCount, takeOffset (+ options). Placeholder: the Mac's own voice.
    text="$(bc_get params.text)" || bc_fail bad_request "No text"
    folder="$(bc_get params.outputDirectory)" || bc_fail bad_request "No outputDirectory"
    count="$(bc_get params.takeCount || echo 1)"
    offset="$(bc_get params.takeOffset || echo 0)"
    takes=""
    index=0
    while [ "$index" -lt "$count" ]; do
        path="$folder/take-$((offset + index + 1)).aiff"
        bc_progress "$index/$count" "Take $((index + 1))"
        say -o "$path" "$text" >&2 || bc_fail say_failed "say could not make $path"
        takes="$takes${takes:+,}{\"audioPath\":$(bc_str "$path")}"
        index=$((index + 1))
    done
    printf '{"takes":[%s]}' "$takes"
# @@ captions.transcribe
    # params: mediaPath, language, outputDirectory, optional startSeconds/endSeconds. Placeholder: one cue.
    folder="$(bc_get params.outputDirectory)" || bc_fail bad_request "No outputDirectory"
    start="$(bc_get params.startSeconds || echo 0)"
    srt="$folder/captions.srt"
    printf '1\n%s --> %s\nReplace this with the transcription\n' "$(timestamp "$start")" \
        "$(timestamp "$(awk -v s="$start" 'BEGIN { print s + 2 }')")" > "$srt"
    printf '{"srtPath":%s}' "$(bc_str "$srt")"
# @@ audio.beats
    # params: mediaPath. Placeholder: a steady 120 BPM grid over the first 4 seconds.
    printf '{"bpm":120,"beatsSeconds":[0.5,1,1.5,2,2.5,3,3.5,4]}'
# @@ audio.loudness
    # params: mediaPath, optional bands. Placeholder numbers; measure the file here.
    printf '{"integratedLUFS":-16.0,"truePeakDbTP":-1.5}'
# @@ audio.sync
    # params: mediaPath, otherPath. Placeholder: no offset found.
    printf '{"offsetSeconds":0,"correlation":0}'
# @@ end
}
# @@ captions.transcribe

# timestamp <seconds>: SubRip time, such as 00:00:02,000.
timestamp() {
    awk -v s="$1" 'BEGIN { m = int(s * 1000 + 0.5); printf "%02d:%02d:%02d,%03d", int(m / 3600000), int(m / 60000) % 60, int(m / 1000) % 60, m % 1000 }'
}
# @@ end
