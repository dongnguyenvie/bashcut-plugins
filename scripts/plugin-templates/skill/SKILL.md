---
name: {{SLUG}}
description: What {{NAME}} does for an edit and when an agent should use it. Use when the user asks for … Triggers: "…", "…".
---

# {{NAME}}

{{SUMMARY}} This skill tells agents when and how to use it; BashCut gives it to them while the plugin
`{{ID}}` is trusted and turned on.

## When to use it

- The situations where this plugin is the right tool, and the ones where another tool is better.

## How

1. The exact `bashcut` commands, in order: for an action `bashcut plugins run {{ID}}.<action> --params '{…}'`,
   for a capability the command that uses it (for example `bashcut captions generate`), and
   `bashcut plugins options {{ID}}` for the options that matter.
2. What to check afterwards (`bashcut timeline get`, `bashcut jobs status`, `bashcut ui frame`).

## Limits

- What the plugin cannot do, what needs the user (Trust, Install Dependencies…), and what to tell them when it fails.
