import threading
from abc import abstractmethod

from core.contracts.Message import Message

_STOP = object()


class DaemonWorker:
    """Reusable base for long-lived daemon threads with a FIFO Message queue.

    Contract
    --------
    - **Subclasses MUST enqueue only `Message` instances.**
      `enqueue()` enforces this at runtime with a strict `isinstance` check.
      Duck-typing is insufficient for long-lived daemon threads where a malformed
      queue item can silently corrupt processing upstream.
    - **Implement `onItem(msg: Message)`** to process each dequeued message.
    - Use `replyTo` inside the message for request/reply patterns.
    - Set `msg.isAsync = True` at the *sender* side (via `Publisher.notifyAsync`)
      to signal that delivery should be offloaded rather than run inline.

    Lifecycle
    ---------
    call `start()` once, `stop()` for graceful drain-and-exit.
    The thread is a daemon — it exits automatically when the main process exits.
    """

    def __init__(self, name: str = 'DaemonWorker'):
        import queue
        self._queue: queue.SimpleQueue = queue.SimpleQueue()
        self._thread = threading.Thread(target=self._loop, daemon=True, name=name)

    def start(self) -> 'DaemonWorker':
        if not self._thread.is_alive():
            self._thread.start()
        return self

    def stop(self) -> None:
        """Enqueue sentinel to gracefully stop after processing pending items."""
        self._queue.put(_STOP)

    def enqueue(self, msg: Message) -> None:
        """Enqueue a Message for processing.
        Raises:
            TypeError: if `msg` is not a `Message` instance.
        """
        if not isinstance(msg, Message):
            raise TypeError(
                f'{self.__class__.__name__}.enqueue() requires a Message instance, '
                f'got {type(msg).__name__!r}. '
                'Wrap your payload in Message(topic=..., payload=...) before enqueuing.'
            )
        self._queue.put(msg)

    def _loop(self) -> None:
        self.onStart()
        while True:
            item = self._queue.get()
            if item is _STOP:
                break
            try:
                self.onItem(item)
            except Exception:
                pass
        self.onStop()

    def onStart(self) -> None:
        """Called once when the daemon thread starts. Override as needed."""

    @abstractmethod
    def onItem(self, msg: Message) -> None:
        """Process a single Message. Must be implemented by subclasses."""

    def onStop(self) -> None:
        """Called once after the stop sentinel is consumed. Override as needed."""
