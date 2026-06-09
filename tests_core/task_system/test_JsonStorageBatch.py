"""
Unit tests for JsonStorage.saveBatch optimization.
Tests batch update behavior and file I/O optimization.
"""

import pytest
import tempfile
import os
import json
import threading
import time
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.taskSystem.storage.JsonStorage import JsonStorage


class TestJsonStorageBatch:
    """Test JsonStorage.saveBatch method functionality."""

    def test_batch_update_multiple_items(self):
        """Test batch update with multiple items."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        try:
            storage = JsonStorage(temp_file)
            # Batch save multiple items
            items = {'key1': 'value1', 'key2': 'value2', 'key3': {'nested': 'data'}}
            storage.saveBatch(items)
            # Verify all items were saved
            assert storage.load('key1') == 'value1'
            assert storage.load('key2') == 'value2'
            assert storage.load('key3') == {'nested': 'data'}
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_batch_vs_individual_saves_file_operations(self):
        """Test that saveBatch results in fewer file operations than individual saves."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        try:
            storage = JsonStorage(temp_file)
            # Mock _save_file to count calls
            original_save_file = storage._save_file
            save_file_calls = []

            def mock_save_file():
                save_file_calls.append(1)
                return original_save_file()

            storage._save_file = mock_save_file
            # Test batch save
            items = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
            storage.saveBatch(items)
            batch_calls = len(save_file_calls)
            # Reset counter
            save_file_calls.clear()
            # Test individual saves
            for key, value in items.items():
                storage.save(f'individual_{key}', value)
            individual_calls = len(save_file_calls)
            # Batch should result in fewer file operations
            assert batch_calls == 1
            assert individual_calls == 3
            assert batch_calls < individual_calls
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_batch_thread_safety(self):
        """Test thread safety with concurrent saveBatch calls."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        try:
            storage = JsonStorage(temp_file)
            results = []
            errors = []

            def batch_save_worker(thread_id):
                try:
                    items = {f'thread_{thread_id}_key1': f'value1_{thread_id}', f'thread_{thread_id}_key2': f'value2_{thread_id}'}
                    storage.saveBatch(items)
                    results.append(thread_id)
                except Exception as e:
                    errors.append((thread_id, str(e)))

            # Start multiple threads
            threads = []
            for i in range(5):
                t = threading.Thread(target=batch_save_worker, args=(i,))
                threads.append(t)
                t.start()
            # Wait for all threads
            for t in threads:
                t.join()
            # Verify no errors and all data saved
            assert len(errors) == 0, f'Errors occurred: {errors}'
            assert len(results) == 5
            # Verify all data was saved correctly
            for thread_id in range(5):
                assert storage.load(f'thread_{thread_id}_key1') == f'value1_{thread_id}'
                assert storage.load(f'thread_{thread_id}_key2') == f'value2_{thread_id}'
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_batch_with_working_set_integration(self):
        """Test integration between WorkingSet.commit() and JsonStorage.saveBatch()."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        try:
            storage = JsonStorage(temp_file)
            # Use WorkingSet
            ws = storage.beginWork()
            ws.save('key1', 'value1')
            ws.save('key2', 'value2')
            # Commit should call saveBatch
            count = ws.commit()
            # Verify results
            assert count == 2
            assert storage.load('key1') == 'value1'
            assert storage.load('key2') == 'value2'
            assert not ws.isDirty
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_batch_empty_items(self):
        """Test saveBatch with empty items dictionary."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        try:
            storage = JsonStorage(temp_file)
            # Test empty batch
            storage.saveBatch({})
            # Should not cause errors and file should still be valid
            assert storage.load('nonexistent') is None
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_batch_overwrites_existing_keys(self):
        """Test that saveBatch properly overwrites existing keys."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        try:
            storage = JsonStorage(temp_file)
            # Set initial values
            storage.save('key1', 'original1')
            storage.save('key2', 'original2')
            # Batch update with some overlapping keys
            items = {
                'key1': 'updated1',  # Overwrite
                'key3': 'new3',  # New key
            }
            storage.saveBatch(items)
            # Verify updates
            assert storage.load('key1') == 'updated1'  # Overwritten
            assert storage.load('key2') == 'original2'  # Unchanged
            assert storage.load('key3') == 'new3'  # New
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_batch_file_persistence(self):
        """Test that saveBatch properly persists data to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        try:
            # Save data with one storage instance
            storage1 = JsonStorage(temp_file)
            items = {'persistent_key': 'persistent_value'}
            storage1.saveBatch(items)
            # Load data with new storage instance
            storage2 = JsonStorage(temp_file)
            assert storage2.load('persistent_key') == 'persistent_value'
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
