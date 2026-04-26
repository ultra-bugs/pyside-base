"""
core.taskSystem.signals

Centralized signal classes for all TaskSystem components.
Each component owns a standalone QObject for signal emission,
decoupling signal lifetime from component inheritance hierarchies.
"""

from .TaskManagerSignals import TaskManagerSignals
from .TaskQueueSignals import TaskQueueSignals
from .TaskSchedulerSignals import TaskSchedulerSignals
from .TaskSignals import TaskSignals
from .TaskTrackerSignals import TaskTrackerSignals

__all__ = ['TaskSignals', 'TaskTrackerSignals', 'TaskQueueSignals', 'TaskSchedulerSignals', 'TaskManagerSignals']
