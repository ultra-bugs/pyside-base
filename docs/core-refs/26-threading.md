# Threading & Concurrency

> **Reusable threading primitives for background execution**
> **Last synced**: `2026-05-26`

## `DaemonWorker`

File: `core/threading/DaemonWorker.py`

`DaemonWorker` provides a reusable base class for long-lived daemon threads utilizing a FIFO `Message` queue (`queue.SimpleQueue`). It abstracts away the boilerplate of thread creation, lifecycle management, and queue consumption.

### Key Characteristics

- **Daemon Thread**: The backing thread is created with `daemon=True`, meaning it will automatically terminate when the main Python process exits, preventing the application from hanging on shutdown.
- **Message-Typed Queue**: Uses a thread-safe `SimpleQueue` that accepts only `Message` instances. `enqueue()` enforces this with a strict `isinstance` check at runtime — passing any other type raises `TypeError`.
- **Graceful Shutdown**: Provides a `stop()` method that enqueues an internal sentinel (`_STOP`). The worker will process all pending items in the queue before terminating gracefully when it encounters this sentinel.
- **Error-Resilient Loop**: Exceptions raised during item processing (`onItem`) are caught and ignored by default to prevent the worker thread from crashing unexpectedly. (Note: You may still want to log exceptions within `onItem`).

### Message Contract

All items enqueued via `enqueue()` must be `Message` instances from `core.contracts.Message`:

```python
from core.contracts.Message import Message

msg = Message(topic='task.run', payload={'value': 42})
msg = Message(topic='cmd.sync', payload={}, isAsync=True)  # async routing hint
```

`Message` fields:
- `topic` (str, required): event or command name — must be non-empty
- `payload` (dict): arbitrary data delivered to the handler
- `isAsync` (bool, default `False`): routing hint set by the **sender** (e.g. `Publisher.notifyAsync`)
- `replyTo` (optional `ReplyChannel`): for request/reply patterns; `None` means fire-and-forget

### Usage Example

To use `DaemonWorker`, subclass it and implement the abstract `onItem(msg: Message)` method.

```python
from core.contracts.Message import Message
from core.threading.DaemonWorker import DaemonWorker

class MyBackgroundProcessor(DaemonWorker):
    def __init__(self):
        super().__init__(name="MyProcessorThread")

    def onStart(self) -> None:
        # Optional: Setup resources before the loop begins
        print("Worker thread started.")

    def onItem(self, msg: Message) -> None:
        # Required: Process a single dequeued Message
        print(f"Processing: {msg.topic} → {msg.payload}")

    def onStop(self) -> None:
        # Optional: Cleanup resources after the loop ends
        print("Worker thread stopped.")

# Instantiation and execution
processor = MyBackgroundProcessor()
processor.start()

# Enqueue Message instances
processor.enqueue(Message(topic='task.run', payload={'step': 1}))
processor.enqueue(Message(topic='task.run', payload={'step': 2}))

# Gracefully stop the worker (processes pending items then exits)
processor.stop()
```

### API Reference

- `__init__(self, name: str = 'DaemonWorker')`: Initializes the `SimpleQueue` and the daemon thread. The `name` is used for thread identification in debuggers.
- `start(self) -> 'DaemonWorker'`: Starts the background thread. Checks `is_alive()` first — safe to call multiple times. Returns `self` for chaining.
- `stop(self)`: Enqueues the internal stop sentinel to initiate a graceful shutdown.
- `enqueue(self, msg: Message) -> None`: Adds a `Message` to the queue. Raises `TypeError` if `msg` is not a `Message` instance.
- `onStart(self) -> None`: Hook called exactly once when the daemon thread starts, before the actual queue processing loop begins.
- `onItem(self, msg: Message) -> None`: **Abstract Method**. Hook called for each `Message` dequeued. Must be implemented in your subclass to perform the actual work.
- `onStop(self) -> None`: Hook called exactly once after the stop sentinel is processed and the processing loop has terminated.
