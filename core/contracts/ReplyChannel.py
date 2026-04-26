import threading
from typing import Any


_UNSET = object()


class ReplyChannel:
    """One-shot reply channel for request/reply patterns over DaemonWorker queues.

    Usage (sender/caller side):
        reply = ReplyChannel()
        pub.notify('db.query', payload={'sql': '...'}, replyTo=reply)
        result = reply.wait(timeout=10.0)   # blocks until handler replies

    Usage (handler side):
        def onDbQuery(self, msg: Message):
            try:
                rows = db.execute(msg.payload['sql'])
                msg.replyTo.reply(rows)
            except Exception as e:
                msg.replyTo.error(e)
    """

    def __init__(self):
        self._event = threading.Event()
        self._result: Any = _UNSET
        self._error: BaseException | None = None

    # ── Handler side ──────────────────────────────────────────────────────────

    def reply(self, result: Any = None) -> None:
        """Send a successful result. Call at most once."""
        if self._event.is_set():
            return
        self._result = result
        self._event.set()

    def error(self, exc: BaseException) -> None:
        """Signal an error. Call at most once."""
        if self._event.is_set():
            return
        self._error = exc
        self._event.set()

    # ── Caller side ───────────────────────────────────────────────────────────

    def wait(self, timeout: float = 30.0) -> Any:
        """Block until `reply()` or `error()` is called, or timeout.
        Raises:
            TimeoutError: if handler did not reply within `timeout` seconds.
            Exception:    re-raises any error passed to `error()`.
        """
        if not self._event.wait(timeout=timeout):
            raise TimeoutError(f'ReplyChannel timed out after {timeout}s')
        if self._error is not None:
            raise self._error
        return self._result

    @property
    def isDone(self) -> bool:
        """True once reply() or error() has been called."""
        return self._event.is_set()
