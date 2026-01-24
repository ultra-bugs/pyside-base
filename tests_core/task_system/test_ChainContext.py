"""
Tests for ChainContext class.
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
import json
import threading
import pytest

from core.taskSystem.ChainContext import ChainContext


def test_chain_context_initialization():
    """Test ChainContext initialization."""
    chain_uuid = 'test-chain-123'
    context = ChainContext(chainUuid=chain_uuid)
    assert context._chainUuid == chain_uuid
    assert isinstance(context._data, dict)
    assert len(context._data) == 0


def test_chain_context_initialization_with_data():
    """Test ChainContext initialization with initial data."""
    chain_uuid = 'test-chain-123'
    initial_data = {'key1': 'value1', 'key2': 42}
    context = ChainContext(chainUuid=chain_uuid, initialData=initial_data)
    assert context._chainUuid == chain_uuid
    assert context.get('key1') == 'value1'
    assert context.get('key2') == 42


def test_chain_context_get():
    """Test ChainContext get method."""
    context = ChainContext(chainUuid='test-chain-123')
    # Test getting non-existent key with default
    assert context.get('nonexistent') is None
    assert context.get('nonexistent', 'default') == 'default'
    # Test setting and getting
    context.set('key1', 'value1')
    assert context.get('key1') == 'value1'


def test_chain_context_set():
    """Test ChainContext set method."""
    context = ChainContext(chainUuid='test-chain-123')
    context.set('string_key', 'string_value')
    context.set('int_key', 42)
    context.set('float_key', 3.14)
    context.set('bool_key', True)
    context.set('list_key', [1, 2, 3])
    context.set('dict_key', {'nested': 'value'})
    assert context.get('string_key') == 'string_value'
    assert context.get('int_key') == 42
    assert context.get('float_key') == 3.14
    assert context.get('bool_key') is True
    assert context.get('list_key') == [1, 2, 3]
    assert context.get('dict_key') == {'nested': 'value'}


def test_chain_context_set_non_serializable():
    """Test ChainContext set method rejects non-JSON serializable values."""
    context = ChainContext(chainUuid='test-chain-123')
    # Test with non-serializable object (function)
    def non_serializable():
        pass
    with pytest.raises(TypeError, match='not JSON serializable'):
        context.set('func_key', non_serializable)
    # Test with non-serializable object (class instance without __dict__)
    class NonSerializable:
        def __init__(self):
            pass
    with pytest.raises(TypeError, match='not JSON serializable'):
        context.set('class_key', NonSerializable())


def test_chain_context_thread_safety():
    """Test ChainContext thread safety."""
    context = ChainContext(chainUuid='test-chain-123')
    results = []
    errors = []
    def set_value(i):
        try:
            context.set(f'key_{i}', f'value_{i}')
        except Exception as e:
            errors.append(e)
    def get_value(i):
        try:
            value = context.get(f'key_{i}')
            results.append((i, value))
        except Exception as e:
            errors.append(e)
    # Create multiple threads
    threads = []
    num_threads = 10
    num_operations = 100
    for i in range(num_threads):
        for j in range(num_operations):
            t = threading.Thread(target=set_value, args=(i * num_operations + j,))
            threads.append(t)
            t.start()
    # Wait for all threads to complete
    for t in threads:
        t.join()
    # Verify no errors occurred
    assert len(errors) == 0, f'Thread safety errors: {errors}'
    # Verify all values were set correctly
    for i in range(num_threads * num_operations):
        assert context.get(f'key_{i}') == f'value_{i}'


def test_chain_context_serialize():
    """Test ChainContext serialization."""
    chain_uuid = 'test-chain-123'
    context = ChainContext(chainUuid=chain_uuid)
    context.set('key1', 'value1')
    context.set('key2', 42)
    serialized = context.serialize()
    assert serialized['chainUuid'] == chain_uuid
    assert serialized['data']['key1'] == 'value1'
    assert serialized['data']['key2'] == 42
    assert isinstance(serialized, dict)
    # Verify it's JSON serializable
    json_str = json.dumps(serialized)
    assert json_str is not None


def test_chain_context_deserialize():
    """Test ChainContext deserialization."""
    chain_uuid = 'test-chain-123'
    data = {'chainUuid': chain_uuid, 'data': {'key1': 'value1', 'key2': 42, 'key3': [1, 2, 3]}}
    context = ChainContext.deserialize(data)
    assert context._chainUuid == chain_uuid
    assert context.get('key1') == 'value1'
    assert context.get('key2') == 42
    assert context.get('key3') == [1, 2, 3]


def test_chain_context_deserialize_missing_chain_uuid():
    """Test ChainContext deserialization with missing chainUuid."""
    data = {'data': {'key1': 'value1'}}
    with pytest.raises(ValueError, match='chainUuid is required'):
        ChainContext.deserialize(data)


def test_chain_context_serialize_deserialize_roundtrip():
    """Test ChainContext serialize/deserialize roundtrip."""
    chain_uuid = 'test-chain-123'
    context1 = ChainContext(chainUuid=chain_uuid)
    context1.set('key1', 'value1')
    context1.set('key2', 42)
    context1.set('key3', {'nested': 'value'})
    serialized = context1.serialize()
    context2 = ChainContext.deserialize(serialized)
    assert context2._chainUuid == context1._chainUuid
    assert context2.get('key1') == context1.get('key1')
    assert context2.get('key2') == context1.get('key2')
    assert context2.get('key3') == context1.get('key3')


def test_chain_context_clear():
    """Test ChainContext clear method."""
    context = ChainContext(chainUuid='test-chain-123')
    context.set('key1', 'value1')
    context.set('key2', 'value2')
    assert context.get('key1') == 'value1'
    assert context.get('key2') == 'value2'
    context.clear()
    assert context.get('key1') is None
    assert context.get('key2') is None
    assert len(context.keys()) == 0


def test_chain_context_keys():
    """Test ChainContext keys method."""
    context = ChainContext(chainUuid='test-chain-123')
    assert len(context.keys()) == 0
    context.set('key1', 'value1')
    context.set('key2', 'value2')
    context.set('key3', 'value3')
    keys = context.keys()
    assert len(keys) == 3
    assert 'key1' in keys
    assert 'key2' in keys
    assert 'key3' in keys


def test_chain_context_has():
    """Test ChainContext has method."""
    context = ChainContext(chainUuid='test-chain-123')
    assert not context.has('key1')
    context.set('key1', 'value1')
    assert context.has('key1')
    assert not context.has('nonexistent')


def test_chain_context_thread_safe_concurrent_reads_writes():
    """Test ChainContext with concurrent reads and writes."""
    context = ChainContext(chainUuid='test-chain-123')
    errors = []
    results = []
    def writer(thread_id, num_writes):
        for i in range(num_writes):
            try:
                context.set(f'key_{thread_id}_{i}', f'value_{thread_id}_{i}')
            except Exception as e:
                errors.append(('write', thread_id, i, str(e)))
    def reader(thread_id, num_reads):
        for i in range(num_reads):
            try:
                value = context.get(f'key_{thread_id}_{i}')
                results.append((thread_id, i, value))
            except Exception as e:
                errors.append(('read', thread_id, i, str(e)))
    # Create multiple writer threads
    writer_threads = []
    num_writer_threads = 5
    writes_per_thread = 50
    for i in range(num_writer_threads):
        t = threading.Thread(target=writer, args=(i, writes_per_thread))
        writer_threads.append(t)
        t.start()
    # Create multiple reader threads (reading after a delay)
    import time
    time.sleep(0.1)  # Let writers start
    reader_threads = []
    num_reader_threads = 5
    reads_per_thread = 50
    for i in range(num_reader_threads):
        t = threading.Thread(target=reader, args=(i, reads_per_thread))
        reader_threads.append(t)
        t.start()
    # Wait for all threads
    for t in writer_threads:
        t.join()
    for t in reader_threads:
        t.join()
    # Verify no errors
    assert len(errors) == 0, f'Concurrent operation errors: {errors}'
