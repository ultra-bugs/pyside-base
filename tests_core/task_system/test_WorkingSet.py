"""
Unit tests for WorkingSet Unit of Work implementation.
Tests dirty detection, save behavior, and commit operations.
"""

import pytest
from unittest.mock import Mock, MagicMock
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.taskSystem.storage.BaseStorage import BaseStorage
from core.taskSystem.storage.JsonStorage import JsonStorage


class MockStorage(BaseStorage):
    """Mock storage implementation for testing WorkingSet."""

    def __init__(self):
        self.data = {}
        self.save_batch_calls = []

    def load(self, key: str, default=None):
        return self.data.get(key, default)

    def save(self, key: str, value):
        self.data[key] = value

    def saveBatch(self, items: dict):
        self.save_batch_calls.append(items.copy())
        self.data.update(items)

    def clear(self, key: str):
        if key in self.data:
            del self.data[key]


class TestWorkingSet:
    """Test WorkingSet dirty detection and commit behavior."""

    def test_working_set_creation(self):
        """Test WorkingSet can be created from storage."""
        storage = MockStorage()
        ws = storage.beginWork()
        assert ws is not None
        assert not ws.isDirty

    def test_dirty_detection_new_value(self):
        """Test dirty detection marks dirty for new values."""
        storage = MockStorage()
        ws = storage.beginWork()
        # Initially not dirty
        assert not ws.isDirty
        # Save new value - should be dirty
        ws.save('test_key', 'test_value')
        assert ws.isDirty

    def test_dirty_detection_same_value(self):
        """Test dirty detection doesn't mark dirty for same values."""
        storage = MockStorage()
        # Pre-populate storage
        storage.data['test_key'] = 'existing_value'
        ws = storage.beginWork()
        # Save same value - should not be dirty
        ws.save('test_key', 'existing_value')
        assert not ws.isDirty

    def test_dirty_detection_different_value(self):
        """Test dirty detection marks dirty for different values."""
        storage = MockStorage()
        # Pre-populate storage
        storage.data['test_key'] = 'existing_value'
        ws = storage.beginWork()
        # Save different value - should be dirty
        ws.save('test_key', 'new_value')
        assert ws.isDirty

    def test_dirty_detection_multiple_saves_same_value(self):
        """Test saving same value multiple times only marks dirty once."""
        storage = MockStorage()
        ws = storage.beginWork()
        # First save - dirty
        ws.save('test_key', 'test_value')
        assert ws.isDirty
        # Save same value again - still dirty (not additional dirty)
        ws.save('test_key', 'test_value')
        assert ws.isDirty
        # Commit and verify only one item was batched
        count = ws.commit()
        assert count == 1
        assert len(storage.save_batch_calls) == 1
        assert storage.save_batch_calls[0] == {'test_key': 'test_value'}

    def test_commit_with_changes(self):
        """Test commit behavior when there are changes."""
        storage = MockStorage()
        ws = storage.beginWork()
        # Add some changes
        ws.save('key1', 'value1')
        ws.save('key2', 'value2')
        # Commit
        count = ws.commit()
        # Verify results
        assert count == 2
        assert len(storage.save_batch_calls) == 1
        assert storage.save_batch_calls[0] == {'key1': 'value1', 'key2': 'value2'}
        assert not ws.isDirty  # Should be clean after commit

    def test_commit_without_changes(self):
        """Test commit behavior when there are no changes."""
        storage = MockStorage()
        ws = storage.beginWork()
        # Commit without changes
        count = ws.commit()
        # Verify no operations
        assert count == 0
        assert len(storage.save_batch_calls) == 0
        assert not ws.isDirty

    def test_commit_clears_dirty_state(self):
        """Test that commit clears dirty state and pending changes."""
        storage = MockStorage()
        ws = storage.beginWork()
        # Make changes
        ws.save('key1', 'value1')
        assert ws.isDirty
        # Commit
        ws.commit()
        assert not ws.isDirty
        # Verify subsequent commit is no-op
        count2 = ws.commit()
        assert count2 == 0

    def test_different_data_types(self):
        """Test WorkingSet handles different data types correctly."""
        storage = MockStorage()
        ws = storage.beginWork()
        # Test various data types
        ws.save('string_key', 'string_value')
        ws.save('int_key', 42)
        ws.save('list_key', [1, 2, 3])
        ws.save('dict_key', {'nested': 'value'})
        ws.save('none_key', None)
        count = ws.commit()
        assert count == 5
        # Verify data was saved correctly
        expected = {'string_key': 'string_value', 'int_key': 42, 'list_key': [1, 2, 3], 'dict_key': {'nested': 'value'}, 'none_key': None}
        assert storage.save_batch_calls[0] == expected

    def test_with_json_storage(self):
        """Test WorkingSet integration with actual JsonStorage."""
        import tempfile
        import os

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        try:
            # Use JsonStorage with temp file
            storage = JsonStorage(temp_file)
            ws = storage.beginWork()
            # Test operations
            ws.save('test_key', 'test_value')
            assert ws.isDirty
            count = ws.commit()
            assert count == 1
            assert not ws.isDirty
            # Verify data persisted
            assert storage.load('test_key') == 'test_value'
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
