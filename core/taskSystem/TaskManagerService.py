"""
TaskManagerService

Main orchestrator for the TaskSystem. Coordinates TaskQueue, TaskTracker, and TaskScheduler.
Provides the primary API for other parts of the application to interact with tasks.
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
from typing import Any, Dict, List, Optional

from PySide6 import QtCore

from . import AbstractTask
from ..Config import Config
from ..Logging import logger
from ..Observer import Publisher, Subscriber
from .ChainRetryBehavior import ChainRetryBehavior
from .Exceptions import TaskNotFoundException
from .storage import BaseStorage
from .storage.JsonStorage import JsonStorage
from .TaskQueue import TaskQueue
from .TaskScheduler import TaskScheduler
from .TaskStatus import TaskStatus
from .TaskTracker import TaskTracker

logger = logger.bind(component='TaskSystem')


class TaskManagerService(QtCore.QObject):
    """
    Central orchestrator for the TaskSystem.

    Responsibilities:
    - Coordinate TaskQueue, TaskTracker, and TaskScheduler
    - Provide unified API for task management
    - Aggregate and relay signals/events
    - Handle Observer pattern integration via Subscriber
    - Manage system lifecycle and persistence

    Signals:
        taskAdded: Emitted when a task is added. Args: (uuid: str)
        taskRemoved: Emitted when a task is removed. Args: (uuid: str)
        taskFinished: Emitted when a task finished (completed/failed/cancelled). Args: (uuid: str, task: AbstractTask)
        taskStatusUpdated: Emitted when task status changes. Args: (uuid: str, status: TaskStatus)
        taskProgressUpdated: Emitted when task progress changes. Args: (uuid: str, progress: int)
        failedTaskLogged: Emitted when a failed task is logged. Args: (taskInfo: dict)
        systemReady: Emitted when system initialization is complete
    """

    taskAdded = QtCore.Signal(str)
    taskRemoved = QtCore.Signal(str)
    taskFinished = QtCore.Signal(str, object, object, object)  # uuid, task instance, result, error
    taskStatusUpdated = QtCore.Signal(str, object)  # uuid, status (TaskStatus)
    taskProgressUpdated = QtCore.Signal(str, int)
    failedTaskLogged = QtCore.Signal(dict)
    systemReady = QtCore.Signal()

    def __init__(self, publisher: Publisher, config: Config, storage: Optional[BaseStorage] = None):
        """
        Initialize TaskManagerService.
        Args:
            publisher: Publisher instance for Observer pattern
            config: Configuration instance
        """
        Subscriber.__init__(self, events=['TaskRequest'], isGlobalSubscriber=True)
        QtCore.QObject.__init__(self)
        self._publisher = publisher
        self._config = config
        self._storage = storage or JsonStorage()
        logger.info('Initializing TaskManagerService subsystems...')
        self._taskTracker = TaskTracker(self._storage)
        self._taskQueue = TaskQueue(self._taskTracker, self._storage, config)
        self._taskScheduler = TaskScheduler(self._taskQueue, self._storage)
        self._connectSubsystemSignals()
        self.loadState()
        self._applyConfig()
        logger.info('TaskManagerService initialized successfully')
        self.systemReady.emit()

    def _connectSubsystemSignals(self) -> None:
        """
        Connect signals from subsystems to aggregate signals.
        """
        self._taskTracker.taskAdded.connect(self._onTaskAdded)
        self._taskTracker.taskRemoved.connect(self._onTaskRemoved)
        self._taskTracker.taskStatusUpdated.connect(self._onTaskUpdated)
        self._taskTracker.taskFinished.connect(self._onTaskFinished)
        self._taskTracker.failedTaskLogged.connect(self._onFailedTaskLogged)
        self._taskQueue.queueStatusChanged.connect(self._onQueueStatusChanged)
        self._taskScheduler.jobScheduled.connect(self._onJobScheduled)
        self._taskScheduler.jobUnscheduled.connect(self._onJobUnscheduled)
        logger.debug('TaskManagerService signals connected')
    
    def _applyConfig(self) -> None:
        """Apply configuration settings to subsystems."""
        maxConcurrent = self._config.get('taskSystem.maxConcurrentTasks', 3)
        self.setMaxConcurrentTasks(maxConcurrent)
        pass

    def addTask(self, task: Any, scheduleInfo: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a task for execution.
        Args:
            task: AbstractTask instance
            scheduleInfo: Optional scheduling information
                - trigger: 'date', 'interval', or 'cron'
                - runDate: datetime for 'date' trigger
                - intervalSeconds: int for 'interval' trigger
                - Other cron-specific kwargs
        """
        if scheduleInfo:
            logger.info(f'Scheduling task: {task.uuid} - {task.name}')
            self._taskScheduler.addScheduledTask(task, **scheduleInfo)
        else:
            logger.info(f'Adding task to queue: {task.uuid} - {task.name}')
            self._taskQueue.addTask(task)

    def addChainTask(
        self,
        name: str,
        tasks: List[Any],
        description: str = '',
        scheduleInfo: Optional[Dict[str, Any]] = None,
        retryBehaviorMap: Optional[Dict[str, ChainRetryBehavior]] = None,
        **kwargs,
    ) -> Any:
        """
        Create and add a TaskChain for execution.
        This is a convenience method for creating TaskChain instances.
        The chain will execute tasks sequentially with shared context.
        Args:
            name: Display name for the chain
            tasks: List of AbstractTask instances to execute sequentially
            description: Detailed description of the chain
            scheduleInfo: Optional scheduling information (same as addTask)
            retryBehaviorMap: Optional map of task class names to retry behaviors
            **kwargs: Additional arguments passed to TaskChain (e.g., isPersistent, maxRetries)
        Returns:
            Created TaskChain instance
        Example:
            ```python
            from core.taskSystem.ChainRetryBehavior import ChainRetryBehavior
            task1 = MyTask1(name='Task 1')
            task2 = MyTask2(name='Task 2')
            retry_map = {'MyTask1': ChainRetryBehavior.SKIP_TASK, 'MyTask2': ChainRetryBehavior.STOP_CHAIN}
            chain = taskManager.addChainTask(name='My Workflow', tasks=[task1, task2], retryBehaviorMap=retry_map, isPersistent=True)
            ```
        """
        from .TaskChain import TaskChain
        chain = TaskChain(name=name, tasks=tasks, description=description, retryBehaviorMap=retryBehaviorMap, **kwargs)
        self.addTask(chain, scheduleInfo=scheduleInfo)
        logger.info(f'TaskChain created and added: {chain.uuid} - {chain.name}')
        return chain

    def stopTasksByTag(self, tag: str, includeChainedChildren: bool = False) -> None:
        """
        Stop all tasks with the specified tag.
        Args:
            tag: Tag to target
            includeChainedChildren: If True, also stop tasks marked as _ChainedChild
        """
        targetUuids = self._taskTracker.getUuidsByTag(tag)
        if not includeChainedChildren:
            chainedUuids = self._taskTracker.getUuidsByTag('_ChainedChild')
            targetUuids = targetUuids - chainedUuids
        logger.info(f"Bulk stopping tasks with tag '{tag}': {len(targetUuids)} tasks targeted.")
        for uuid in targetUuids:
            try:
                self.cancelTask(uuid)
            except Exception as e:
                logger.warning(f'Failed to stop task {uuid} during bulk operation: {e}')

    def pauseTasksByTag(self, tag: str, includeChainedChildren: bool = False) -> None:
        """
        Pause all tasks with the specified tag.
        Args:
            tag: Tag to target
            includeChainedChildren: If True, also pause tasks marked as _ChainedChild
        """
        targetUuids = self._taskTracker.getUuidsByTag(tag)
        if not includeChainedChildren:
            chainedUuids = self._taskTracker.getUuidsByTag('_ChainedChild')
            targetUuids = targetUuids - chainedUuids
        logger.info(f"Bulk pausing tasks with tag '{tag}': {len(targetUuids)} tasks targeted.")
        for uuid in targetUuids:
            try:
                self.pauseTask(uuid)
            except Exception as e:
                logger.warning(f'Failed to pause task {uuid} during bulk operation: {e}')

    def cancelTask(self, uuid: str) -> None:
        """
        Cancel a task.
        Args:
            uuid: Task UUID
        Raises:
            TaskNotFoundException: If task is not found
        """
        try:
            taskInfo = self._taskTracker.getTaskInfo(uuid)
            task = self._taskTracker._activeTasks.get(uuid)
            if task:
                logger.info(f'Cancelling task: {uuid}')
                task.cancel()
            else:
                raise TaskNotFoundException(uuid)
        except TaskNotFoundException:
            logger.error(f'Cannot cancel task {uuid}: not found')
            raise

    def pauseTask(self, uuid: str) -> None:
        '''
        Pause a running task.
        The task thread will block at its next checkPaused() call.
        Args:
            uuid: Task UUID
        Raises:
            TaskNotFoundException: If task is not found
        '''
        try:
            task = self._taskTracker._activeTasks.get(uuid)
            if not task:
                raise TaskNotFoundException(uuid)
            if task.status != TaskStatus.RUNNING:
                logger.warning(f'Cannot pause task {uuid}: not RUNNING (status={task.status.name})')
                return
            task.pause()
        except TaskNotFoundException:
            logger.error(f'Cannot pause task {uuid}: not found')
            raise

    def resumeTask(self, uuid: str) -> None:
        '''
        Resume a paused task.
        Args:
            uuid: Task UUID
        Raises:
            TaskNotFoundException: If task is not found
        '''
        try:
            task = self._taskTracker._activeTasks.get(uuid)
            if not task:
                raise TaskNotFoundException(uuid)
            if task.status != TaskStatus.PAUSED:
                logger.warning(f'Cannot resume task {uuid}: not PAUSED (status={task.status.name})')
                return
            task.resume()
        except TaskNotFoundException:
            logger.error(f'Cannot resume task {uuid}: not found')
            raise

    def getTaskStatus(self, uuid: str) -> TaskStatus:
        """
        Get current status of a task.
        Args:
            uuid: Task UUID
        Returns:
            Current TaskStatus
        Raises:
            TaskNotFoundException: If task is not found
        """
        taskInfo = self._taskTracker.getTaskInfo(uuid)
        return TaskStatus[taskInfo['status']]

    def getAllTasks(self) -> List[Dict[str, Any]]:
        """
        Get information about all active tasks.
        Returns:
            List of task information dictionaries
        """
        return self._taskTracker.getAllTasksInfo()

    def getFailedTasks(self) -> List[Dict[str, Any]]:
        """
        Get history of failed tasks.
        Returns:
            List of failed task information dictionaries
        """
        return self._taskTracker.getFailedTaskHistory()

    def getTasksByTag(self, tag: str) -> List[Any]:
        """
        Get all active task instances matching a tag.
        Args:
            tag: Tag to filter by (e.g. 'SinglePayTask', 'Device_abc123')
        Returns:
            List of task instances
        """
        return self._taskTracker.getTasksByTag(tag)

    def hasTasksWithTag(self, tag: str) -> bool:
        """
        Check if any active tasks exist with the given tag.
        Lightweight check without serialization overhead.
        """
        return self._taskTracker.hasTasksWithTag(tag)

    def setMaxConcurrentTasks(self, count: int) -> None:
        """
        Set maximum number of concurrent tasks.
        Args:
            count: Maximum concurrent tasks (must be > 0)
        """
        if count is None:
            return
        logger.info(f'Setting max concurrent tasks to: {count}')
        self._taskQueue.setMaxConcurrentTasks(count)

    def getQueueStatus(self) -> Dict[str, Any]:
        """
        Get current queue status.
        Returns:
            Dictionary with queue statistics
        """
        return self._taskQueue.getQueueStatus()

    def getScheduledJobs(self) -> List[Dict[str, Any]]:
        """
        Get list of scheduled jobs.
        Returns:
            List of scheduled job information
        """
        return self._taskScheduler.getScheduledJobs()

    def loadState(self) -> None:
        """
        Load persisted state from all subsystems.
        """
        logger.info('Loading TaskManagerService state...')
        try:
            self._taskQueue.loadState()
            self._taskTracker.loadState()
            logger.info('TaskManagerService state loaded successfully')
        except Exception as e:
            logger.error(f'Error loading TaskManagerService state: {e}')

    def saveState(self) -> None:
        """
        Save state to all subsystems.
        """
        logger.info('Saving TaskManagerService state...')
        try:
            self._taskQueue.saveState()
            self._taskTracker.saveState()
            logger.info('TaskManagerService state saved successfully')
        except Exception as e:
            logger.error(f'Error saving TaskManagerService state: {e}')

    def shutdown(self) -> None:
        """
        Shutdown the TaskManagerService gracefully.
        """
        logger.info('Shutting down TaskManagerService...')
        self.saveState()
        self._taskScheduler.shutdown(wait=True)
        logger.info('TaskManagerService shutdown complete')

    def onTaskRequest(self, task: Any, scheduleInfo: Optional[Dict[str, Any]] = None) -> None:
        """
        Handle TaskRequest event from Observer pattern.
        Args:
            task: AbstractTask instance
            scheduleInfo: Optional scheduling information
        """
        logger.info(f'Received TaskRequest event for task: {task.name}')
        self.addTask(task, scheduleInfo)

    def _onTaskAdded(self, uuid: str) -> None:
        """Handle taskAdded signal from TaskTracker."""
        logger.debug(f'Task added: {uuid}')
        self.taskAdded.emit(uuid)

    def _onTaskRemoved(self, uuid: str) -> None:
        """Handle taskRemoved signal from TaskTracker."""
        logger.debug(f'Task removed: {uuid}')
        self.taskRemoved.emit(uuid)

    def _onTaskUpdated(self, uuid: str) -> None:
        """Handle taskStatusUpdated signal from TaskTracker."""
        try:
            task = self._taskTracker._activeTasks.get(uuid)
            if task:
                self.taskStatusUpdated.emit(uuid, task.status)
                self.taskProgressUpdated.emit(uuid, task.progress)
        except Exception as e:
            logger.warning(f'Error handling task update for {uuid}: {e}')

    def _onTaskFinished(self, uuid: str, task: AbstractTask, res: Any, err: Optional[Dict[str, str|Exception]]) -> None:
        """Handle taskFinished signal from TaskTracker."""
        logger.debug(f'Task execution finished: {uuid}')
        self.taskFinished.emit(uuid, task, res, err)

    def _onFailedTaskLogged(self, taskInfo: Dict[str, Any]) -> None:
        """Handle failedTaskLogged signal from TaskTracker."""
        logger.debug(f'Failed task logged: {taskInfo.get("uuid")}')
        self.failedTaskLogged.emit(taskInfo)

    def _onQueueStatusChanged(self) -> None:
        """Handle queueStatusChanged signal from TaskQueue."""
        status = self._taskQueue.getQueueStatus()
        logger.debug(f'Queue status changed: {status}')

    def _onJobScheduled(self, jobId: str, taskUuid: str) -> None:
        """Handle jobScheduled signal from TaskScheduler."""
        logger.debug(f'Job scheduled: {jobId} for task {taskUuid}')

    def _onJobUnscheduled(self, jobId: str) -> None:
        """Handle jobUnscheduled signal from TaskScheduler."""
        logger.debug(f'Job unscheduled: {jobId}')
