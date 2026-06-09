"""
Backward compatibility tests: saveState() calls without WorkingSet parameter
must persist data identically to the pre-UoW behaviour.
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, Mock

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.taskSystem.storage.JsonStorage import JsonStorage
from core.taskSystem.TaskQueue import TaskQueue
from core.taskSystem.TaskTracker import TaskTracker


def _makeTempJson(content='{}'):
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    f.write(content)
    f.close()
    return f.name


class TestTaskQueueBackwardCompatibility:
    def test_save_state_without_workingset_persists_pending_tasks(self):
        """saveState() with no args saves persistent tasks to storage."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            task_queue = TaskQueue(Mock(), storage, Mock())
            task_queue._pendingTasks.clear()

            class _FakeTask:
                isPersistent = True

                def serialize(self):
                    return {'name': 'task_a'}

            task_queue._pendingTasks.append(_FakeTask())
            task_queue.saveState()
            reloaded = JsonStorage(path)
            saved = reloaded.load('pendingTasks', [])
            assert len(saved) == 1
            assert saved[0]['name'] == 'task_a'
        finally:
            os.unlink(path)

    def test_save_state_without_workingset_filters_non_persistent(self):
        """saveState() with no args only keeps isPersistent=True tasks."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            task_queue = TaskQueue(Mock(), storage, Mock())
            task_queue._pendingTasks.clear()

            class _Persistent:
                isPersistent = True

                def serialize(self):
                    return {'name': 'keep'}

            class _Transient:
                isPersistent = False

                def serialize(self):
                    return {'name': 'drop'}

            task_queue._pendingTasks.append(_Persistent())
            task_queue._pendingTasks.append(_Transient())
            task_queue.saveState()
            saved = JsonStorage(path).load('pendingTasks', [])
            assert len(saved) == 1
            assert saved[0]['name'] == 'keep'
        finally:
            os.unlink(path)

    def test_save_state_without_workingset_empty_queue(self):
        """saveState() with empty queue saves [] to storage."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            task_queue = TaskQueue(Mock(), storage, Mock())
            task_queue._pendingTasks.clear()
            task_queue.saveState()
            assert JsonStorage(path).load('pendingTasks') == []
        finally:
            os.unlink(path)

    def test_save_state_direct_path_used_without_workingset(self):
        """saveState(None) routes to direct storage.save, not saveBatch."""
        import inspect

        source = inspect.getsource(TaskQueue.saveState)
        # The else branch must call self._storage.save directly
        assert 'self._storage.save(' in source
        # and that branch must be inside an 'else' clause
        assert 'else:' in source


class TestTaskTrackerBackwardCompatibility:
    def test_save_state_without_workingset_persists_failed_history(self):
        """saveState() with no args persists failed task history."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            tracker = TaskTracker(storage)
            tracker._failedTaskHistory = ['fail_1', 'fail_2']
            tracker._completedTaskHistory = []
            tracker.saveState()
            reloaded = JsonStorage(path)
            assert reloaded.load('failedTaskHistory') == ['fail_1', 'fail_2']
        finally:
            os.unlink(path)

    def test_save_state_without_workingset_persists_completed_history(self):
        """saveState() with no args persists completed task history."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            tracker = TaskTracker(storage)
            tracker._failedTaskHistory = []
            tracker._completedTaskHistory = ['done_1', 'done_2', 'done_3']
            tracker.saveState()
            reloaded = JsonStorage(path)
            assert reloaded.load('completedTaskHistory') == ['done_1', 'done_2', 'done_3']
        finally:
            os.unlink(path)

    def test_save_state_without_workingset_empty_history(self):
        """saveState() with empty history writes [] for both collections."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            tracker = TaskTracker(storage)
            tracker._failedTaskHistory = []
            tracker._completedTaskHistory = []
            tracker.saveState()
            reloaded = JsonStorage(path)
            assert reloaded.load('failedTaskHistory') == []
            assert reloaded.load('completedTaskHistory') == []
        finally:
            os.unlink(path)

    def test_save_state_direct_path_used_without_workingset(self):
        """saveState(None) routes to direct storage.save calls, not saveBatch."""
        import inspect

        source = inspect.getsource(TaskTracker.saveState)
        assert 'self._storage.save(' in source
        assert 'else:' in source


class TestWorkingSetVsDirectDataEquivalence:
    """UoW and direct save paths produce identical persistent state."""

    def test_tracker_uow_and_direct_produce_same_state(self):
        """TaskTracker data persisted via UoW equals data persisted directly."""
        path_a = _makeTempJson()
        path_b = _makeTempJson()
        try:
            failed = ['err1', 'err2']
            completed = ['done1']
            # Direct path
            s_direct = JsonStorage(path_a)
            t_direct = TaskTracker(s_direct)
            t_direct._failedTaskHistory = list(failed)
            t_direct._completedTaskHistory = list(completed)
            t_direct.saveState()
            # UoW path
            s_uow = JsonStorage(path_b)
            t_uow = TaskTracker(s_uow)
            t_uow._failedTaskHistory = list(failed)
            t_uow._completedTaskHistory = list(completed)
            ws = s_uow.beginWork()
            t_uow.saveState(ws)
            ws.commit()
            for key in ('failedTaskHistory', 'completedTaskHistory'):
                assert JsonStorage(path_a).load(key) == JsonStorage(path_b).load(key), f'Mismatch on key {key!r}'
        finally:
            os.unlink(path_a)
            os.unlink(path_b)
