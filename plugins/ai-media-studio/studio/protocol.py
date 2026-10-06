"""Multiplexed session transport: reader never blocks on network, work, or nested host calls."""
import json
import queue
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

SEND_LOCK = threading.Lock()
CALL_LOCK = threading.Lock()
CALLS = {}
ACTIVE = {}
FEATURES = set()


class Cancelled(Exception):
    pass


class HostError(Exception):
    pass


def send(message):
    with SEND_LOCK:
        sys.stdout.write(json.dumps(message, ensure_ascii=False, allow_nan=False)+'\n')
        sys.stdout.flush()


class Request:
    def __init__(self, message):
        self.id = message['id']
        self.method = message['method']
        self.params = message.get('params') or {}
        self.stop = threading.Event()

    def cancelled(self):
        return self.stop.is_set()

    def check_cancelled(self):
        if self.cancelled():
            raise Cancelled('Operation cancelled.')

    def progress(self, value, message):
        self.check_cancelled()
        result = {'type': 'progress', 'id': self.id, 'message': message}
        if value is not None:
            result['progress'] = min(1, max(0, value))
        send(result)

    def render(self, body):
        self.check_cancelled()
        send({'type': 'event', 'id': self.id, 'event': {'kind': 'render', 'body': body}})

    def call(self, method, params=None, timeout=300):
        self.check_cancelled()
        call_id = str(uuid.uuid4())
        replies = queue.Queue(maxsize=1)
        with CALL_LOCK:
            CALLS[call_id] = replies
        try:
            send({'type': 'call', 'id': self.id, 'callId': call_id, 'method': method, 'params': params or {}})
            deadline = time.monotonic()+timeout
            while time.monotonic() < deadline:
                self.check_cancelled()
                try:
                    answer = replies.get(timeout=.1)
                except queue.Empty:
                    continue
                if 'error' in answer:
                    # Host messages can include raw option values. Return only method + generic guidance.
                    raise HostError(f'BashCut refused {method}. Check the project revision, layer locks and edit permissions.')
                return answer.get('result') or {}
            raise HostError(f'BashCut {method} timed out.')
        finally:
            with CALL_LOCK:
                CALLS.pop(call_id, None)

    def wait_job(self, started, timeout=3600):
        job = started.get('job')
        if not job:
            return started
        deadline = time.monotonic()+timeout
        try:
            while time.monotonic() < deadline:
                self.check_cancelled()
                result = self.call('jobs.status', {'job': job})
                if result.get('state') == 'completed':
                    return result.get('result') or {}
                if result.get('state') in ('failed','cancelled'):
                    raise HostError('BashCut job failed or was cancelled. See the job details.')
                self.progress(None, 'Waiting for BashCut job')
                self.stop.wait(.4)
            raise HostError('BashCut job timed out.')
        except Cancelled:
            # Caller cancellation should stop the nested job as well.
            self.stop.clear()
            try:
                self.call('jobs.cancel', {'job': job}, timeout=5)
            finally:
                self.stop.set()
            raise


def safe_error(error, params):
    from .vibi import VibiError
    if isinstance(error, (VibiError, HostError, Cancelled, ValueError, FileNotFoundError)):
        message = str(error)[:1000]
    else:
        message = 'AI Media Studio could not complete this request. Check the input files and installed dependencies.'
    secret = str((params.get('options') or {}).get('apiKey') or '')
    if secret:
        message = message.replace(secret, '[redacted]')
    return {'code': 'cancelled' if isinstance(error, Cancelled) else 'failed', 'message': message}


def execute(request):
    try:
        from .app import handle
        result = handle(request)
        request.check_cancelled()
        send({'id': request.id, 'result': result})
    except Exception as error:
        send({'id': request.id, 'error': safe_error(error, request.params)})
    finally:
        with CALL_LOCK:
            ACTIVE.pop(request.id, None)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'rpc':
        message = json.loads(sys.stdin.readline())
        request = Request(dict(message, id=message.get('id', 'rpc')))
        execute(request)
        return
    pool = ThreadPoolExecutor(max_workers=16)
    try:
        for line in sys.stdin:
            if len(line.encode()) > 8*1024*1024:
                break
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                break
            kind = message.get('type')
            if kind == 'hello':
                FEATURES.update(message.get('features') or [])
                send({'type': 'hello', 'apiVersion': 8})
            elif kind == 'request':
                request = Request(message)
                with CALL_LOCK:
                    if request.id in ACTIVE or len(ACTIVE) >= 16:
                        send({'id': request.id, 'error': {'code': 'busy', 'message': 'Too many active requests.'}})
                        continue
                    ACTIVE[request.id] = request
                pool.submit(execute, request)
            elif kind == 'callResult':
                with CALL_LOCK:
                    replies = CALLS.get(message.get('callId'))
                if replies:
                    replies.put_nowait(message)
            elif kind == 'cancel':
                with CALL_LOCK:
                    request = ACTIVE.get(message.get('id'))
                if request:
                    request.stop.set()
            elif kind == 'shutdown':
                break
    finally:
        with CALL_LOCK:
            for request in ACTIVE.values():
                request.stop.set()
        pool.shutdown(wait=True, cancel_futures=True)


if __name__ == '__main__':
    main()
