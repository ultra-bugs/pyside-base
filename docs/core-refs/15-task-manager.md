# TaskManagerService - Task Orchestration API

> **Central API for background task management, scheduling, and monitoring**

## Overview

`TaskManagerService` offers a unified API providing interfaces for:

- Explicit background task execution queues
- Dynamic scheduling (date-based, repetitive intervals, cron syntaxes)
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
# QtAppContext inherently runs `bootstrap()` followed strictly by injecting loaded persistence maps post AppReady.
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

### Cancel Task

```python
taskManager.cancelTask(uuid)
```

### Bulk Actions

```python
# Stop all tasks targeted by tag
taskManager.stopTasksByTag('Network')
# Include chained children (danger zone)
taskManager.stopTasksByTag('Network', includeChainedChildren=True)

# Pause all tasks targeted by tag
taskManager.pauseTasksByTag('HeavyComputation')
```

### Get Status

```python
status = taskManager.getTaskStatus(uuid)
allTasks = taskManager.getAllTasks()
failedTasks = taskManager.getFailedTasks()
```

### Configuration

```python
taskManager.setMaxConcurrentTasks(5)
queueStatus = taskManager.getQueueStatus()
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

### Cron

```python
taskManager.addTask(task, scheduleInfo={
    'trigger': 'cron',
    'hour': 9,
    'minute': 0,
    'day_of_week': 'mon-fri'
})
```

## Signals

```python
taskManager.taskAdded.connect(lambda uuid: print(f'Added: {uuid}'))
taskManager.taskRemoved.connect(lambda uuid: print(f'Removed: {uuid}'))
taskManager.statusChanged.connect(lambda uuid, status: print(f'{uuid}: {status}'))
taskManager.progressUpdated.connect(lambda uuid, progress: print(f'{uuid}: {progress}%'))
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

ctx = QtAppContext.globalInstance()
taskManager = ctx.taskManager

# Lưu ý: Không tự khởi tạo TaskManagerService.
# QtAppContext sẽ gọi bootstrap() sau khi AppReady để nạp state.

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
        'Fetch': ChainRetryBehavior.RETRY_TASK,
        'Process': ChainRetryBehavior.SKIP_TASK,
        'Save': ChainRetryBehavior.FAIL_CHAIN
    }
)
```

### Monitoring

```python
# Monitor all tasks
def onStatusChanged(uuid, status):
    print(f'Task {uuid}: {status}')

def onProgress(uuid, progress):
    print(f'Task {uuid}: {progress}%')

taskManager.statusChanged.connect(onStatusChanged)
taskManager.progressUpdated.connect(onProgress)

# Get queue status
status = taskManager.getQueueStatus()
print(f'Active: {status["active"]}, Pending: {status["pending"]}')
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
# Check if tasks enabled
ctx = QtAppContext.globalInstance()
if ctx.isFeatureEnabled('tasks'):
    taskManager = ctx.taskManager

# Monitor task status
taskManager.statusChanged.connect(onStatusChanged)

# Set appropriate max concurrent
taskManager.setMaxConcurrentTasks(3)

# Use descriptive names
task = MyTask(name='Download User Data')
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
