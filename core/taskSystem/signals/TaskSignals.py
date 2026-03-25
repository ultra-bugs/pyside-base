"""
Task Signals

Standalone QObject holding all signals emitted by AbstractTask.
Extracted to decouple Qt signal machinery (QObject) from
thread-pool execution (QRunnable).
"""

from PySide6 import QtCore


class TaskSignals(QtCore.QObject):
    """Standalone signal emitter for task lifecycle events.

    Signals:
        statusChanged(uuid: str, newStatus: TaskStatus)
        progressUpdated(uuid: str, progress: int)
        taskFinished(uuid: str, taskInstance: object, result: object, error: object|None)
            error object: {message: str, exception: Exception}
    """

    statusChanged = QtCore.Signal(str, object)
    progressUpdated = QtCore.Signal(str, int, str)  # uuid, progress, label (default '')
    taskFinished = QtCore.Signal(str, object, object, object)
