"""
TaskQueue

Manages FIFO queue of tasks with concurrency limits and retry logic.
Uses DaemonWorker pattern for serialized queue processing — all mutations
to _pendingTasks/_runningTasks happen on a single worker thread, eliminating
race conditions and re-entrancy risks.

Submits tasks to QThreadPool for execution.
"""

#                  M"""""""`M            dP
#                  Mmmmmm   .M            88
#                  MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#                  MMP  .MMMMM  88    88  88888"    88'  `88
#                  M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#                  M         M  `88888P'  dP   `YP  `88888P'
#                  MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#                  * * * * * * * * * * * * * * * * * * * * *
#                  * -    - -   F.R.E.E.M.I.N.D   - -    - *
#                  * -  Copyright © 2026 (Z) Programing  - *
#                  *    -  -  All Rights Reserved  -  -    *
#                  * * * * * * * * * * * * * * * * * * * * *
import threading as _threading
from collections import deque
from typing import Any, Dict, Optional

from PySide6 import QtCore

from ..Config import Config
from ..Logging import logger
from ..contracts.Message import Message
from ..threading.DaemonWorker import DaemonWorker
from .Exceptions import TaskNotFoundException
from .signals.TaskQueueSignals import TaskQueueSignals
from .storage.BaseStorage import BaseStorage
from .TaskStatus import TaskStatus
from .TaskTracker import TaskTracker
from .UniqueType import UniqueType

# Initialize logger for TaskSystem
logger = logger.bind(component='TaskSystem')

# ── Internal queue command topics ─────────────────────────────────────────────
_CMD_ADD = 'queue.add'
_CMD_PROCESS = 'queue.process'
_CMD_COMPLETION = 'queue.done'
_CMD_RETRY = 'queue.retry'


class _TaskQueueWorker(DaemonWorker):
    """Single-thread FIFO worker for TaskQueue commands.

    All mutations to pending/running state happen here — naturally serialized,
    no locks needed, no re-entrancy risk.
    """

    def __init__(self, taskQueue: 'TaskQueue'):
        super().__init__('TaskQueueWorker')
        self._taskQueue = taskQueue

    def onItem(self, msg: Message) -> None:
        topic = msg.topic
        payload = msg.payload
        if topic == _CMD_ADD:
            self._taskQueue._addTaskInternal(payload['task'])
        elif topic == _CMD_PROCESS:
            self._taskQueue._processQueue()
        elif topic == _CMD_COMPLETION:
            self._taskQueue._handleTaskCompletionInternal(payload['uuid'], payload['task'], payload['result'], payload['error'])
        elif topic == _CMD_RETRY:
            self._taskQueue._retryTaskInternal(payload['task'])


class TaskQueue(QtCore.QObject):
    """FIFO queue manager for tasks with concurrency control.

    Uses a DaemonWorker for serialized queue processing:
    - `addTask()` can be called from ANY thread — enqueues a Message
    - `_processQueue()` runs ONLY on the worker thread (serialized)
    - `_handleTaskCompletion` defers to worker via signal → Message

    Responsibilities:
    - Maintain pending task queue
    - Track running tasks
    - Enforce concurrency limits
    - Handle task completion and retry logic
    - Persist pending tasks

    Signals:
        queueStatusChanged: Emitted when queue status changes
        taskQueued: Emitted when a task is added to queue
        taskDequeued: Emitted when a task starts execution
    """

    # Signals are provided by TaskQueueSignals (composition).
    # Proxy properties below for backward-compat.

    def __init__(self, taskTracker: TaskTracker, storage: BaseStorage, config: Config, maxConcurrentTasks: int = 3):
        """Initialize TaskQueue.
        Args:
            taskTracker: TaskTracker instance for monitoring
            storage: Storage backend for persistence
            config: Configuration instance
            maxConcurrentTasks: Maximum number of concurrent tasks (default: 3)
        """
        super().__init__()
        self.signals = TaskQueueSignals()
        self._taskTracker = taskTracker
        self._storage = storage
        self._config = config
        self._maxConcurrentTasks = maxConcurrentTasks
        # Task queues
        self._pendingTasks = deque()  # FIFO queue of pending tasks
        self._runningTasks = {}  # uuid -> task mapping
        # Unique Task Index: key -> {'pending': int, 'running': int}
        self._activeUniqueKeys: dict[str, dict[str, int]] = {}
        # Thread pool for task execution
        self._threadPool = QtCore.QThreadPool.globalInstance()
        self._threadPool.setMaxThreadCount(maxConcurrentTasks)
        # DaemonWorker for serialized queue processing
        self._worker = _TaskQueueWorker(self)
        # Load persisted state
        self.loadState()
        logger.info(f'TaskQueue initialized with max concurrent tasks: {maxConcurrentTasks}')

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Start the queue worker. Must be called before tasks can be processed."""
        self._worker.start()
        logger.info('TaskQueue worker started')
        # Trigger initial processing for any tasks loaded from state
        self._enqueueCommand(_CMD_PROCESS)

    def stop(self) -> None:
        """Gracefully stop the queue worker after draining pending commands."""
        self._worker.stop()
        logger.info('TaskQueue worker stopped')

    # ── Signal proxy properties (backward-compat) ─────────────────────────────

    @property
    def queueStatusChanged(self):
        return self.signals.queueStatusChanged

    @property
    def taskQueued(self):
        return self.signals.taskQueued

    @property
    def taskDequeued(self):
        return self.signals.taskDequeued

    # ── Public API (callable from any thread) ─────────────────────────────────

    def addTask(self, task: Any) -> None:
        """Add a task to the queue. Thread-safe — can be called from any thread.
        Args:
            task: AbstractTask instance to queue
        """
        self._enqueueCommand(_CMD_ADD, task=task)

    def setMaxConcurrentTasks(self, count: int) -> None:
        """Set maximum number of concurrent tasks.
        Args:
            count: Maximum concurrent tasks (must be > 0)
        """
        if count is None:
            return
        if count <= 0:
            logger.warning(f'Invalid max concurrent tasks: {count}. Must be > 0')
            return
        self._maxConcurrentTasks = count
        self._threadPool.setMaxThreadCount(count)
        logger.info(f'Max concurrent tasks set to: {count}')
        # Trigger processing in case limit increased
        self._enqueueCommand(_CMD_PROCESS)

    # ── Internal: runs on DaemonWorker thread ─────────────────────────────────

    def _enqueueCommand(self, topic: str, **payload) -> None:
        """Enqueue a command Message to the worker. Thread-safe."""
        self._worker.enqueue(Message(topic=topic, payload=payload))

    def _addTaskInternal(self, task: Any) -> None:
        """Process ADD command on worker thread.
        Validates uniqueness, adds to pending queue, triggers processing.
        """
        # Check Uniqueness Constraints
        if task.uniqueType != UniqueType.NONE:
            key = task.uniqueVia()
            stats = self._activeUniqueKeys.get(key, {'pending': 0, 'running': 0})
            if task.uniqueType == UniqueType.JOB:
                if stats['pending'] > 0 or stats['running'] > 0:
                    logger.warning(f"UniqueJob violation: Task '{task.name}' with key '{key}' already exists (Pending: {stats['pending']}, Running: {stats['running']}). Ignoring.")
                    return
            elif task.uniqueType == UniqueType.UNTIL_PROCESSING:
                if stats['pending'] > 0:
                    logger.warning(f"UniqueUntilProcessing violation: Task '{task.name}' with key '{key}' already pending. Ignoring.")
                    return
            # Update Index (Add to Pending)
            if key not in self._activeUniqueKeys:
                self._activeUniqueKeys[key] = {'pending': 0, 'running': 0}
            self._activeUniqueKeys[key]['pending'] += 1
        # Add to pending queue
        self._pendingTasks.append(task)
        # Add to tracker
        self._taskTracker.addTask(task)
        logger.info(f'Task queued: {task.uuid} - {task.name} (Queue size: {len(self._pendingTasks)})')
        self.taskQueued.emit(task.uuid)
        self.queueStatusChanged.emit()
        # Process queue immediately (already on worker thread)
        self._processQueue()

    def _processQueue(self) -> None:
        """Process pending tasks if there are available slots.
        Runs ONLY on the DaemonWorker thread — naturally serialized.
        """
        while len(self._runningTasks) < self._maxConcurrentTasks and self._pendingTasks:
            task = self._pendingTasks.popleft()
            # Update Unique Index (Remove from Pending)
            if task.uniqueType != UniqueType.NONE:
                key = task.uniqueVia()
                if key in self._activeUniqueKeys:
                    self._activeUniqueKeys[key]['pending'] -= 1
            # Skip if task was already cancelled
            if task.status == TaskStatus.CANCELLED:
                logger.info(f'Skipping cancelled task: {task.uuid}')
                self._taskTracker.removeTask(task.uuid)
                # Cleanup unique key if empty
                if task.uniqueType != UniqueType.NONE:
                    self._cleanupUniqueKey(task.uniqueVia())
                continue
            # Update Unique Index (Add to Running)
            if task.uniqueType != UniqueType.NONE:
                key = task.uniqueVia()
                if key in self._activeUniqueKeys:
                    self._activeUniqueKeys[key]['running'] += 1
            # Move to running
            self._runningTasks[task.uuid] = task
            # Connect to task finished signal — defers to worker via _onTaskFinishedSignal
            task.taskFinished.connect(self._onTaskFinishedSignal)
            # Submit to thread pool
            self._threadPool.start(task)
            logger.info(f'Task started: {task.uuid} - {task.name} (Running: {len(self._runningTasks)})')
            self.taskDequeued.emit(task.uuid)
            self.queueStatusChanged.emit()

    def _onTaskFinishedSignal(self, uuid: str, task, result: Any, error: Optional[Dict[str, str | Exception]]) -> None:
        """Signal slot: receives taskFinished from worker threads.
        Defers actual processing to the DaemonWorker thread via a COMPLETION message.
        This ensures the worker thread has fully released back to QThreadPool
        before we try to submit new tasks.
        """
        self._enqueueCommand(_CMD_COMPLETION, uuid=uuid, task=task, result=result, error=error)

    def _handleTaskCompletionInternal(self, uuid: str, task, result: Any, error: Optional[Dict[str, str | Exception]]) -> None:
        """Handle task completion on worker thread. Includes retry logic.
        Args:
            uuid: Task UUID
            task: The completed task instance
            result: Task result (if successful)
            error: Error dict (if failed)
        """
        finalStatus: TaskStatus = task.status
        if uuid not in self._runningTasks:
            logger.critical(f'Task {uuid} not found in running tasks')
            logger.critical('--------------- NEED RECHECK')
            return
        task = self._runningTasks.pop(uuid)
        # Disconnect to prevent duplicate connections on retry
        try:
            task.taskFinished.disconnect(self._onTaskFinishedSignal)
        except RuntimeError:
            pass
        # Update Unique Index (Remove from Running)
        if task.uniqueType != UniqueType.NONE:
            key = task.uniqueVia()
            if key in self._activeUniqueKeys:
                self._activeUniqueKeys[key]['running'] -= 1
            self._cleanupUniqueKey(key)
        logger.info(f'Task completed: {uuid} - Status: {finalStatus.name}')
        # Handle retry logic for failed tasks (skip if cancelled)
        if finalStatus == TaskStatus.FAILED and task.isStopped() is False and task.currentRetryAttempts < task.maxRetries:
            task.currentRetryAttempts += 1
            task.setStatus(TaskStatus.RETRYING)
            logger.info(f'Task {uuid} will retry (attempt {task.currentRetryAttempts}/{task.maxRetries}) in {task.retryDelaySeconds}s')
            # Log this retry attempt
            self._taskTracker.logFailedTask(task)
            # Schedule retry via threading.Timer → works on DaemonWorker thread
            # (QTimer.singleShot requires a Qt event loop which DaemonWorker doesn't have)
            _threading.Timer(task.retryDelaySeconds, lambda t=task: self._enqueueCommand(_CMD_RETRY, task=t)).start()
        else:
            # Task is done (completed, cancelled, or failed without retry)
            if finalStatus == TaskStatus.FAILED:
                # Log permanent failure
                self._taskTracker.logFailedTask(task)
            # Remove from tracker
            try:
                self._taskTracker.removeTask(uuid)
            except TaskNotFoundException:
                logger.critical(f'Task {uuid} was not in tracker')
                logger.critical('--------------- NEED RECHECK')
        # Save state and process next tasks
        self.saveState()
        self.queueStatusChanged.emit()
        self._processQueue()

    def _retryTaskInternal(self, task: Any) -> None:
        """Re-enqueue a failed task for retry. Runs on worker thread.
        Args:
            task: Task to retry
        """
        # Guard: skip retry if task was cancelled while waiting for retry timer
        if task.isStopped() or task.status == TaskStatus.CANCELLED:
            logger.info(f'Skipping retry for cancelled task: {task.uuid} - {task.name}')
            try:
                self._taskTracker.removeTask(task.uuid)
            except TaskNotFoundException:
                pass
            return
        logger.info(f'Retrying task: {task.uuid} - {task.name}')
        # Reset task state for retry
        task.setStatus(TaskStatus.PENDING)
        task.error = None
        task.errorException = None
        task.taskState.reset()
        # Re-enqueue directly — task stays in tracker (already tracked)
        self._pendingTasks.append(task)
        self.queueStatusChanged.emit()
        self._processQueue()

    # ── Persistence ───────────────────────────────────────────────────────────

    def loadState(self) -> None:
        """Load pending tasks from storage and re-enqueue them.
        Only tasks serialized as persistent are restored.
        """
        try:
            tasksData = self._storage.load('pendingTasks', [])
            if not tasksData:
                logger.debug('No pending tasks to restore')
                return
            restored = 0
            for taskData in tasksData:
                try:
                    className = taskData.get('className')
                    if not className:
                        logger.warning('Pending task missing className, skipping')
                        continue
                    moduleName, clsName = className.rsplit('.', 1)
                    module = __import__(moduleName, fromlist=[clsName])
                    taskCls = getattr(module, clsName)
                    task = taskCls.deserialize(taskData)
                    if task:
                        self.addTask(task)
                        restored += 1
                except Exception as e:
                    logger.opt(exception=e).error(f'Failed to restore pending task: {e}')
            logger.info(f'Restored {restored}/{len(tasksData)} pending tasks from storage')
        except Exception as e:
            logger.opt(exception=e).error(f'Error loading TaskQueue state: {e}')

    def saveState(self) -> None:
        """Save pending tasks to storage. Only persistent tasks are saved."""
        try:
            # Serialize persistent pending tasks
            persistentTasks = [task.serialize() for task in self._pendingTasks if task.isPersistent]
            self._storage.save('pendingTasks', persistentTasks)
            logger.debug(f'Saved {len(persistentTasks)} persistent pending tasks')
        except Exception as e:
            logger.error(f'Error saving TaskQueue state: {e}')

    # ── Status queries ────────────────────────────────────────────────────────

    def getPendingCount(self) -> int:
        """Get number of pending tasks."""
        return len(self._pendingTasks)

    def getRunningCount(self) -> int:
        """Get number of running tasks."""
        return len(self._runningTasks)

    def getQueueStatus(self) -> dict:
        """Get current queue status.
        Returns:
            Dictionary with queue statistics
        """
        return {
            'pending': len(self._pendingTasks),
            'running': len(self._runningTasks),
            'maxConcurrent': self._maxConcurrentTasks,
            'threadPoolActive': self._threadPool.activeThreadCount(),
        }

    def _cleanupUniqueKey(self, key: str) -> None:
        """Remove key from active index if no pending or running tasks exist."""
        if key in self._activeUniqueKeys:
            stats = self._activeUniqueKeys[key]
            if stats['pending'] <= 0 and stats['running'] <= 0:
                del self._activeUniqueKeys[key]
