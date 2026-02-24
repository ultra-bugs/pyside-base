"""
TaskQueue

Manages FIFO queue of tasks with concurrency limits and retry logic.
Submits tasks to QThreadPool and handles task completion/retry.
"""

#                  M""""""""`M            dP
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

#
from collections import deque
from typing import Any, Dict, Optional

from PySide6 import QtCore

from ..Config import Config
from ..Logging import logger
from .Exceptions import TaskNotFoundException
from .storage.BaseStorage import BaseStorage
from .TaskStatus import TaskStatus
from .TaskTracker import TaskTracker
from .UniqueType import UniqueType

# Initialize logger for TaskSystem
logger = logger.bind(component='TaskSystem')


class TaskQueue(QtCore.QObject):
    """
    FIFO queue manager for tasks with concurrency control.

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

    # Qt Signals
    queueStatusChanged = QtCore.Signal()  # Queue status changed
    taskQueued = QtCore.Signal(str)  # uuid
    taskDequeued = QtCore.Signal(str)  # uuid

    def __init__(self, taskTracker: TaskTracker, storage: BaseStorage, config: Config, maxConcurrentTasks: int = 3):
        """
        Initialize TaskQueue.
        Args:
            taskTracker: TaskTracker instance for monitoring
            storage: Storage backend for persistence
            config: Configuration instance
            maxConcurrentTasks: Maximum number of concurrent tasks (default: 3)
        """
        super().__init__()
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
        # Load persisted state
        self.loadState()
        logger.info(f'TaskQueue initialized with max concurrent tasks: {maxConcurrentTasks}')

    def addTask(self, task: Any) -> None:
        """
        Add a task to the queue.
        Args:
            task: AbstractTask instance to queue
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
        # Try to process queue
        self._processQueue()

    def setMaxConcurrentTasks(self, count: int) -> None:
        """
        Set maximum number of concurrent tasks.
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
        # Try to process more tasks if limit increased
        self._processQueue()

    def _processQueue(self) -> None:
        """
        Process pending tasks if there are available slots.
        Internal method called when:
        - A new task is added
        - A running task finishes
        - Max concurrent tasks is changed
        """
        # Check if we can start more tasks
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
            # Connect to task finished signal
            task.taskFinished.connect(self._handleTaskCompletion)
            # Submit to thread pool
            self._threadPool.start(task)
            logger.info(f'Task started: {task.uuid} - {task.name} (Running: {len(self._runningTasks)})')
            self.taskDequeued.emit(task.uuid)
            self.queueStatusChanged.emit()

    def _handleTaskCompletion(self, uuid: str, task, result: Any, error: Optional[Dict[str, str | Exception]]) -> None:
        """
        Handle task completion, including retry logic.
        Args:
            uuid: Task UUID
            finalStatus: Final task status
            result: Task result (if successful)
            error: Error message (if failed)
        """
        # Get task from running tasks
        finalStatus: TaskStatus = task.status
        if uuid not in self._runningTasks:
            logger.critical(f'Task {uuid} not found in running tasks')
            logger.critical('--------------- NEED RECHECK')
            return
        task = self._runningTasks.pop(uuid)
        # Disconnect to prevent duplicate connections on retry
        try:
            task.taskFinished.disconnect(self._handleTaskCompletion)
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
            # Schedule retry via timer
            QtCore.QTimer.singleShot(task.retryDelaySeconds * 1000, lambda: self._retryTask(task))
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

    def _retryTask(self, task: Any) -> None:
        """
        Re-enqueue a failed task for retry.
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
        task._stopMutex.lock()
        task._stopped = False
        task._stopMutex.unlock()
        # Re-enqueue directly — task stays in tracker (already tracked)
        self._pendingTasks.append(task)
        self.queueStatusChanged.emit()
        self._processQueue()

    def loadState(self) -> None:
        """
        Load pending tasks from storage and re-enqueue them.
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
        """
        Save pending tasks to storage.
        Only persistent tasks are saved.
        """
        try:
            # Serialize persistent pending tasks
            persistentTasks = [task.serialize() for task in self._pendingTasks if task.isPersistent]
            self._storage.save('pendingTasks', persistentTasks)
            logger.debug(f'Saved {len(persistentTasks)} persistent pending tasks')
        except Exception as e:
            logger.error(f'Error saving TaskQueue state: {e}')

    def getPendingCount(self) -> int:
        """Get number of pending tasks."""
        return len(self._pendingTasks)

    def getRunningCount(self) -> int:
        """Get number of running tasks."""
        return len(self._runningTasks)

    def getQueueStatus(self) -> dict:
        """
        Get current queue status.
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
        """
        Remove key from active index if no pending or running tasks exist.
        """
        if key in self._activeUniqueKeys:
            stats = self._activeUniqueKeys[key]
            if stats['pending'] <= 0 and stats['running'] <= 0:
                del self._activeUniqueKeys[key]
