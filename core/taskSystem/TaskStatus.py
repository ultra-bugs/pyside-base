"""
TaskStatus Enum

Defines all possible states for a task in the TaskSystem.
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
from enum import Enum, auto

from ..Logging import logger

# Initialize logger for TaskSystem
logger = logger.bind(component='TaskSystem')


class TaskStatus(Enum):
    """
    Enumeration of all possible task states.

    States:
        PENDING: Task is waiting in the queue
        RUNNING: Task is currently executing
        COMPLETED: Task finished successfully
        FAILED: Task failed (may or may not retry)
        CANCELLED: Task was cancelled by user/system
        PAUSED: Task is temporarily paused
        RETRYING: Task is waiting to retry after failure
    """

    PENDING = auto()  # Đang chờ trong hàng đợi
    RUNNING = auto()  # Đang thực thi
    COMPLETED = auto()  # Hoàn thành thành công
    FAILED = auto()  # Thất bại (có thể thử lại hoặc không)
    CANCELLED = auto()  # Bị hủy bởi người dùng/hệ thống
    PAUSED = auto()  # Tạm dừng
    RETRYING = auto()  # Đang chờ thử lại
