"""
Tests for Bulk Action on Task Management.
"""
#              M""""""""`M            dP
#              Mmmmmm   .M            88
#              MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#              MMP  .MMMMM  88    88  88888"    88'  `88
#              M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#              M         M  `88888P'  dP   `YP  `88888P'
#              MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#              * * * * * * * * * * * * * * * * * * * * *
#              * -    - -   F.R.E.E.M.I.N.D   - -    - *
#              * -  Copyright © 2026 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *
from typing import Dict, Any, List, Optional
import pytest
from core.taskSystem.TaskManagerService import TaskManagerService
from core.taskSystem.TaskTracker import TaskTracker
from core.taskSystem.TaskChain import TaskChain
from core.taskSystem.AbstractTask import AbstractTask
from tests_core.task_system.test_AbstractTask import ConcreteTask


def test_task_tagging_basics():
    """Test basic tagging functionality in AbstractTask."""
    task = ConcreteTask(name='Tags Test')
    # Default tag (class name)
    assert task.hasTag('ConcreteTask')
    # Add tag
    task.addTag('TagA')
    assert task.hasTag('TagA')
    assert 'TagA' in task.tags
    # Remove tag
    task.removeTag('TagA')
    assert not task.hasTag('TagA')
    # Init with tags
    task2 = ConcreteTask(name='Init Tags', tags={'TagB', 'TagC'})
    assert task2.hasTag('TagB')
    assert task2.hasTag('TagC')
    assert task2.hasTag('ConcreteTask')


def test_task_chain_auto_tagging(mock_publisher, mock_config):
    """Test auto-tagging in TaskChain."""
    t1 = ConcreteTask(name='T1')
    t2 = ConcreteTask(name='T2')
    chain = TaskChain(name='Chain1', tasks=[t1, t2])
    # Check chain UUID
    chain_uuid = chain.uuid
    # Check children tags
    assert t1.hasTag('_ChainedChild')
    assert t1.hasTag(f'Parent_{chain_uuid}')
    assert t2.hasTag('_ChainedChild')
    assert t2.hasTag(f'Parent_{chain_uuid}')


def test_task_tracker_indexing(mock_publisher, mock_config):
    """Test TaskTracker efficient indexing."""
    mock_config.get.return_value = 3
    mock_config.load.return_value = []
    service = TaskManagerService(mock_publisher, mock_config, storage=mock_config)
    tracker = service._taskTracker
    t1 = ConcreteTask(name='T1', tags={'GroupA'})
    t2 = ConcreteTask(name='T2', tags={'GroupA', 'GroupB'})
    t3 = ConcreteTask(name='T3', tags={'GroupB'})
    service.addTask(t1)
    service.addTask(t2)
    service.addTask(t3)
    # Verify indexing
    uuids_a = tracker.getUuidsByTag('GroupA')
    assert t1.uuid in uuids_a
    assert t2.uuid in uuids_a
    assert t3.uuid not in uuids_a
    uuids_b = tracker.getUuidsByTag('GroupB')
    assert t1.uuid not in uuids_b
    assert t2.uuid in uuids_b
    assert t3.uuid in uuids_b
    # Verify removal
    tracker.removeTask(t1.uuid)
    uuids_a_after = tracker.getUuidsByTag('GroupA')
    assert t1.uuid not in uuids_a_after
    assert t2.uuid in uuids_a_after


def test_bulk_actions(mock_publisher, mock_config):
    """Test bulk stop/pause operations."""
    mock_config.get.return_value = 3
    mock_config.load.return_value = []
    service = TaskManagerService(mock_publisher, mock_config, storage=mock_config)
    # Create independent tasks
    t1 = ConcreteTask(name='Net1', tags={'Network'})
    t2 = ConcreteTask(name='Net2', tags={'Network'})
    t3 = ConcreteTask(name='Disk1', tags={'Disk'})
    # Create chained tasks
    c1 = ConcreteTask(name='ChainChild1', tags={'Network'})  # Has Network tag
    chain = TaskChain(name='Chain', tasks=[c1])
    service.addTask(t1)
    service.addTask(t2)
    service.addTask(t3)
    service.addTask(chain)
    # Bulk Stop 'Network'
    # Default: exclude chained children
    service.stopTasksByTag('Network')
    assert t1.isStopped()
    assert t2.isStopped()
    assert not t3.isStopped()
    assert not c1.isStopped()  # Should NOT be stopped (default behavior)
    # Now stop with includeChainedChildren=True
    service.stopTasksByTag('Network', includeChainedChildren=True)
    assert c1.isStopped()
