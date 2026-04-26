"""
TaskState

Thread-safe task lifecycle state object. Injectable into services
so they can check whether the owning task has been cancelled or paused.

The TaskStatus *enum* is unchanged — TaskState wraps it and adds
cooperative lifecycle flags (stopped, paused) with QMutex protection.
"""

#                  M""""""`M            dP
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
from PySide6.QtCore import QMutex, QWaitCondition

from .Exceptions import TaskCancellationException
from .TaskStatus import TaskStatus


class TaskState:
    """Thread-safe task lifecycle state. Injectable into services.

    Holds the current TaskStatus enum value *and* the cooperative
    cancellation / pause flags.  Services that receive a TaskState
    can call ``isStopped()`` or ``isPaused()`` without any dependency
    on AbstractTask itself.

    Usage in a service::

        class MyService:
            def __init__(self, taskState: TaskState):
                self._taskState = taskState

            def longRunningOp(self):
                for item in items:
                    self._taskState.throwIfCancelled()
                    # ... do work ...
    """

    _TERMINAL = frozenset({TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED})

    def __init__(self, initial: TaskStatus = TaskStatus.PENDING):
        self._current: TaskStatus = initial
        self._stopped: bool = False
        self._paused: bool = False
        self._mutex = QMutex()
        self._pauseCondition = QWaitCondition()
        self._pauseCheckIntervalMs: int = 500

    # -- Read-only queries (thread-safe) ----------------------------------

    @property
    def current(self) -> TaskStatus:
        """Current TaskStatus enum value.
        Backward-compatible: ``task.status == TaskStatus.RUNNING`` still works
        when AbstractTask exposes ``status`` as a property returning this.
        """
        self._mutex.lock()
        val = self._current
        self._mutex.unlock()
        return val

    @property
    def name(self) -> str:
        """Shortcut for ``current.name``."""
        return self.current.name

    def isCancelled(self) -> bool:
        """True when cancel has been requested OR status is CANCELLED."""
        self._mutex.lock()
        val = self._stopped or self._current == TaskStatus.CANCELLED
        self._mutex.unlock()
        return val

    def isPaused(self) -> bool:
        self._mutex.lock()
        val = self._paused
        self._mutex.unlock()
        return val

    def isStopped(self) -> bool:
        """True if cancel was requested (may precede status transition)."""
        self._mutex.lock()
        val = self._stopped
        self._mutex.unlock()
        return val

    def isRunning(self) -> bool:
        return self.current == TaskStatus.RUNNING

    def isTerminal(self) -> bool:
        return self.current in self._TERMINAL

    # -- Lifecycle commands (thread-safe) ---------------------------------

    def requestCancel(self) -> None:
        """Signal cancellation. Wakes paused threads."""
        self._mutex.lock()
        self._stopped = True
        self._paused = False
        self._pauseCondition.wakeAll()
        self._mutex.unlock()

    def requestPause(self) -> None:
        self._mutex.lock()
        self._paused = True
        self._mutex.unlock()

    def requestResume(self) -> None:
        """Resume from paused state. Wakes blocked threads."""
        self._mutex.lock()
        self._paused = False
        self._pauseCondition.wakeAll()
        self._mutex.unlock()

    def waitIfPaused(self) -> None:
        """Block calling thread while paused. Wakes on resume or cancel."""
        self._mutex.lock()
        while self._paused and not self._stopped:
            self._pauseCondition.wait(self._mutex, self._pauseCheckIntervalMs)
        self._mutex.unlock()

    def transition(self, newStatus: TaskStatus) -> TaskStatus:
        """Thread-safe status transition. Returns the *old* status."""
        self._mutex.lock()
        old = self._current
        self._current = newStatus
        self._mutex.unlock()
        return old

    def reset(self) -> None:
        """Clear stopped/paused flags for retry."""
        self._mutex.lock()
        self._stopped = False
        self._paused = False
        self._mutex.unlock()

    # -- Convenience -------------------------------------------------------

    def throwIfCancelled(self) -> None:
        """Raise ``TaskCancellationException`` if cancel was requested."""
        if self.isStopped():
            raise TaskCancellationException('Operation cancelled by task lifecycle')
