"""
Integration tests: orchestrated UoW saves vs direct saves.
Verifies I/O reduction, data correctness, and all scenarios.
"""

import pytest
import tempfile
import os
import json
import sys
from pathlib import Path
from unittest.mock import patch, Mock

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.taskSystem.storage.JsonStorage import JsonStorage


def _makeTempJson():
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    f.write('{}')
    f.close()
    return f.name


def _countSaveFileCallsOnStorage(storage: JsonStorage):
    """Wrap _save_file to count calls."""
    calls = []
    original = storage._save_file

    def counted():
        calls.append(1)
        original()

    storage._save_file = counted
    return calls


class TestOrchestrationVsDirectComparison:
    """Compare orchestrated (UoW) saves vs direct saves."""

    def test_orchestrated_produces_single_file_write(self):
        """Orchestrated save: 3 subsystem keys → 1 file write."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            calls = _countSaveFileCallsOnStorage(storage)
            ws = storage.beginWork()
            ws.save('pendingTasks', ['task1'])
            ws.save('failedTaskHistory', ['err1'])
            ws.save('completedTaskHistory', ['done1'])
            ws.commit()
            assert len(calls) == 1
        finally:
            os.unlink(path)

    def test_direct_produces_multiple_file_writes(self):
        """Direct saves: 3 keys → 3 file writes (baseline comparison)."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            calls = _countSaveFileCallsOnStorage(storage)
            storage.save('pendingTasks', ['task1'])
            storage.save('failedTaskHistory', ['err1'])
            storage.save('completedTaskHistory', ['done1'])
            assert len(calls) == 3
        finally:
            os.unlink(path)

    def test_orchestrated_data_identical_to_direct(self):
        """Data saved via UoW must match data saved directly."""
        path_uow = _makeTempJson()
        path_direct = _makeTempJson()
        try:
            data = {'pendingTasks': [{'name': 't1'}, {'name': 't2'}], 'failedTaskHistory': ['err1', 'err2'], 'completedTaskHistory': ['done1']}
            # UoW path
            s1 = JsonStorage(path_uow)
            ws = s1.beginWork()
            for k, v in data.items():
                ws.save(k, v)
            ws.commit()
            # Direct path
            s2 = JsonStorage(path_direct)
            for k, v in data.items():
                s2.save(k, v)
            # Both files must contain identical data
            with open(path_uow) as f1, open(path_direct) as f2:
                assert json.load(f1) == json.load(f2)
        finally:
            os.unlink(path_uow)
            os.unlink(path_direct)

    def test_no_write_when_unchanged(self):
        """UoW writes 0 times when all saved values equal existing values."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            storage.save('pendingTasks', [])
            storage.save('failedTaskHistory', [])
            storage.save('completedTaskHistory', [])
            calls = _countSaveFileCallsOnStorage(storage)
            ws = storage.beginWork()
            ws.save('pendingTasks', [])
            ws.save('failedTaskHistory', [])
            ws.save('completedTaskHistory', [])
            written = ws.commit()
            assert written == 0
            assert len(calls) == 0
        finally:
            os.unlink(path)

    def test_partial_change_writes_only_changed_keys(self):
        """Only changed keys are written to the batch."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            storage.save('pendingTasks', ['old_task'])
            storage.save('failedTaskHistory', [])
            storage.save('completedTaskHistory', ['done1'])
            ws = storage.beginWork()
            ws.save('pendingTasks', ['new_task'])  # changed
            ws.save('failedTaskHistory', [])  # unchanged
            ws.save('completedTaskHistory', ['done1'])  # unchanged
            written = ws.commit()
            assert written == 1
            assert storage.load('pendingTasks') == ['new_task']
            assert storage.load('failedTaskHistory') == []
            assert storage.load('completedTaskHistory') == ['done1']
        finally:
            os.unlink(path)

    def test_large_dataset_single_write(self):
        """Large dataset (100 tasks) still produces single file write."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            calls = _countSaveFileCallsOnStorage(storage)
            tasks = [{'name': f'task_{i}', 'id': i} for i in range(100)]
            ws = storage.beginWork()
            ws.save('pendingTasks', tasks)
            ws.save('failedTaskHistory', [f'err_{i}' for i in range(50)])
            ws.save('completedTaskHistory', [f'done_{i}' for i in range(200)])
            ws.commit()
            assert len(calls) == 1
            assert len(storage.load('pendingTasks')) == 100
            assert len(storage.load('failedTaskHistory')) == 50
            assert len(storage.load('completedTaskHistory')) == 200
        finally:
            os.unlink(path)

    def test_data_persists_across_instances(self):
        """Data committed via UoW is readable by a fresh storage instance."""
        path = _makeTempJson()
        try:
            s1 = JsonStorage(path)
            ws = s1.beginWork()
            ws.save('pendingTasks', [{'name': 'persistent_task'}])
            ws.save('failedTaskHistory', ['err'])
            ws.commit()
            s2 = JsonStorage(path)
            assert s2.load('pendingTasks') == [{'name': 'persistent_task'}]
            assert s2.load('failedTaskHistory') == ['err']
        finally:
            os.unlink(path)
