"""
Error handling tests for WorkingSet failure scenarios.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.taskSystem.storage.BaseStorage import BaseStorage


class BrokenStorage(BaseStorage):
    """Storage that raises on saveBatch."""

    def __init__(self, fail_on_batch=False):
        self.data = {}
        self.fail_on_batch = fail_on_batch

    def load(self, key, default=None):
        return self.data.get(key, default)

    def save(self, key, value):
        self.data[key] = value

    def saveBatch(self, items):
        if self.fail_on_batch:
            raise OSError('disk full')
        self.data.update(items)

    def clear(self, key):
        self.data.pop(key, None)


class TestWorkingSetErrorHandling:
    def test_commit_raises_when_savebatch_fails(self):
        """commit() propagates exceptions from saveBatch."""
        storage = BrokenStorage(fail_on_batch=True)
        ws = storage.beginWork()
        ws.save('key', 'value')
        with pytest.raises(OSError, match='disk full'):
            ws.commit()

    def test_dirty_state_preserved_after_failed_commit(self):
        """After a failed commit, pending changes are NOT cleared."""
        storage = BrokenStorage(fail_on_batch=True)
        ws = storage.beginWork()
        ws.save('key', 'value')
        try:
            ws.commit()
        except OSError:
            pass
        # _dirty and _pending should still contain the unsaved change
        assert ws.isDirty
        assert ws._pending.get('key') == 'value'

    def test_successful_commit_after_failure(self):
        """After fixing storage, retry commit succeeds."""
        storage = BrokenStorage(fail_on_batch=True)
        ws = storage.beginWork()
        ws.save('key', 'value')
        try:
            ws.commit()
        except OSError:
            pass
        # Fix storage and retry
        storage.fail_on_batch = False
        written = ws.commit()
        assert written == 1
        assert storage.load('key') == 'value'
        assert not ws.isDirty

    def test_empty_commit_never_calls_savebatch(self):
        """commit() with no dirty keys never calls saveBatch (even if broken)."""
        storage = BrokenStorage(fail_on_batch=True)
        ws = storage.beginWork()
        # Should not raise even though saveBatch would fail
        written = ws.commit()
        assert written == 0

    def test_save_with_none_key_still_marks_dirty(self):
        """Saving None as a value for a new key marks the WorkingSet dirty."""
        storage = BrokenStorage()
        ws = storage.beginWork()
        ws.save('nullable_key', None)
        assert ws.isDirty

    def test_save_same_none_value_does_not_mark_dirty(self):
        """Saving None when existing value is already None skips dirty mark."""
        storage = BrokenStorage()
        storage.data['nullable_key'] = None
        ws = storage.beginWork()
        ws.save('nullable_key', None)
        assert not ws.isDirty

    def test_overwrite_with_empty_collection_marks_dirty(self):
        """Replacing a non-empty list with [] marks dirty."""
        storage = BrokenStorage()
        storage.data['tasks'] = ['task1']
        ws = storage.beginWork()
        ws.save('tasks', [])
        assert ws.isDirty

    def test_commit_clears_after_success_not_after_failure(self):
        """Dirty is cleared only on success, not on exception."""
        storage = BrokenStorage(fail_on_batch=True)
        ws = storage.beginWork()
        ws.save('k', 'v')
        try:
            ws.commit()
        except OSError:
            pass
        assert ws.isDirty  # still dirty
        storage.fail_on_batch = False
        ws.commit()
        assert not ws.isDirty  # now clean

    def test_multiple_saves_to_same_key_last_value_wins(self):
        """Multiple saves to the same key: the last value is committed."""
        storage = BrokenStorage()
        ws = storage.beginWork()
        ws.save('key', 'first')
        ws.save('key', 'second')
        ws.save('key', 'third')
        written = ws.commit()
        assert written == 1
        assert storage.load('key') == 'third'

    def test_begin_work_creates_independent_working_sets(self):
        """Two WorkingSets from the same storage are independent."""
        storage = BrokenStorage()
        storage.data['shared'] = 'original'
        ws1 = storage.beginWork()
        ws2 = storage.beginWork()
        ws1.save('shared', 'from_ws1')
        ws2.save('shared', 'from_ws2')
        assert ws1.isDirty
        assert ws2.isDirty
        ws1.commit()  # writes 'from_ws1'
        assert storage.load('shared') == 'from_ws1'
        # ws2 still has its own pending change
        ws2.commit()  # writes 'from_ws2'
        assert storage.load('shared') == 'from_ws2'
