"""
TaskManagerService

Main orchestrator for the TaskSystem. Coordinates TaskQueue, TaskTracker, and TaskScheduler.
Provides the primary API for other parts of the application to interact with tasks.
"""

from typing import Any, Dict, List, Optional
from PySide6 import QtCore
from .ChainRetryBehavior import ChainRetryBehavior
from .Exceptions import TaskNotFoundException
from .TaskQueue import TaskQueue
from .TaskScheduler import TaskScheduler
from .TaskStatus import TaskStatus
from .TaskTracker import TaskTracker
from .storage.JsonStorage import JsonStorage
from ..Config import Config
from ..Logging import logger
from ..Observer import Publisher, Subscriber

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
        taskAdded: Emitted when a task is added
        taskRemoved: Emitted when a task is removed
        taskStatusUpdated: Emitted when task status changes
        taskProgressUpdated: Emitted when task progress changes
        failedTaskLogged: Emitted when a failed task is logged
        systemReady: Emitted when system initialization is complete
    """

    taskAdded = QtCore.Signal(str)
    taskRemoved = QtCore.Signal(str)
    taskStatusUpdated = QtCore.Signal(str, object)
    taskProgressUpdated = QtCore.Signal(str, int)
    failedTaskLogged = QtCore.Signal(dict)
    systemReady = QtCore.Signal()

    def __init__(self, publisher: Publisher, config: Config):
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
        self._storage = JsonStorage()
        logger.info('Initializing TaskManagerService subsystems...')
        self._taskTracker = TaskTracker(self._storage)
        self._taskQueue = TaskQueue(self._taskTracker, self._storage, config)
        self._taskScheduler = TaskScheduler(self._taskQueue, self._storage)
        self._connectSignals()
        self.loadState()
        self._applyConfig()
        logger.info('TaskManagerService initialized successfully')
        self.systemReady.emit()

    def _connectSignals(self) -> None:
        """
        Connect signals from subsystems to aggregate signals.
        """
        self._taskTracker.taskAdded.connect(self._onTaskAdded)
        self._taskTracker.taskRemoved.connect(self._onTaskRemoved)
        self._taskTracker.taskUpdated.connect(self._onTaskUpdated)
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
        """
        Pause a task (if supported).
        Args:
            uuid: Task UUID
        Note: Currently not fully implemented - requires task-specific pause logic
        """
        try:
            task = self._taskTracker._activeTasks.get(uuid)
            if task:
                logger.info(f'Pausing task: {uuid}')
                task.setStatus(TaskStatus.PAUSED)
            else:
                raise TaskNotFoundException(uuid)
        except TaskNotFoundException:
            logger.error(f'Cannot pause task {uuid}: not found')
            raise

    def resumeTask(self, uuid: str) -> None:
        """
        Resume a paused task.
        Args:
            uuid: Task UUID
        Note: Currently not fully implemented - requires task-specific resume logic
        """
        try:
            task = self._taskTracker._activeTasks.get(uuid)
            if task:
                logger.info(f'Resuming task: {uuid}')
                task.setStatus(TaskStatus.PENDING)
                self._taskQueue.addTask(task)
            else:
                raise TaskNotFoundException(uuid)
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

    def setMaxConcurrentTasks(self, count: int) -> None:
        """
        Set maximum number of concurrent tasks.
        Args:
            count: Maximum concurrent tasks (must be > 0)
        """
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
        """Handle taskUpdated signal from TaskTracker."""
        try:
            task = self._taskTracker._activeTasks.get(uuid)
            if task:
                self.taskStatusUpdated.emit(uuid, task.status)
                self.taskProgressUpdated.emit(uuid, task.progress)
        except Exception as e:
            logger.warning(f'Error handling task update for {uuid}: {e}')

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
