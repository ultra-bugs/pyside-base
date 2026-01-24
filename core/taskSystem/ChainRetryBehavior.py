"""
ChainRetryBehavior Enum

Defines retry behaviors for TaskChain when a child task fails.
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
from enum import Enum, auto

from ..Logging import logger

# Initialize logger for TaskSystem
logger = logger.bind(component='TaskSystem')


class ChainRetryBehavior(Enum):
    """
    Enumeration of retry behaviors for TaskChain when a child task fails.

    These behaviors determine how the chain should proceed when a child task
    fails after exhausting its own retry attempts.
    """

    STOP_CHAIN = auto()
    """
    Stop the entire chain immediately when a child task fails.
    This is the default behavior if no retry behavior is configured.
    """

    SKIP_TASK = auto()
    """
    Skip the failed task and continue with the next task in the chain.
    Useful when some tasks are optional or can be skipped on failure.
    """

    RETRY_TASK = auto()
    """
    Retry only the failed task (this is handled at the task level,
    but can be used for clarity in configuration).
    Note: Task-level retry is already handled by _executeSubTaskWithRetry.
    This behavior is essentially the same as STOP_CHAIN after task retries are exhausted.
    """

    RETRY_CHAIN = auto()
    """
    Retry the entire chain from the beginning.
    Useful when the chain must complete as a whole unit.
    """
