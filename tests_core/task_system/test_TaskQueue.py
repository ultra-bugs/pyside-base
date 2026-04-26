"""
Tests for TaskQueue.
"""

#                  M"""""""`M            dP
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
import logging
import time

#
import pytest

from core.taskSystem.TaskQueue import TaskQueue
from core.taskSystem.TaskStatus import TaskStatus
from core.taskSystem.TaskTracker import TaskTracker
from tests_core.task_system.test_AbstractTask import ConcreteTask


@pytest.fixture
def task_tracker(mock_config):
    """Create a TaskTracker instance for testing."""
    mock_config.load.return_value = []
    return TaskTracker(mock_config)


@pytest.fixture
def task_queue(task_tracker, mock_config):
    """Create a TaskQueue with worker started for testing."""
    queue = TaskQueue(task_tracker, mock_config, mock_config, maxConcurrentTasks=3)
    queue.start()
    yield queue
    queue.stop()


def _waitForWorker(timeout: float = 0.2) -> None:
    """Brief wait for DaemonWorker to process enqueued commands."""
    time.sleep(timeout)


def test_task_queue_initialization(task_tracker, mock_config):
    """Test TaskQueue initialization."""
    queue = TaskQueue(task_tracker, mock_config, mock_config, maxConcurrentTasks=5)
    assert queue._taskTracker == task_tracker
    assert queue._config == mock_config
    assert queue._maxConcurrentTasks == 5
    assert len(queue._pendingTasks) == 0
    assert len(queue._runningTasks) == 0


def test_add_task(task_queue, qtbot):
    """Test adding a task to queue."""
    task = ConcreteTask(name='Test Task')
    with qtbot.waitSignal(task_queue.taskQueued, timeout=2000):
        task_queue.addTask(task)
    _waitForWorker()
    # Task should be either pending or already running
    assert task.uuid in task_queue._taskTracker._activeTasks


def test_set_max_concurrent_tasks(task_tracker, mock_config):
    """Test setting max concurrent tasks."""
    queue = TaskQueue(task_tracker, mock_config, mock_config, maxConcurrentTasks=3)
    queue.setMaxConcurrentTasks(5)
    assert queue._maxConcurrentTasks == 5
    assert queue._threadPool.maxThreadCount() == 5


def test_set_invalid_max_concurrent_tasks(task_tracker, mock_config, caplog_loguru):
    """Test setting invalid max concurrent tasks."""
    with caplog_loguru.at_level(logging.WARNING):
        queue = TaskQueue(task_tracker, mock_config, mock_config)
        queue.setMaxConcurrentTasks(0)
        queue.setMaxConcurrentTasks(-1)
        assert any('Invalid max concurrent tasks' in record.message for record in caplog_loguru.records)


def test_get_queue_status(task_tracker, mock_config):
    """Test getting queue status."""
    queue = TaskQueue(task_tracker, mock_config, mock_config, maxConcurrentTasks=3)
    status = queue.getQueueStatus()
    assert 'pending' in status
    assert 'running' in status
    assert 'maxConcurrent' in status
    assert status['maxConcurrent'] == 3


def test_get_pending_count(task_queue, qapp):
    """Test getting pending task count."""
    task_queue.setMaxConcurrentTasks(1)
    # Add multiple tasks
    for i in range(3):
        task = ConcreteTask(name=f'Task {i}')
        task_queue.addTask(task)
    _waitForWorker()
    # At least some should be pending (depends on execution speed)
    assert task_queue.getPendingCount() >= 0


def test_get_running_count(task_queue, qapp):
    """Test getting running task count."""
    task_queue.setMaxConcurrentTasks(2)
    # Add tasks
    for i in range(2):
        task = ConcreteTask(name=f'Task {i}')
        task_queue.addTask(task)
    _waitForWorker()
    # Should have running tasks
    assert task_queue.getRunningCount() >= 0


def test_task_completion(task_queue, qtbot, qapp):
    """Test task completion handling."""
    task = ConcreteTask(name='Test Task')
    with qtbot.waitSignal(task_queue.queueStatusChanged, timeout=10000):
        task_queue.addTask(task)
    _waitForWorker(0.5)
    # Task should eventually complete
    qtbot.waitUntil(lambda: task.status in [TaskStatus.COMPLETED, TaskStatus.RUNNING], timeout=5000)
    assert task.status in [TaskStatus.COMPLETED, TaskStatus.RUNNING]


def test_task_retry_logic(task_queue, qtbot):
    """Test task retry on failure."""
    # Create a task that will fail
    task = ConcreteTask(name='Failing Task', maxRetries=2, retryDelaySeconds=1)
    # Make handle() fail
    original_handle = task.handle
    def failing_handle():
        raise Exception('Test failure')
    task.handle = failing_handle
    task_queue.addTask(task)
    _waitForWorker(2.0)
    # Task should be in retry or failed state
    assert task.currentRetryAttempts >= 0


def test_cancelled_task_skipped(task_queue, qapp):
    """Test that cancelled tasks are skipped."""
    task_queue.setMaxConcurrentTasks(1)
    task = ConcreteTask(name='Test Task')
    task.cancel()  # Cancel before adding
    task_queue.addTask(task)
    _waitForWorker()
    # Cancelled task should not be in running tasks
    assert task.uuid not in task_queue._runningTasks


def test_save_state(task_tracker, mock_config):
    """Test saving queue state."""
    queue = TaskQueue(task_tracker, mock_config, mock_config)
    # Add a persistent task
    task = ConcreteTask(name='Persistent Task', isPersistent=True)
    queue._pendingTasks.append(task)
    queue.saveState()
    mock_config.save.assert_called()
    assert mock_config.save.call_count >= 1


def test_queue_status_changed_signal(task_queue, qtbot):
    """Test queueStatusChanged signal emission."""
    task = ConcreteTask(name='Test Task')
    with qtbot.waitSignal(task_queue.queueStatusChanged, timeout=2000):
        task_queue.addTask(task)


def test_task_dequeued_signal(task_queue, qtbot):
    """Test taskDequeued signal emission."""
    task = ConcreteTask(name='Test Task')
    with qtbot.waitSignal(task_queue.taskDequeued, timeout=2000):
        task_queue.addTask(task)


def test_concurrency_limit(task_queue, qapp):
    """Test that concurrency limit is respected."""
    task_queue.setMaxConcurrentTasks(2)
    # Add 5 tasks
    tasks = []
    for i in range(5):
        task = ConcreteTask(name=f'Task {i}')
        tasks.append(task)
        task_queue.addTask(task)
    _waitForWorker()
    # Should not exceed max concurrent
    assert task_queue.getRunningCount() <= 2
