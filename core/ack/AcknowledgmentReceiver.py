"""
AcknowledgmentReceiver - Base class for components waiting for acknowledgments.

This abstract base class provides generic methods for:
- Generating unique acknowledgment IDs
- Emitting events with acknowledgments
- Waiting for all acknowledgments to be received
- Handling acknowledgment callbacks

Subclasses must implement:
- _do_emit_event(): How to emit events (Publisher, signals, etc.)
"""
import uuid
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from core.Logging import logger
from .AcknowledgmentTracker import AcknowledgmentTracker

class AcknowledgmentReceiver(ABC):
    """
    Base class for components that emit events and wait for acknowledgments.

    Generic and reusable - no assumptions about:
    - How events are emitted (Publisher, Qt signals, etc.)
    - What resources need cleanup (browser, connections, etc.)
    """

    def __init__(self, ackTracker: Optional[AcknowledgmentTracker]=None):
        """
        Initialize receiver with optional shared tracker.
        Args:
            ack_tracker: Optional shared tracker. If None, creates its own.
                        Pass shared tracker to coordinate with HandlerService.
        """
        self._ack_tracker = ackTracker if ackTracker else AcknowledgmentTracker()
        self._ack_results: Dict[str, Any] = {}

    def generateAckId(self) -> str:
        """
        Generate unique acknowledgment ID.
        Returns:
            Unique ack_id string
        """
        return f'ack_{uuid.uuid4().hex[:12]}'

    def emitEventWithAck(self, eventName: str, timeout: float=30.0, **eventData) -> str:
        """
        Emit event and register pending acknowledgment.
        Args:
            event_name: Name of event to emit
            timeout: Timeout in seconds
            **event_data: Event data to pass to handler
        Returns:
            ack_id for tracking this acknowledgment
        Note: Subclass must implement _do_emit_event() to actually emit the event
        """
        ackId = self.generateAckId()
        self._ack_tracker.registerPending(ackId, successCallback=self._on_ack_received, errorCallback=self._on_ack_error, timeoutCallback=self._on_ack_timeout, timeout=timeout)
        logger.debug(f'Emitting event {eventName} with ack_id={ackId}')
        try:
            self._do_emit_event(eventName, ackId, **eventData)
        except Exception as e:
            logger.error(f'Failed to emit event {eventName}: {e}')
            self._ack_tracker.acknowledgeError(ackId, e)
            raise
        return ackId

    @abstractmethod
    def _do_emit_event(self, eventName: str, ackId: str, **kwargs) -> None:
        """
        Emit event - subclass must implement.
        Args:
            event_name: Event name
            ack_id: Acknowledgment ID to include in event data
            **kwargs: Event data
        Example implementations:
            # Using Publisher:
            Publisher().notify(event_name, ack_id=ack_id, **kwargs)
            # Using Qt signals:
            self.eventEmitted.emit(event_name, ack_id, kwargs)
        """
        pass

    def waitForAcknowledgments(self, timeout: float=60.0) -> bool:
        """
        Block and wait for all pending acknowledgments.
        Args:
            timeout: Maximum time to wait in seconds
        Returns:
            True if all acks received, False if timeout
        Note: Uses polling with 100ms interval
        """
        startTime = time.time()
        logger.debug(f'Waiting for {self._ack_tracker.pendingCount()} acknowledgments (timeout={timeout}s)')
        while self._ack_tracker.pendingCount() > 0:
            if time.time() - startTime > timeout:
                pending = self._ack_tracker.getAllPendingIds()
                logger.warning(f'Timeout waiting for acknowledgments: {pending}')
                return False
            time.sleep(0.1)
        logger.debug('All acknowledgments received')
        return True

    def getAckResult(self, ackId: str) -> Optional[Any]:
        """
        Get result from acknowledged event.
        Args:
            ack_id: Acknowledgment ID
        Returns:
            Result data, or None if not found
        """
        return self._ack_results.get(ackId)

    def pendingAckCount(self) -> int:
        """
        Get number of pending acknowledgments.
        Returns:
            Number of pending acks
        """
        return self._ack_tracker.pendingCount()

    def _on_ack_received(self, ackId: str, result: Any) -> None:
        """
        Callback when acknowledgment received.
        Default: Store result in _ack_results dict.
        Subclass can override for custom handling.
        Args:
            ack_id: Acknowledgment ID
            result: Result data from sender
        """
        self._ack_results[ackId] = result
        logger.debug(f'Ack received: {ackId}')

    def _on_ack_error(self, ackId: str, error: Exception) -> None:
        """
        Callback when error acknowledgment received.
        Default: Log error.
        Subclass can override for custom error handling.
        Args:
            ack_id: Acknowledgment ID
            error: Error from sender
        """
        logger.error(f'Ack error for {ackId}: {error}')

    def _on_ack_timeout(self, ackId: str) -> None:
        """
        Callback when acknowledgment times out.
        Default: Log warning.
        Subclass can override for custom timeout handling.
        Args:
            ack_id: Acknowledgment ID that timed out
        """
        logger.warning(f'Ack timeout: {ackId}')

    def clearAckResults(self) -> None:
        """Clear all stored acknowledgment results."""
        self._ack_results.clear()