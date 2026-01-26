import pytest
from unittest.mock import MagicMock
from PySide6 import QtCore
from core.taskSystem.AbstractTask import AbstractTask
from core.taskSystem.TaskQueue import TaskQueue
from core.taskSystem.TaskTracker import TaskTracker
from core.taskSystem.UniqueType import UniqueType
from core.taskSystem.TaskStatus import TaskStatus
from core.Logging import logger

class ConcreteUniqueTask(AbstractTask):
    def __init__(self, name, uniqueType=UniqueType.NONE, uniqueKey=None, **kwargs):
        super().__init__(name=name, uniqueType=uniqueType, **kwargs)
        self._uniqueKey = uniqueKey

    def handle(self):
        pass

    def _performCancellationCleanup(self):
        pass

    def uniqueVia(self) -> str:
        if self._uniqueKey:
            return self._uniqueKey
        return super().uniqueVia()

@pytest.fixture
def task_tracker(mock_config):
    mock_config.load.return_value = []
    return TaskTracker(mock_config)

@pytest.fixture
def mock_thread_pool(mocker):
    # Mock QThreadPool class
    mock_pool_cls = mocker.patch('core.taskSystem.TaskQueue.QtCore.QThreadPool')
    # Since TaskQueue uses globalInstance(), we mock that
    mock_pool_instance = mock_pool_cls.globalInstance.return_value
    mock_pool_instance.activeThreadCount.return_value = 0
    return mock_pool_instance

@pytest.fixture
def task_queue(task_tracker, mock_config, mock_thread_pool):
    # maxConcurrentTasks=1
    return TaskQueue(task_tracker, mock_config, mock_config, maxConcurrentTasks=1)

def test_unique_job_constraint(task_queue, mock_thread_pool, qtbot):
    """Test UniqueType.JOB prevents duplicate tasks."""
    # 1. Add a dummy task that is RUNNING to occupy the slot
    dummy = ConcreteUniqueTask("Dummy")
    task_queue.addTask(dummy)
    
    # Verify dummy started
    assert task_queue.getRunningCount() == 1
    assert task_queue.getPendingCount() == 0
    mock_thread_pool.start.assert_called_with(dummy)
    
    # 2. Add Task 1 (Should remain Pending)
    task1 = ConcreteUniqueTask(name="Task 1", uniqueType=UniqueType.JOB, uniqueKey="KEY_A")
    task_queue.addTask(task1)
    
    assert task_queue.getPendingCount() == 1
    # Check uniqueness index
    assert task_queue._activeUniqueKeys["KEY_A"]["pending"] == 1
    
    # 3. Add Task 2 (Duplicate) -> Should be IGNORED
    task2 = ConcreteUniqueTask(name="Task 1 (Dup)", uniqueType=UniqueType.JOB, uniqueKey="KEY_A")
    task_queue.addTask(task2)
    
    assert task_queue.getPendingCount() == 1  # Still 1
    
    # 4. Finish dummy task to check if Task 1 starts
    # We manually trigger completion handler
    dummy.setStatus(TaskStatus.COMPLETED)
    dummy.taskFinished.emit(dummy.uuid, TaskStatus.COMPLETED, None, None)
    
    # TaskQueue should process queue and start Task 1
    assert task_queue.getRunningCount() == 1
    assert task_queue.getPendingCount() == 0
    mock_thread_pool.start.assert_called_with(task1)
    
    # Index should update: pending 0, running 1
    assert task_queue._activeUniqueKeys["KEY_A"]["pending"] == 0
    assert task_queue._activeUniqueKeys["KEY_A"]["running"] == 1
    
    # 5. Add Task 3 (Duplicate Key) while Running -> Should be IGNORED (UniqueJob)
    task3 = ConcreteUniqueTask(name="Task 3", uniqueType=UniqueType.JOB, uniqueKey="KEY_A")
    task_queue.addTask(task3)
    assert task_queue.getPendingCount() == 0 # Ignored

    # 6. Finish Task 1
    task1.setStatus(TaskStatus.COMPLETED)
    task1.taskFinished.emit(task1.uuid, TaskStatus.COMPLETED, None, None)
    
    # Index should clear
    assert "KEY_A" not in task_queue._activeUniqueKeys

def test_unique_until_processing_constraint(task_queue, mock_thread_pool):
    """Test UniqueType.UNTIL_PROCESSING constraint."""
    # 1. Occupy slot
    dummy = ConcreteUniqueTask("Dummy")
    task_queue.addTask(dummy)
    
    assert task_queue.getRunningCount() == 1
    
    # 2. Add Task 1 (Pending)
    task1 = ConcreteUniqueTask(name="Task 1", uniqueType=UniqueType.UNTIL_PROCESSING, uniqueKey="KEY_B")
    task_queue.addTask(task1)
    
    assert task_queue.getPendingCount() == 1
    assert task_queue._activeUniqueKeys["KEY_B"]["pending"] == 1
    
    # 3. Add Task 2 (Duplicate Pending) -> IGNORED
    task2 = ConcreteUniqueTask(name="Task 2", uniqueType=UniqueType.UNTIL_PROCESSING, uniqueKey="KEY_B")
    task_queue.addTask(task2)
    assert task_queue.getPendingCount() == 1
    
    # 4. Finish dummy -> Task 1 starts
    dummy.setStatus(TaskStatus.COMPLETED)
    dummy.taskFinished.emit(dummy.uuid, TaskStatus.COMPLETED, None, None)
    
    assert task_queue.getRunningCount() == 1 # Task 1 running
    assert task_queue.getPendingCount() == 0
    
    # Index: pending 0, running 1
    assert task_queue._activeUniqueKeys["KEY_B"]["pending"] == 0
    # For UNTIL_PROCESSING, we track running? Yes, logic adds to running count.
    assert task_queue._activeUniqueKeys["KEY_B"]["running"] == 1
    
    # 5. Add Task 3 (Duplicate Key) while Running -> ACCEPTED (Until Processing)
    task3 = ConcreteUniqueTask(name="Task 3", uniqueType=UniqueType.UNTIL_PROCESSING, uniqueKey="KEY_B")
    task_queue.addTask(task3)
    
    assert task_queue.getPendingCount() == 1 # Accepted!
    assert task_queue._activeUniqueKeys["KEY_B"]["pending"] == 1

def test_cancellation_clears_unique_index(task_queue, mock_thread_pool, qtbot):
    """Test that cancelling a pending task clears the unique index."""
    # 1. Occupy slot
    dummy = ConcreteUniqueTask("Dummy")
    task_queue.addTask(dummy)
    
    task1 = ConcreteUniqueTask(name="Task 1", uniqueType=UniqueType.JOB, uniqueKey="KEY_C")
    task_queue.addTask(task1)
    
    assert task_queue._activeUniqueKeys["KEY_C"]["pending"] == 1
    
    # 2. Cancel Task 1 (while pending)
    # AbstractTask.cancel sets status to CANCELLED and sets EVENT
    task1.cancel()
    
    # 3. Finish dummy
    # TaskQueue processing loop calls _processQueue
    # _processQueue pops Task 1. Checks status.
    # If CANCELLED, skips and updates index.
    
    dummy.setStatus(TaskStatus.COMPLETED)
    dummy.taskFinished.emit(dummy.uuid, TaskStatus.COMPLETED, None, None)
    
    # Task 1 was skipped. Queue empty. Running 0.
    assert task_queue.getPendingCount() == 0
    assert task_queue.getRunningCount() == 0
    
    # Index should be cleared
    if "KEY_C" in task_queue._activeUniqueKeys:
        assert task_queue._activeUniqueKeys["KEY_C"]["pending"] == 0
        assert task_queue._activeUniqueKeys["KEY_C"]["running"] == 0
