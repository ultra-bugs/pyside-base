# ScheduleInfo - Typed Scheduling Containers

> **Type-safe scheduling configuration replacing raw dicts**
> **Last synced**: `2026-06-09`

## Overview

`ScheduleInfo` is an abstract base class with three concrete subclasses that carry scheduling configuration for `TaskManagerService.addTask()`. They replace the raw `dict` approach with validated, typed objects and a fluent mutation API.

`TaskManagerService` accepts **both** formats at its boundary — raw dicts are automatically coerced via `ScheduleInfoFactory.ensure()`, so existing dict-based code continues to work.

All classes are in `core/taskSystem/ScheduleInfo.py`.

## Class Hierarchy

```
ScheduleInfo (abstract)
├── DateScheduleInfo      — one-time execution at a specific datetime
├── IntervalScheduleInfo  — recurring at a fixed interval
└── CronScheduleInfo      — daily at a specific local time
```

---

## DateScheduleInfo

One-time execution at a specific `datetime`.

```python
from datetime import datetime, timedelta
from core.taskSystem.ScheduleInfo import DateScheduleInfo

info = DateScheduleInfo(runDate=datetime.now() + timedelta(hours=1))

taskManager.addTask(task, scheduleInfo=info)
```

### Fluent mutation

```python
info.changeWhen(datetime.now() + timedelta(days=2))  # returns self
```

### Properties

| Property | Type | Description |
|---|---|---|
| `trigger` | `str` | Always `'date'` |
| `runDate` | `datetime` | Target execution datetime |
| `nextRun` | `datetime` | Alias for `runDate` |
| `delaySeconds` | `float` | Seconds until execution (negative if overdue) |
| `needsCheckpointRearm` | `bool` | True if delay exceeds QTimer's 32-bit limit (~24.8 days) |

---

## IntervalScheduleInfo

Recurring execution at a fixed interval, optionally deferred to a `startDate`.

```python
from core.taskSystem.ScheduleInfo import IntervalScheduleInfo

# Every 30 minutes, starting now
info = IntervalScheduleInfo(intervalSeconds=1800)

# Every 2 hours, starting tomorrow at noon
from datetime import datetime, timedelta
tomorrow = datetime.now().replace(hour=12, minute=0, second=0) + timedelta(days=1)
info = IntervalScheduleInfo(intervalSeconds=7200, startDate=tomorrow)

taskManager.addTask(task, scheduleInfo=info)
```

### Fluent mutation

```python
info.setInterval(3600)      # change cadence
info.everyMinutes(45)       # shorthand
info.everyHours(2)          # shorthand
info.everyDays(1)           # shorthand
info.startAt(future_date)   # change first-run anchor
```

All fluent methods return `self`.

### Properties

| Property | Type | Description |
|---|---|---|
| `trigger` | `str` | Always `'interval'` |
| `intervalSeconds` | `int` | Repeat cadence in seconds |
| `startDate` | `Optional[datetime]` | Optional first-run anchor |
| `nextRun` | `datetime` | Next execution time |
| `delaySeconds` | `float` | Seconds until next execution |

---

## CronScheduleInfo

Daily execution at a specific local time (hour:minute). Reschedules itself automatically after each fire.

```python
from core.taskSystem.ScheduleInfo import CronScheduleInfo

# Every day at 09:00
info = CronScheduleInfo(hour=9, minute=0)

# Every day at 18:30
info = CronScheduleInfo(hour=18, minute=30)

taskManager.addTask(task, scheduleInfo=info)
```

### Fluent mutation

```python
info.every(hour=22, minute=15)   # change to 22:15 daily, returns self
```

### Properties

| Property | Type | Description |
|---|---|---|
| `trigger` | `str` | Always `'cron'` |
| `hour` | `int` | Hour (0–23) |
| `minute` | `int` | Minute (0–59) |
| `nextRun` | `datetime` | Next scheduled execution |
| `delaySeconds` | `float` | Seconds until next execution |

---

## ScheduleInfoFactory

Creates `ScheduleInfo` instances from dicts or keyword args. Used internally by `TaskManagerService` to accept both dict and typed input.

```python
from core.taskSystem.ScheduleInfo import ScheduleInfoFactory

# From dict (backward-compat)
info = ScheduleInfoFactory.fromDict({'trigger': 'interval', 'intervalSeconds': 3600})

# By trigger keyword
info = ScheduleInfoFactory.create('cron', hour=9, minute=0)
info = ScheduleInfoFactory.create('date', runDate=datetime.now() + timedelta(hours=1))
info = ScheduleInfoFactory.create('interval', intervalSeconds=300)

# Named shortcuts
info = ScheduleInfoFactory.date(runDate=...)
info = ScheduleInfoFactory.interval(intervalSeconds=...)
info = ScheduleInfoFactory.cron(hour=9, minute=0)

# Idempotent coerce — pass-through if already ScheduleInfo, convert dict otherwise
info = ScheduleInfoFactory.ensure(scheduleInfo)  # used at facade boundary
```

---

## Backward compatibility — raw dicts still work

`TaskManagerService.addTask()` accepts raw dicts at the boundary and coerces them internally:

```python
# These are all equivalent:

# Typed (preferred)
taskManager.addTask(task, scheduleInfo=CronScheduleInfo(hour=9))

# Via factory
taskManager.addTask(task, scheduleInfo=ScheduleInfoFactory.cron(hour=9))

# Dict (still works)
taskManager.addTask(task, scheduleInfo={'trigger': 'cron', 'hour': 9, 'minute': 0})
```

---

## QTimer limits

`TaskScheduler` uses `QTimer` internally. The maximum timer interval is ~24.8 days (signed 32-bit millisecond cap). Scheduling further into the future is handled via checkpoint re-arming:

```python
info.needsCheckpointRearm  # True if > ~24.8 days away
```

The scheduler logs a warning and clamps the first timer tick, then re-arms when it fires. This is transparent to callers.

---

## Related Documentation

- [TaskManager](15-task-manager.md) - `addTask` API
- [Task System Overview](12-task-system-overview.md) - Architecture
