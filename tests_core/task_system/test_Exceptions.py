"""
Tests for TaskSystem exceptions.
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

#
from core.taskSystem.Exceptions import (InvalidTaskStateException,
                                        TaskCancellationException,
                                        TaskNotFoundException,
                                        TaskSystemException)


def test_task_system_exception():
    """Test base TaskSystemException."""
    exc = TaskSystemException('Test error')
    assert str(exc) == 'Test error'
    assert isinstance(exc, Exception)


def test_task_not_found_exception():
    """Test TaskNotFoundException."""
    uuid = 'test-uuid-123'
    exc = TaskNotFoundException(uuid)
    assert uuid in str(exc)
    assert exc.uuid == uuid
    assert isinstance(exc, TaskSystemException)


def test_task_not_found_exception_custom_message():
    """Test TaskNotFoundException with custom message."""
    uuid = 'test-uuid-123'
    message = 'Custom error message'
    exc = TaskNotFoundException(uuid, message)
    assert str(exc) == message
    assert exc.uuid == uuid


def test_invalid_task_state_exception():
    """Test InvalidTaskStateException."""
    uuid = 'test-uuid-123'
    state = 'RUNNING'
    operation = 'cancel'
    exc = InvalidTaskStateException(uuid, state, operation)
    assert uuid in str(exc)
    assert state in str(exc)
    assert operation in str(exc)
    assert exc.uuid == uuid
    assert exc.currentState == state
    assert exc.operation == operation
    assert isinstance(exc, TaskSystemException)


def test_task_cancellation_exception():
    """Test TaskCancellationException."""
    uuid = 'test-uuid-123'
    exc = TaskCancellationException(uuid)
    assert uuid in str(exc)
    assert exc.uuid == uuid
    assert isinstance(exc, TaskSystemException)
