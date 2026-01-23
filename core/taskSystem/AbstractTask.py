"""
AbstractTask

Base class for all tasks in the TaskSystem.
Provides common functionality, lifecycle management, and Qt signals integration.
"""

import abc
import threading
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING
from PySide6 import QtCore
from .Exceptions import TaskCancellationException
from .TaskStatus import TaskStatus
from ..Logging import logger

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
    taskFinished = QtCore.Signal(str, object, object, str)

    def __init__(
        self,
        name: str,
        description: str = '',
        isPersistent: bool = False,
        maxRetries: int = 0,
        retryDelaySeconds: int = 5,
        failSilently: bool = False,
        chainUuid: Optional[str] = None,
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
        """
        QtCore.QObject.__init__(self)
        # QtCore.QRunnable.__init__(self)
        self.uuid = uuid.uuid4().hex
        self.name = name
        self.description = description
        self.chainUuid = chainUuid
        self._chainContext: Optional['ChainContext'] = None
        self.status = TaskStatus.PENDING
        self.progress = 0
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.createdAt = datetime.now()
        self.startedAt: Optional[datetime] = None
        self.finishedAt: Optional[datetime] = None
        self.isPersistent = isPersistent
        self.maxRetries = maxRetries
        # Ensure >= 1
        self.retryDelaySeconds = max(int(retryDelaySeconds), 1)
        self.currentRetryAttempts = 0
        self.failSilently = failSilently
        self._stopEvent = threading.Event()
        logger.debug(f'Task created: {self.uuid} - {self.name}' + (f' (chain: {chainUuid})' if chainUuid else ''))

    serializables: Optional[Any] = None

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
        return self._stopEvent.is_set()

    def cancel(self) -> None:
        """
        Request task cancellation.
        Sets the stop event and performs cancellation cleanup.
        If task is PENDING or PAUSED, immediately transitions to CANCELLED.
        """
        logger.info(f'Cancelling task {self.uuid} - {self.name}')
        self._stopEvent.set()
        if self.status in (TaskStatus.PENDING, TaskStatus.PAUSED):
            self.setStatus(TaskStatus.CANCELLED)
        try:
            self._performCancellationCleanup()
        except Exception as e:
            logger.error(f'Error during cancellation cleanup for task {self.uuid}: {e}')

    def fail(self, reason: str = 'Task failed by itself') -> None:
        """
        Mark task as failed with a reason.
        Args:
            reason: Description of why the task failed
        """
        logger.warning(f'Task {self.uuid} failed: {reason}')
        self.error = reason
        self.setStatus(TaskStatus.FAILED)
        raise TaskFailedException(reason)

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
        }
        coreKeys = set(data.keys())
        def _to_serializable(v: Any) -> Any:
            if isinstance(v, datetime):
                return v.isoformat()
            if isinstance(v, TaskStatus):
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
                logger.info(f'Task {self.uuid} was cancelled during execution')
            else:
                self.setStatus(TaskStatus.COMPLETED)
                logger.info(f'Task {self.uuid} completed successfully')
        except TaskCancellationException as e:
            self.error = str(e)
            self.setStatus(TaskStatus.CANCELLED)
            logger.info(f'Task {self.uuid} was cancelled: {e}')
        except Exception as e:
            self.error = str(e)
            self.setStatus(TaskStatus.FAILED)
            logger.error(f'Task {self.uuid} failed with error: {e}', exc_info=True)
            if not self.failSilently:
                raise
        finally:
            self.finishedAt = datetime.now()
            duration = (self.finishedAt - self.startedAt).total_seconds()
            logger.info(f'Task {self.uuid} finished in {duration:.2f}s with status {self.status.name}')
            self.taskFinished.emit(self.uuid, self.status, self.result, self.error)
