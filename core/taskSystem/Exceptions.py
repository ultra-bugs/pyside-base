"""
TaskSystem Exceptions

Custom exception classes for the TaskSystem module.
All exceptions inherit from ..Exceptions.AppException.
"""

#              M""""""""`M            dP
#              Mmmmmm   .M            88
#              MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#              MMP  .MMMMM  88    88  88888"    88'  `88
#              M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#              M         M  `88888P'  dP   `YP  `88888P'
#              MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#              * * * * * * * * * * * * * * * * * * * * *
#              * -    - -   F.R.E.E.M.I.N.D   - -    - *
#              * -  Copyright © 2025 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *
from ..Exceptions import AppException
from ..Logging import logger

# Initialize logger for TaskSystem
logger = logger.bind(component='TaskSystem')


class TaskSystemException(AppException):
    """
    Base exception for all TaskSystem-related errors.
    """

    pass


class TaskNotFoundException(TaskSystemException):
    """
    Raised when a task with a given UUID is not found.

    Args:
        uuid: The UUID of the task that was not found
        message: Optional custom error message
    """

    def __init__(self, uuid: str, message: str = None):
        self.uuid = uuid
        if message is None:
            message = f"Task with UUID '{uuid}' not found"
        super().__init__(message)


class InvalidTaskStateException(TaskSystemException):
    """
    Raised when an operation is performed on a task in an invalid state.

    Args:
        uuid: The UUID of the task
        currentState: The current state of the task
        operation: The operation that was attempted
        message: Optional custom error message
    """

    def __init__(self, uuid: str, currentState: str, operation: str, message: str = None):
        self.uuid = uuid
        self.currentState = currentState
        self.operation = operation
        if message is None:
            message = f"Cannot perform '{operation}' on task '{uuid}' in state '{currentState}'"
        super().__init__(message)


class TaskCancellationException(TaskSystemException):
    """
    Raised when a task is cancelled during execution.

    This exception is used internally to signal task cancellation
    and should be caught by the task execution framework.

    Args:
        uuid: The UUID of the cancelled task
        message: Optional custom error message
    """

    def __init__(self, uuid: str, message: str = None):
        self.uuid = uuid
        if message is None:
            message = f"Task '{uuid}' was cancelled"
        super().__init__(message)
