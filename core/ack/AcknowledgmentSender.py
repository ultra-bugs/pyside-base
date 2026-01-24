"""
AcknowledgmentSender - Base class for components sending acknowledgments.

This abstract base class provides generic methods for:
- Sending successful acknowledgments
- Sending error acknowledgments
- Hooks for post-send actions

Subclasses typically:
- Process events from Receiver
- Perform operations (API calls, DB writes, etc.)
- Send acknowledgment back to Tracker
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

from abc import ABC
from typing import Any
from core.Logging import logger
from .AcknowledgmentTracker import AcknowledgmentTracker


class AcknowledgmentSender(ABC):
    """
    Base class for components that send acknowledgments.

    Generic and reusable - no assumptions about:
    - What operations are performed
    - How sender receives events
    - What the sender does after sending ack
    """

    def __init__(self, ackTracker: AcknowledgmentTracker):
        """
        Initialize sender with shared tracker.
        Args:
            ack_tracker: Shared AcknowledgmentTracker instance
                        (must be same instance used by Receiver)
        """
        self._ack_tracker = ackTracker

    def sendAcknowledgment(self, ackId: str, result: Any = None) -> None:
        """
        Send successful acknowledgment.
        Args:
            ack_id: Acknowledgment ID from event
            result: Result data to send back to receiver
        Note: Safe to call even if ack_id not registered (logs warning)
        """
        try:
            self._ack_tracker.acknowledge(ackId, result)
            self._on_ack_sent(ackId, result)
            logger.debug(f'Sent ack: {ackId}')
        except Exception as e:
            logger.error(f'Error sending ack {ackId}: {e}', excInfo=True)

    def sendErrorAcknowledgment(self, ackId: str, error: Exception) -> None:
        """
        Send error acknowledgment.
        Args:
            ack_id: Acknowledgment ID from event
            error: Error that occurred during processing
        Note: Safe to call even if ack_id not registered (logs warning)
        """
        try:
            self._ack_tracker.acknowledgeError(ackId, error)
            self._on_error_ack_sent(ackId, error)
            logger.debug(f'Sent error ack: {ackId}')
        except Exception as e:
            logger.error(f'Error sending error ack {ackId}: {e}', excInfo=True)

    def _on_ack_sent(self, ackId: str, result: Any) -> None:
        """
        Hook called after successful acknowledgment sent.
        Subclass can override for custom actions like:
        - Logging metrics
        - Updating UI
        - Triggering next action
        Args:
            ack_id: Acknowledgment ID
            result: Result data that was sent
        """
        pass

    def _on_error_ack_sent(self, ackId: str, error: Exception) -> None:
        """
        Hook called after error acknowledgment sent.
        Subclass can override for custom error actions like:
        - Logging to monitoring system
        - Sending alerts
        - Retry logic
        Args:
            ack_id: Acknowledgment ID
            error: Error that was sent
        """
        pass
