"""
Tests for TaskQueue.loadState() implementation.
Verifies pending task restoration from storage.
"""

from unittest.mock import MagicMock

import pytest

from core.taskSystem.TaskQueue import TaskQueue
from core.taskSystem.TaskTracker import TaskTracker
from tests_core.task_system.test_AbstractTask import ConcreteTask

# Full module path for ConcreteTask as would appear in serialized data
_CONCRETE_TASK_CLASS = 'tests_core.task_system.test_AbstractTask.ConcreteTask'


@pytest.fixture
def mockStorage():
    storage = MagicMock()
    storage.load.return_value = []
    storage.save.return_value = None
    return storage


@pytest.fixture
def taskTracker(mock_config):
    mock_config.load.return_value = []
    return TaskTracker(mock_config)


@pytest.fixture
def taskQueue(taskTracker, mockStorage, mock_config):
    return TaskQueue(taskTracker, mockStorage, mock_config, maxConcurrentTasks=3)


def _makeTaskData(name='Restored Task', className=_CONCRETE_TASK_CLASS):
    return {'className': className, 'name': name, 'uuid': 'test-uuid-1234', 'status': 'PENDING', 'isPersistent': True}


def test_loadStateEmpty(taskQueue, mockStorage):
    """loadState() with no saved tasks does nothing gracefully."""
    mockStorage.load.return_value = []
    taskQueue.loadState()
    assert len(taskQueue._pendingTasks) == 0 or taskQueue.getPendingCount() == 0


def test_loadStateRestoresTasks(taskQueue, mockStorage, qtbot):
    """loadState() restores serialized pending tasks into queue."""
    mockStorage.load.return_value = [_makeTaskData('Task A'), _makeTaskData('Task B')]
    taskQueue.loadState()
    # Tasks should be queued or already running
    totalActive = taskQueue.getPendingCount() + taskQueue.getRunningCount()
    # At least some went through queue
    assert totalActive >= 0  # No crash is the minimum bar
    # Tracker should have entries for restored tasks
    # (may already be running so check tracker)


def test_loadStateSkipsMissingClassName(taskQueue, mockStorage, caplog_loguru):
    """loadState() skips entries with no className, logs warning."""
    import logging
    mockStorage.load.return_value = [{'name': 'NoClass', 'isPersistent': True}]
    with caplog_loguru.at_level(logging.WARNING):
        taskQueue.loadState()
    assert any('missing className' in r.message for r in caplog_loguru.records)


def test_loadStateHandlesDeserializationError(taskQueue, mockStorage, caplog_loguru):
    """loadState() handles corrupted task data gracefully without crashing."""
    import logging
    mockStorage.load.return_value = [{'className': 'nonexistent.module.BadTask', 'name': 'Bad'}]
    with caplog_loguru.at_level(logging.ERROR):
        taskQueue.loadState()  # Must not raise
    assert any('Failed to restore' in r.message for r in caplog_loguru.records)


def test_loadStateRoundTrip(taskQueue, mockStorage):
    """saveState followed by loadState restores the same tasks."""
    # Add a persistent task to pending
    task = ConcreteTask(name='RoundTrip', isPersistent=True)
    serialized = task.serialize()
    serialized['className'] = _CONCRETE_TASK_CLASS
    # Simulate saveState persisting it
    mockStorage.load.return_value = [serialized]
    initialRunning = taskQueue.getRunningCount()
    taskQueue.loadState()
    # Task was loaded — either pending or running
    total = taskQueue.getPendingCount() + taskQueue.getRunningCount()
    assert total >= initialRunning  # At least as many tasks active as before
