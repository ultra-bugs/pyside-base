"""
Tests for TaskStatus enum.
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
#              * -  Copyright © 2025 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *
from core.taskSystem.TaskStatus import TaskStatus


def test_task_status_values():
    """Test that all expected statuses exist."""
    assert TaskStatus.PENDING
    assert TaskStatus.RUNNING
    assert TaskStatus.COMPLETED
    assert TaskStatus.FAILED
    assert TaskStatus.CANCELLED
    assert TaskStatus.PAUSED
    assert TaskStatus.RETRYING


def test_task_status_uniqueness():
    """Test that all statuses have unique values."""
    statuses = list(TaskStatus)
    values = [s.value for s in statuses]
    assert len(values) == len(set(values)), 'Status values must be unique'


def test_task_status_names():
    """Test that status names match expectations."""
    assert TaskStatus.PENDING.name == 'PENDING'
    assert TaskStatus.RUNNING.name == 'RUNNING'
    assert TaskStatus.COMPLETED.name == 'COMPLETED'
    assert TaskStatus.FAILED.name == 'FAILED'
    assert TaskStatus.CANCELLED.name == 'CANCELLED'
    assert TaskStatus.PAUSED.name == 'PAUSED'
    assert TaskStatus.RETRYING.name == 'RETRYING'
