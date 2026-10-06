# Review Check Example

A sample `review.check` provider for BashCut (plugin API 9), in one Python file with no dependencies. It adds two
rules to BashCut's review:

- **Brand fonts**: on-screen text drawn with a font outside the `fonts` option (a comma-separated list; empty turns
  the rule off) is a warning, once per font.
- **Call to action**: no text in the last `ctaSeconds` (default 5) that asks the viewer to follow, subscribe,
  comment or buy (English and Vietnamese words) is a note.

It is a sample: never published to the registry (the registry refuses `python3` plugins for end users).

## Try it

```sh
scripts/dev-link.sh samples/review-check-example
```

Open **Plugins** in BashCut and choose **Trust**. Then, in a project:

```sh
bashcut review measure            # a job: renders the picture checks and runs every plugin review check
bashcut jobs status <job>
bashcut review run --summary      # plugin issues have "source": "example.review-check"
bashcut plugins hooks             # reviewChecks lists the check and whether this project enables it
```

In the app, the Review sheet's **Measure picture** runs the same job; plugin issues show *From plugin …*. A project
turns the check off with `review.disabledChecks`:

```sh
echo '[{"op":"setProjectProperties","patch":{"review":{"disabledChecks":["example.review-check"]}}}]' > ops.json
bashcut timeline apply ops.json --base-rev <rev> --label "No brand check"
```

Run its tests with `python3 -m unittest discover -s samples/review-check-example/tests`.

## How a check works

BashCut starts `bin/provider rpc` with one JSON request on stdin and reads one JSON line back:

```json
{"id": "…", "apiVersion": 9, "method": "review.check", "provider": "example.review-check.rules",
 "params": {"project": {…}, "revision": 12, "fps": 30, "duration": 900, "width": 1080, "height": 1920,
            "projectRoot": "/…/my-video", "options": {"fonts": "Be Vietnam Pro", "ctaSeconds": 5}}}
```

```json
{"id": "…", "result": {"issues": [{"id": "cta", "title": "No call to action at the end",
  "detail": "…", "frame": 750, "endFrame": 900, "severity": "info", "fix": {"hint": "Add an end card…"}}]}}
```

`id`, `title` and `frame` are required; `detail`, `endFrame`, `severity` (`error`, `warning` — the default — or
`info`) and `fix` (`command` + `arguments`, and/or `hint`) are optional; at most 50 issues count. BashCut prefixes each
ID with the provider ID and adds the plugin as `source`. A check gets 30 seconds at most (this one asks for 10 with
`timeoutSeconds`); a crash, a malformed answer or a timeout becomes one info issue ("Plugin check failed") and never
stops the review.
