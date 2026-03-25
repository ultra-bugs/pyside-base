# AbstractTask - Base Task Class

> **Base class for background tasks with lifecycle management, signals, and serialization**

## Overview

`AbstractTask` is the abstract base class for all background tasks. It provides:

- QRunnable integration (via QThreadPool)
- Qt signals (`statusChanged`, `progressUpdated`, `taskFinished`)
- Lifecycle management (PENDING → RUNNING → COMPLETED/FAILED/CANCELLED/PAUSED)
- Serialization and deserialization
- Retry mechanism
- Cancellation support
- Unique Task constraint support

## API Reference

### Constructor

```python
from core.taskSystem import AbstractTask, UniqueType

class MyTask(AbstractTask):
    def __init__(self, name, **kwargs):
        super().__init__(
            name=name,
            description='Task description',
            isPersistent=False,
            maxRetries=0,
            retryDelaySeconds=5,
            failSilently=False,
            retryDelaySeconds=5,
            failSilently=False,
            chainUuid=None,
            tags=None,
            uniqueType=UniqueType.NONE
        )
        )
```

### Abstract Methods

```python
def handle(self):
    """Main task logic - must be implemented"""
    pass

def _performCancellationCleanup(self):
    """Cleanup upon cancellation - must be implemented"""
    pass

@classmethod
def deserialize(cls, data: dict):
    """Deserialize from dict - must implement if isPersistent=True"""
    pass
def deserialize(cls, data: dict):
    """Deserialize from dict - must implement if isPersistent=True"""
    pass
```

### Tagging

```python
task.addTag('Network')
task.removeTag('Network')
hasTag = task.hasTag('Network')
tags = task.tags  # Set[str]
```

### Lifecycle & Status Management (`TaskState`)

Tasks use a thread-safe `TaskState` object to wrap the native `TaskStatus` enum. Services can be injected with the `taskState` parameter to seamlessly check cooperative lifecycle flags (stopped, paused) without carrying hard dependencies on the `AbstractTask` implementation.

```python
# Propagate UI updates and trigger events via task instance wrappers
self.setStatus(TaskStatus.RUNNING)
self.setProgress(50)  # 0-100

# Accessing properties directly
current_status = self.status  # Proxy for self.taskState.current
if self.taskState.isPaused():
    self.taskState.waitIfPaused()  # Block executing thread inherently until resumed
```

### Cancellation

```python
if self.isStopped():
    return

self.cancel()  # Request cancellation cooperatively
self.fail('Reason')  # Mark manually as failed
```

### Serialization

```python
# Auto-serialization for persistence
data = task.serialize()

# Defining custom fields to serialize
class MyTask(AbstractTask):
    serializables = ['customField1', 'customField2']
```

## Unique Tasks

Used to prevent duplicate tasks from queueing or running concurrently across the task ecosystem.

### Concepts

**UniqueType Enum**:
- `UniqueType.NONE`: No uniqueness constraint (default behavior).
- `UniqueType.JOB`: **Global Uniqueness**. Ensures only one instance exists in the entire system (Pending OR Running). If a duplicate is queued, it is simply ignored (deduplicated).
- `UniqueType.UNTIL_PROCESSING`: **Queue Uniqueness**. Ensures only one instance exists in the **Pending** queue. Once the task structurally begins running, another new instance can be pushed to the queue.

**uniqueVia()**:
- Defines the actual unique key signature for the task.
- Default: Returns `self.__class__.__name__` (Class-based uniqueness).
- Override to provide granular target definitions (e.g., uniqueness based on specific file, network payload, per ID).

### Usage

```python
from core.taskSystem import AbstractTask, UniqueType

class ProcessFileTask(AbstractTask):
    def __init__(self, filePath):
        super().__init__(
            name=f'Process {filePath}',
            uniqueType=UniqueType.JOB  # Global uniqueness enforced for this task
        )
        self.filePath = filePath

    def uniqueVia(self) -> str:
        # Create a unique key mapped directly to file path strings
        return f"{self.__class__.__name__}_{self.filePath}"
```

## Task Status

```python
from core.taskSystem import TaskStatus

TaskStatus.PENDING     # Waiting in queue to start
TaskStatus.RUNNING     # Currently executing in runner
TaskStatus.COMPLETED   # Finished successfully
TaskStatus.FAILED      # Failed alongside raising an error
TaskStatus.CANCELLED   # Cancelled externally by user workflow
TaskStatus.PAUSED      # Execution suspended temporarily over the pause barrier
```

## Signals

```python
task.statusChanged.connect(lambda status: print(f'Status: {status}'))
task.progressUpdated.connect(lambda progress: print(f'Progress: {progress}%'))
task.taskFinished.connect(lambda: print('Task finished'))
```

## Usage Examples

### Basic Task

```python
from core.taskSystem import AbstractTask

class DownloadTask(AbstractTask):
    def __init__(self, url, savePath):
        super().__init__(name=f'Download {url}')
        self.url = url
        self.savePath = savePath
    
    def handle(self):
        import requests
        
        response = requests.get(self.url, stream=True)
        total = int(response.headers.get('content-length', 0))
        
        with open(self.savePath, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if self.isStopped():
                    return
                
                f.write(chunk)
                downloaded += len(chunk)
                self.setProgress(int(downloaded / total * 100))
    
    def _performCancellationCleanup(self):
        # Remove partial file segments
        if os.path.exists(self.savePath):
            os.remove(self.savePath)
```

### With Scoped Resources

```python
class BrowserTask(AbstractTask):
    def __init__(self, url):
        super().__init__(name=f'Browse {url}')
        self.url = url
    
    def handle(self):
        from core import QtAppContext
        
        ctx = QtAppContext.globalInstance()
        taskId = self.uuid
        
        browser = ChromeBrowserService()
        ctx.registerScopedService(taskId, browser)
        
        try:
            browser.navigate(self.url)
            
            # Do scraping...
            for i in range(10):
                if self.isStopped():
                    return
                # Process...
                self.setProgress(i * 10)
        
        finally:
            ctx.releaseScope(taskId)
    
    def _performCancellationCleanup(self):
        # Browser cleanup inherently handled safely through releaseScope
        pass
```

### Persistent Task

```python
class DataProcessTask(AbstractTask):
    serializables = ['dataPath', 'outputPath']
    
    def __init__(self, dataPath, outputPath):
        super().__init__(
            name='Process Data',
            isPersistent=True
        )
        self.dataPath = dataPath
        self.outputPath = outputPath
    
    def handle(self):
        # Process data...
        pass
    
    @classmethod
    def deserialize(cls, data: dict):
        return cls(
            dataPath=data['dataPath'],
            outputPath=data['outputPath']
        )
    
    def _performCancellationCleanup(self):
        pass
```

### With Retry

```python
class ApiTask(AbstractTask):
    def __init__(self, endpoint):
        super().__init__(
            name=f'API Call {endpoint}',
            maxRetries=3,
            retryDelaySeconds=5
        )
        self.endpoint = endpoint
    
    def handle(self):
        import requests
        
        try:
            response = requests.get(self.endpoint)
            response.raise_for_status()
            # Process response payload...
        except requests.RequestException as e:
            self.fail(f'API call failed: {e}')
    
    def _performCancellationCleanup(self):
        pass
```

## Lifecycle

```python
# 1. Created
task = MyTask(name='My Task')
# Status: PENDING

# 2. Added to queue
taskManager.addTask(task)
# Status: PENDING

# 3. Execution starts
# Status: RUNNING
# Calls: handle()

# 4. Completion hooks
# Success => Status: COMPLETED
# Error => Status: FAILED
# Cancelled => Status: CANCELLED

# 5. Finished and cleaned up
# Emits: taskFinished signal internally
```

## Best Practices

### ✅ DO

```python
# Check isStopped() regularly
def handle(self):
    for item in items:
        if self.isStopped():
            return
        # Carry across pipeline...

# Update progress
def handle(self):
    total = len(items)
    for i, item in enumerate(items):
        # Process block logic...
        self.setProgress(int(i / total * 100))

# Use try-finally for cleanup
def handle(self):
    try:
        # Hard operations...
        pass
    finally:
        # Cleanup...
        pass

# Ensure full adherence inside pure cancellation triggers
def _performCancellationCleanup(self):
    # Remove temp files, kill processes, etc.
    pass
```

### ❌ DON'T

```python
# Avoid infinite unmonitored blocking segments inside handle loops
def handle(self):
    while True:  # No stop check!
        # Work...
        pass

# Don't forget progress updates
def handle(self):
    # Extreme overhead heavy task calculation layer...
    pass  # Ignores setProgress() emitting protocols entirely!

# Don't use UI thread APIs
def handle(self):
    ctx = QtAppContext.globalInstance()
    network = ctx.network  # Strongly forbidden natively mapping QNetworkAccessManager within background
    
# Disregard crucial abstract clean up mandates enforcing partial footprint traces
def _performCancellationCleanup(self):
    pass  # Completely nullified execution ignores payload traces leftover completely!
```

## Related Documentation

- [Task System Overview](12-task-system-overview.md) - Architecture
- [TaskChain](14-task-chain.md) - Sequential execution
- [TaskManager](15-task-manager.md) - Task management
- [ServiceLocator](02-dependency-injection.md) - Scoped resources
