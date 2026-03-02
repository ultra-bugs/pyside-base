"""
TaskManager Signals

Standalone QObject holding all signals emitted by TaskManagerService.
"""

from PySide6 import QtCore


class TaskManagerSignals(QtCore.QObject):
    """Signal emitter for TaskManagerService events.

    Signals:
        taskAdded(uuid: str)
        taskRemoved(uuid: str)
        taskFinished(uuid: str, task: object, result: object, error: object|None)
        taskStatusUpdated(uuid: str, status: TaskStatus)
        taskProgressUpdated(uuid: str, progress: int)
        failedTaskLogged(taskInfo: dict)
        systemReady()
    """

    taskAdded = QtCore.Signal(str)
    taskRemoved = QtCore.Signal(str)
    taskFinished = QtCore.Signal(str, object, object, object)
    taskStatusUpdated = QtCore.Signal(str, object)
    taskProgressUpdated = QtCore.Signal(str, int)
    failedTaskLogged = QtCore.Signal(dict)
    systemReady = QtCore.Signal()
