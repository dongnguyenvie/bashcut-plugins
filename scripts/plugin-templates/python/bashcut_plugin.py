"""The BashCut plugin protocol for {{NAME}} (Python standard library only). You rarely need to change this file.

BashCut runs the entrypoint as `provider rpc` (one JSON request on stdin, one JSON response on stdout) or, with
"transport": "session" in plugin.json, as `provider session` (newline-delimited JSON until it says shutdown).
Handlers get a `Host` to report progress, stream chat events and call BashCut commands. Diagnostics go to stderr:
stdout carries only protocol lines.
"""
import collections
import json
import sys
import threading
import time

# The host features the session hello listed (API 8), such as "views.colorPicker" or "overlays". Check one before
# using what it names, so the plugin still works in an older BashCut. Empty over the one-shot transport.
HOST_FEATURES = set()
_SEND_LOCK = threading.Lock()


class PluginError(Exception):
    """A failure with a stable code BashCut can show, such as PluginError("model_missing", "Install the model")."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


class Cancelled(Exception):
    """BashCut cancelled the request (session transport only)."""


def send(message):
    with _SEND_LOCK:  # a background thread may send view updates while a request answers
        sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
        sys.stdout.flush()


def view_update(view, answer):
    """Redraws one of the plugin's views outside a request (session transport, host feature `viewUpdate`): `answer`
    is a whole view answer ({"body", "title"?, "state"?, "notify"?}). BashCut draws it only while the view is on
    screen and drops updates beyond about ten a second; an older BashCut ignores the line."""
    send({"type": "viewUpdate", "view": view, **answer})


def send_overlays(overlays):
    """Replaces the plugin's marks on the timeline and viewer at any time (host feature `overlays`); [] clears them.
    From a request, host.call("plugins.set-overlays", …) does the same and reports a bad set."""
    send({"type": "overlays", "overlays": overlays})


class Host:
    """What a handler can do while its request runs."""

    def __init__(self, request_id, session=None):
        self.request_id = request_id
        self.session = session
        self.calls = 0

    def progress(self, fraction=None, message=None):
        """Shows progress on the job (session transport). Keeps a long request alive; send one at least every minute."""
        if self.session is None:
            print(f"progress {fraction} {message or ''}", file=sys.stderr)
            return
        line = {"type": "progress", "id": self.request_id}
        if fraction is not None:
            line["progress"] = max(0.0, min(1.0, float(fraction)))
        if message:
            line["message"] = message
        send(line)

    def event(self, event):
        """Hands a UI event to the caller, such as {"kind": "text", "delta": "Hi"} for a chat agent (API 4)."""
        if self.session is None:
            raise PluginError("no_host_channel", "Events need the session transport")
        send({"type": "event", "id": self.request_id, "event": event})

    def call(self, method, params=None):
        """Runs a BashCut command, such as host.call("timeline.get"), and returns its result (API 4, chat agents)."""
        if self.session is None:
            raise PluginError("no_host_channel", "Calling BashCut needs the session transport")
        self.calls += 1
        call_id = f"{self.request_id}-c{self.calls}"
        send({"type": "call", "id": self.request_id, "callId": call_id, "method": method, "params": params or {}})
        reply = self.session.wait_for_call(call_id, self.request_id)
        if "error" in reply:
            error = reply["error"]
            raise PluginError(str(error.get("code", "call_failed")), error.get("message", "BashCut refused the call"))
        return reply.get("result")

    def render(self, body, title=None):
        """Redraws the view that asked while the request still works (view requests): a progress bar, partial results."""
        event = {"kind": "render", "body": body}
        if title:
            event["title"] = title
        self.event(event)

    def wait_job(self, started, timeout=600, interval=0.4):
        """Commands that run as jobs (voice.speak, plugins.invoke, export.start …) answer {"job": id}: polls
        jobs.status until the job ends and returns its result. Other answers come back unchanged."""
        job = (started or {}).get("job") if isinstance(started, dict) else None
        if not job:
            return started
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            status = self.call("jobs.status", {"job": job}) or {}
            status = status.get("job", status)
            if status.get("state") == "completed":
                return status.get("result")
            if status.get("state") in ("failed", "cancelled"):
                raise PluginError("job_" + status["state"], str(status.get("error") or f"The job {status['state']}"))
            time.sleep(interval)
        raise PluginError("timeout", f"The job {job} did not end in {timeout} s")


def respond(request, handler, session=None):
    request_id = request.get("id")
    host = Host(request_id, session)
    try:
        result = handler(request.get("method"), request.get("params") or {}, host)
        return {"id": request_id, "result": result if result is not None else {}}
    except PluginError as error:
        return {"id": request_id, "error": {"code": error.code, "message": error.message}}
    except Cancelled:
        return {"id": request_id, "error": {"code": "cancelled", "message": "Cancelled"}}
    except Exception as error:  # noqa: BLE001 - every failure goes back to BashCut
        return {"id": request_id, "error": {"code": "failed", "message": str(error) or type(error).__name__}}


class Session:
    """The session transport, one request at a time. Messages that arrive while a handler waits for a call result
    are kept and handled next, in order."""

    def __init__(self, handler):
        self.handler = handler
        self.backlog = collections.deque()

    def read(self):
        while True:
            line = sys.stdin.readline()
            if not line:
                return None
            if line.strip():
                return json.loads(line)

    def wait_for_call(self, call_id, request_id):
        while True:
            message = self.read()
            if message is None:
                raise PluginError("host_closed", "BashCut closed the session")
            kind = message.get("type")
            if kind == "callResult" and message.get("callId") == call_id:
                return message
            if kind == "callResult":
                continue  # the answer to a call that was given up on
            if kind == "cancel" and message.get("id") == request_id:
                raise Cancelled()
            self.backlog.append(message)

    def run(self):
        while True:
            message = self.backlog.popleft() if self.backlog else self.read()
            if message is None:
                return
            kind = message.get("type")
            if kind == "hello":
                HOST_FEATURES.update(str(feature) for feature in message.get("features") or [])
                send({"type": "hello", "apiVersion": message.get("apiVersion", 2)})
            elif kind == "shutdown":
                return
            elif kind in ("cancel", "callResult"):
                continue  # nothing is running for it any more
            else:
                send(respond(message, self.handler, self))


def run(handler):
    """Entry point: `provider rpc` or `provider session`."""
    mode = sys.argv[1] if len(sys.argv) > 1 else "rpc"
    if mode == "session":
        Session(handler).run()
        return
    line = sys.stdin.readline()
    try:
        request = json.loads(line)
    except ValueError:
        sys.exit("expected one JSON request on stdin")
    send(respond(request, handler))
