# Views Example

A sample plugin panel for BashCut (plugin API 8), in one Python file with no dependencies. It adds an icon to the
left rail that opens a panel with two views:

- **Components** (`gallery`): every view component — text and markdown, badges, key/value rows, progress, buttons
  (with `confirm`), a live search field, toggle, picker, slider, text area, a list with selection and row buttons,
  images, a before/after comparison and an audio preview — and how events and `state` work.
- **Voice** (`voice`): how a plugin reuses other plugins without knowing them. It generates speech with
  `voice.speak` (BashCut picks the user's `voice.synthesize` plugin, such as VieNeu TTS), measures a take's loudness
  with `plugins.invoke` (`audio.loudness`, listed in `uses`) and places the chosen take with `media.import`.

It also has a Tools action (**Say hello**) that calls BashCut while it runs, a skill for agents, and
`requires` on the built-in `bashcut.audio-analysis` plugin.

It is a sample: never published to the registry (the registry refuses `python3` plugins for end users).

## Try it

```sh
scripts/dev-link.sh samples/views-example
```

Open **Plugins** in BashCut, choose **Trust**, then click the new icon under the panels on the left. From the
command line (or an agent):

```sh
bashcut plugins views
bashcut plugins view bashcut.views-example --view gallery --open
bashcut plugins view-event bashcut.views-example --view gallery --node add
bashcut plugins view-event bashcut.views-example --view gallery --node query --type change --value coffee
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

Keep what the view needs in `state` (64 KiB at most). BashCut only renders views that are on screen, sends one
request per view at a time and merges fast typing, so a plain request/answer plugin stays responsive.

The full reference (every component and field, limits, commands) is in BashCut's plugin guide:
[Plugin panels and views](https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#plugin-panels-and-views)
and [Using other plugins](https://github.com/dongnguyenvie/BashCut/blob/main/docs/guides/plugins.md#using-other-plugins).
