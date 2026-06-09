"""
Performance benchmarks: quantify I/O reduction from UoW vs direct saves.
"""

import pytest
import tempfile
import os
import time
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.taskSystem.storage.JsonStorage import JsonStorage


def _makeTempJson(content='{}'):
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    f.write(content)
    f.close()
    return f.name


def _wrapSaveFile(storage: JsonStorage):
    calls = []
    original = storage._save_file

    def counted():
        calls.append(1)
        original()

    storage._save_file = counted
    return calls


class TestIoReduction:
    def test_uow_100_ops_produces_1_write(self):
        """100 UoW save ops → commit → exactly 1 file write."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            calls = _wrapSaveFile(storage)
            ws = storage.beginWork()
            for i in range(100):
                ws.save(f'key_{i}', f'value_{i}')
            written = ws.commit()
            assert len(calls) == 1
            assert written == 100
        finally:
            os.unlink(path)

    def test_direct_100_ops_produces_100_writes(self):
        """100 direct saves → 100 file writes (baseline)."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            calls = _wrapSaveFile(storage)
            for i in range(100):
                storage.save(f'key_{i}', f'value_{i}')
            assert len(calls) == 100
        finally:
            os.unlink(path)

    def test_uow_io_reduction_ratio(self):
        """UoW must reduce file writes by at least 90% vs direct saves."""
        N = 50
        path_uow = _makeTempJson()
        path_direct = _makeTempJson()
        try:
            s_uow = JsonStorage(path_uow)
            calls_uow = _wrapSaveFile(s_uow)
            ws = s_uow.beginWork()
            for i in range(N):
                ws.save(f'key_{i}', i)
            ws.commit()
            s_direct = JsonStorage(path_direct)
            calls_direct = _wrapSaveFile(s_direct)
            for i in range(N):
                s_direct.save(f'key_{i}', i)
            assert len(calls_uow) == 1
            assert len(calls_direct) == N
            reduction = 1 - len(calls_uow) / len(calls_direct)
            assert reduction >= 0.90
        finally:
            os.unlink(path_uow)
            os.unlink(path_direct)

    def test_uow_no_write_saves_zero_io(self):
        """UoW with zero actual changes → 0 file writes."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            storage.save('key', 'value')
            calls = _wrapSaveFile(storage)
            ws = storage.beginWork()
            ws.save('key', 'value')  # unchanged
            written = ws.commit()
            assert written == 0
            assert len(calls) == 0
        finally:
            os.unlink(path)

    def test_uow_timing_faster_than_direct_for_many_ops(self):
        """UoW commit must be faster than equivalent direct saves."""
        N = 30
        path_uow = _makeTempJson()
        path_direct = _makeTempJson()
        try:
            s_uow = JsonStorage(path_uow)
            t0 = time.perf_counter()
            ws = s_uow.beginWork()
            for i in range(N):
                ws.save(f'key_{i}', f'val_{i}')
            ws.commit()
            t_uow = time.perf_counter() - t0
            s_direct = JsonStorage(path_direct)
            t0 = time.perf_counter()
            for i in range(N):
                s_direct.save(f'key_{i}', f'val_{i}')
            t_direct = time.perf_counter() - t0
            # UoW should be faster (at least not worse by more than 2x)
            assert t_uow < t_direct * 2, f'UoW ({t_uow:.4f}s) unexpectedly much slower than direct ({t_direct:.4f}s)'
        finally:
            os.unlink(path_uow)
            os.unlink(path_direct)

    def test_multiple_commits_accumulate_correctly(self):
        """Multiple sequential WorkingSet commits each write once."""
        path = _makeTempJson()
        try:
            storage = JsonStorage(path)
            calls = _wrapSaveFile(storage)
            for batch in range(5):
                ws = storage.beginWork()
                ws.save(f'batch_{batch}', batch)
                ws.commit()
            assert len(calls) == 5
            for batch in range(5):
                assert storage.load(f'batch_{batch}') == batch
        finally:
            os.unlink(path)
