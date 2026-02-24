## Summary (tasks-3.md)

- **Tasks in this file**: 8
- **Task IDs**: 027 - 034

## Tasks

### Task ID: 027

- **Title**: Add QMutex/QWaitCondition pause gate to AbstractTask
- **File**: core/taskSystem/AbstractTask.py
- **Complete**: [ ]

#### Prompt:

```markdown
**Objective:** Add pause/resume mechanism to AbstractTask using Qt primitives (QMutex + QWaitCondition).

**File to Modify:** core/taskSystem/AbstractTask.py

**Detailed Instructions:**
1. Import QMutex, QWaitCondition from PySide6.QtCore
2. In __init__, add: _pauseMutex (QMutex), _pauseCondition (QWaitCondition), _isPaused (bool=False), _pauseCheckIntervalMs (int=500)
3. Add pause() method: lock mutex, set _isPaused=True, unlock, call setStatus(PAUSED)
4. Add resume() method: lock mutex, set _isPaused=False, wakeAll, unlock, call setStatus(RUNNING)
5. Add checkPaused() method: lock mutex, while _isPaused and not isStopped(): _pauseCondition.wait(mutex, _pauseCheckIntervalMs), unlock
6. Update cancel(): after _stopEvent.set(), also lock mutex, _isPaused=False, wakeAll, unlock — so paused threads can exit
7. Follow camelCase naming convention

**Acceptance Criteria:**
- pause() sets status to PAUSED and _isPaused flag
- resume() sets status to RUNNING and wakes blocked thread
- checkPaused() blocks thread when paused, unblocks on resume or cancel
- cancel() unblocks paused thread
```

### Task ID: 028

- **Title**: Update TaskManagerService pauseTask/resumeTask
- **File**: core/taskSystem/TaskManagerService.py
- **Complete**: [ ]

#### Prompt:

```markdown
**Objective:** Wire TaskManagerService.pauseTask()/resumeTask() to the new AbstractTask.pause()/resume() methods.

**File to Modify:** core/taskSystem/TaskManagerService.py

**Detailed Instructions:**
1. pauseTask(uuid): lookup task, verify status is RUNNING, call task.pause(). Remove "not fully implemented" docstring note.
2. resumeTask(uuid): lookup task, verify status is PAUSED, call task.resume(). Remove "not fully implemented" docstring note.
3. Add proper status guard (warn if wrong state)
4. Raise TaskNotFoundException if task not found

**Acceptance Criteria:**
- pauseTask only works on RUNNING tasks
- resumeTask only works on PAUSED tasks
- TaskNotFoundException raised for unknown UUID
- Docstrings updated (no "not implemented" notes)
```

### Task ID: 029

- **Title**: Fix auto-retry double signal connection
- **File**: core/taskSystem/TaskQueue.py
- **Complete**: [ ]

#### Prompt:

```markdown
**Objective:** Fix the auto-retry mechanism which has 3 bugs causing duplicate signal handlers and missing status signals.

**File to Modify:** core/taskSystem/TaskQueue.py

**Detailed Instructions:**

**Bug 1 — Disconnect on pop:**
In _handleTaskCompletion, after `task = self._runningTasks.pop(uuid)`, disconnect `task.taskFinished` from `self._handleTaskCompletion`. Use try/except RuntimeError to handle cases where not connected.

**Bug 2 — Fix _retryTask:**
Replace current _retryTask implementation:
- Use `task.setStatus(TaskStatus.PENDING)` instead of `task.status = TaskStatus.PENDING`
- Clear `task.errorException` as well as `task.error`
- Re-enqueue directly to `self._pendingTasks.append(task)` instead of calling `self.addTask(task)` (task is still tracked)
- Emit `self.queueStatusChanged.emit()` and call `self._processQueue()`
- Do NOT call `self._taskTracker.addTask(task)` since the task is still in tracker

**Acceptance Criteria:**
- _handleTaskCompletion fires exactly once per task execution (no duplicate)
- Status signal emitted when task enters PENDING for retry
- Task not double-added to tracker
```

### Task ID: 030

- **Title**: Implement TaskQueue.loadState
- **File**: core/taskSystem/TaskQueue.py
- **Complete**: [ ]

#### Prompt:

```markdown
**Objective:** Implement TaskQueue.loadState() to restore pending tasks from storage.

**File to Modify:** core/taskSystem/TaskQueue.py

**Detailed Instructions:**
1. Load 'pendingTasks' list from self._storage
2. For each taskData:
   - Get className, split into module + class
   - Dynamic import via __import__(moduleName, fromlist=[clsName])
   - Call taskCls.deserialize(taskData) to reconstruct
   - Call self.addTask(task) to add to queue
3. Skip entries with missing className (log warning)
4. Wrap individual task restoration in try/except (log error, continue)
5. Log total restored count
6. Use logger.opt(exception=e).error() pattern per project rules

**Acceptance Criteria:**
- Persisted pending tasks restored on loadState()
- Corrupted entries skipped gracefully
- Proper logging for success and failure
```

### Task ID: 031

- **Title**: Write unit tests for pause/resume in AbstractTask
- **File**: tests_core/task_system/test_PauseResume.py
- **Complete**: [ ]

#### Prompt:

```markdown
**Objective:** Write unit tests for the new pause/resume mechanism.

**File to Create:** tests_core/task_system/test_PauseResume.py

**Detailed Instructions:**
Create a SlowTask subclass that loops and calls checkPaused(). Test:
1. test_pause_sets_status — pause() sets PAUSED
2. test_resume_sets_status — resume() after pause sets RUNNING
3. test_checkPaused_blocks_thread — verify thread blocks when paused (use threading + timeout)
4. test_cancel_while_paused — cancel() unblocks paused thread
5. test_pause_resume_cycle — full cycle: start → pause → resume → complete

Use qtbot, ConcreteTask from test_AbstractTask, pytest fixtures.
Follow camelCase for test helper methods, test_ prefix for test functions.

**Acceptance Criteria:**
- All 5 tests pass
- Tests use Qt fixtures (qtbot)
- SlowTask properly calls checkPaused() in its handle()
```

### Task ID: 032

- **Title**: Write unit tests for auto-retry fix
- **File**: tests_core/task_system/test_AutoRetry.py
- **Complete**: [ ]

#### Prompt:

```markdown
**Objective:** Write unit tests verifying the auto-retry fix works correctly.

**File to Create:** tests_core/task_system/test_AutoRetry.py

**Detailed Instructions:**
Create a FailingTask that fails N times then succeeds. Test:
1. test_retry_fires_exactly_once_per_attempt — verify _handleTaskCompletion fires once per execution
2. test_retry_emits_status_signals — verify RETRYING → PENDING status signals emitted
3. test_retry_then_success — task fails twice, succeeds third time
4. test_cancel_during_retry_wait — cancel while waiting for retry timer
5. test_no_retry_when_max_zero — task with maxRetries=0 fails permanently

Use qtbot, mock_config, TaskQueue/TaskTracker fixtures.

**Acceptance Criteria:**
- All tests pass
- No duplicate signal handler firing
- Status signals correctly emitted
```

### Task ID: 033

- **Title**: Write unit tests for TaskQueue.loadState
- **File**: tests_core/task_system/test_LoadState.py
- **Complete**: [ ]

#### Prompt:

```markdown
**Objective:** Write unit tests for TaskQueue.loadState() implementation.

**File to Create:** tests_core/task_system/test_LoadState.py

**Detailed Instructions:**
Test:
1. test_loadState_empty — No tasks in storage, nothing restored
2. test_loadState_restores_tasks — Save tasks, load them back
3. test_loadState_skips_invalid — Entry with missing className skipped
4. test_loadState_handles_deserialization_error — Corrupted task data handled gracefully
5. test_loadState_round_trip — saveState → loadState → verify same tasks

Use mock_config/storage, ConcreteTask.

**Acceptance Criteria:**
- All tests pass
- Error cases handled gracefully
- Round-trip serialization verified
```

### Task ID: 034

- **Title**: Update docs/task-system-api.md with pause/resume API
- **File**: core/taskSystem/docs/task-system-api.md
- **Complete**: [ ]

#### Prompt:

```markdown
**Objective:** Update API documentation to reflect new pause/resume methods and loadState.

**File to Modify:** core/taskSystem/docs/task-system-api.md

**Detailed Instructions:**
1. Add AbstractTask.pause(), resume(), checkPaused() to API reference
2. Add _pauseCheckIntervalMs parameter documentation
3. Update TaskManagerService.pauseTask/resumeTask docs (remove "not implemented" note)
4. Add TaskQueue.loadState() documentation
5. Add note about subclass contract for checkPaused()

**Acceptance Criteria:**
- API docs accurate and complete
- Pause/resume contract documented
```
