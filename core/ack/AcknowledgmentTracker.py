"""
AcknowledgmentTracker - Core coordinator for ACK/NACK protocol.

This class manages pending acknowledgments and coordinates callbacks between
sender and receiver components.

Thread-Safety: Uses QMutex for all critical sections.
Timeout: Uses threading.Timer for each pending acknowledgment.
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

import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional
from PySide6.QtCore import QMutex, QMutexLocker
from core.Logging import logger


@dataclass
class PendingAck:
    """Data structure for a pending acknowledgment."""

    ackId: str
    successCallback: Callable[[str, Any], None]
    errorCallback: Optional[Callable[[str, Exception], None]]
    timeoutCallback: Optional[Callable[[str], None]]
    timeout: float
    registeredAt: float
    timer: Optional[threading.Timer] = None


class AcknowledgmentTracker:
    """
    Generic acknowledgment coordinator.

    Manages pending acknowledgments and triggers appropriate callbacks when:
    - Acknowledgment received (success)
    - Error acknowledgment received
    - Timeout expires

    Thread-safe for concurrent operations.
    """

    def __init__(self):
        self._pending: Dict[str, PendingAck] = {}
        self._lock = QMutex()

    def registerPending(
        self,
        ackId: str,
        successCallback: Callable[[str, Any], None],
        errorCallback: Optional[Callable[[str, Exception], None]] = None,
        timeoutCallback: Optional[Callable[[str], None]] = None,
        timeout: float = 30.0,
    ) -> None:
        """
        Register a pending acknowledgment.
        Args:
            ack_id: Unique acknowledgment ID
            success_callback: Called when acknowledgment received
            error_callback: Called when error acknowledgment received
            timeout_callback: Called when timeout expires
            timeout: Timeout in seconds
        Raises:
            ValueError: If ack_id already pending
        """
        locker = QMutexLocker(self._lock)
        if ackId in self._pending:
            raise ValueError(f'Acknowledgment {ackId} already pending')
        pendingAck = PendingAck(
            ackId=ackId, successCallback=successCallback, errorCallback=errorCallback, timeoutCallback=timeoutCallback, timeout=timeout, registeredAt=time.time()
        )
        if timeout > 0:
            timer = threading.Timer(timeout, self._handle_timeout, args=[ackId])
            timer.daemon = True
            pendingAck.timer = timer
            timer.start()
        self._pending[ackId] = pendingAck
        logger.debug(f'Registered pending ack: {ackId} (timeout: {timeout}s)')

    def acknowledge(self, ackId: str, result: Any = None) -> None:
        """
        Receive successful acknowledgment.
        Args:
            ack_id: Acknowledgment ID
            result: Result data from sender
        Note: Does nothing if ack_id not found (may have already timed out)
        """
        locker = QMutexLocker(self._lock)
        if ackId not in self._pending:
            logger.warning(f'Ack {ackId} not pending (may have timed out)')
            return
        pendingAck = self._pending.pop(ackId)
        if pendingAck.timer:
            pendingAck.timer.cancel()
        locker.unlock()
        try:
            elapsed = time.time() - pendingAck.registeredAt
            logger.debug(f'Ack received: {ackId} ({elapsed:.2f}s)')
            pendingAck.successCallback(ackId, result)
        except Exception as e:
            logger.error(f'Error in success callback for {ackId}: {e}', exc_info=True)

    def acknowledgeError(self, ackId: str, error: Exception) -> None:
        """
        Receive error acknowledgment.
        Args:
            ack_id: Acknowledgment ID
            error: Error from sender
        Note: Does nothing if ack_id not found (may have already timed out)
        """
        locker = QMutexLocker(self._lock)
        if ackId not in self._pending:
            logger.warning(f'Ack {ackId} not pending (may have timed out)')
            return
        pendingAck = self._pending.pop(ackId)
        if pendingAck.timer:
            pendingAck.timer.cancel()
        locker.unlock()
        try:
            elapsed = time.time() - pendingAck.registeredAt
            logger.debug(f'Ack error received: {ackId} ({elapsed:.2f}s)')
            if pendingAck.errorCallback:
                pendingAck.errorCallback(ackId, error)
            else:
                logger.error(f'Ack error for {ackId}: {error}')
        except Exception as e:
            logger.opt(exception=e).error(f'Error in error callback for {ackId}: {e}', exc_info=True)

    def isPending(self, ackId: str) -> bool:
        """
        Check if acknowledgment is still pending.
        Args:
            ack_id: Acknowledgment ID
        Returns:
            True if pending, False otherwise
        """
        locker = QMutexLocker(self._lock)
        return ackId in self._pending

    def pendingCount(self) -> int:
        """
        Get number of pending acknowledgments.
        Returns:
            Number of pending acks
        """
        locker = QMutexLocker(self._lock)
        return len(self._pending)

    def cleanupExpired(self) -> None:
        """
        Manually cleanup expired acknowledgments.
        Note: Normally not needed as Timer handles this automatically.
        Provided for testing and edge cases.
        """
        locker = QMutexLocker(self._lock)
        now = time.time()
        expired = []
        for ackId, pendingAck in self._pending.items():
            if now - pendingAck.registeredAt >= pendingAck.timeout:
                expired.append(ackId)
        for ackId in expired:
            pendingAck = self._pending.pop(ackId)
            if pendingAck.timer:
                pendingAck.timer.cancel()
            locker.unlock()
            try:
                logger.warning(f'Ack timeout (manual cleanup): {ackId}')
                if pendingAck.timeoutCallback:
                    pendingAck.timeoutCallback(ackId)
            except Exception as e:
                logger.error(f'Error in timeout callback for {ackId}: {e}', exc_info=True)
            locker.relock()

    def _handle_timeout(self, ackId: str) -> None:
        """
        Internal timeout handler (called by Timer).
        Args:
            ack_id: Acknowledgment ID that timed out
        """
        locker = QMutexLocker(self._lock)
        if ackId not in self._pending:
            return
        pendingAck = self._pending.pop(ackId)
        locker.unlock()
        try:
            elapsed = time.time() - pendingAck.registeredAt
            logger.warning(f'Ack timeout: {ackId} ({elapsed:.2f}s)')
            if pendingAck.timeoutCallback:
                pendingAck.timeoutCallback(ackId)
        except Exception as e:
            logger.error(f'Error in timeout callback for {ackId}: {e}', exc_info=True)

    def getAllPendingIds(self) -> list[str]:
        """
        Get list of all pending acknowledgment IDs.
        Returns:
            List of pending ack_ids
        Note: For debugging/testing purposes
        """
        locker = QMutexLocker(self._lock)
        return list(self._pending.keys())

    def clearAll(self) -> None:
        """
        Clear all pending acknowledgments and cancel timers.
        Warning: This does NOT call callbacks. Use for cleanup/shutdown only.
        """
        locker = QMutexLocker(self._lock)
        for pendingAck in self._pending.values():
            if pendingAck.timer:
                pendingAck.timer.cancel()
        count = len(self._pending)
        self._pending.clear()
        logger.info(f'Cleared {count} pending acknowledgments')
