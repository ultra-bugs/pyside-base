# TaskManagerService - Task Orchestration API

> **Central API for background task management, scheduling, and monitoring**
> **Last synced**: `2026-06-09`

## Overview

`TaskManagerService` offers a unified API providing interfaces for:

- Explicit background task execution queues
- Dynamic scheduling (date-based, repetitive intervals, daily cron)
- Segmented task chains and conditional branching
- Broad event-based status and execution monitoring
- Runtime logging controls (targeting Task System debug analysis)
- Persistence encoding & State persistence recoveries
- Deferred Initialization hooks routing subsystem payloads reliably post-boot

## API Reference

### Global Access

```python
from core import QtAppContext

ctx = QtAppContext.globalInstance()
taskManager = ctx.taskManager

# Remember: NEVER manually instantiate TaskManagerService objects.
# QtAppContext calls booted() after AppReady to start the queue worker and load persisted state.
```

### Add Task

```python
taskManager.addTask(task, scheduleInfo=None)
```

### Add Chain

```python
chain = taskManager.addChainTask(
    name='Chain Name',
    tasks=[task1, task2],
    retryBehaviorMap={...}
)
```

### Cancel / Pause / Resume Task

```python
taskManager.cancelTask(uuid)
taskManager.pauseTask(uuid)
taskManager.resumeTask(uuid)
```

### Bulk Actions

```python
# Stop all tasks targeted by tag
taskManager.stopTasksByTag('Network')
# Include chained children (danger zone)
taskManager.stopTasksByTag('Network', includeChainedChildren=True)

# Pause / resume all tasks targeted by tag
taskManager.pauseTasksByTag('HeavyComputation')

# Pause / resume / stop all active tasks
taskManager.pauseAll()
taskManager.resumeAll()
taskManager.stopAll()
```

### Query Tasks

```python
status = taskManager.getTaskStatus(uuid)
allTasks = taskManager.getAllTasks()
failedTasks = taskManager.getFailedTasks()
tasksByTag = taskManager.getTasksByTag('MyTag')   # returns task instances
hasTag = taskManager.hasTasksWithTag('MyTag')     # lightweight bool check
hasPaused = taskManager.hasPausedTasks()
```

### Configuration

```python
taskManager.setMaxConcurrentTasks(5)
taskManager.getMaxConcurrentTasks()
queueStatus = taskManager.getQueueStatus()
scheduledJobs = taskManager.getScheduledJobs()
```

## Scheduling

### Date-based

```python
from datetime import datetime, timedelta

taskManager.addTask(task, scheduleInfo={
    'trigger': 'date',
    'runDate': datetime.now() + timedelta(hours=1)
})
```

### Interval

```python
taskManager.addTask(task, scheduleInfo={
    'trigger': 'interval',
    'intervalSeconds': 60  # Every minute
})
```

### Daily Cron

```python
taskManager.addTask(task, scheduleInfo={
    'trigger': 'cron',
    'hour': 9,
    'minute': 0
})
```

## Signals

```python
taskManager.taskAdded.connect(lambda uuid: print(f'Added: {uuid}'))
taskManager.taskRemoved.connect(lambda uuid: print(f'Removed: {uuid}'))
taskManager.taskFinished.connect(lambda uuid, task, result, err: print(f'Finished: {uuid}'))
taskManager.taskStatusUpdated.connect(lambda uuid, status: print(f'{uuid}: {status}'))
taskManager.taskProgressUpdated.connect(lambda uuid, progress, label: print(f'{uuid}: {progress}%'))
taskManager.failedTaskLogged.connect(lambda taskInfo: print(f'Failed: {taskInfo}'))
taskManager.systemReady.connect(lambda: print('System ready'))
```

## Usage Examples

### Basic Task Execution

```python
from core import QtAppContext
from core.taskSystem import AbstractTask

class MyTask(AbstractTask):
    def handle(self):
        # Task logic...
        pass
    
    def _performCancellationCleanup(self):
        pass
    
    @classmethod
    def deserialize(cls, data: dict):
        return cls(name=data['name'])

ctx = QtAppContext.globalInstance()
taskManager = ctx.taskManager

task = MyTask(name='My Task')
taskManager.addTask(task)
```

### Scheduled Task

```python
from datetime import datetime, timedelta

# Run in 1 hour
task = MyTask(name='Scheduled Task')
taskManager.addTask(task, scheduleInfo={
    'trigger': 'date',
    'runDate': datetime.now() + timedelta(hours=1)
})

# Run every 5 minutes
task = MyTask(name='Periodic Task')
taskManager.addTask(task, scheduleInfo={
    'trigger': 'interval',
    'intervalSeconds': 300
})
```

### Task Chain

```python
chain = taskManager.addChainTask(
    name='Data Pipeline',
    tasks=[
        FetchTask(name='Fetch'),
        ProcessTask(name='Process'),
        SaveTask(name='Save')
    ],
    retryBehaviorMap={
        'FetchTask': ChainRetryBehavior.RETRY_TASK,
        'ProcessTask': ChainRetryBehavior.SKIP_TASK,
        'SaveTask': ChainRetryBehavior.STOP_CHAIN
    }
)
```

### Monitoring

```python
# Monitor all tasks
def onStatusChanged(uuid, status):
    print(f'Task {uuid}: {status}')

def onProgress(uuid, progress, label):
    print(f'Task {uuid}: {progress}% — {label}')

taskManager.taskStatusUpdated.connect(onStatusChanged)
taskManager.taskProgressUpdated.connect(onProgress)

# Get queue status
status = taskManager.getQueueStatus()
print(f'Active: {status["running"]}, Pending: {status["pending"]}')
```

### Cancel Task

```python
# Add task
task = MyTask(name='Cancellable Task')
taskManager.addTask(task)

# Cancel later
taskManager.cancelTask(task.uuid)
```

## Best Practices

### ✅ DO

```python
# Monitor task status
taskManager.taskStatusUpdated.connect(onStatusChanged)

# Set appropriate max concurrent
taskManager.setMaxConcurrentTasks(3)

# Use descriptive names
task = MyTask(name='Download User Data')

# Use tag queries to check for active tasks
if taskManager.hasTasksWithTag('Device_abc123'):
    print('Device task already running')
```

### ❌ DON'T

```python
# Don't assume tasks enabled
taskManager = ctx.taskManager  # May be None!

# Don't create too many concurrent tasks
taskManager.setMaxConcurrentTasks(100)  # Too many!

# Don't forget to handle failures
# Monitor failedTasks and handle appropriately
```

## Related Documentation

- [AbstractTask](13-abstract-task.md) - Task implementation
- [TaskChain](14-task-chain.md) - Task chaining
- [Task System Overview](12-task-system-overview.md) - Architecture
