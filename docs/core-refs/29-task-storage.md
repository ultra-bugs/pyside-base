# Task Storage Layer

> **JSON persistence for task state, history, and scheduled jobs**
> **Last synced**: `2026-06-09`

## Overview

The Task System uses a dedicated storage layer to persist its data separately from the main application config. All classes live in `core/taskSystem/storage/`.

```
BaseStorage (abstract)
└── JsonStorage    — default file-backed implementation
    └── WorkingSet — Unit of Work for atomic multi-key saves
```

---

## BaseStorage

Abstract interface all storage backends must implement (`core/taskSystem/storage/BaseStorage.py`).

```python
class BaseStorage(abc.ABC):
    def load(self, key: str, default: Any = None) -> Any: ...
    def save(self, key: str, value: Any) -> None: ...
    def saveBatch(self, items: Dict[str, Any]) -> None: ...
    def clear(self, key: str) -> None: ...
    def beginWork(self) -> WorkingSet: ...  # returns a Unit of Work
```

Custom storage backends (e.g. SQLite, Redis) only need to implement these five methods.

---

## JsonStorage

Default implementation. Stores all data in a single JSON file at `config/task_storage.json` (resolved via `PathHelper.buildDataPath`).

```python
# Injected automatically by TaskManagerService — no manual instantiation needed.
# TaskManagerService creates JsonStorage() with the default path unless a custom
# BaseStorage instance is passed to its constructor.
```

### Behavior

- Loads the entire JSON file into memory on startup.
- Each `save()` call re-writes the full file (protected by a `threading.Lock`).
- `saveBatch()` updates multiple keys in one file write — preferred for atomic saves.
- `CustomJsonEncoder` handles `DictSerializable` objects automatically.

### Storage keys used by the Task System

| Key | Owner | Contents |
|---|---|---|
| `pendingTasks` | `TaskQueue` | Serialized persistent pending tasks restored on next boot |
| `scheduledJobs` | `TaskScheduler` | Scheduled job metadata; timers are re-armed on `_loadJobs()` |
| `failedTaskHistory` | `TaskTracker` | Serialized history of failed persistent tasks (max 1000) |
| `completedTaskHistory` | `TaskTracker` | Serialized history of completed persistent tasks (max 1000) |

---

## WorkingSet — Unit of Work

`BaseStorage.beginWork()` returns a `WorkingSet` that batches multiple `save()` calls and commits them atomically in a single `saveBatch()`. It also performs **dirty detection** — if a value hasn't changed, the key is not written.

```python
# TaskManagerService.saveState() uses this pattern:
workingSet = self._storage.beginWork()

self._taskQueue.saveState(workingSet)    # writes 'pendingTasks'
self._taskTracker.saveState(workingSet)  # writes 'failedTaskHistory', 'completedTaskHistory'

written = workingSet.commit()            # single file write; returns count of changed keys
# written == 0 means nothing changed → no I/O performed
```

### WorkingSet API

```python
ws = storage.beginWork()

ws.save(key, value)  # buffers write; only marks dirty if value changed
ws.isDirty           # bool — True if any key changed
ws.commit()          # int — flushes to storage; returns number of keys written
```

---

## Auto-save timer

`TaskManagerService` runs a `QTimer` that calls `saveState()` on an interval configurable in the app config:

```python
# config key: taskSystem.autoSaveIntervalSecs (default: 30)
# Set to 0 or None to disable auto-save.
```

`saveState()` uses the `WorkingSet` pattern — if no task state has changed between ticks, no file I/O occurs.

---

## Providing a custom storage backend

Pass a `BaseStorage` instance to `TaskManagerService.__init__()`:

```python
class RedisStorage(BaseStorage):
    def load(self, key, default=None): ...
    def save(self, key, value): ...
    def saveBatch(self, items): ...
    def clear(self, key): ...

# Injected via QtAppContext / ServiceProvider at bootstrap
storage = RedisStorage(...)
taskManager = TaskManagerService(publisher, config, storage=storage)
```

---

## Related Documentation

- [Task System Overview](12-task-system-overview.md) — persistence section
- [TaskManager](15-task-manager.md) — `loadState` / `saveState` methods
- [Configuration](06-configuration.md) — `taskSystem.*` config keys
