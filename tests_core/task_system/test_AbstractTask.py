"""
Tests for AbstractTask base class.
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

import pytest

#
from core.taskSystem.AbstractTask import AbstractTask
from core.taskSystem.TaskStatus import TaskStatus


class ConcreteTask(AbstractTask):
    """Concrete implementation for testing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handle_called = False
        self.cleanup_called = False

    def handle(self):
        """Test implementation."""
        self.handle_called = True
        self.setProgress(50)
        if not self.isStopped():
            self.setProgress(100)

    def _performCancellationCleanup(self):
        """Test implementation."""
        self.cleanup_called = True

    @classmethod
    def deserialize(cls, data):
        """Test implementation."""
        return cls(name=data['name'])


def test_task_initialization():
    """Test task initialization."""
    task = ConcreteTask(name='Test Task', description='Test Description', maxRetries=3, retryDelaySeconds=10)
    assert task.name == 'Test Task'
    assert task.description == 'Test Description'
    assert task.maxRetries == 3
    assert task.retryDelaySeconds == 10
    assert task.status == TaskStatus.PENDING
    assert task.progress == 0
    assert task.uuid is not None
    assert task.createdAt is not None


def test_set_status(qtbot):
    """Test setStatus method and signal emission."""
    task = ConcreteTask(name='Test')
    with qtbot.waitSignal(task.statusChanged, timeout=1000):
        task.setStatus(TaskStatus.RUNNING)
    assert task.status == TaskStatus.RUNNING


def test_set_progress(qtbot):
    """Test setProgress method and signal emission."""
    task = ConcreteTask(name='Test')
    with qtbot.waitSignal(task.progressUpdated, timeout=1000):
        task.setProgress(50)
    assert task.progress == 50


def test_progress_clamping():
    """Test that progress is clamped to 0-100."""
    task = ConcreteTask(name='Test')
    task.setProgress(-10)
    assert task.progress == 0
    task.setProgress(150)
    assert task.progress == 100


def test_is_stopped():
    """Test isStopped method."""
    task = ConcreteTask(name='Test')
    assert not task.isStopped()
    task.cancel()
    assert task.isStopped()


def test_cancel(qtbot):
    """Test cancel method."""
    task = ConcreteTask(name='Test')
    task.cancel()
    assert task.isStopped()
    assert task.cleanup_called
    assert task.status == TaskStatus.CANCELLED


def test_fail():
    """Test fail method."""
    from core.taskSystem.AbstractTask import TaskFailedException
    task = ConcreteTask(name='Test')
    reason = 'Test failure reason'
    with pytest.raises(TaskFailedException):
        task.fail(reason)
    assert task.status == TaskStatus.FAILED
    assert task.error == reason


def test_serialize():
    """Test task serialization."""
    task = ConcreteTask(name='Test Task', description='Test Description')
    task.deviceSerial = 'DEVICE123'
    data = task.serialize()
    assert data['name'] == 'Test Task'
    assert data['description'] == 'Test Description'
    assert data['deviceSerial'] == 'DEVICE123'
    assert data['status'] == TaskStatus.PENDING.name
    assert 'uuid' in data
    assert 'createdAt' in data


def test_run_success(qtbot):
    """Test successful task execution."""
    task = ConcreteTask(name='Test')
    with qtbot.waitSignal(task.taskFinished, timeout=2000):
        task.run()
    assert task.handle_called
    assert task.status == TaskStatus.COMPLETED
    assert task.startedAt is not None
    assert task.finishedAt is not None


def test_run_with_cancellation(qtbot):
    """Test task execution with cancellation."""
    task = ConcreteTask(name='Test')
    # Cancel before running
    task.cancel()
    with qtbot.waitSignal(task.taskFinished, timeout=2000):
        task.run()
    assert task.status == TaskStatus.CANCELLED
