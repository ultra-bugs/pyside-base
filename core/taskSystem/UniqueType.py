from enum import Enum, auto


class UniqueType(Enum):
    """
    Defines the uniqueness constraints for a Task.
    """
    NONE = auto()
    """No uniqueness constraint."""

    JOB = auto()
    """
    Unique Job: Only one instance of this task (by unique key) can exist in the system at any time.
    If a task is Pending or Running, a new one cannot be added.
    """

    UNTIL_PROCESSING = auto()
    """
    Unique Until Processing: Only one instance of this task can exist in the Pending queue.
    Once it starts Running, another one can be added to the Pending queue.
    """
