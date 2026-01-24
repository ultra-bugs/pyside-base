"""
Tests for TaskTracker.
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
import pytest

from core.taskSystem.Exceptions import TaskNotFoundException
from core.taskSystem.TaskStatus import TaskStatus
from core.taskSystem.TaskTracker import TaskTracker
from tests_core.task_system.test_AbstractTask import ConcreteTask
import logging


def test_task_tracker_initialization(mock_config):
    """Test TaskTracker initialization."""
    mock_config.load.return_value = []
    tracker = TaskTracker(mock_config)
    assert tracker._storage == mock_config
    assert len(tracker._activeTasks) == 0
    assert len(tracker._failedTaskHistory) == 0


def test_add_task(mock_config, qtbot):
    """Test adding a task to tracker."""
    mock_config.load.return_value = []
    tracker = TaskTracker(mock_config)
    task = ConcreteTask(name='Test Task')
    with qtbot.waitSignal(tracker.taskAdded, timeout=1000):
        tracker.addTask(task)
    assert task.uuid in tracker._activeTasks
    assert tracker._activeTasks[task.uuid] == task


def test_add_duplicate_task(mock_config, caplog_loguru):
    """Test adding the same task twice."""
    with caplog_loguru.at_level(logging.WARNING):
        mock_config.load.return_value = []
        tracker = TaskTracker(mock_config)
        task = ConcreteTask(name='Test Task')
        tracker.addTask(task)
        tracker.addTask(task)  # Add again
        assert 'already tracked' in caplog_loguru.text


def test_remove_task(mock_config, qtbot):
    """Test removing a task from tracker."""
    mock_config.load.return_value = []
    tracker = TaskTracker(mock_config)
    task = ConcreteTask(name='Test Task')
    tracker.addTask(task)
    with qtbot.waitSignal(tracker.taskRemoved, timeout=1000):
        tracker.removeTask(task.uuid)
    assert task.uuid not in tracker._activeTasks


def test_remove_nonexistent_task(mock_config):
    """Test removing a task that doesn't exist."""
    mock_config.load.return_value = []
    tracker = TaskTracker(mock_config)
    with pytest.raises(TaskNotFoundException):
        tracker.removeTask('nonexistent-uuid')


def test_get_task_info(mock_config):
    """Test getting task information."""
    mock_config.load.return_value = []
    tracker = TaskTracker(mock_config)
    task = ConcreteTask(name='Test Task', description='Test Description')
    tracker.addTask(task)
    info = tracker.getTaskInfo(task.uuid)
    assert info['name'] == 'Test Task'
    assert info['description'] == 'Test Description'
    assert info['status'] == TaskStatus.PENDING.name


def test_get_task_info_not_found(mock_config):
    """Test getting info for nonexistent task."""
    mock_config.load.return_value = []
    tracker = TaskTracker(mock_config)
    with pytest.raises(TaskNotFoundException):
        tracker.getTaskInfo('nonexistent-uuid')


def test_get_all_tasks_info(mock_config):
    """Test getting all tasks information."""
    mock_config.load.return_value = []
    tracker = TaskTracker(mock_config)
    task1 = ConcreteTask(name='Task 1')
    task2 = ConcreteTask(name='Task 2')
    tracker.addTask(task1)
    tracker.addTask(task2)
    all_tasks = tracker.getAllTasksInfo()
    assert len(all_tasks) == 2
    assert any(t['name'] == 'Task 1' for t in all_tasks)
    assert any(t['name'] == 'Task 2' for t in all_tasks)


def test_log_failed_task(mock_config, qtbot):
    """Test logging a failed task."""
    mock_config.load.return_value = []
    tracker = TaskTracker(mock_config)
    task = ConcreteTask(name='Failed Task')
    try:
        task.fail('Test failure reason')
    except Exception:
        pass
    with qtbot.waitSignal(tracker.failedTaskLogged, timeout=1000):
        tracker.logFailedTask(task)
    history = tracker.getFailedTaskHistory()
    assert len(history) == 1
    assert history[0]['name'] == 'Failed Task'
    assert history[0]['error'] == 'Test failure reason'
    assert 'failedAt' in history[0]


def test_failed_task_history_limit(mock_config):
    """Test that failed task history is limited to 1000 entries."""
    mock_config.load.return_value = []
    tracker = TaskTracker(mock_config)
    for i in range(1100):
        task = ConcreteTask(name=f'Task {i}')
        try:
            task.fail('Test failure')
        except Exception:
            pass
        tracker.logFailedTask(task)
    history = tracker.getFailedTaskHistory()
    print(f'DEBUG: History len = {len(history)}')
    assert len(history) == 1000


def test_load_state(mock_config):
    """Test loading state from config."""
    failed_tasks = [{'uuid': 'task-1', 'name': 'Failed Task 1'}, {'uuid': 'task-2', 'name': 'Failed Task 2'}]
    mock_config.load.return_value = failed_tasks
    tracker = TaskTracker(mock_config)
    assert len(tracker._failedTaskHistory) == 2
    mock_config.load.assert_any_call('failedTaskHistory', [])


def test_load_state_invalid_data(mock_config):
    """Test loading state with invalid data."""
    mock_config.load.return_value = 'invalid data'  # Not a list
    tracker = TaskTracker(mock_config)
    assert len(tracker._failedTaskHistory) == 0


def test_save_state(mock_config):
    """Test saving state to config."""
    mock_config.load.return_value = []
    tracker = TaskTracker(mock_config)
    task = ConcreteTask(name='Failed Task')
    try:
        task.fail('Test failure')
    except Exception:
        pass
    tracker.logFailedTask(task)
    mock_config.save.assert_any_call('failedTaskHistory', tracker._failedTaskHistory)
    mock_config.save.assert_called()


def test_task_status_changed_signal(mock_config, qtbot):
    """Test that tracker emits taskUpdated when task status changes."""
    mock_config.load.return_value = []
    tracker = TaskTracker(mock_config)
    task = ConcreteTask(name='Test Task')
    tracker.addTask(task)
    with qtbot.waitSignal(tracker.taskUpdated, timeout=1000):
        task.setStatus(TaskStatus.RUNNING)


def test_task_progress_updated_signal(mock_config, qtbot):
    """Test that tracker emits taskUpdated when task progress changes."""
    mock_config.load.return_value = []
    tracker = TaskTracker(mock_config)
    task = ConcreteTask(name='Test Task')
    tracker.addTask(task)
    with qtbot.waitSignal(tracker.taskUpdated, timeout=1000):
        task.setProgress(50)


def test_task_finished_signal(mock_config, qtbot):
    """Test that tracker handles taskFinished signal."""
    mock_config.load.return_value = []
    tracker = TaskTracker(mock_config)
    task = ConcreteTask(name='Test Task')
    tracker.addTask(task)
    with qtbot.waitSignal(tracker.taskUpdated, timeout=2000):
        task.run()
