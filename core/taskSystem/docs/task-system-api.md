# TaskSystem API Documentation

## Overview

The TaskSystem provides a comprehensive framework for managing asynchronous tasks with:

- **Task Queuing**: FIFO queue with concurrency control
- **Task Scheduling**: Time-based and recurring task execution
- **Task Tracking**: Monitor status, progress, and history
- **Retry Logic**: Automatic retry with configurable delays
- **Persistence**: Save/restore tasks across sessions
- **Qt Integration**: Signals for UI updates

## Architecture

```
TaskManagerService (Orchestrator)
├── TaskQueue (Execution Management)
│   └── QThreadPool (Worker Threads)
├── TaskTracker (Monitoring & History)
└── TaskScheduler (Time-based Scheduling)
    └── Storage (JsonStorage)
```

### Storage Layer

The TaskSystem uses a dedicated storage layer to persist task data, separating it from the main application configuration.

- **BaseStorage**: Abstract base class defining the storage interface.
- **JsonStorage**: Default implementation storing data in `data/tasks/task_storage.json`.

This ensures that task history, pending tasks, and scheduled jobs are preserved across application restarts without cluttering the main config file.

### Task Serialization & Scheduling

**Important**: When scheduling tasks, the TaskScheduler serializes task data instead of storing task objects directly.
This enables:

- ✅ Persistence across app restarts
- ✅ JSON storage compatibility
- ✅ Task reconstruction from serialized data

**How it works**:

1. Task is serialized via `task.serialize()` → Dict
2. Task class name is stored as string reference
3. Scheduler stores: `{uuid, className, serializedData}`
4. On trigger: Task is reconstructed via `TaskClass.deserialize(data)`
5. Reconstructed task is added to execution queue

**Requirements for custom tasks**:

- Must implement `serialize()` method (inherited from `AbstractTask`)
- Must implement `deserialize(data)` classmethod
- All task-specific data must be JSON-serializable

## Naming Conventions

Following Qt conventions:

- **Files/Classes**: PascalCase (e.g., `TaskManagerService.py`, `AbstractTask`)
- **Methods/Variables**: camelCase (e.g., `addTask()`, `maxRetries`)
- **No snake_case** anywhere in the codebase
- **Logger**: All modules use `logger.bind(component="TaskSystem")`

## Core Components

### TaskStatus Enum

Defines all possible task states:

```python
from ..taskSystem import TaskStatus

# Available statuses
TaskStatus.PENDING  # Waiting in queue
TaskStatus.RUNNING  # Currently executing
TaskStatus.COMPLETED  # Finished successfully
TaskStatus.FAILED  # Failed (may retry)
TaskStatus.CANCELLED  # Cancelled by user/system
TaskStatus.PAUSED  # Temporarily paused
TaskStatus.RETRYING  # Waiting to retry after failure
```

### AbstractTask

Base class for all tasks. Provides:

- Lifecycle management (PENDING → RUNNING → COMPLETED/FAILED/CANCELLED)
- Progress tracking (0-100%)
- Cancellation support
- Qt signals for status/progress updates
- Serialization for persistence

**Key Methods:**
```python
class AbstractTask(QtCore.QObject, QtCore.QRunnable, abc.ABC):
    # Signals
    statusChanged = QtCore.Signal(str, object)  # uuid, TaskStatus
    progressUpdated = QtCore.Signal(str, int)  # uuid, progress
    taskFinished = QtCore.Signal(str, object, object, str)  # uuid, self instance, result, error
    # error object: {message: str - reason, exception: Exception instance}

    def __init__(self, name, description = "",
                 isPersistent = False, maxRetries = 0, retryDelaySeconds = 5,
                 failSilently = False):
        """Initialize task with configuration."""
    
    def setStatus(self, newStatus: TaskStatus) -> None:
        """Update status and emit signal."""
    
    def setProgress(self, value: int) -> None:
        """Update progress (0-100) and emit signal."""
    
    def isStopped(self) -> bool:
        """Check if cancellation was requested."""
    
    def cancel(self) -> None:
        """Request task cancellation."""
    
    def fail(self, reason: str) -> None:
        """Mark task as failed."""
    
    def serialize(self) -> dict:
        """
        Convert task to dictionary for persistence.

        Notes:
        - Luôn bao gồm các trường lõi (uuid, className, name, description, status, progress,
          result, error, createdAt, startedAt, finishedAt, isPersistent, maxRetries,
          retryDelaySeconds, currentRetryAttempts, failSilently, chainUuid).
        - Thuộc tính task-specific là động theo class:
          - Nếu subclass định nghĩa `serializables` (list/tuple/set tên thuộc tính), chỉ những thuộc tính đó được thêm vào.
          - Mặc định (không có `serializables`): tự động thêm mọi thuộc tính public (không bắt đầu bằng `_`) không thuộc nhóm lõi.
        """
    
    @classmethod
    @abc.abstractmethod
    def deserialize(cls, data: dict) -> 'AbstractTask':
        """Reconstruct task from dictionary."""
    
    @abc.abstractmethod
    def handle(self) -> None:
        """Execute task logic (must be implemented by subclasses)."""
    
    @abc.abstractmethod
    def _performCancellationCleanup(self) -> None:
        """Clean up resources on cancellation."""
```

**Lifecycle:**

1. Task created → `PENDING`
2. Submitted to queue → remains `PENDING`
3. Execution starts → `RUNNING`
4. During execution:
    - Check `isStopped()` periodically
    - Update progress with `setProgress()`
    - Can call `fail()` for business logic errors
5. Completion:
    - Success → `COMPLETED`
    - Error → `FAILED` (may retry)
    - Cancelled → `CANCELLED`

### TaskTracker

Monitors active tasks and maintains failed task history.

**Key Methods:**

```python
class TaskTracker(QtCore.QObject):
    # Signals
    taskAdded = QtCore.Signal(str)  # uuid
    taskRemoved = QtCore.Signal(str)
    taskUpdated = QtCore.Signal(str)
    failedTaskLogged = QtCore.Signal(dict)
    
    def addTask(self, task: AbstractTask) -> None:
        """Add task to tracking."""
    
    def removeTask(self, uuid: str) -> None:
        """Remove task from tracking."""
    
    def getTaskInfo(self, uuid: str) -> dict:
        """Get current task information."""
    
    def getAllTasksInfo(self) -> list:
        """Get all active tasks."""
    
    def logFailedTask(self, task: AbstractTask) -> None:
        """Log failed task to history."""
    
    def getFailedTaskHistory(self) -> list:
        """Get failed task history."""
```

### TaskQueue

Manages FIFO queue with concurrency limits and retry logic.

**Key Methods:**

```python
class TaskQueue(QtCore.QObject):
    # Signals
    queueStatusChanged = QtCore.Signal()
    taskQueued = QtCore.Signal(str)
    taskDequeued = QtCore.Signal(str)
    
    def __init__(self, taskTracker, storage, config, maxConcurrentTasks = 3):
        """Initialize queue with concurrency limit."""
    
    def addTask(self, task: AbstractTask) -> None:
        """Add task to queue."""
    
    def setMaxConcurrentTasks(self, count: int) -> None:
        """Set concurrency limit."""
    
    def getQueueStatus(self) -> dict:
        """Get queue statistics."""
```

**Retry Logic:**

When a task fails:

1. Check if `currentRetryAttempts < maxRetries`
2. If yes:
    - Increment `currentRetryAttempts`
    - Set status to `RETRYING`
    - Schedule retry after `retryDelaySeconds`
3. If no:
    - Log to failed task history
    - Remove from tracking

### TaskScheduler

Schedules tasks using QTimer with JsonStorage persistence.

**Task Serialization Approach:**

TaskScheduler uses a **serialize-reconstruct** pattern to enable persistence:

1. **On Schedule**: Task is serialized to a dictionary
   ```python
   taskData = task.serialize()  # → Dict with all task state
   taskClass = "services.tasks.AdbCommandTask.AdbCommandTask"  # Fully qualified name
   ```

2. **Storage**: Scheduler stores serializable data in JsonStorage
   ```python
   # Stored in job: {taskUuid, taskClass, taskData}
   # All primitives - no Qt objects, no threading objects
   ```

3. **On Trigger**: Task is reconstructed dynamically
   ```python
   # Import class dynamically
   module = __import__(module_name, fromlist=[class_name])
   task_cls = getattr(module, class_name)
   
   # Reconstruct from data
   task = task_cls.deserialize(taskData)
   
   # Add to execution queue
   taskQueue.addTask(task)
   ```

**Key Methods:**

```python
class TaskScheduler(QtCore.QObject):
    # Signals
    jobScheduled = QtCore.Signal(str, str)  # jobId, taskUuid
    jobUnscheduled = QtCore.Signal(str)
    
    def addScheduledTask(self, task, trigger, runDate = None,
                         intervalSeconds = None, **kwargs) -> str:
        """
        Schedule a task.
        
        Args:
            task: AbstractTask to schedule
            trigger: 'date', 'interval', or 'cron'
            runDate: For 'date' trigger (datetime)
            intervalSeconds: For 'interval' trigger (int)
            **kwargs: For 'cron' trigger (hour, minute, etc.)
            
        Returns:
            Job ID
            
        Note: Task is serialized, not stored directly.
              Requires task.serialize() and TaskClass.deserialize()
        """
    
    def removeScheduledTask(self, jobId: str) -> None:
        """Remove scheduled job."""
    
    def getScheduledJobs(self) -> list:
        """Get all scheduled jobs."""
```

**Trigger Types:**

```python
# One-time execution
scheduler.addScheduledTask(
        task,
        trigger='date',
        runDate=datetime(2025, 12, 31, 23, 59)
)

# Recurring every N seconds
scheduler.addScheduledTask(
        task,
        trigger='interval',
        intervalSeconds=3600  # Every hour
)

# Cron-style scheduling
scheduler.addScheduledTask(
        task,
        trigger='cron',
        hour=9,
        minute=0,
        day_of_week='mon-fri'  # 9 AM on weekdays
)
```

### TaskManagerService

Main orchestrator providing unified API.

**Key Methods:**

```python
class TaskManagerService(QtCore.QObject, Subscriber):
    # Signals
    taskAdded = QtCore.Signal(str)
    taskRemoved = QtCore.Signal(str)
    taskStatusUpdated = QtCore.Signal(str, object)
    taskProgressUpdated = QtCore.Signal(str, int)
    failedTaskLogged = QtCore.Signal(dict)
    systemReady = QtCore.Signal()
    
    def __init__(self, publisher: Publisher, config: Config):
        """Initialize with Observer publisher and config."""
    
    def addTask(self, task, scheduleInfo = None) -> None:
        """
        Add task for execution.
        
        Args:
            task: AbstractTask instance
            scheduleInfo: Optional dict with scheduling params
        """
    
    def cancelTask(self, uuid: str) -> None:
        """Cancel a task."""
    
    def pauseTask(self, uuid: str) -> None:
        """Pause a task."""
    
    def resumeTask(self, uuid: str) -> None:
        """Resume a paused task."""
    
    def getTaskStatus(self, uuid: str) -> TaskStatus:
        """Get task status."""
    
    def getAllTasks(self) -> list:
        """Get all active tasks."""
    
    def getFailedTasks(self) -> list:
        """Get failed task history."""
    
    def setMaxConcurrentTasks(self, count: int) -> None:
        """Set concurrency limit."""
    
    def getQueueStatus(self) -> dict:
        """Get queue statistics."""
    
    def getScheduledJobs(self) -> list:
        """Get scheduled jobs."""
```

## Task Implementations

### AdbCommandTask

Executes ADB commands on Android devices.

**Example:**

```python
from app.tasks import AdbCommandTask

task = AdbCommandTask(
        name="Install APK",
        command="install -r /path/to/app.apk",
        deviceSerial="DEVICE123",
        maxRetries=2,
        retryDelaySeconds=10
)

taskManager.addTask(task)
```

**Features:**

- Executes ADB commands via subprocess
- Supports device-specific commands
- Cancellation terminates subprocess
- Captures stdout/stderr

### RpaScriptTask

Skeleton for RPA script execution (placeholder).

**Example:**

```python
from app.tasks import RpaScriptTask

task = RpaScriptTask(
        name="Login Flow",
        scriptPath="/scripts/login.rpa",
        scriptParams={'username': 'user', 'password': 'pass'},
        deviceSerial="DEVICE123"
)

taskManager.addTask(task)
```

## Usage Examples

### Basic Task Execution

```python
from ..taskSystem import TaskManagerService
from ..Observer import Publisher
from ..Config import Config
from app.tasks import AdbCommandTask

# Initialize (usually done at app startup)
publisher = Publisher()
config = Config()
taskManager = TaskManagerService(publisher, config)

# Create and execute task
task = AdbCommandTask(
        name="Check Device",
        command="devices"
)

taskManager.addTask(task)

# Monitor via signals
taskManager.taskStatusUpdated.connect(
        lambda uuid, status: print(f"Task {uuid}: {status.name}")
)
```

### Scheduled Task

```python
from datetime import datetime, timedelta

# Schedule task to run in 1 hour
task = AdbCommandTask(name="Reboot", command="reboot")

taskManager.addTask(task, scheduleInfo={
    'trigger': 'date',
    'runDate': datetime.now() + timedelta(hours=1)
})
```

### Recurring Task

```python
# Run every 5 minutes
task = AdbCommandTask(name="Health Check", command="shell getprop")

taskManager.addTask(task, scheduleInfo={
    'trigger': 'interval',
    'intervalSeconds': 300
})
```

### Task with Retry

```python
task = AdbCommandTask(
        name="Flaky Command",
        command="shell am start ...",
        maxRetries=3,
        retryDelaySeconds=5
)

taskManager.addTask(task)
# Will retry up to 3 times with 5-second delays
```

### Custom Task Implementation

```python
from ..taskSystem import AbstractTask


class MyCustomTask(AbstractTask):
    def __init__(self, name, myParam, **kwargs):
        super().__init__(name, **kwargs)
        self.myParam = myParam
    
    def handle(self):
        """Execute custom logic."""
        self.setProgress(25)
        
        # Check for cancellation
        if self.isStopped():
            return
        
        # Do work
        result = self._doWork()
        
        self.setProgress(100)
        self.result = result
    
    def _performCancellationCleanup(self):
        """Clean up resources."""
        pass
    
    @classmethod
    def deserialize(cls, data):
        """Reconstruct from dict."""
        return cls(
                name=data['name'],
                myParam=data['myParam']
        )
```

## Observer Integration

TaskManagerService subscribes to `TaskRequest` events:

```python
# From a handler or controller
publisher.notify('TaskRequest', task=myTask, scheduleInfo=None)

# TaskManagerService.onTaskRequest() will handle it
```

## Configuration

TaskSystem uses these config keys:

```json
{
  "taskSystem": {
    "maxConcurrentTasks": 3,
    "retryMaps": {}
  }
}
```

Task data is stored separately in `data/tasks/task_storage.json`.

## Best Practices

1. **Always check `isStopped()`** in long-running tasks
2. **Update progress regularly** for UI feedback
3. **Use appropriate retry settings** for flaky operations
4. **Mark persistent tasks** if they should survive restarts
5. **Handle cleanup** in `_performCancellationCleanup()`
6. **Use logger** with component="TaskSystem" for all logging
7. **Follow Qt naming** (camelCase methods, PascalCase classes)

## Error Handling

```python
from .Exceptions import (
    TaskNotFoundException,
    InvalidTaskStateException,
    TaskCancellationException
)

try:
    taskManager.cancelTask("unknown-uuid")
except TaskNotFoundException as e:
    print(f"Task not found: {e}")
```

## Signals Reference

All signals use Qt's signal/slot mechanism:

| Signal               | Parameters                  | Description              |
|----------------------|-----------------------------|--------------------------|
| `statusChanged`      | uuid, TaskStatus            | Task status changed      |
| `progressUpdated`    | uuid, int                   | Task progress updated    |
| `taskFinished`       | uuid, status, result, error | Task completed           |
| `taskAdded`          | uuid                        | Task added to system     |
| `taskRemoved`        | uuid                        | Task removed from system |
| `taskUpdated`        | uuid                        | Task state updated       |
| `failedTaskLogged`   | dict                        | Failed task logged       |
| `queueStatusChanged` | -                           | Queue state changed      |
| `jobScheduled`       | jobId, taskUuid             | Job scheduled            |
| `jobUnscheduled`     | jobId                       | Job removed              |
| `systemReady`        | -                           | System initialized       |

## Thread Safety

- All public methods are thread-safe
- Qt signals are thread-safe
- Config operations use mutex locks
- TaskTracker uses signal connections for updates

## Performance Considerations

- Default concurrency: 3 tasks
- Failed task history: Last 1000 tasks
- Storage: JSON file (persistent)
- Thread pool: Qt's global instance

## Task Chaining

Task Chaining allows multiple tasks to execute sequentially as a unified workflow with shared context and configurable retry behaviors.

### Overview

`TaskChain` is a meta-task that:
- Executes child tasks sequentially
- Shares data between tasks via `ChainContext`
- Supports configurable retry behaviors when tasks fail
- Provides progress tracking (default or external via events)
- Supports full serialization for persistence across app restarts

### ChainContext

Thread-safe context manager for sharing data between tasks in a chain.

```python
from core.taskSystem.ChainContext import ChainContext

# Context is automatically created by TaskChain
# Access from within a task:
if self._chainContext:
    # Get value
    token = self._chainContext.get('auth_token')
    
    # Set value (must be JSON serializable)
    self._chainContext.set('auth_token', 'abc123')
    self._chainContext.set('user_data', {'id': 1, 'name': 'John'})
```

**Key Methods:**
- `get(key, default=None)`: Get value from context
- `set(key, value)`: Set value (must be JSON serializable)
- `has(key)`: Check if key exists
- `keys()`: Get all keys
- `clear()`: Clear all data

### ChainRetryBehavior

Enum defining retry behaviors when a child task fails:

```python
from core.taskSystem.ChainRetryBehavior import ChainRetryBehavior

# Available behaviors:
ChainRetryBehavior.STOP_CHAIN    # Stop entire chain (default)
ChainRetryBehavior.SKIP_TASK     # Skip failed task and continue
ChainRetryBehavior.RETRY_TASK    # Retry only the failed task
ChainRetryBehavior.RETRY_CHAIN   # Retry entire chain from beginning
```

### TaskChain

Main class for creating and executing task chains.

**Creating a Chain:**

```python
from services.tasks import TaskChain
from core.taskSystem.ChainRetryBehavior import ChainRetryBehavior

# Create individual tasks
task1 = LoginTask(name="Login")
task2 = GetDataTask(name="Get Data")
task3 = ProcessDataTask(name="Process")

# Configure retry behaviors
retry_map = {
    'LoginTask': ChainRetryBehavior.RETRY_TASK,
    'GetDataTask': ChainRetryBehavior.SKIP_TASK,
    'ProcessDataTask': ChainRetryBehavior.STOP_CHAIN
}

# Create chain
chain = TaskChain(
    name="Data Processing Workflow",
    tasks=[task1, task2, task3],
    retryBehaviorMap=retry_map,
    isPersistent=True,
    maxRetries=3
)
```

**Using TaskManagerService:**

```python
from core.taskSystem.TaskManagerService import TaskManagerService

# Convenience method
chain = taskManager.addChainTask(
    name="My Workflow",
    tasks=[task1, task2, task3],
    retryBehaviorMap=retry_map,
    isPersistent=True
)
```

**Sharing Data Between Tasks:**

```python
# In LoginTask
class LoginTask(AbstractTask):
    def handle(self):
        # Perform login
        token = "abc123"
        
        # Store in chain context
        if self._chainContext:
            self._chainContext.set('auth_token', token)
            self._chainContext.set('login_time', datetime.now().isoformat())

# In GetDataTask
class GetDataTask(AbstractTask):
    def handle(self):
        # Retrieve from chain context
        if self._chainContext:
            token = self._chainContext.get('auth_token')
            login_time = self._chainContext.get('login_time')
            
            # Use token to fetch data
            data = fetch_data(token)
            self._chainContext.set('fetched_data', data)
```

**Progress Updates:**

TaskChain automatically calculates progress based on task completion. You can also update progress externally via events:

```python
from core.Observer import Publisher

# External progress update
Publisher().notify('ChainProgressUpdateRequest', {
    'chainUuid': chain.uuid,
    'progress': 75
})
```

**Serialization & Recovery:**

TaskChain fully supports serialization for persistence:

```python
# Serialize
chain_data = chain.serialize()

# Deserialize
chain = TaskChain.deserialize(chain_data)
```

When an app restarts, a persisted TaskChain will resume from the last completed task.

### TaskTracker Integration

TaskTracker automatically recognizes TaskChain and tracks child tasks:

```python
# Get chain info (includes child tasks)
chain_info = taskTracker.getTaskInfo(chain.uuid)
# Returns: {
#     'uuid': '...',
#     'name': 'My Workflow',
#     'subTasks': [...],  # Child task info
#     'chainContext': {...},  # Serialized context
#     ...
# }

# Get child task info (includes parent chain info)
child_info = taskTracker.getTaskInfo(child_task.uuid)
# Returns: {
#     'uuid': '...',
#     'isChainChild': True,
#     'chainUuid': '...',
#     'parentChainName': 'My Workflow',
#     ...
# }
```

### Retry Behavior Examples

**Example 1: Skip Optional Tasks**

```python
retry_map = {
    'OptionalValidationTask': ChainRetryBehavior.SKIP_TASK,
    'CriticalTask': ChainRetryBehavior.STOP_CHAIN
}
```

**Example 2: Retry Entire Chain**

```python
retry_map = {
    'NetworkTask': ChainRetryBehavior.RETRY_CHAIN
}

chain = TaskChain(
    name="Network Workflow",
    tasks=[network_task, process_task],
    retryBehaviorMap=retry_map,
    maxRetries=3  # Retry entire chain up to 3 times
)
```

**Example 3: Task-Level Retry Only**

```python
# Task has its own retry logic
task = MyTask(name="Task", maxRetries=5)

# Chain uses default behavior (STOP_CHAIN after task retries exhausted)
chain = TaskChain(name="Workflow", tasks=[task])
```

### Best Practices

1. **Use ChainContext for Data Sharing**: Always use `ChainContext` instead of global variables or class attributes
2. **JSON Serializable Values**: Only store JSON-serializable data in context
3. **Configure Retry Behaviors**: Explicitly configure retry behaviors for predictable failure handling
4. **Persistent Chains**: Set `isPersistent=True` for long-running workflows
5. **Progress Updates**: Use external progress updates for complex workflows with variable task durations

### Error Handling

TaskChain handles errors at two levels:

1. **Task Level**: Each task can retry based on `task.maxRetries`
2. **Chain Level**: After task retries are exhausted, chain retry behavior is applied

```python
# Task fails after 3 retries → Chain behavior applied
task = MyTask(name="Task", maxRetries=3)
chain = TaskChain(
    name="Workflow",
    tasks=[task],
    retryBehaviorMap={'MyTask': ChainRetryBehavior.SKIP_TASK}
)
```

### See Also

- [Architecture Documentation](architecture.md)
- [Task System Design Diagram](diagrams/task-system-architect-design.mermaid)
- [PySide6 Project Rules](.cursor/rules/)
