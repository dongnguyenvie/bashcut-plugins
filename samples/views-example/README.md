# Views Example

A sample of plugin views for BashCut (plugin API 8), in one Python file with no dependencies. It shows the three
places a view can live:

- **Components** (`gallery`, the rail panel): every view component — text and markdown, badges, key/value rows, progress, buttons
  (with `confirm`), a live search field, toggle, picker, slider, text area, a list with selection and row buttons,
  images, a before/after comparison and an audio preview — and how events and `state` work. The newer colour well
  (`colorPicker`) and font menu (`fontPicker`, by family) show only when the hello's `features` list
  `views.colorPicker` / `views.fontPicker`; an older BashCut gets text fields. The image drags its `file` onto the
  timeline (`views.drag`).
- **Voice** (`voice`, `"location": "dock"`: a tab in the agent dock on the right): how a plugin reuses other plugins without knowing them. It generates speech with
  `voice.speak` (BashCut picks the user's `voice.synthesize` plugin, such as VieNeu TTS), measures a take's loudness
  with `plugins.invoke` (`audio.loudness`, listed in `uses`) and places the chosen take with `voice.place`. Its
  **Voice plugin** picker lists the `voice.synthesize` providers (`capabilities.get`) and saves the choice in the
  plugin's own `provider` option with the host call `plugins.option` (host feature `options.set`), so the tab
  opens with it next time and Settings shows it.
- **Live** (`live`, the rail panel): **Mark the playhead** sets overlays on the timeline and viewer (a marker, a
  3-second range and a region, host call `plugins.set-overlays`, feature `overlays`); **Clear marks** sends `[]`.
  **Count to five in the background** answers at once and keeps redrawing the view from a thread with
  `{"type": "viewUpdate", "view": "live", "body": …}` lines (feature `viewUpdate`) until it is done.

- **Title card** (`titleCard`, `"location": "sheet"`): a short form in a sheet. The gallery's button and the
  **New title card…** action open it with the host call `plugins.show-view`; the answer `"close": true` closes it.

It also has a Tools action (**Say hello**) that calls BashCut while it runs, a skill for agents, and
`requires` on the built-in `bashcut.audio-analysis` plugin.

It is a sample: never published to the registry (the registry refuses `python3` plugins for end users). Its manifest
has `"category": "sample"`, so BashCut hides it (rail, menus, Plugins) until **Settings › General › Developer mode** is on;
the command line and agents still reach it.

## Try it

```sh
scripts/dev-link.sh samples/views-example
```

Open **Plugins** in BashCut, choose **Trust**, then click the new icon under the panels on the left. From the
command line (or an agent):

```sh
bashcut plugins list --views
bashcut plugins view bashcut.views-example --view gallery --open
bashcut plugins view-event bashcut.views-example --view gallery --node add
bashcut plugins view-event bashcut.views-example --view gallery --node query --type change --value coffee
bashcut plugins show-view bashcut.views-example --view titleCard
bashcut plugins view-event bashcut.views-example --view live --node mark
bashcut plugins overlays bashcut.views-example
bashcut plugins view-event bashcut.views-example --view voice --node provider --type change --value bashcut.vieneu-tts.synthesize
bashcut plugins options bashcut.views-example
```

Run its tests with `python3 -m unittest discover -s samples/views-example/tests`.

## How a view works

1. BashCut sends `view.render` with `{view, state, values, locale, context, options}` when the panel shows the view.
2. The plugin answers `{title, body: [components], state}`. BashCut draws the components natively; no plugin code
   runs in the app.
3. When the user clicks, types or selects, BashCut sends `view.event` with the same fields plus
   `event: {node, type, value}`. The plugin answers with the whole new view.
4. While working, the plugin may send `{"type":"event","event":{"kind":"render","body":[…]}}` to show progress, and
   `{"type":"call","method":…}` to run a BashCut command (`Request.call` in `bin/provider`). Commands that take long
   answer `{"job": id}`; poll `jobs.status` (`Request.wait_job`).

Outside a request, the plugin may write `{"type": "viewUpdate", "view": "<id>", "body": […], "state"?, "notify"?}`
(a whole view answer for one of its views; drawn only while that view is on screen) and
`{"type": "overlays", "overlays": […]}` (the whole set of its marks). Both are new host features: check them in the
hello's `features`, as `live` does.

Keep what the view needs in `state` (64 KiB at most). BashCut only renders views that are on screen, sends one
request per view at a time and merges fast typing, so a plain request/answer plugin stays responsive.

The full reference (every component and field, limits, commands) is in BashCut's plugin guide:
[Plugin panels and views](https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#plugin-panels-and-views)
and [Using other plugins](https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#using-other-plugins).
