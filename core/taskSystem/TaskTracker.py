"""
TaskTracker.py

Tracks active tasks and maintains history of failed tasks with persistence.
Monitors task status, progress, and logs failures for analysis.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from PySide6 import QtCore
from .Exceptions import TaskNotFoundException
from .TaskStatus import TaskStatus
from .storage.BaseStorage import BaseStorage
from ..Logging import logger

if TYPE_CHECKING:
    pass

logger = logger.bind(component='TaskSystem')


class TaskTracker(QtCore.QObject):
    """
    Tracks active tasks, manages signals, and persists history.
    """

    taskAdded = QtCore.Signal(str)
    taskRemoved = QtCore.Signal(str)
    taskUpdated = QtCore.Signal(str)
    failedTaskLogged = QtCore.Signal(dict)

    def __init__(self, storage: BaseStorage):
        super().__init__()
        self._storage = storage
        self._activeTasks: Dict[str, Any] = {}
        self._failedTaskHistory: List[Dict[str, Any]] = []
        self._completedTaskHistory: List[Dict[str, Any]] = []
        # Stores metadata for tasks that are part of a chain
        self._chainChildTasks: Dict[str, Dict[str, Any]] = {}
        self.loadState()
        logger.info('TaskTracker initialized')

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def addTask(self, task: Any) -> None:
        """Add a task (or chain) to tracking and connect signals."""
        uuid = task.uuid
        if uuid in self._activeTasks:
            logger.warning(f'Task {uuid} already tracked')
            return
        isChain = self._isTaskChain(task)
        self._activeTasks[uuid] = task
        # Connect signals for the main task
        self._connectTaskSignals(task)
        # Handle Chain Children
        if isChain:
            for child in task._tasks:
                childUuid = child.uuid
                self._chainChildTasks[childUuid] = {'isChainChild': True, 'chainUuid': uuid, 'parentChainName': task.name}
                # Track child if not already tracked
                if childUuid not in self._activeTasks:
                    self._activeTasks[childUuid] = child
                    self._connectTaskSignals(child)
        logger.info(f'Task added: {uuid} ({task.name})')
        self.taskAdded.emit(uuid)

    def removeTask(self, uuid: str) -> None:
        """Remove task from tracking and disconnect signals."""
        if uuid not in self._activeTasks:
            raise TaskNotFoundException(uuid, f'Cannot remove {uuid}: not tracked')
        # Retrieve and remove the main task
        task = self._activeTasks.pop(uuid)
        # Cleanup if it is a Chain
        if self._isTaskChain(task):
            for child in task._tasks:
                c_uuid = child.uuid
                self._chainChildTasks.pop(c_uuid, None)
                if c_uuid in self._activeTasks:
                    child_task = self._activeTasks.pop(c_uuid)
                    self._disconnectTaskSignals(child_task)
        # Cleanup metadata if it was a child
        self._chainChildTasks.pop(uuid, None)
        # Disconnect main task
        self._disconnectTaskSignals(task)
        logger.info(f'Task removed: {uuid} ({task.name})')
        self.taskRemoved.emit(uuid)

    def getTaskInfo(self, uuid: str) -> Dict[str, Any]:
        """Get serialized info for a task."""
        if uuid not in self._activeTasks:
            raise TaskNotFoundException(uuid)
        task = self._activeTasks[uuid]
        info = task.serialize()
        if self._isTaskChain(task):
            info['subTasks'] = [t.serialize() for t in task._tasks]
            if hasattr(task, '_chainContext'):
                info['chainContext'] = task._chainContext.serialize()
        elif uuid in self._chainChildTasks:
            meta = self._chainChildTasks[uuid]
            info.update({'isChainChild': True, 'chainUuid': meta['chainUuid'], 'parentChainName': meta['parentChainName']})
        return info

    def getAllTasksInfo(self) -> List[Dict[str, Any]]:
        return [t.serialize() for t in self._activeTasks.values()]

    def getCompletedTaskHistory(self) -> List[Dict[str, Any]]:
        return self._completedTaskHistory.copy()

    def getFailedTaskHistory(self) -> List[Dict[str, Any]]:
        return self._failedTaskHistory.copy()

    def logFailedTask(self, task: Any) -> None:
        data = task.serialize()
        data['failedAt'] = datetime.now().isoformat()
        self._addToHistory(self._failedTaskHistory, data)
        self.saveState()
        logger.warning(f'Failed task: {task.uuid} - {task.error}')
        self.failedTaskLogged.emit(data)

    # -------------------------------------------------------------------------
    # Internal Logic & Persistence
    # -------------------------------------------------------------------------

    def _connectTaskSignals(self, task: Any):
        """Connect task signals to internal handlers."""
        task.statusChanged.connect(self._onTaskStatusChanged)
        task.progressUpdated.connect(self._onTaskProgressUpdated)
        task.taskFinished.connect(self._onTaskFinished)

    def _disconnectTaskSignals(self, task: Any):
        """Safely disconnect signals, suppressing errors if not connected."""
        self._safeDisconnect(task.statusChanged, self._onTaskStatusChanged)
        self._safeDisconnect(task.progressUpdated, self._onTaskProgressUpdated)
        self._safeDisconnect(task.taskFinished, self._onTaskFinished)

    def _safeDisconnect(self, signal, slot):
        """Disconnect signal from slot, ignoring errors if not connected."""
        try:
            signal.disconnect(slot)
        except (RuntimeError, TypeError, RuntimeWarning):
            # Signal was not connected or object already deleted
            pass
        except Exception as e:
            logger.debug(f'Unexpected disconnect error: {e}')

    def _onTaskStatusChanged(self, uuid: str, status: TaskStatus):
        # logger.debug(f'Task {uuid} status: {status.name}') # Reduce spam
        self.taskUpdated.emit(uuid)

    def _onTaskProgressUpdated(self, uuid: str, progress: int):
        self.taskUpdated.emit(uuid)

    def _onTaskFinished(self, uuid: str, status: TaskStatus, res: Any, err: Optional[str]):
        logger.info(f'Task finished: {uuid} [{status.name}]')
        self.taskUpdated.emit(uuid)
        if status == TaskStatus.COMPLETED:
            task = self._activeTasks.get(uuid)
            if task:
                data = task.serialize()
                data['completedAt'] = datetime.now().isoformat()
                self._addToHistory(self._completedTaskHistory, data)
                self.saveState()

    def _addToHistory(self, history_list: list, item: dict, limit: int = 1000):
        history_list.append(item)
        if len(history_list) > limit:
            history_list[:] = history_list[-limit:]

    def _isTaskChain(self, task: Any) -> bool:
        return task.__class__.__name__ == 'TaskChain'

    def loadState(self):
        try:
            self._failedTaskHistory = self._storage.load('failedTaskHistory', []) or []
            self._completedTaskHistory = self._storage.load('completedTaskHistory', []) or []
        except Exception as e:
            logger.error(f'Load state failed: {e}')
            self._failedTaskHistory = []
            self._completedTaskHistory = []

    def saveState(self):
        try:
            self._storage.save('failedTaskHistory', self._failedTaskHistory)
            self._storage.save('completedTaskHistory', self._completedTaskHistory)
        except Exception as e:
            logger.error(f'Save state failed: {e}')
