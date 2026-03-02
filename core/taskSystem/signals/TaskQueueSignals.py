"""
TaskQueue Signals

Standalone QObject holding all signals emitted by TaskQueue.
"""

from PySide6 import QtCore


class TaskQueueSignals(QtCore.QObject):
    """Signal emitter for TaskQueue events.

    Signals:
        queueStatusChanged()
        taskQueued(uuid: str)
        taskDequeued(uuid: str)
    """

    queueStatusChanged = QtCore.Signal()
    taskQueued = QtCore.Signal(str)
    taskDequeued = QtCore.Signal(str)
