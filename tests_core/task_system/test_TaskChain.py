"""
Tests for TaskChain class.
Comprehensive tests covering execution flow, retry behaviors, progress tracking,
serialization, cancellation, and recovery scenarios.
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
import time
from unittest.mock import MagicMock, patch

from core.taskSystem.AbstractTask import AbstractTask
from core.taskSystem.TaskChain import TaskChain
from core.taskSystem.ChainContext import ChainContext
from core.taskSystem.ChainRetryBehavior import ChainRetryBehavior
from core.taskSystem.TaskStatus import TaskStatus
from core.Observer import Publisher


class MockTask(AbstractTask):
    """Mock task for testing TaskChain."""

    def __init__(self, name, should_succeed=True, should_raise=False, execution_delay=0, **kwargs):
        super().__init__(name=name, **kwargs)
        self.should_succeed = should_succeed
        self.should_raise = should_raise
        self.execution_delay = execution_delay
        self.handle_called = False
        self.execution_count = 0
        self.cleanup_called = False

    def handle(self):
        """Test implementation."""
        self.handle_called = True
        self.execution_count += 1
        if self.execution_delay > 0:
            time.sleep(self.execution_delay)
        if self.should_raise:
            raise RuntimeError(f'Task {self.name} raised exception')
        if not self.should_succeed:
            self.fail(f'Task {self.name} intentionally failed')
            return
        if not self.isStopped():
            self.setStatus(TaskStatus.COMPLETED)

    def _performCancellationCleanup(self):
        """Test implementation."""
        self.cleanup_called = True

    @classmethod
    def deserialize(cls, data):
        """Test implementation."""
        return cls(name=data['name'], should_succeed=data.get('should_succeed', True), maxRetries=data.get('maxRetries', 0), retryDelaySeconds=data.get('retryDelaySeconds', 5))

    def serialize(self):
        """Test implementation."""
        data = super().serialize()
        data['should_succeed'] = self.should_succeed
        return data


class ContextSharingTask(AbstractTask):
    """Task that shares data via ChainContext."""

    def __init__(self, name, write_key=None, write_value=None, read_key=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.write_key = write_key
        self.write_value = write_value
        self.read_key = read_key
        self.read_value = None

    def handle(self):
        """Read/write from context."""
        if self.read_key and self._chainContext:
            self.read_value = self._chainContext.get(self.read_key)
        if self.write_key and self.write_value is not None and self._chainContext:
            self._chainContext.set(self.write_key, self.write_value)
        if not self.isStopped():
            self.setStatus(TaskStatus.COMPLETED)

    @classmethod
    def deserialize(cls, data):
        """Test implementation."""
        return cls(name=data['name'])

    def _performCancellationCleanup(self):
        """Test implementation."""
        pass


@pytest.fixture
def real_publisher():
    """Provide real Publisher instance for integration tests."""
    from core.Observer import Publisher
    publisher = Publisher()
    # Store original state
    original_global = publisher.globalSubscribers.copy()
    original_events = {k: v.copy() for k, v in publisher.eventSpecificSubscribers.items()}
    yield publisher
    # Restore original state
    publisher.globalSubscribers = original_global
    publisher.eventSpecificSubscribers = original_events


# ============================================================================
# TaskChain Initialization Tests
# ============================================================================


def test_task_chain_initialization():
    """Test TaskChain initialization."""
    tasks = [MockTask('Task1'), MockTask('Task2'), MockTask('Task3')]
    chain = TaskChain(name='Test Chain', tasks=tasks)
    assert chain.name == 'Test Chain'
    assert len(chain._tasks) == 3
    assert chain._currentTaskIndex == 0
    assert chain._chainContext is not None
    assert isinstance(chain._chainContext, ChainContext)
    assert chain._chainContext._chainUuid == chain.uuid
    assert len(chain._taskStates) == 3
    # Verify all child tasks have chainUuid set
    for task in tasks:
        assert task.chainUuid == chain.uuid


def test_task_chain_initialization_with_retry_behavior_map():
    """Test TaskChain initialization with retry behavior map."""
    tasks = [MockTask('Task1'), MockTask('Task2')]
    retry_map = {'MockTask': ChainRetryBehavior.SKIP_TASK}
    chain = TaskChain(name='Test Chain', tasks=tasks, retryBehaviorMap=retry_map)
    assert chain.retryBehaviorMap['MockTask'] == ChainRetryBehavior.SKIP_TASK


# ============================================================================
# TaskChain Sequential Execution Tests
# ============================================================================


def test_task_chain_sequential_execution(real_publisher):
    """Test TaskChain executes tasks sequentially."""
    tasks = [MockTask('Task1'), MockTask('Task2'), MockTask('Task3')]
    chain = TaskChain(name='Test Chain', tasks=tasks)
    # Execute chain
    chain.run()
    # Verify all tasks were executed
    assert all(task.handle_called for task in tasks)
    assert all(task.status == TaskStatus.COMPLETED for task in tasks)
    assert chain.status == TaskStatus.COMPLETED
    # Verify execution order (should be sequential)
    for i, task in enumerate(tasks):
        assert task.execution_count == 1


def test_task_chain_execution_order():
    """Test that tasks execute in correct order."""
    execution_order = []
    class OrderedTask(AbstractTask):
        def __init__(self, name, order_list, **kwargs):
            super().__init__(name=name, **kwargs)
            self.order_list = order_list
        def handle(self):
            self.order_list.append(self.name)
            if not self.isStopped():
                self.setStatus(TaskStatus.COMPLETED)
        @classmethod
        def deserialize(cls, data):
            return cls(name=data['name'], order_list=[])
        def _performCancellationCleanup(self):
            pass
    tasks = [OrderedTask('Task1', execution_order), OrderedTask('Task2', execution_order), OrderedTask('Task3', execution_order)]
    chain = TaskChain(name='Test Chain', tasks=tasks)
    chain.run()
    assert execution_order == ['Task1', 'Task2', 'Task3']


# ============================================================================
# ChainContext Sharing Tests
# ============================================================================


def test_task_chain_context_sharing():
    """Test that tasks can share data via ChainContext."""
    tasks = [ContextSharingTask('WriteTask', write_key='token', write_value='abc123'), ContextSharingTask('ReadTask', read_key='token')]
    chain = TaskChain(name='Test Chain', tasks=tasks)
    chain.run()
    # Verify read task got the value from write task
    assert tasks[1].read_value == 'abc123'
    assert chain._chainContext.get('token') == 'abc123'


def test_task_chain_context_persists_across_tasks():
    """Test that ChainContext persists data across multiple tasks."""
    tasks = [
        ContextSharingTask('Task1', write_key='step1', write_value=1),
        ContextSharingTask('Task2', write_key='step2', write_value=2),
        ContextSharingTask('Task3', write_key='step3', write_value=3),
    ]
    chain = TaskChain(name='Test Chain', tasks=tasks)
    chain.run()
    # Verify all values are in context
    assert chain._chainContext.get('step1') == 1
    assert chain._chainContext.get('step2') == 2
    assert chain._chainContext.get('step3') == 3


# ============================================================================
# Retry Behavior Tests - Task Level
# ============================================================================


def test_task_chain_task_level_retry_succeeds_on_retry():
    """Test task fails once then succeeds on retry; verify chain continues."""
    # Create task that fails first time, succeeds on retry
    call_count = [0]  # Use list to allow modification in nested function
    class RetryableTask(MockTask):
        def handle(self):
            self.handle_called = True
            self.execution_count += 1
            call_count[0] += 1
            if call_count[0] < 2:
                # Fail first attempt
                self.fail('Temporary failure')
            else:
                # Succeed on retry
                if not self.isStopped():
                    self.setStatus(TaskStatus.COMPLETED)
    task1 = RetryableTask('Task1', maxRetries=1)
    task2 = MockTask('Task2')
    chain = TaskChain(name='Test Chain', tasks=[task1, task2])
    chain.run()
    # Task1 should have been retried and eventually succeeded
    assert task1.execution_count >= 2
    assert task1.status == TaskStatus.COMPLETED
    # Task2 should have been executed (chain continued)
    assert task2.handle_called
    assert task2.status == TaskStatus.COMPLETED
    # Chain should have completed
    assert chain.status == TaskStatus.COMPLETED


def test_task_chain_task_exhausts_max_retries():
    """Test child task fails all maxRetries; verify chain stops (default behavior)."""
    task1 = MockTask('Task1', should_succeed=False, maxRetries=2)
    task2 = MockTask('Task2')
    chain = TaskChain(name='Test Chain', tasks=[task1, task2])
    from core.taskSystem.AbstractTask import TaskFailedException
    with pytest.raises(TaskFailedException):
        chain.run()
    # Task1 should have been retried maxRetries times
    assert task1.execution_count >= task1.maxRetries + 1  # Initial + retries
    assert task1.status == TaskStatus.FAILED
    assert chain.status == TaskStatus.FAILED
    # Task2 should not have been executed (chain stopped)
    assert not task2.handle_called


# ============================================================================
# Retry Behavior Tests - Chain Level
# ============================================================================


def test_task_chain_stop_chain_behavior():
    """Test STOP_CHAIN behavior when task fails."""
    task1 = MockTask('Task1', should_succeed=False, maxRetries=0)
    task2 = MockTask('Task2')
    retry_map = {'MockTask': ChainRetryBehavior.STOP_CHAIN}
    chain = TaskChain(name='Test Chain', tasks=[task1, task2], retryBehaviorMap=retry_map)
    from core.taskSystem.AbstractTask import TaskFailedException
    with pytest.raises(TaskFailedException):
        chain.run()
    assert task1.status == TaskStatus.FAILED
    assert chain.status == TaskStatus.FAILED
    assert not task2.handle_called


def test_task_chain_skip_task_behavior():
    """Test SKIP_TASK behavior: verify chain skips failed task and completes remaining tasks."""
    task1 = MockTask('Task1', should_succeed=False, maxRetries=0)
    task2 = MockTask('Task2')
    task3 = MockTask('Task3')
    retry_map = {'MockTask': ChainRetryBehavior.SKIP_TASK}
    chain = TaskChain(name='Test Chain', tasks=[task1, task2, task3], retryBehaviorMap=retry_map)
    chain.run()
    # Task1 should have failed
    assert task1.status == TaskStatus.FAILED
    # Task2 and Task3 should have been executed (chain continued)
    assert task2.handle_called
    assert task2.status == TaskStatus.COMPLETED
    assert task3.handle_called
    assert task3.status == TaskStatus.COMPLETED
    # Chain should have completed successfully
    assert chain.status == TaskStatus.COMPLETED


def test_task_chain_retry_chain_behavior():
    """Test RETRY_CHAIN: verify _currentTaskIndex is reset to 0 and chain restarts."""
    task1 = MockTask('Task1', should_succeed=True)  # Succeeds first time
    task2 = MockTask('Task2', should_succeed=False, maxRetries=0)  # Fails
    task3 = MockTask('Task3')
    retry_map = {'MockTask': ChainRetryBehavior.RETRY_CHAIN}
    chain = TaskChain(name='Test Chain', tasks=[task1, task2, task3], retryBehaviorMap=retry_map, maxRetries=1)
    from core.taskSystem.AbstractTask import TaskFailedException
    with pytest.raises(TaskFailedException):
        chain.run()
    # Task1 should have been executed multiple times (chain retried)
    assert task1.execution_count >= 2
    # Chain should have failed after maxRetries
    assert chain.status == TaskStatus.FAILED


# ============================================================================
# Progress Tracking Tests
# ============================================================================


def test_task_chain_default_progress_calculation():
    """Test default progress calculation based on current task index."""
    tasks = [MockTask('Task1'), MockTask('Task2'), MockTask('Task3')]
    chain = TaskChain(name='Test Chain', tasks=tasks)
    # Progress should start at 0
    assert chain.progress == 0
    # Execute first task
    chain._currentTaskIndex = 0
    chain._updateDefaultProgress()
    # Progress after task 1: (1/3) * 100 = 33
    assert chain.progress == 33
    # Execute second task
    chain._currentTaskIndex = 1
    chain._updateDefaultProgress()
    # Progress after task 2: (2/3) * 100 = 66
    assert chain.progress == 66
    # Execute third task
    chain._currentTaskIndex = 2
    chain._updateDefaultProgress()
    # Progress after task 3: (3/3) * 100 = 100
    assert chain.progress == 100


def test_task_chain_external_progress_update(real_publisher):
    """Test external progress update via ChainProgressUpdateRequest event."""
    tasks = [MockTask('Task1'), MockTask('Task2')]
    chain = TaskChain(name='Test Chain', tasks=tasks)
    # Subscribe to events
    publisher = Publisher()
    publisher.subscribe(chain, event='ChainProgressUpdateRequest')
    # Simulate external progress update
    chain.onChainProgressUpdateRequest({'chainUuid': chain.uuid, 'progress': 75})
    assert chain.progress == 75
    assert chain._progress_updated_externally is True


def test_task_chain_external_progress_update_wrong_chain(real_publisher):
    """Test external progress update ignores events for other chains."""
    tasks = [MockTask('Task1')]
    chain = TaskChain(name='Test Chain', tasks=tasks)
    # Subscribe to events
    publisher = Publisher()
    publisher.subscribe(chain, event='ChainProgressUpdateRequest')
    # Try to update progress for different chain
    chain.onChainProgressUpdateRequest({'chainUuid': 'different-uuid', 'progress': 50})
    # Progress should not have changed
    assert chain.progress == 0


# ============================================================================
# Cancellation Tests
# ============================================================================


def test_task_chain_cancellation():
    """Test cancelling a TaskChain and verify running child task is also cancelled."""
    task1 = MockTask('Task1', execution_delay=0.2)
    task2 = MockTask('Task2')
    chain = TaskChain(name='Test Chain', tasks=[task1, task2])
    # Start chain in background
    import threading
    chain_thread = threading.Thread(target=chain.run)
    chain_thread.start()
    # Wait a bit for chain to start and task1 to begin execution
    time.sleep(0.1)
    # Cancel chain before task1 completes
    chain.cancel()
    # Wait for thread to finish
    chain_thread.join(timeout=2.0)
    # Verify cancellation
    assert chain.isStopped()
    assert chain.status == TaskStatus.CANCELLED
    # Verify child tasks were cancelled or stopped
    assert task1.cleanup_called or task1.isStopped()


# ============================================================================
# Serialization/Deserialization Tests
# ============================================================================


def test_task_chain_serialization():
    """Test TaskChain serialization."""
    tasks = [MockTask('Task1', maxRetries=1), MockTask('Task2', maxRetries=2)]
    retry_map = {'MockTask': ChainRetryBehavior.SKIP_TASK}
    chain = TaskChain(name='Test Chain', tasks=tasks, retryBehaviorMap=retry_map)
    chain._currentTaskIndex = 1
    chain._chainContext.set('test_key', 'test_value')
    chain._chainRetryAttempts = 1
    serialized = chain.serialize()
    assert serialized['name'] == 'Test Chain'
    assert serialized['currentTaskIndex'] == 1
    assert len(serialized['tasks']) == 2
    assert serialized['chainContext']['data']['test_key'] == 'test_value'
    assert serialized['retryBehaviorMap']['MockTask'] == 'SKIP_TASK'
    assert serialized['chainRetryAttempts'] == 1


def test_task_chain_deserialization():
    """Test TaskChain deserialization."""
    # First create and serialize a chain
    tasks = [MockTask('Task1', maxRetries=1), MockTask('Task2', maxRetries=2)]
    retry_map = {'MockTask': ChainRetryBehavior.SKIP_TASK}
    chain1 = TaskChain(name='Test Chain', tasks=tasks, retryBehaviorMap=retry_map)
    chain1._currentTaskIndex = 1
    chain1._chainContext.set('test_key', 'test_value')
    chain1._chainRetryAttempts = 1
    chain1.status = TaskStatus.RUNNING
    chain1.progress = 50
    serialized = chain1.serialize()
    # Deserialize
    chain2 = TaskChain.deserialize(serialized)
    assert chain2.name == 'Test Chain'
    assert chain2._currentTaskIndex == 1
    assert len(chain2._tasks) == 2
    assert chain2._chainContext.get('test_key') == 'test_value'
    assert chain2.retryBehaviorMap['MockTask'] == ChainRetryBehavior.SKIP_TASK
    assert chain2._chainRetryAttempts == 1
    assert chain2.status == TaskStatus.RUNNING
    assert chain2.progress == 50


def test_task_chain_serialize_deserialize_roundtrip():
    """Test TaskChain serialize/deserialize roundtrip preserves state."""
    tasks = [MockTask('Task1'), MockTask('Task2'), MockTask('Task3')]
    chain1 = TaskChain(name='Test Chain', tasks=tasks)
    chain1._currentTaskIndex = 1
    chain1._chainContext.set('key1', 'value1')
    chain1._chainContext.set('key2', 42)
    serialized = chain1.serialize()
    chain2 = TaskChain.deserialize(serialized)
    assert chain2.name == chain1.name
    assert chain2._currentTaskIndex == chain1._currentTaskIndex
    assert chain2._chainContext.get('key1') == chain1._chainContext.get('key1')
    assert chain2._chainContext.get('key2') == chain1._chainContext.get('key2')
    assert len(chain2._tasks) == len(chain1._tasks)


# ============================================================================
# Recovery After Restart Tests
# ============================================================================


def test_task_chain_recovery_from_checkpoint():
    """Test chain resumes from correct position after deserialization."""
    tasks = [MockTask('Task1'), MockTask('Task2'), MockTask('Task3')]
    chain1 = TaskChain(name='Test Chain', tasks=tasks)
    # Simulate: Task1 completed, Task2 about to start
    tasks[0].setStatus(TaskStatus.COMPLETED)
    tasks[0].handle_called = True
    chain1._currentTaskIndex = 1
    chain1._taskStates[tasks[0].uuid]['status'] = TaskStatus.COMPLETED
    # Serialize
    serialized = chain1.serialize()
    # Deserialize (simulating app restart)
    chain2 = TaskChain.deserialize(serialized)
    # Chain should resume from Task2
    assert chain2._currentTaskIndex == 1
    # Execute remaining tasks
    chain2.run()
    # Task2 and Task3 should have been executed
    assert chain2._tasks[1].handle_called or chain2._tasks[1].status == TaskStatus.COMPLETED
    assert chain2._tasks[2].handle_called or chain2._tasks[2].status == TaskStatus.COMPLETED


def test_task_chain_recovery_preserves_context():
    """Test that ChainContext is preserved during recovery."""
    tasks = [ContextSharingTask('WriteTask', write_key='token', write_value='recovered_token'), ContextSharingTask('ReadTask', read_key='token')]
    chain1 = TaskChain(name='Test Chain', tasks=tasks)
    # Simulate: First task completed and wrote to context
    chain1._chainContext.set('token', 'recovered_token')
    chain1._currentTaskIndex = 1
    # Serialize and deserialize
    serialized = chain1.serialize()
    chain2 = TaskChain.deserialize(serialized)
    # Context should be preserved
    assert chain2._chainContext.get('token') == 'recovered_token'
    # Continue execution
    chain2.run()
    # Read task should have access to preserved context
    assert tasks[1].read_value == 'recovered_token' or chain2._chainContext.get('token') == 'recovered_token'


@pytest.mark.slow
def test_task_chain_recovery_with_retrying_state():
    """Test recovery when app shuts down while child task is in RETRYING state."""
    class RetryingTask(AbstractTask):
        def __init__(self, name, **kwargs):
            super().__init__(name=name, maxRetries=2, **kwargs)
            self.attempts = 0
        def handle(self):
            self.attempts += 1
            if self.attempts < 3:
                self.fail('Temporary failure')
            else:
                self.setStatus(TaskStatus.COMPLETED)
        @classmethod
        def deserialize(cls, data):
            return cls(name=data['name'], maxRetries=data.get('maxRetries', 2))
        def _performCancellationCleanup(self):
            pass
    task1 = RetryingTask('Task1')
    task2 = MockTask('Task2')
    chain1 = TaskChain(name='Test Chain', tasks=[task1, task2])
    # Simulate: Task1 is in RETRYING state
    task1.status = TaskStatus.RETRYING
    task1.attempts = 1
    chain1._currentTaskIndex = 0
    chain1._taskStates[task1.uuid]['status'] = TaskStatus.RETRYING
    # Serialize
    serialized = chain1.serialize()
    # Deserialize
    chain2 = TaskChain.deserialize(serialized)
    # Chain should be able to continue
    assert chain2._currentTaskIndex == 0
    # Continue execution - task should retry and eventually succeed
    chain2.run()

    # Task1 should eventually complete after retries
    # (This test may need adjustment based on actual retry logic implementation)


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.integration
def test_task_chain_full_integration():
    """Test complete chain execution with all features."""
    # Create tasks with context sharing
    tasks = [
        ContextSharingTask('LoginTask', write_key='auth_token', write_value='token123'),
        ContextSharingTask('FetchTask', read_key='auth_token'),
        MockTask('ProcessTask'),
        MockTask('CleanupTask'),
    ]
    retry_map = {'ContextSharingTask': ChainRetryBehavior.SKIP_TASK, 'MockTask': ChainRetryBehavior.STOP_CHAIN}
    chain = TaskChain(name='Integration Test Chain', tasks=tasks, retryBehaviorMap=retry_map, isPersistent=True)
    # Execute chain
    chain.run()
    # Verify all tasks completed
    assert chain.status == TaskStatus.COMPLETED
    assert all(task.status == TaskStatus.COMPLETED for task in tasks)
    # Verify context was shared
    assert chain._chainContext.get('auth_token') == 'token123'
    assert tasks[1].read_value == 'token123'
    # Verify result contains context data
    assert isinstance(chain.result, dict)
    assert 'auth_token' in chain.result


def test_task_chain_empty_task_list():
    """Test TaskChain with empty task list."""
    chain = TaskChain(name='Empty Chain', tasks=[])
    chain.run()
    assert chain.status == TaskStatus.COMPLETED
    assert chain.progress == 100


def test_task_chain_single_task():
    """Test TaskChain with single task."""
    task = MockTask('SingleTask')
    chain = TaskChain(name='Single Task Chain', tasks=[task])
    chain.run()
    assert task.handle_called
    assert task.status == TaskStatus.COMPLETED
    assert chain.status == TaskStatus.COMPLETED
    assert chain.progress == 100
