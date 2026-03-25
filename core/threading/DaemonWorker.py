import queue
import threading
from abc import abstractmethod

_STOP = object()


class DaemonWorker:
    """Reusable base for long-lived daemon threads with a FIFO message queue.

    Subclass and implement `onItem(item)` to process each enqueued message.
    The backing thread is a daemon thread — it dies automatically when the
    main process exits. Call `stop()` for a graceful shutdown.
    """

    def __init__(self, name: str = 'DaemonWorker'):
        self._queue: queue.SimpleQueue = queue.SimpleQueue()
        self._thread = threading.Thread(target=self._loop, daemon=True, name=name)

    def start(self) -> 'DaemonWorker':
        if not self._thread.is_alive():
            self._thread.start()
        return self

    def stop(self):
        """Enqueue sentinel to gracefully stop the loop after processing pending items."""
        self._queue.put(_STOP)

    def enqueue(self, item) -> None:
        self._queue.put(item)

    def _loop(self):
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
    def onItem(self, item) -> None:
        """Process a single dequeued item. Must be implemented by subclasses."""

    def onStop(self) -> None:
        """Called once after the stop sentinel is consumed. Override as needed."""
