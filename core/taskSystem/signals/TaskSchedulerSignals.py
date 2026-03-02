"""
TaskScheduler Signals

Standalone QObject holding all signals emitted by TaskScheduler.
"""

from PySide6 import QtCore


class TaskSchedulerSignals(QtCore.QObject):
    """Signal emitter for TaskScheduler events.

    Signals:
        jobScheduled(jobId: str, taskUuid: str)
        jobUnscheduled(jobId: str)
        jobExecuted(jobId: str, taskUuid: str)
    """

    jobScheduled = QtCore.Signal(str, str)
    jobUnscheduled = QtCore.Signal(str)
    jobExecuted = QtCore.Signal(str, str)
