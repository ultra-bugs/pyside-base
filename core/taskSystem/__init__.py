"""
TaskSystem Module

This module provides a comprehensive task management system with:
- Task queuing and execution
- Task scheduling
- Task tracking and monitoring
- Retry logic and failure handling
- Qt signals integration for UI updates

All components follow Qt naming conventions (PascalCase for files/classes, camelCase for methods/variables).
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
from ..Logging import logger

# Initialize logger for TaskSystem
logger = logger.bind(component='TaskSystem')

# Export main components (will be uncommented as they are implemented)
from .TaskStatus import TaskStatus
from .Exceptions import TaskSystemException, TaskNotFoundException, InvalidTaskStateException, TaskCancellationException
from .AbstractTask import AbstractTask
from .TaskTracker import TaskTracker
from .TaskQueue import TaskQueue
from .TaskScheduler import TaskScheduler
from .TaskManagerService import TaskManagerService
from .TaskChain import TaskChain
from .ChainContext import ChainContext
from .ChainRetryBehavior import ChainRetryBehavior

__all__ = [
    'TaskStatus',
    'TaskSystemException',
    'TaskNotFoundException',
    'InvalidTaskStateException',
    'TaskCancellationException',
    'AbstractTask',
    'TaskTracker',
    'TaskQueue',
    'TaskScheduler',
    'TaskManagerService',
    'TaskChain',
    'ChainContext',
    'ChainRetryBehavior',
]
