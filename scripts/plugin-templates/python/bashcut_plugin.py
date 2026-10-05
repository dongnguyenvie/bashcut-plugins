"""The BashCut plugin protocol for {{NAME}} (Python standard library only). You rarely need to change this file.

BashCut runs the entrypoint as `provider rpc` (one JSON request on stdin, one JSON response on stdout) or, with
"transport": "session" in plugin.json, as `provider session` (newline-delimited JSON until it says shutdown).
Handlers get a `Host` to report progress, stream chat events and call BashCut commands. Diagnostics go to stderr:
stdout carries only protocol lines.
"""
import collections
import json
import sys


class PluginError(Exception):
    """A failure with a stable code BashCut can show, such as PluginError("model_missing", "Install the model")."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


class Cancelled(Exception):
    """BashCut cancelled the request (session transport only)."""


def send(message):
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


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
