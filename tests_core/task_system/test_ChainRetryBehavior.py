"""
Tests for ChainRetryBehavior enum.
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

from core.taskSystem.ChainRetryBehavior import ChainRetryBehavior


def test_chain_retry_behavior_enum_exists():
    """Test that ChainRetryBehavior enum exists and has all expected values."""
    assert ChainRetryBehavior is not None
    assert isinstance(ChainRetryBehavior.STOP_CHAIN, ChainRetryBehavior)
    assert isinstance(ChainRetryBehavior.SKIP_TASK, ChainRetryBehavior)
    assert isinstance(ChainRetryBehavior.RETRY_TASK, ChainRetryBehavior)
    assert isinstance(ChainRetryBehavior.RETRY_CHAIN, ChainRetryBehavior)


def test_chain_retry_behavior_all_values():
    """Test that all expected ChainRetryBehavior values are defined."""
    expected_values = {'STOP_CHAIN', 'SKIP_TASK', 'RETRY_TASK', 'RETRY_CHAIN'}
    actual_values = {behavior.name for behavior in ChainRetryBehavior}
    assert actual_values == expected_values, f'Expected {expected_values}, got {actual_values}'


def test_chain_retry_behavior_stop_chain():
    """Test STOP_CHAIN behavior value."""
    assert ChainRetryBehavior.STOP_CHAIN.name == 'STOP_CHAIN'
    assert ChainRetryBehavior.STOP_CHAIN.value is not None


def test_chain_retry_behavior_skip_task():
    """Test SKIP_TASK behavior value."""
    assert ChainRetryBehavior.SKIP_TASK.name == 'SKIP_TASK'
    assert ChainRetryBehavior.SKIP_TASK.value is not None


def test_chain_retry_behavior_retry_task():
    """Test RETRY_TASK behavior value."""
    assert ChainRetryBehavior.RETRY_TASK.name == 'RETRY_TASK'
    assert ChainRetryBehavior.RETRY_TASK.value is not None


def test_chain_retry_behavior_retry_chain():
    """Test RETRY_CHAIN behavior value."""
    assert ChainRetryBehavior.RETRY_CHAIN.name == 'RETRY_CHAIN'
    assert ChainRetryBehavior.RETRY_CHAIN.value is not None


def test_chain_retry_behavior_uniqueness():
    """Test that all ChainRetryBehavior values are unique."""
    values = [behavior.value for behavior in ChainRetryBehavior]
    assert len(values) == len(set(values)), 'All enum values must be unique'


def test_chain_retry_behavior_access_by_name():
    """Test accessing ChainRetryBehavior by name."""
    assert ChainRetryBehavior['STOP_CHAIN'] == ChainRetryBehavior.STOP_CHAIN
    assert ChainRetryBehavior['SKIP_TASK'] == ChainRetryBehavior.SKIP_TASK
    assert ChainRetryBehavior['RETRY_TASK'] == ChainRetryBehavior.RETRY_TASK
    assert ChainRetryBehavior['RETRY_CHAIN'] == ChainRetryBehavior.RETRY_CHAIN


def test_chain_retry_behavior_in_dict():
    """Test using ChainRetryBehavior in dictionaries."""
    retry_map = {'TaskA': ChainRetryBehavior.STOP_CHAIN, 'TaskB': ChainRetryBehavior.SKIP_TASK, 'TaskC': ChainRetryBehavior.RETRY_CHAIN}
    assert retry_map['TaskA'] == ChainRetryBehavior.STOP_CHAIN
    assert retry_map['TaskB'] == ChainRetryBehavior.SKIP_TASK
    assert retry_map['TaskC'] == ChainRetryBehavior.RETRY_CHAIN


def test_chain_retry_behavior_comparison():
    """Test comparing ChainRetryBehavior values."""
    assert ChainRetryBehavior.STOP_CHAIN == ChainRetryBehavior.STOP_CHAIN
    assert ChainRetryBehavior.STOP_CHAIN != ChainRetryBehavior.SKIP_TASK
    assert ChainRetryBehavior.SKIP_TASK != ChainRetryBehavior.RETRY_TASK


def test_chain_retry_behavior_string_representation():
    """Test string representation of ChainRetryBehavior."""
    assert str(ChainRetryBehavior.STOP_CHAIN) == 'ChainRetryBehavior.STOP_CHAIN'
    # repr() includes value: <ChainRetryBehavior.SKIP_TASK: 2>
    assert repr(ChainRetryBehavior.SKIP_TASK).startswith('<ChainRetryBehavior.SKIP_TASK:')


def test_chain_retry_behavior_name_property():
    """Test name property of ChainRetryBehavior."""
    assert ChainRetryBehavior.STOP_CHAIN.name == 'STOP_CHAIN'
    assert ChainRetryBehavior.SKIP_TASK.name == 'SKIP_TASK'
    assert ChainRetryBehavior.RETRY_TASK.name == 'RETRY_TASK'
    assert ChainRetryBehavior.RETRY_CHAIN.name == 'RETRY_CHAIN'
