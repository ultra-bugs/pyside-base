"""
Pytest configuration and shared fixtures for bvauto2 automated tests.

This file provides:
- Publisher/Subscriber mocking fixtures
- PySide6 QApplication setup
- Common test utilities
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
import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Ensure project root is in sys.path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Skip QApplication fixture for now due to pytest-qt compatibility issue
# from PySide6.QtWidgets import QApplication


# ============================================================================
# PySide6 Application Setup
# ============================================================================

# @pytest.fixture(scope='session')
# def qapp():
#     """Provide QApplication instance for tests requiring Qt."""
#     app = QApplication.instance()
#     if app is None:
#         app = QApplication([])
#     yield app
#     # Note: Don't quit app as it's shared across session


# ============================================================================
# Publisher/Subscriber Mocking Fixtures
# ============================================================================


@pytest.fixture
def mock_publisher():
    """
    Mock Publisher singleton for testing without real Publisher.
    Usage:
        def test_something(mock_publisher):
            # Publisher is automatically mocked
            Publisher().notify('event', data='test')
            mock_publisher.notify.assert_called_once_with('event', data='test')
    """
    with patch('core.Observer.Publisher') as mock:
        instance = MagicMock()
        mock.return_value = instance
        mock.instance.return_value = instance
        # Mock common methods
        instance.subscribe = MagicMock(return_value=instance)
        instance.unsubscribe = MagicMock(return_value=instance)
        instance.unsubscribeEvent = MagicMock(return_value=instance)
        instance.notify = MagicMock(return_value=instance)
        yield instance


@pytest.fixture
def mock_subscriber():
    """
    Create a mock Subscriber for testing.
    Usage:
        def test_handler(mock_subscriber):
            mock_subscriber.update('event', data='test')
            mock_subscriber.update.assert_called_once()
    """
    subscriber = MagicMock()
    subscriber.update = MagicMock()
    return subscriber


@pytest.fixture
def real_publisher():
    """
    Provide real Publisher instance for integration tests.
    Automatically cleans up subscribers after each test.
    Usage:
        def test_with_real_publisher(real_publisher):
            # Use actual Publisher
            real_publisher.subscribe(subscriber, 'event')
    """
    from core.Observer import Publisher
    publisher = Publisher()
    # Store original state
    original_global = publisher.globalSubscribers.copy()
    original_events = {k: v.copy() for k, v in publisher.eventSpecificSubscribers.items()}
    yield publisher
    # Restore original state
    publisher.globalSubscribers = original_global
    publisher.eventSpecificSubscribers = original_events


# ============================================================================
# Acknowledgment Testing Fixtures (for ACK mechanism tests)
# ============================================================================


@pytest.fixture
def mock_ack_tracker():
    """
    Mock AcknowledgmentTracker for testing without real implementation.
    Usage:
        def test_receiver(mock_ack_tracker):
            tracker = mock_ack_tracker
            tracker.register_pending('ack_1', callback)
    """
    with patch('core.ack.AcknowledgmentTracker.AcknowledgmentTracker') as mock:
        instance = MagicMock()
        mock.return_value = instance
        # Mock tracker methods
        instance.register_pending = MagicMock()
        instance.acknowledge = MagicMock()
        instance.acknowledge_error = MagicMock()
        instance.is_pending = MagicMock(return_value=True)
        instance.pending_count = MagicMock(return_value=0)
        instance.cleanup_expired = MagicMock()
        yield instance


@pytest.fixture
def event_tracker():
    """
    Simple event tracker to verify events were emitted in correct order.
    Usage:
        def test_events(event_tracker):
            event_tracker.record('event1')
            event_tracker.record('event2')
            assert event_tracker.events == ['event1', 'event2']
    """
    class EventTracker:
        def __init__(self):
            self.events = []
            self.data = {}
        def record(self, event_name, **kwargs):
            self.events.append(event_name)
            self.data[event_name] = kwargs
        def reset(self):
            self.events = []
            self.data = {}
        def assert_events_in_order(self, *expected_events):
            assert self.events == list(expected_events), f'Expected {expected_events}, got {self.events}'
        def assert_event_emitted(self, event_name):
            assert event_name in self.events, f"Event '{event_name}' not emitted. Emitted: {self.events}"
    return EventTracker()


# ============================================================================
# Thread Testing Utilities
# ============================================================================


@pytest.fixture
def thread_pool():
    """
    Provide ThreadPoolExecutor for testing concurrent operations.
    Automatically shuts down after test.
    Usage:
        def test_concurrent(thread_pool):
            futures = [thread_pool.submit(func, i) for i in range(10)]
            results = [f.result() for f in futures]
    """
    from concurrent.futures import ThreadPoolExecutor
    pool = ThreadPoolExecutor(max_workers=10)
    yield pool
    pool.shutdown(wait=True)


# ============================================================================
# Mock Config (for testing without real Config)
# ============================================================================


@pytest.fixture
def mock_config():
    """
    Mock Config singleton for testing without real Config.
    Usage:
        def test_with_config(mock_config):
            mock_config.get.return_value = "test_value"
            value = mock_config.get("some.key")
            assert value == "test_value"
    """
    with patch('core.Config.Config') as mock:
        instance = MagicMock()
        mock.return_value = instance
        mock.instance.return_value = instance
        # Mock common methods
        instance.get = MagicMock(return_value=None)
        instance.set = MagicMock(return_value=None)
        instance.save = MagicMock(return_value=None)
        instance.load = MagicMock(return_value=instance)
        yield instance


# ============================================================================
# Mock API Client (for service testing)
# ============================================================================


@pytest.fixture
def mock_api_client():
    """
    Mock BetMateApiClient for testing services without real API calls.
    Usage:
        def test_service(mock_api_client):
            mock_api_client.find_account_by_username_sync.return_value = {'id': 1}
    """
    with patch('services.BetMateApiClient.BetMateApiClient') as mock:
        instance = MagicMock()
        mock.return_value = instance
        # Common API methods
        instance.find_account_by_username_sync = MagicMock(return_value=None)
        instance.update_account_metadata_sync = MagicMock(return_value={'success': True})
        instance.create_job_sync = MagicMock(return_value={'id': 1})
        instance.check_job_exists_sync = MagicMock(return_value=None)
        instance.format_scheduled_at = MagicMock(return_value='2025-10-03T18:00:00Z')
        yield instance


# ============================================================================
# Test Helpers
# ============================================================================


class Helpers:
    """Common test helper functions."""

    @staticmethod
    def wait_for_condition(condition_func, timeout=5.0, interval=0.1):
        """
        Wait for a condition to become True.
        Args:
            condition_func: Callable that returns bool
            timeout: Maximum time to wait in seconds
            interval: Check interval in seconds
        Returns:
            bool: True if condition met, False if timeout
        """
        import time
        start = time.time()
        while time.time() - start < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        return False

    @staticmethod
    def assert_called_with_partial(mock_call, **expected_kwargs):
        """
        Assert mock was called with at least the expected kwargs.
        Useful when you don't care about all parameters.
        Usage:
            Helpers.assert_called_with_partial(
                mock.notify.call_args,
                event='vndTokenFound',
                ack_id='ack_123'
            )
        """
        actual_kwargs = mock_call.kwargs
        for key, expected_value in expected_kwargs.items():
            assert key in actual_kwargs, f"Expected kwarg '{key}' not found"
            assert actual_kwargs[key] == expected_value, f'Expected {key}={expected_value}, got {actual_kwargs[key]}'


@pytest.fixture
def caplog_loguru(caplog):
    """
    Fixture to propagate loguru logs to the standard logging module so caplog can capture them.
    """
    import logging
    from loguru import logger
    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)
    # Sink returns an ID we can use for removal
    # We set level to 0 to capture everything and let caplog filter it
    sink_id = logger.add(PropagateHandler(), format='{message}', level=0)
    yield caplog
    logger.remove(sink_id)


@pytest.fixture
def helpers():
    """Provide helper functions for tests."""
    return Helpers()
