# Task Chaining Feature Implementation

## Summary (tasks-task-chaining.md)

- **Tasks in this file**: 8
- **Task IDs**: 001 - 008

## Tasks

### Task ID: 001

- **Title**: Create ChainContext class for shared data management
- **File**: core/taskSystem/ChainContext.py
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Create a thread-safe ChainContext class to manage shared data between tasks in a chain.

**File to Create:** `core/taskSystem/ChainContext.py`

**Requirements:**
1. Thread-safe data storage using threading.Lock
2. Methods: `get(key, default)`, `set(key, value)`
3. JSON serializable data only
4. Serialization/deserialization support
5. Chain UUID tracking

**Implementation Details:**
- Use `threading.Lock` for thread safety
- Store data in a dictionary
- Validate that values are JSON serializable in `set()` method
- Implement `serialize()` returning dict with `chainUuid` and `data`
- Implement `deserialize()` class method

**Acceptance Criteria:**
- Thread-safe operations
- Can serialize/deserialize context
- Values must be JSON serializable
```

### Task ID: 002

- **Title**: Create ChainRetryBehavior enum for retry strategies
- **File**: core/taskSystem/ChainRetryBehavior.py
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Create an enum defining retry behaviors for task chains.

**File to Create:** `core/taskSystem/ChainRetryBehavior.py`

**Requirements:**
1. Enum with 4 values:
   - STOP_CHAIN: Stop entire chain immediately
   - SKIP_TASK: Skip failed task and continue
   - RETRY_TASK: Retry only the failed task (default)
   - RETRY_CHAIN: Retry entire chain from beginning

**Implementation Details:**
- Use Python's `enum.Enum` with `auto()`
- Add docstrings for each enum value

**Acceptance Criteria:**
- Enum properly defined with all 4 behaviors
- Clear documentation for each behavior
```

### Task ID: 003

- **Title**: Modify AbstractTask to support chain context injection
- **File**: core/taskSystem/AbstractTask.py
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Add chain support to AbstractTask for Task Chaining feature.

**File to Modify:** `core/taskSystem/AbstractTask.py`

**Requirements:**
1. Add `chainUuid` parameter to `__init__` (optional, default None)
2. Add `_chainContext` attribute (private, initially None)
3. Add `setChainContext(context: ChainContext)` method
4. Update `serialize()` to include `chainUuid` and `className`
5. Ensure `className` includes full module path

**Implementation Details:**
- Import ChainContext (use TYPE_CHECKING for type hints)
- Add `chainUuid` as optional parameter in `__init__`
- Initialize `_chainContext = None`
- Implement `setChainContext()` that sets `_chainContext`
- Update `serialize()` to include:
  - `chainUuid`: self.chainUuid
  - `className`: f"{self.__class__.__module__}.{self.__class__.__name__}"
- Update docstring to document chain support

**Acceptance Criteria:**
- AbstractTask can receive chainUuid
- ChainContext can be injected via setChainContext()
- Serialization includes chain information
- Backward compatible (chainUuid is optional)
```

### Task ID: 004

- **Title**: Create TaskChain class implementing chain execution
- **File**: core/taskSystem/TaskChain.py
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Create TaskChain class that executes multiple tasks sequentially with shared context.

**File to Create:** `core/taskSystem/TaskChain.py`

**Requirements:**
1. Inherit from both AbstractTask and Subscriber
2. Initialize with name, tasks list, and optional retryBehaviorMap
3. Set chainUuid for all child tasks
4. Implement sequential execution in `handle()` method
5. Support retry behaviors from ChainRetryBehavior
6. Support progress updates (default and external via events)
7. Implement serialization/deserialization for persistence
8. Handle cancellation of child tasks

**Implementation Details:**
- Import: AbstractTask, Subscriber, ChainContext, ChainRetryBehavior, TaskStatus, Publisher, logger, time
- In `__init__`:
  - Call `AbstractTask.__init__()` and `Subscriber.__init__()`
  - Subscribe to 'ChainProgressUpdateRequest' event
  - Set `chainUuid` for all child tasks
  - Initialize `_chainContext = ChainContext(self.uuid)`
  - Initialize `_taskStates` dict tracking each task's status
  - Store `retryBehaviorMap` (dict mapping task class names to ChainRetryBehavior)
- Implement `handle()`:
  - Loop through tasks sequentially
  - Check `isStopped()` before each task
  - Inject context: `task.setChainContext(self._chainContext)`
  - Call `_executeSubTaskWithRetry(task)`
  - Handle retry behaviors if task fails
  - Update progress (default or external)
- Implement `_executeSubTaskWithRetry(task)`:
  - Retry loop based on `task.maxRetries`
  - Reset task status before each attempt
  - Call `task.run()` synchronously
  - Return True if successful, False if failed after all retries
- Implement `onChainProgressUpdateRequest(data)`:
  - Check if chainUuid matches
  - Update progress if valid (0-100)
  - Set `_progress_updated_externally` flag
- Implement `_updateDefaultProgress()`:
  - Calculate based on current task index
  - Formula: `((currentTaskIndex + 1) / totalTasks) * 100`
- Override `cancel()`:
  - Unsubscribe from events
  - Cancel all child tasks
  - Call super().cancel()
- Implement `serialize()`:
  - Include all AbstractTask fields
  - Add: `tasks` (list of serialized child tasks)
  - Add: `currentTaskIndex`
  - Add: `chainContext` (serialized)
  - Add: `taskStates`
  - Add: `retryBehaviorMap` (convert enum to name)
- Implement `deserialize()`:
  - Reconstruct TaskChain with deserialized tasks
  - Restore `_currentTaskIndex`
  - Restore `_chainContext`
  - Restore `_taskStates`
  - Restore `retryBehaviorMap` (convert names back to enum)
- Implement `_performCancellationCleanup()`:
  - Cancel all child tasks
  - Unsubscribe from events

**Acceptance Criteria:**
- Tasks execute sequentially
- Context is shared between tasks
- Retry behaviors work correctly
- Progress updates work (default and external)
- Serialization/deserialization works for persistence
- Cancellation works for chain and child tasks
- Chain can recover from app restart
```

### Task ID: 005

- **Title**: Update TaskTracker to handle TaskChain display
- **File**: core/taskSystem/TaskTracker.py
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Enhance TaskTracker to recognize and display TaskChain structure with child tasks.

**File to Modify:** `core/taskSystem/TaskTracker.py`

**Requirements:**
1. Detect TaskChain in `addTask()` method
2. Track child tasks with chain relationship metadata
3. Update `getTaskInfo()` to return chain structure if applicable
4. Maintain backward compatibility with regular tasks

**Implementation Details:**
- In `addTask()`:
  - Check if task is TaskChain (import TaskChain, use isinstance)
  - If TaskChain, iterate through `task._tasks` (child tasks)
  - Add each child task to tracking with metadata:
    - `isChainChild: True`
    - `chainUuid: task.uuid`
    - `parentChainName: task.name`
  - Store child task references in a separate dict or extend `_activeTasks` structure
- In `getTaskInfo(uuid)`:
  - Check if uuid is a TaskChain
  - If TaskChain, return task info with additional field:
    - `subTasks`: List of child task info dictionaries
    - `chainContext`: Serialized chain context (if available)
  - If regular task, check if it's a chain child
  - If chain child, include parent chain info in response
- Consider adding helper method `_isTaskChain(task)` for cleaner code

**Acceptance Criteria:**
- TaskChain is recognized and tracked
- Child tasks are tracked with chain relationship
- `getTaskInfo()` returns chain structure for TaskChain
- Child tasks show parent chain information
- Backward compatible with existing tasks
```

### Task ID: 006

- **Title**: Add addChainTask method to TaskManagerService
- **File**: core/taskSystem/TaskManagerService.py
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Add convenience method to TaskManagerService for creating and adding TaskChain.

**File to Modify:** `core/taskSystem/TaskManagerService.py`

**Requirements:**
1. Add `addChainTask()` method
2. Method should create TaskChain and add it to system
3. Support same scheduling options as `addTask()`

**Implementation Details:**
- Import TaskChain from services.tasks.TaskChain
- Add method signature:
  ```python
  def addChainTask(
      self, 
      name: str, 
      tasks: List[AbstractTask], 
      scheduleInfo: Optional[Dict[str, Any]] = None,
      retryBehaviorMap: Optional[Dict[str, ChainRetryBehavior]] = None,
      **kwargs
  ) -> TaskChain:
  ```
- Create TaskChain instance with provided parameters
- Call `self.addTask(chain, scheduleInfo=scheduleInfo)`
- Return the created TaskChain instance
- Add docstring explaining usage and parameters

**Acceptance Criteria:**
- Method creates TaskChain correctly
- Supports scheduling like regular tasks
- Returns TaskChain instance
- Properly integrated with existing task system
```

### Task ID: 007

- **Title**: Create core/taskSystem/__init__.py for module exports
- **File**: core/taskSystem/__init__.py
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Create __init__.py file for core/taskSystem module to export TaskChain.

**File to Create:** `core/taskSystem/__init__.py`

**Requirements:**
1. Export TaskChain class
2. Follow Python package conventions

**Implementation Details:**
- Add `__all__` list with 'TaskChain'
- Import TaskChain from .TaskChain
- Add module docstring

**Acceptance Criteria:**
- TaskChain can be imported from services.tasks
- Module follows Python conventions
```

### Task ID: 008

- **Title**: Update documentation for Task Chaining feature
- **File**: docs/task-system-api.md (or create if not exists)
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Document the Task Chaining feature API and usage patterns.

**File to Create/Modify:** `docs/task-system-api.md`

**Requirements:**
1. Document ChainContext API
2. Document ChainRetryBehavior enum
3. Document TaskChain class API
4. Provide usage examples
5. Document serialization/deserialization
6. Document retry behavior configuration

**Implementation Details:**
- Create or update documentation file
- Include:
  - Overview of Task Chaining feature
  - ChainContext usage examples
  - ChainRetryBehavior explanation
  - TaskChain creation and execution
  - Retry behavior configuration examples
  - Context sharing patterns
  - Serialization/deserialization guide
  - Recovery after app restart
- Add code examples showing:
  - Creating a simple chain
  - Using ChainContext to share data
  - Configuring retry behaviors
  - Handling chain failures

**Acceptance Criteria:**
- Complete API documentation
- Clear usage examples
- Covers all major use cases
- Explains serialization for persistence
```

### Task ID: 009

- **Title**: Add Sample Chaining Task and Update UI/Docs
- **File**: app/tasks/ChainDemoTask.py
- **Complete**: [x]

#### Prompt:

```markdown
**Objective:** Add a sample chaining task, update UI to display chain status, and update documentation structure.

**Files to Create/Modify:**
- `app/tasks/ChainDemoTask.py` (Create)
- `app/tasks/__init__.py` (Modify)
- `app/windows/main/MainController.py` (Modify)
- `app/windows/main/MainControllerHandler.py` (Modify)
- `README.base.md` (Modify)
- `README.base.vi.md` (Modify)
- `docs/provided-by-base/TaskSystem.md` (Create/Move)
- `docs/TaskSystem.md` (Delete)

**Requirements:**
1. Create `ChainDemoTask` with sub-tasks (`DataGeneratorTask`, `DataProcessorTask`, `FlakyTask`) demonstrating context sharing and retry logic.
2. Update `MainController` to display chain status and child statuses correctly (filtering child tasks from main view, logging child status updates).
3. Update `MainControllerHandler` to handle "Add Chain Task" action.
4. Update `README.base.md` and `README.base.vi.md` with correct directory structure.
5. Move `docs/TaskSystem.md` content to `docs/provided-by-base/TaskSystem.md` and update it with new TaskSystem details.
6. Remove old `docs/TaskSystem.md`.

**Implementation Details:**
- Implement `ChainDemoTask` factory and sub-task classes in `app/tasks/ChainDemoTask.py`.
- Export new tasks in `app/tasks/__init__.py`.
- In `MainController.py`:
  - Filter out `isChainChild` tasks from the main table.
  - Update `ontask_status_updated` and `onfailed_task_logged` to log child task events with parent context.
- In `MainControllerHandler.py`:
  - Add `onbtnAddChainTask_clicked` handler.
- Update READMEs to reflect `docs/provided-by-base` structure.
- Create `docs/provided-by-base/TaskSystem.md` with updated content covering TaskChain.

**Acceptance Criteria:**
- "Add Chain Task" button works and creates a chain.
- UI shows the chain task but not individual child tasks in the main list.
- Logs show progress of child tasks clearly.
- Documentation is up-to-date and in the correct location.
```
