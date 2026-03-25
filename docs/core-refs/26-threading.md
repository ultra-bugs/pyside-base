# Threading & Concurrency

> **Reusable threading primitives for background execution**

## `DaemonWorker`

File: `core/threading/DaemonWorker.py`

`DaemonWorker` provides a reusable base class for long-lived daemon threads utilizing a FIFO message queue (`queue.SimpleQueue`). It abstracts away the boilerplate of thread creation, lifecycle management, and queue consumption.

### Key Characteristics

- **Daemon Thread**: The backing thread is created with `daemon=True`, meaning it will automatically terminate when the main Python process exits, preventing the application from hanging on shutdown.
- **FIFO Queue**: Uses a thread-safe `SimpleQueue` to receive messages.
- **Graceful Shutdown**: Provides a `stop()` method that enqueues an internal sentinel (`_STOP`). The worker will process all pending items in the queue before terminating gracefully when it encounters this sentinel.
- **Error-Resilient Loop**: Exceptions raised during item processing (`onItem`) are caught and ignored by default to prevent the worker thread from crashing unexpectedly. (Note: You may still want to log exceptions within `onItem`).

### Usage Example

To use `DaemonWorker`, you must subclass it and implement the abstract `onItem(item)` method.

```python
from core.threading.DaemonWorker import DaemonWorker

class MyBackgroundProcessor(DaemonWorker):
    def __init__(self):
        super().__init__(name="MyProcessorThread")

    def onStart(self) -> None:
        # Optional: Setup resources before the loop begins
        print("Worker thread started.")

    def onItem(self, item) -> None:
        # Required: Process a single dequeued item
        print(f"Processing item: {item}")

    def onStop(self) -> None:
        # Optional: Cleanup resources after the loop ends
        print("Worker thread stopped.")

# Instantiation and execution
processor = MyBackgroundProcessor()
processor.start()

# Send items to the worker thread
processor.enqueue("Task 1")
processor.enqueue({"type": "data", "value": 42})

# Gracefully stop the worker (processes pending items then exits)
processor.stop()
```

### API Reference

- `__init__(self, name: str = 'DaemonWorker')`: Initializes the queue and the daemon thread. You can optionally name the thread for debugging purposes.
- `start(self) -> 'DaemonWorker'`: Starts the background thread. It checks `is_alive()` first, so it is safe to call multiple times. Returns `self` for chaining.
- `stop(self)`: Enqueues the internal stop sentinel to initiate a graceful shutdown.
- `enqueue(self, item) -> None`: Adds a generic item to the end of the queue.
- `onStart(self) -> None`: Hook called exactly once when the daemon thread starts, before the actual queue processing loop begins.
- `onItem(self, item) -> None`: **Abstract Method**. Hook called for each item dequeued. You must implement this in your subclass to perform the actual work.
- `onStop(self) -> None`: Hook called exactly once after the stop sentinel is processed and the processing loop has terminated.
