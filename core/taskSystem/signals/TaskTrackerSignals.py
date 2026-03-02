"""
TaskTracker Signals

Standalone QObject holding all signals emitted by TaskTracker.
"""

from PySide6 import QtCore


class TaskTrackerSignals(QtCore.QObject):
    """Signal emitter for TaskTracker events.

    Signals:
        taskAdded(uuid: str)
        taskRemoved(uuid: str)
        taskStatusUpdated(uuid: str, status: TaskStatus)
        taskFinished(uuid: str, task: object, result: object, error: object|None)
        failedTaskLogged(taskInfo: dict)
    """

    taskAdded = QtCore.Signal(str)
    taskRemoved = QtCore.Signal(str)
    taskStatusUpdated = QtCore.Signal(str, object)
    taskFinished = QtCore.Signal(str, object, object, object)
    failedTaskLogged = QtCore.Signal(dict)
