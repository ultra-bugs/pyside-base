# TaskState - Thread-Safe Lifecycle State

> **Injectable cancellation/pause state, decoupled from AbstractTask**
> **Last synced**: `2026-06-09`

## Overview

`TaskState` is a thread-safe wrapper around `TaskStatus` that also holds cooperative lifecycle flags (stopped, paused). It lives in `core/taskSystem/TaskState.py`.

Its primary purpose is **injection into services**: a service that receives a `taskState` can check whether the owning task has been cancelled or paused without importing or depending on `AbstractTask`. This enables clean service boundaries where a service can cooperate with task lifecycle without knowing it's running inside one.

```python
class MyService:
    def __init__(self, taskState: TaskState):
        self._taskState = taskState

    def processLargeDataset(self, items):
        for item in items:
            self._taskState.throwIfCancelled()   # raises if cancelled
            self._taskState.waitIfPaused()        # blocks if paused
            self._process(item)
```

Inside `AbstractTask`, `taskState` is exposed directly as `self.taskState`. The task's convenience methods (`isStopped()`, `pause()`, `resume()`, `checkPaused()`) all delegate to it.

---

## API Reference

### Read-Only Queries (thread-safe)

```python
state.current      # TaskStatus — current enum value
state.name         # str — shortcut for current.name

state.isStopped()     # bool — cancel was requested (may precede CANCELLED transition)
state.isCancelled()   # bool — stopped OR current == CANCELLED
state.isPaused()      # bool — pause is active
state.isRunning()     # bool — current == RUNNING
state.isTerminal()    # bool — current in {COMPLETED, FAILED, CANCELLED}
```

### Cooperative Blocking

```python
state.waitIfPaused()
```

Blocks the calling thread while the task is paused. Wakes automatically when `requestResume()` or `requestCancel()` is called. Uses `QWaitCondition.wait()` with a 500 ms polling interval as a safety net against spurious misses.

```python
state.throwIfCancelled()
```

Raises `TaskCancellationException` if cancel was requested. Convenience wrapper around `isStopped()` for long loops.

### Lifecycle Commands (thread-safe)

```python
state.requestCancel()   # set stopped=True, wake paused threads
state.requestPause()    # set paused=True
state.requestResume()   # set paused=False, wake paused threads
state.transition(newStatus: TaskStatus) -> TaskStatus   # returns old status
state.reset()           # clear stopped/paused flags (used before retry)
```

---

## Usage in external services

The recommended pattern when a service needs to co-operate with task lifecycle:

```python
from core.taskSystem.TaskState import TaskState

class FileProcessor:
    def __init__(self, taskState: TaskState):
        self._taskState = taskState

    def processFiles(self, filePaths: list):
        for path in filePaths:
            # Raises TaskCancellationException → task runner catches it → CANCELLED
            self._taskState.throwIfCancelled()

            # Blocks here until resume() or cancel() is called
            self._taskState.waitIfPaused()

            self._processOne(path)
```

Inside the task:

```python
class MyTask(AbstractTask):
    def handle(self):
        processor = FileProcessor(taskState=self.taskState)
        processor.processFiles(self._files)
```

---

## Usage inside handle()

`AbstractTask` wraps `TaskState` methods via convenience proxies. Prefer these inside `handle()`:

```python
def handle(self):
    for item in items:
        if self.isStopped():          # delegates to self.taskState.isStopped()
            return

        self.checkPaused()            # delegates to self.taskState.waitIfPaused()

        process(item)
```

---

## Threading internals

`TaskState` uses `QMutex` + `QWaitCondition`:

- All property reads acquire/release the mutex to avoid torn reads on non-atomic flags.
- `waitIfPaused()` uses `QWaitCondition.wait(mutex, 500ms)` — the timeout is a safety heartbeat; the thread wakes correctly on `wakeAll()` without relying on polling.
- `requestCancel()` sets `_stopped=True` and calls `wakeAll()` so a thread blocked in `waitIfPaused()` exits cleanly rather than waiting up to 500 ms.

---

## Related Documentation

- [AbstractTask](13-abstract-task.md) — exposes `taskState` and proxy methods
- [Task System Overview](12-task-system-overview.md) — threading model
