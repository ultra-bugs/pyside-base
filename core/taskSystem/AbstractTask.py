"""
AbstractTask

Base class for all tasks in the TaskSystem.
Provides common functionality, lifecycle management, and Qt signals integration.
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

import abc
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from PySide6 import QtCore
from PySide6.QtCore import QMutex, QWaitCondition

from ..Logging import logger
from .Exceptions import TaskCancellationException
from .TaskStatus import TaskStatus
from .UniqueType import UniqueType

if TYPE_CHECKING:
    from .ChainContext import ChainContext
logger = logger.bind(component='TaskSystem')


class QObjectABCMeta(type(QtCore.QObject), abc.ABCMeta):
    """
    Metaclass that combines QObject's metaclass with ABCMeta.

    This is necessary because both QObject and ABC have their own metaclasses,
    and Python doesn't allow multiple metaclasses without explicit resolution.
    """

    pass


class TaskFailedException(Exception):
    pass


class AbstractTask(QtCore.QObject, QtCore.QRunnable, abc.ABC, metaclass=QObjectABCMeta):
    """
    Abstract base class for all tasks in the TaskSystem.

    Inherits from:
        - QtCore.QObject: For Qt signals support
        - QtCore.QRunnable: For QThreadPool execution
        - abc.ABC: For abstract method enforcement

    Attributes:
        uuid (str): Unique identifier for the task
        name (str): Display name of the task
        description (str): Detailed description
        status (TaskStatus): Current task status
        progress (int): Progress percentage (0-100)
        result (Any): Task execution result
        error (str): Error message if task failed
        createdAt (datetime): Task creation timestamp
        startedAt (datetime): Task start timestamp
        finishedAt (datetime): Task completion timestamp
        isPersistent (bool): Whether task should be persisted across sessions
        maxRetries (int): Maximum number of retry attempts
        retryDelaySeconds (int): Delay between retry attempts
        currentRetryAttempts (int): Current number of retry attempts
        failSilently (bool): Whether to suppress error propagation
    """

    statusChanged = QtCore.Signal(str, object)
    progressUpdated = QtCore.Signal(str, int)
    taskFinished = QtCore.Signal(str, object, object, object)  # uuid, self instance, result, error|None
    # error object: {message: str - reason, exception: Exception instance}

    def __init__(
        self,
        name: str,
        description: str = '',
        isPersistent: bool = False,
        maxRetries: int = 0,
        retryDelaySeconds: int = 5,
        failSilently: bool = True,
        chainUuid: Optional[str] = None,
        tags: Optional[set[str]] = None,
        uniqueType: UniqueType = UniqueType.NONE,
    ):
        """
        Initialize the abstract task.
        Args:
            name: Display name for the task
            description: Detailed description of the task
            isPersistent: Whether to persist task across sessions
            maxRetries: Maximum number of retry attempts (0 = no retry)
            retryDelaySeconds: Seconds to wait before retry
            failSilently: If True, errors won't be propagated
            chainUuid: Optional UUID of the parent TaskChain
            tags: Set of tags for categorizing the task
            uniqueType: Uniqueness constraint for the task
        """
        QtCore.QObject.__init__(self)
        # this is temporary fix for PyCharm debugger (pydevd)
        import os
        if not os.getenv('PYTHONUNBUFFERED', False):
            QtCore.QRunnable.__init__(self)
        self.uuid = uuid.uuid4().hex
        self.name = name
        self.description = description
        self.chainUuid = chainUuid
        self._chainContext: Optional['ChainContext'] = None
        self.status = TaskStatus.PENDING
        self.progress = 0
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.errorException: Optional[Exception] = None
        self.createdAt = datetime.now()
        self.startedAt: Optional[datetime] = None
        self.finishedAt: Optional[datetime] = None
        self.isPersistent = isPersistent
        self.maxRetries = maxRetries
        # Ensure >= 1
        self.retryDelaySeconds = max(int(retryDelaySeconds), 1)
        self.currentRetryAttempts = 0
        self.failSilently = failSilently
        self._stopMutex = QMutex()
        self._stopped = False
        # Pause gate — Qt-native primitives (QMutex + QWaitCondition)
        self._pauseMutex = QMutex()
        self._pauseCondition = QWaitCondition()
        self._isPaused = False
        self._pauseCheckIntervalMs = 500
        # Tags Management
        self.tags = tags if tags is not None else set()
        # Handle deserialization: tags might come as list from JSON
        if isinstance(self.tags, list):
            self.tags = set(self.tags)
        self.tags.add(self.__class__.__name__)
        # Unique Task Features
        self.uniqueType = uniqueType
        logger.debug(f'{self.__class__.__name__} Task created: {self.uuid} - {self.name}' + (f' (chain: {chainUuid})' if chainUuid else ''))

    serializables: Optional[Any] = None

    def uniqueVia(self) -> str:
        """
        Define the unique key for the task.
        Default is the class name.
        Override this to provide a dynamic unique key (e.g., based on target file).
        """
        return self.__class__.__name__

    def setStatus(self, newStatus: TaskStatus) -> None:
        """
        Update task status and emit statusChanged signal.
        Args:
            newStatus: The new status to set
        """
        oldStatus = self.status
        self.status = newStatus
        logger.debug(f'Task {self.uuid} status changed: {oldStatus.name} -> {newStatus.name}')
        self.statusChanged.emit(self.uuid, newStatus)

    def setProgress(self, value: int) -> None:
        """
        Update task progress and emit progressUpdated signal.
        Args:
            value: Progress percentage (0-100)
        """
        self.progress = max(0, min(100, value))
        logger.debug(f'Task {self.uuid} progress: {self.progress}%')
        self.progressUpdated.emit(self.uuid, self.progress)

    def addTag(self, tag: str) -> None:
        """Add a tag to the task."""
        self.tags.add(tag)

    def removeTag(self, tag: str) -> None:
        """Remove a tag from the task."""
        self.tags.discard(tag)

    def hasTag(self, tag: str) -> bool:
        """Check if task has a specific tag."""
        return tag in self.tags

    def pause(self) -> None:
        """
        Request task pause. Thread will block at next checkPaused() call.
        Only effective if handle() calls checkPaused() periodically.
        """
        self._pauseMutex.lock()
        self._isPaused = True
        self._pauseMutex.unlock()
        self.setStatus(TaskStatus.PAUSED)
        logger.info(f'Task {self.uuid} paused')

    def resume(self) -> None:
        """Resume a paused task. Wakes the blocked thread."""
        self._pauseMutex.lock()
        self._isPaused = False
        self._pauseCondition.wakeAll()
        self._pauseMutex.unlock()
        self.setStatus(TaskStatus.RUNNING)
        logger.info(f'Task {self.uuid} resumed')

    def checkPaused(self) -> None:
        """
        Call periodically inside handle() to respect pause requests.
        Blocks the executing thread until resume() or cancel() is called.
        No-op if task is not paused.
        """
        self._pauseMutex.lock()
        while self._isPaused and not self.isStopped():
            self._pauseCondition.wait(self._pauseMutex, self._pauseCheckIntervalMs)
        self._pauseMutex.unlock()

    def setChainContext(self, context: 'ChainContext') -> None:
        """
        Set the chain context for this task.
        This method is called by TaskChain to inject the shared context.
        Should not be called directly from outside TaskChain.
        Args:
            context: ChainContext instance to inject
        """
        self._chainContext = context
        logger.debug(f'Task {self.uuid} received chain context from chain {context._chainUuid}')

    def isStopped(self) -> bool:
        """
        Check if task has been requested to stop.
        Returns:
            True if stop was requested, False otherwise
        """
        self._stopMutex.lock()
        stopped = self._stopped
        self._stopMutex.unlock()
        return stopped

    def cancel(self) -> None:
        """
        Request task cancellation.
        Sets the stop event and wakes any paused thread so it can exit.
        If task is PENDING or PAUSED, immediately transitions to CANCELLED.
        """
        logger.info(f'Cancelling task {self.uuid} - {self.name}')
        self._stopMutex.lock()
        self._stopped = True
        self._stopMutex.unlock()
        # Wake paused thread so it can detect stop and exit cleanly
        self._pauseMutex.lock()
        self._isPaused = False
        self._pauseCondition.wakeAll()
        self._pauseMutex.unlock()
        if self.status in (TaskStatus.PENDING, TaskStatus.PAUSED):
            self.setStatus(TaskStatus.CANCELLED)
        try:
            self._performCancellationCleanup()
        except Exception as e:
            logger.opt(exception=e).error(f'Error during cancellation cleanup for task {self.uuid}: {e}')

    def fail(self, reason: str = 'Task failed by itself', exception: Optional[Exception] = None) -> None:
        """
        Mark task as failed with a reason.
        Args:
            :param reason: Description of why the task failed
            :param exception: Exception
        """
        logger.warning(f'Task {self.uuid} failed: {reason}')
        self.error = reason
        self.setStatus(TaskStatus.FAILED)
        if not exception:
            exception = TaskFailedException(reason)
        self.errorException = exception
        raise self.errorException

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize task to dictionary for persistence.
        Behavior:
        - Always includes core runtime fields (uuid, className, status, timestamps, etc.).
        - Task-specific fields are dynamic:
          - If subclass defines `serializables` (iterable of attribute names), only those are included.
          - Otherwise, all public instance attributes not starting with '_' and not core fields are included.
        """
        data: Dict[str, Any] = {
            'uuid': self.uuid,
            'className': f'{self.__class__.__module__}.{self.__class__.__name__}',
            'name': self.name,
            'description': self.description,
            'status': self.status.name if isinstance(self.status, TaskStatus) else str(self.status),
            'progress': self.progress,
            'result': self.result,
            'error': self.error,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'startedAt': self.startedAt.isoformat() if self.startedAt else None,
            'finishedAt': self.finishedAt.isoformat() if self.finishedAt else None,
            'isPersistent': self.isPersistent,
            'maxRetries': self.maxRetries,
            'retryDelaySeconds': self.retryDelaySeconds,
            'currentRetryAttempts': self.currentRetryAttempts,
            'failSilently': self.failSilently,
            'chainUuid': self.chainUuid,
            'tags': list(self.tags),
        }
        coreKeys = set(data.keys())
        def _to_serializable(v: Any) -> Any:
            if isinstance(v, Exception):
                return v.__class__.__name__ + ': ' + str(v)
            if isinstance(v, datetime):
                return v.isoformat()
            if isinstance(v, TaskStatus):
                return v.name
            if isinstance(v, UniqueType):
                return v.name
            if callable(v):
                raise TypeError('Cannot serialize callable')
            return v
        extras: Dict[str, Any] = {}
        keys = getattr(self, 'serializables', None)
        if keys:
            for k in keys:
                if isinstance(k, str) and hasattr(self, k) and (not k.startswith('_')):
                    try:
                        extras[k] = _to_serializable(getattr(self, k))
                    except Exception:
                        pass
        else:
            for k, v in self.__dict__.items():
                if k.startswith('_') or k in coreKeys:
                    continue
                try:
                    extras[k] = _to_serializable(v)
                except Exception:
                    continue
        data.update(extras)
        return data

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'AbstractTask':
        """
        Deserialize task from dictionary.
        Must be implemented by subclasses to reconstruct task-specific data.
        Args:
            data: Dictionary containing serialized task state
        Returns:
            Reconstructed task instance
        """
        pass

    @abc.abstractmethod
    def handle(self) -> None:
        """
        Execute the main task logic.
        Must be implemented by subclasses.
        Should periodically check isStopped() and return early if True.
        Should update progress using setProgress().
        Can call fail() to mark task as failed.
        """
        pass

    @abc.abstractmethod
    def _performCancellationCleanup(self) -> None:
        """
        Perform task-specific cleanup when cancelled.
        Must be implemented by subclasses.
        Should clean up resources (close files, kill processes, etc.)
        """
        pass

    def run(self) -> None:
        """
        QRunnable entry point - executes the task.
        This method wraps handle() with proper lifecycle management:
        - Sets startedAt timestamp
        - Updates status to RUNNING
        - Calls handle()
        - Handles completion, cancellation, and errors
        - Emits taskFinished signal
        """
        self.startedAt = datetime.now()
        logger.info(f'Task {self.uuid} - {self.name} starting execution')
        try:
            self.setStatus(TaskStatus.RUNNING)
            self.handle()
            if self.isStopped():
                self.setStatus(TaskStatus.CANCELLED)
                self.error = 'CANCELLED'
                logger.info(f'Task {self.uuid} was cancelled during execution')
            elif self.status == TaskStatus.FAILED:
                logger.info(f'Task {self.uuid} failed silently: {self.error}', exc_info=True)
            else:
                self.setStatus(TaskStatus.COMPLETED)
                logger.info(f'Task {self.uuid} completed successfully')
        except TaskCancellationException as e:
            self.error = 'CANCELLED'
            self.setStatus(TaskStatus.CANCELLED)
            logger.info(f'Task {self.uuid} was cancelled: {e}', exc_info=True)
        except Exception as e:
            self.error = f'{e.__class__.__name__}: {e}'
            self.setStatus(TaskStatus.FAILED)
            logger.opt(exception=e).error(f'Task {self.uuid} failed with error: {e}', exc_info=True)
            self.errorException = e
            if not self.failSilently:
                raise
        finally:
            self.finishedAt = datetime.now()
            duration = (self.finishedAt - self.startedAt).total_seconds()
            logger.info(f'Task {self.uuid} finished in {duration:.2f}s with status {self.status.name}')
            err: Optional[Dict[str, str | Exception]] = {'message': self.error, 'exception': self.errorException} if self.error else None
            self.taskFinished.emit(self.uuid, self, self.result, err)
