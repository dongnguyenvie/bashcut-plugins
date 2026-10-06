---
name: views-example
description: Drive the Views Example plugin panel from the command line — render its views, click buttons, type in inputs, and generate voice takes through the user's voice plugin. Use when testing plugin views, showing how plugin panels work, or when the user asks to try the Views Example plugin. Triggers: "views example", "ví dụ giao diện", "thử plugin view", "plugin panel".
---

# Views Example

The plugin adds a panel to BashCut's left rail with two views: `gallery` (every view component) and `voice`
(generates speech with whichever voice plugin the user installed).

## Look at a view

```sh
bashcut plugins views
bashcut plugins view bashcut.views-example --view gallery --open
```

`plugins view` returns the components with their ids and the current input values.

## Act like the user

```sh
bashcut plugins view-event bashcut.views-example --view gallery --node add
bashcut plugins view-event bashcut.views-example --view gallery --node query --type change --value coffee
bashcut plugins view-event bashcut.views-example --view gallery --node shots --type select --value s2
```

## Voice takes

```sh
bashcut plugins view-event bashcut.views-example --view voice --node text --type change --value "Xin chào"
bashcut plugins view-event bashcut.views-example --view voice --node speak
```

The second command waits while the voice plugin works. It needs a `voice.synthesize` plugin (such as VieNeu TTS);
without one, the view says so — suggest `bashcut plugins search --capability voice.synthesize`.

## Limits

- The user must Trust the plugin in Plugins first.
- `--type action --value '{"item": "<take path>", "action": "use"}'` places a take on the timeline (undoable).
