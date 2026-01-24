"""
TaskChain

Meta-task that executes multiple tasks sequentially with shared context.
Supports retry behaviors, progress tracking, and persistence.
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
import importlib
import time
from typing import Any, Dict, List, Optional
from core.Logging import logger
from core.Observer import Publisher, Subscriber
from core.taskSystem.AbstractTask import AbstractTask, TaskFailedException
from core.taskSystem.ChainContext import ChainContext
from core.taskSystem.ChainRetryBehavior import ChainRetryBehavior
from core.taskSystem.TaskStatus import TaskStatus

logger = logger.bind(component='TaskSystem')


class TaskChain(AbstractTask, Subscriber):
    """
    Meta-task that executes multiple tasks sequentially with shared context.

    TaskChain is a special type of AbstractTask that contains and executes
    other tasks in sequence. It provides:
    - Shared context (ChainContext) between child tasks
    - Configurable retry behaviors for failed tasks
    - Progress tracking (default or external via events)
    - Full serialization support for persistence

    Attributes:
        _tasks: List of child tasks to execute
        _currentTaskIndex: Index of currently executing task
        _chainContext: Shared context for child tasks
        _taskStates: Dictionary tracking state of each child task
        retryBehaviorMap: Map of task class names to retry behaviors
        _chainRetryAttempts: Number of times the entire chain has been retried
        _progress_updated_externally: Flag indicating external progress update
    """

    def __init__(self, name: str, tasks: List[AbstractTask], description: str = '', retryBehaviorMap: Optional[Dict[str, ChainRetryBehavior]] = None, **kwargs):
        """
        Initialize TaskChain.
        Args:
            name: Display name for the chain
            tasks: List of AbstractTask instances to execute sequentially
            description: Detailed description of the chain
            retryBehaviorMap: Optional map of task class names to retry behaviors
            **kwargs: Additional arguments passed to AbstractTask.__init__
        """
        AbstractTask.__init__(self, name=name, description=description, **kwargs)
        Subscriber.__init__(self, events=['ChainProgressUpdateRequest'])
        for task in tasks:
            task.chainUuid = self.uuid
            task.addTag('_ChainedChild')
            task.addTag(f'Parent_{self.uuid}')
        self._tasks = tasks
        self._currentTaskIndex = 0
        self._chainContext = ChainContext(self.uuid)
        self._taskStates = {task.uuid: {'status': TaskStatus.PENDING, 'result': None, 'error': ''} for task in tasks}
        self.retryBehaviorMap = retryBehaviorMap if retryBehaviorMap is not None else {}
        self._chainRetryAttempts = 0
        self._progress_updated_externally = False
        logger.info(f'TaskChain created: {self.uuid} - {self.name} with {len(tasks)} tasks')

    def onChainProgressUpdateRequest(self, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Handle ChainProgressUpdateRequest event.
        Updates chain progress if the event is for this chain.
        Args:
            data: Event data containing chainUuid and progress
        """
        if data and data.get('chainUuid') == self.uuid:
            progress = data.get('progress')
            if isinstance(progress, int) and 0 <= progress <= 100:
                self.setProgress(progress)
                self._progress_updated_externally = True
                logger.debug(f'TaskChain {self.uuid} progress updated externally to {progress}%')

    def _updateDefaultProgress(self) -> None:
        """
        Calculate and update default progress based on current task index.
        Progress is calculated as: ((currentTaskIndex + 1) / totalTasks) * 100
        """
        if len(self._tasks) == 0:
            self.setProgress(100)
            return
        progress = int((self._currentTaskIndex + 1) / len(self._tasks) * 100)
        self.setProgress(progress)

    def cancel(self) -> None:
        """
        Cancel the chain and all child tasks.
        Overrides AbstractTask.cancel() to ensure proper cleanup.
        """
        logger.info(f'Cancelling TaskChain {self.uuid} - {self.name}')
        publisher = Publisher()
        publisher.unsubscribe(self, event='ChainProgressUpdateRequest')
        self._performCancellationCleanup()
        super().cancel()

    def handle(self) -> None:
        """
        Execute the chain by running tasks sequentially.
        This is the main execution loop that:
        1. Iterates through tasks in order
        2. Injects chain context into each task
        3. Executes each task with retry logic
        4. Handles retry behaviors based on configuration
        5. Updates progress
        """
        logger.info(f'TaskChain {self.uuid} - {self.name} starting execution')
        if not self._tasks:
            self._updateDefaultProgress()
            return
        while self._currentTaskIndex < len(self._tasks):
            if self.isStopped():
                self.setStatus(TaskStatus.CANCELLED)
                logger.info(f'TaskChain {self.uuid} was cancelled')
                return
            self._progress_updated_externally = False
            task = self._tasks[self._currentTaskIndex]
            task.setChainContext(self._chainContext)
            logger.info(f'TaskChain {self.uuid} executing task {self._currentTaskIndex + 1}/{len(self._tasks)}: {task.name}')
            isTaskSuccess = self._executeSubTaskWithRetry(task)
            if self.isStopped() or task.status == TaskStatus.CANCELLED:
                if self.status != TaskStatus.FAILED:
                    self.setStatus(TaskStatus.CANCELLED)
                logger.info(f'TaskChain {self.uuid} was cancelled or sub-task was cancelled')
                return
            if not isTaskSuccess:
                taskClassName = task.__class__.__name__
                chainBehavior = self.retryBehaviorMap.get(taskClassName, ChainRetryBehavior.STOP_CHAIN)
                logger.warning(f"TaskChain {self.uuid}: Task '{task.name}' failed. Chain behavior: {chainBehavior.name}")
                if chainBehavior == ChainRetryBehavior.STOP_CHAIN:
                    self.fail(f"Sub-task '{task.name}' failed and chain is configured to stop.")
                    return
                elif chainBehavior == ChainRetryBehavior.SKIP_TASK:
                    logger.warning(f"TaskChain {self.uuid}: Skipping failed task '{task.name}' as per configuration.")
                    self._currentTaskIndex += 1
                    continue
                elif chainBehavior == ChainRetryBehavior.RETRY_CHAIN:
                    if self._chainRetryAttempts < self.maxRetries:
                        self._chainRetryAttempts += 1
                        logger.info(f'TaskChain {self.uuid}: Retrying entire chain (Attempt {self._chainRetryAttempts}/{self.maxRetries}).')
                        self._currentTaskIndex = 0
                        for taskUuid in self._taskStates:
                            self._taskStates[taskUuid]['status'] = TaskStatus.PENDING
                            self._taskStates[taskUuid]['error'] = ''
                        continue
                    else:
                        self.fail(f'Chain failed after {self.maxRetries} retry attempts.')
                        return
            if not self._progress_updated_externally:
                self._updateDefaultProgress()
            self._currentTaskIndex += 1
        self.result = self._chainContext.serialize()['data']
        logger.info(f'TaskChain {self.uuid} - {self.name} completed successfully')
        publisher = Publisher()
        publisher.unsubscribe(self, event='ChainProgressUpdateRequest')

    def _executeSubTaskWithRetry(self, task: AbstractTask) -> bool:
        """
        Execute a child task with retry logic.
        This method handles task-level retries based on task.maxRetries.
        Returns True if task succeeds, False if it fails after all retries.
        Args:
            task: Child task to execute
        Returns:
            True if task succeeded, False if failed after all retries
        """
        attempts = 0
        maxAttempts = task.maxRetries + 1
        while attempts < maxAttempts:
            if self.isStopped():
                return False
            if attempts > 0:
                self.setStatus(TaskStatus.RETRYING)
                logger.info(f"TaskChain {self.uuid}: Retrying sub-task '{task.name}' (Attempt {attempts}/{task.maxRetries}).")
                time.sleep(task.retryDelaySeconds)
                self.setStatus(TaskStatus.RUNNING)
            if self.isStopped():
                return False
            task.setStatus(TaskStatus.PENDING)
            try:
                task.run()
                if task.status == TaskStatus.COMPLETED:
                    self._taskStates[task.uuid]['status'] = task.status
                    self._taskStates[task.uuid]['result'] = task.result
                    logger.info(f"TaskChain {self.uuid}: Sub-task '{task.name}' completed successfully")
                    return True
                if task.status == TaskStatus.CANCELLED or self.isStopped():
                    return False
            except TaskFailedException as e:
                logger.error(f"TaskChain {self.uuid}: Sub-task '{task.name}' crashed with exception.", exc_info=True)
            except Exception as e:
                task.fail(str(e))
                logger.error(f"TaskChain {self.uuid}: Sub-task '{task.name}' crashed with exception.", exc_info=True)
            attempts += 1
            self._taskStates[task.uuid]['status'] = task.status
            self._taskStates[task.uuid]['error'] = task.error or 'Unknown error'
        logger.warning(f"TaskChain {self.uuid}: Sub-task '{task.name}' failed after {maxAttempts} attempts")
        return False

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize TaskChain to dictionary for persistence.
        Returns:
            Dictionary containing chain state including child tasks
        """
        baseData = super().serialize()
        serializedTasks = []
        for task in self._tasks:
            serializedTasks.append(task.serialize())
        retryMapSerialized = {}
        for key, value in self.retryBehaviorMap.items():
            retryMapSerialized[key] = value.name
        baseData.update(
            {
                'tasks': serializedTasks,
                'currentTaskIndex': self._currentTaskIndex,
                'chainContext': self._chainContext.serialize(),
                'taskStates': {
                    uuid: {'status': state['status'].name if isinstance(state['status'], TaskStatus) else state['status'], 'result': state['result'], 'error': state['error']}
                    for uuid, state in self._taskStates.items()
                },
                'retryBehaviorMap': retryMapSerialized,
                'chainRetryAttempts': self._chainRetryAttempts,
            }
        )
        return baseData

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'TaskChain':
        """
        Deserialize TaskChain from dictionary.
        Args:
            data: Dictionary containing serialized chain data
        Returns:
            Reconstructed TaskChain instance
        """
        name = data['name']
        description = data.get('description', '')
        tasks = []
        for taskData in data.get('tasks', []):
            className = taskData.get('className')
            if not className:
                logger.warning('Cannot deserialize task: missing className')
                continue
            try:
                modulePath, className = className.rsplit('.', 1)
                module = importlib.import_module(modulePath)
                taskClass = getattr(module, className)
                task = taskClass.deserialize(taskData)
                tasks.append(task)
            except Exception as e:
                logger.error(f'Failed to deserialize task {className}: {e}', exc_info=True)
                continue
        retryMap = {}
        for key, valueName in data.get('retryBehaviorMap', {}).items():
            try:
                retryMap[key] = ChainRetryBehavior[valueName]
            except KeyError:
                logger.warning(f'Unknown retry behavior: {valueName}, using default')
                retryMap[key] = ChainRetryBehavior.STOP_CHAIN
        chain = cls(
            name=name,
            tasks=tasks,
            description=description,
            retryBehaviorMap=retryMap,
            isPersistent=data.get('isPersistent', False),
            maxRetries=data.get('maxRetries', 0),
            retryDelaySeconds=data.get('retryDelaySeconds', 5),
            failSilently=data.get('failSilently', False),
        )
        chain._currentTaskIndex = data.get('currentTaskIndex', 0)
        chain._chainContext = ChainContext.deserialize(data.get('chainContext', {}))
        chain._chainRetryAttempts = data.get('chainRetryAttempts', 0)
        taskStatesData = data.get('taskStates', {})
        for uuid, stateData in taskStatesData.items():
            chain._taskStates[uuid] = {
                'status': TaskStatus[stateData['status']] if isinstance(stateData['status'], str) else stateData['status'],
                'result': stateData.get('result'),
                'error': stateData.get('error', ''),
            }
        chain.status = TaskStatus[data.get('status', 'PENDING')]
        chain.progress = data.get('progress', 0)
        chain.result = data.get('result')
        chain.error = data.get('error')
        logger.info(f'TaskChain deserialized: {chain.uuid} - {chain.name} (resuming at task {chain._currentTaskIndex + 1})')
        return chain

    def _performCancellationCleanup(self) -> None:
        """
        Perform cleanup when chain is cancelled.
        Cancels all child tasks and unsubscribes from events.
        """
        logger.debug(f'TaskChain {self.uuid}: Performing cancellation cleanup')
        for task in self._tasks:
            try:
                task.cancel()
            except Exception as e:
                logger.warning(f'Error cancelling child task {task.uuid}: {e}')
        publisher = Publisher()
        try:
            publisher.unsubscribe(self, event='ChainProgressUpdateRequest')
        except Exception as e:
            logger.warning(f'Error unsubscribing from events: {e}')
