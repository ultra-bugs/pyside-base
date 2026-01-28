"""
TaskTracker.py

Tracks active tasks and maintains history of failed tasks with persistence.
Monitors task status, progress, and logs failures for analysis.
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

import threading
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from PySide6 import QtCore

from ..Logging import logger
from .Exceptions import TaskNotFoundException
from .storage.BaseStorage import BaseStorage
from .TaskStatus import TaskStatus

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
        # Reverse Indexing: Tag -> Set[UUID]
        self._tagIndex: Dict[str, set[str]] = {}
        self._lock = threading.RLock()
        self.loadState()
        logger.info('TaskTracker initialized')

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def addTask(self, task: Any) -> None:
        """Add a task (or chain) to tracking and connect signals."""
        with self._lock:
            uuid = task.uuid
            if uuid in self._activeTasks:
                logger.warning(f'Task {uuid} already tracked')
                return
            isChain = self._isTaskChain(task)
            self._activeTasks[uuid] = task
            # Connect signals for the main task
            self._connectTaskSignals(task)
            # Index tags
            self._indexTask(task)
            # Handle Chain Children
            if isChain:
                for child in task._tasks:
                    childUuid = child.uuid
                    self._chainChildTasks[childUuid] = {'isChainChild': True, 'chainUuid': uuid, 'parentChainName': task.name}
                    # Track child if not already tracked
                    if childUuid not in self._activeTasks:
                        self._activeTasks[childUuid] = child
                        self._connectTaskSignals(child)
                        self._indexTask(child)
            logger.info(f'Task added: {uuid} ({task.name})')
            self.taskAdded.emit(uuid)

    def removeTask(self, uuid: str) -> None:
        """Remove task from tracking and disconnect signals."""
        with self._lock:
            if uuid not in self._activeTasks:
                raise TaskNotFoundException(uuid, f'Cannot remove {uuid}: not tracked')
            # Retrieve and remove the main task
            task = self._activeTasks.pop(uuid)
            self._unindexTask(task)
            # Cleanup if it is a Chain
            if self._isTaskChain(task):
                for child in task._tasks:
                    c_uuid = child.uuid
                    self._chainChildTasks.pop(c_uuid, None)
                    if c_uuid in self._activeTasks:
                        child_task = self._activeTasks.pop(c_uuid)
                        self._disconnectTaskSignals(child_task)
                        self._unindexTask(child_task)
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

    def getUuidsByTag(self, tag: str) -> set[str]:
        """Get all UUIDs associated with a tag."""
        with self._lock:
            return self._tagIndex.get(tag, set()).copy()

    # -------------------------------------------------------------------------
    # Internal Logic & Persistence
    # -------------------------------------------------------------------------

    def _indexTask(self, task: Any) -> None:
        """Helper to index tags for a task."""
        if hasattr(task, 'tags'):
            for tag in task.tags:
                if tag not in self._tagIndex:
                    self._tagIndex[tag] = set()
                self._tagIndex[tag].add(task.uuid)

    def _unindexTask(self, task: Any) -> None:
        """Helper to remove tags for a task."""
        if hasattr(task, 'tags'):
            for tag in task.tags:
                if tag in self._tagIndex:
                    self._tagIndex[tag].discard(task.uuid)
                    if not self._tagIndex[tag]:
                        del self._tagIndex[tag]

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
        except (RuntimeError, TypeError, RuntimeWarning) as e:
            logger.opt(exception=e).warning(str(e))
            # Signal was not connected or object already deleted
            pass
        except Exception as e:
            logger.opt(exception=e).debug(f'Unexpected disconnect error: {e}')

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
            val_failed = self._storage.load('failedTaskHistory', [])
            self._failedTaskHistory = val_failed if isinstance(val_failed, list) else []
            val_completed = self._storage.load('completedTaskHistory', [])
            self._completedTaskHistory = val_completed if isinstance(val_completed, list) else []
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
