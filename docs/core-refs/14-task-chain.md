# TaskChain - Sequential Task Execution

> **Execute tasks sequentially with shared context and retry behaviors**
> **Last synced**: `2026-07-06`

## Overview

`TaskChain` allows:

- Sequential task execution
- Shared context (`ChainContext`)
- Per-task retry behaviors
- Error handling strategies
- Progress aggregation (sub-task progress propagated with step labels)
- **Auto-tagging**: Automatically tags children with `_ChainedChild` and `Parent_{UUID}`

## API Reference

### Create Chain

```python
from core.taskSystem import TaskChain, ChainRetryBehavior

chain = TaskChain(
    name='Data Pipeline',
    tasks=[task1, task2, task3],
    description='Process data pipeline',
    retryBehaviorMap={
        'Task1': ChainRetryBehavior.RETRY_TASK,
        'Task2': ChainRetryBehavior.SKIP_TASK,
        'Task3': ChainRetryBehavior.STOP_CHAIN
    }
)
```

### Via TaskManager

```python
taskManager.addChainTask(
    name='Pipeline',
    tasks=[task1, task2, task3],
    retryBehaviorMap={...}
)
```

## ChainContext

Shared state between tasks:

```python
# In task
def handle(self):
    # Access chain context
    context = self._chainContext
    
    # Set data
    context.set('user_id', 123)
    context.set('data', {'key': 'value'})
    
    # Get data
    userId = context.get('user_id')
    data = context.get('data', default={})
```

## ChainRetryBehavior

```python
from core.taskSystem import ChainRetryBehavior

ChainRetryBehavior.STOP_CHAIN   # Stop the entire chain immediately (default when no entry in map)
ChainRetryBehavior.SKIP_TASK    # Skip failed task and continue with next
ChainRetryBehavior.RETRY_TASK   # Task-level retries only (uses task.maxRetries); if still failing, chain falls through and advances to the next task
ChainRetryBehavior.RETRY_CHAIN  # Retry entire chain from the beginning (uses chain.maxRetries)
```

> **Default behavior**: If a task class name is not present in `retryBehaviorMap`, the chain defaults to `STOP_CHAIN`.

> **RETRY_TASK note**: Task-level retries are always applied via `task.maxRetries` inside `_executeSubTaskWithRetry`, regardless of this map entry. `handle()` has no dedicated `RETRY_TASK` branch — when the task fails after exhausting its own retries, execution falls through the switch and the chain advances to the next task (effectively same as `SKIP_TASK`). Use `STOP_CHAIN` (default) if you want the chain to halt on task-level exhaustion.

## Usage Examples

### Basic Chain

```python
from core.taskSystem import AbstractTask

class FetchTask(AbstractTask):
    def handle(self):
        import requests
        response = requests.get('https://api.example.com/data')
        
        # Share data with next task
        self._chainContext.set('raw_data', response.json())

class ProcessTask(AbstractTask):
    def handle(self):
        # Get data from previous task
        rawData = self._chainContext.get('raw_data')
        
        # Process...
        processed = self._process(rawData)
        
        # Share with next task
        self._chainContext.set('processed_data', processed)

class SaveTask(AbstractTask):
    def handle(self):
        # Get processed data
        data = self._chainContext.get('processed_data')
        
        # Save to database
        self._save(data)

# Create chain
chain = taskManager.addChainTask(
    name='Data Pipeline',
    tasks=[FetchTask(), ProcessTask(), SaveTask()]
)
```

### With Retry Behaviors

```python
chain = taskManager.addChainTask(
    name='Robust Pipeline',
    tasks=[
        FetchTask(name='Fetch'),
        ProcessTask(name='Process'),
        SaveTask(name='Save')
    ],
    retryBehaviorMap={
        'FetchTask': ChainRetryBehavior.RETRY_TASK,    # Task-level retries only (task.maxRetries); advances if exhausted
        'ProcessTask': ChainRetryBehavior.SKIP_TASK,   # Skip if processing fails
        'SaveTask': ChainRetryBehavior.STOP_CHAIN      # Critical - stop chain
    }
)
```

> To actually retry on network error, set `task.maxRetries` on `FetchTask` (e.g. `FetchTask(maxRetries=3, retryDelaySeconds=5)`). The chain map entry alone does not add retries.

### Browser Automation Chain

```python
class LoginTask(AbstractTask):
    def handle(self):
        ctx = QtAppContext.globalInstance()
        browser = ctx.getService('browser')
        
        browser.navigate('https://example.com/login')
        browser.fillForm({'username': 'user', 'password': 'pass'})
        browser.click('#login-button')
        
        # Share session
        self._chainContext.set('logged_in', True)

class ScrapeTask(AbstractTask):
    def handle(self):
        if not self._chainContext.get('logged_in'):
            self.fail('Not logged in')
            return
        
        ctx = QtAppContext.globalInstance()
        browser = ctx.getService('browser')
        
        data = browser.extractData('.data-table')
        self._chainContext.set('scraped_data', data)

class ExportTask(AbstractTask):
    def handle(self):
        data = self._chainContext.get('scraped_data')
        
        with open('output.json', 'w') as f:
            json.dump(data, f)

# Chain with shared browser
chain = taskManager.addChainTask(
    name='Scraping Pipeline',
    tasks=[LoginTask(), ScrapeTask(), ExportTask()],
    retryBehaviorMap={
        'LoginTask': ChainRetryBehavior.RETRY_TASK,
        'ScrapeTask': ChainRetryBehavior.RETRY_TASK,
        'ExportTask': ChainRetryBehavior.STOP_CHAIN
    }
)
```

## Progress Tracking

Chain progress aggregates sub-task progress automatically. Each sub-task's progress contributes proportionally, and the chain emits labeled progress strings like `[1/3] FetchTask: Downloading...`.

```python
# Chain aggregates progress from all tasks
chain.progressUpdated.connect(lambda uuid, progress, label: print(f'Chain: {progress}% — {label}'))

# Individual task progress
task1.progressUpdated.connect(lambda uuid, progress, label: print(f'Task 1: {progress}%'))
```

## Error Handling

```python
# Task fails
class RiskyTask(AbstractTask):
    def handle(self):
        if error_condition:
            self.fail('Something went wrong')

# Chain behavior depends on retryBehaviorMap
chain = taskManager.addChainTask(
    name='Chain',
    tasks=[RiskyTask()],
    retryBehaviorMap={
        'RiskyTask': ChainRetryBehavior.SKIP_TASK  # Continue despite failure
    }
)
```

## Best Practices

### ✅ DO

```python
# Use descriptive task names
tasks = [
    FetchDataTask(name='FetchData'),
    ProcessDataTask(name='ProcessData'),
    SaveDataTask(name='SaveData')
]

# Share data via context
self._chainContext.set('key', value)

# Check context data exists
data = self._chainContext.get('key')
if data is None:
    self.fail('Missing required data')
    return

# Use appropriate retry behaviors
retryBehaviorMap={
    'NetworkTask': ChainRetryBehavior.RETRY_TASK,
    'OptionalTask': ChainRetryBehavior.SKIP_TASK,
    'CriticalTask': ChainRetryBehavior.STOP_CHAIN
}
```

### ❌ DON'T

```python
# Don't use global variables
global_data = None  # Wrong! Use context

def handle(self):
    global global_data
    global_data = result  # Use self._chainContext.set()

# Don't assume task order
def handle(self):
    data = self._chainContext.get('data')
    # What if previous task was skipped?

# Don't forget error handling
def handle(self):
    data = self._chainContext.get('required_data')
    process(data)  # May be None!
```

## Related Documentation

- [AbstractTask](13-abstract-task.md) - Base task class
- [TaskManager](15-task-manager.md) - Chain creation
- [Task System Overview](12-task-system-overview.md) - Architecture
