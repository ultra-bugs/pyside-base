"""
Tests for core.Observer (Publisher/Subscriber) - async, thread-aware dispatch.

Run:
    pixi run ctests tests_core/observer/ -v
"""
import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.Observer import Publisher, Subscriber


# ── Helpers ───────────────────────────────────────────────────────────────────

def _waitFor(qtbot, condition, timeout=2000) -> bool:
    try:
        qtbot.waitUntil(condition, timeout=timeout)
        return True
    except Exception:
        return False


class _RecordingSubscriber(Subscriber):
    def __init__(self, events):
        super().__init__(events)
        self.received = []
        self.receivedThreads = []

    def onTestEvent(self, value=None):
        self.received.append(value)
        self.receivedThreads.append(threading.current_thread())

    def onEventA(self, value=None):
        self.received.append(('A', value))

    def onEventB(self, value=None):
        self.received.append(('B', value))


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def pub(qtbot):
    """Real Publisher with subscriber state restored after each test."""
    p = Publisher()
    saved_global = p._globalSubscribers.copy()
    saved_events = {k: v.copy() for k, v in p._eventSubscribers.items()}
    yield p
    p._globalSubscribers = saved_global
    p._eventSubscribers = saved_events


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.qt
def test_notifyNonBlocking(qtbot, pub):
    """notify() must return before subscriber finishes processing."""
    delay = 0.3
    received = []

    class _SlowSub(Subscriber):
        def __init__(self):
            super().__init__(['testEvent'])
        def onTestEvent(self):
            time.sleep(delay)
            received.append(1)

    sub = _SlowSub()
    start = time.time()
    pub.notify('testEvent')
    elapsed = time.time() - start
    assert elapsed < delay, f'notify() blocked for {elapsed:.3f}s, expected < {delay}s'
    assert _waitFor(qtbot, lambda: len(received) == 1, timeout=3000), 'Subscriber never received event'


@pytest.mark.qt
def test_subscriberReceivesEvent(qtbot, pub):
    sub = _RecordingSubscriber(['testEvent'])
    pub.notify('testEvent', value=42)
    assert _waitFor(qtbot, lambda: len(sub.received) == 1)
    assert sub.received[0] == 42


@pytest.mark.qt
def test_fifoOrder(qtbot, pub):
    """Events notified in order 0..4 must be received in same order."""
    received = []

    class _OrderSub(Subscriber):
        def __init__(self):
            super().__init__(['orderEvent'])
        def onOrderEvent(self, idx=None):
            received.append(idx)

    sub = _OrderSub()
    for i in range(5):
        pub.notify('orderEvent', idx=i)

    assert _waitFor(qtbot, lambda: len(received) == 5, timeout=3000)
    assert received == [0, 1, 2, 3, 4], f'FIFO violated: {received}'


@pytest.mark.qt
def test_mainThreadDelivery(qtbot, pub):
    """Subscriber registered on main thread must receive update on main thread."""
    mainThread = threading.main_thread()
    deliveredOn = []

    class _MainSub(Subscriber):
        def __init__(self):
            super().__init__(['mainTest'])
        def onMainTest(self):
            deliveredOn.append(threading.current_thread())

    sub = _MainSub()
    assert sub._homeThread is mainThread
    pub.notify('mainTest')
    assert _waitFor(qtbot, lambda: len(deliveredOn) == 1, timeout=2000), 'Event not delivered to main-thread subscriber'
    assert deliveredOn[0] is mainThread, f'Wrong thread: {deliveredOn[0]}'


@pytest.mark.qt
def test_childThreadSubscriberRunsOnDispatcher(qtbot, pub):
    """Subscriber registered from a child thread must NOT run on main thread."""
    mainThread = threading.main_thread()
    deliveredOn = []
    ready = threading.Event()

    def _registerAndWait():
        class _ChildSub(Subscriber):
            def __init__(self):
                super().__init__(['childTest'])
            def onChildTest(self):
                deliveredOn.append(threading.current_thread())
        _ChildSub()
        ready.set()
        time.sleep(1.0)

    t = threading.Thread(target=_registerAndWait, daemon=True)
    t.start()
    ready.wait(timeout=1.0)
    pub.notify('childTest')
    assert _waitFor(qtbot, lambda: len(deliveredOn) == 1, timeout=2000), 'Event not delivered to child-thread subscriber'
    assert deliveredOn[0] is not mainThread, 'Child subscriber delivered on main thread'


@pytest.mark.qt
def test_unsubscribeStopsDelivery(qtbot, pub):
    sub = _RecordingSubscriber(['testEvent'])
    pub.notify('testEvent', value=1)
    assert _waitFor(qtbot, lambda: len(sub.received) == 1)
    pub.unsubscribe(sub, 'testEvent')
    pub.notify('testEvent', value=2)
    qtbot.wait(300)
    assert len(sub.received) == 1, f'Event delivered after unsubscribe: {sub.received}'


@pytest.mark.qt
def test_fireAndForgetFallbackInlineWhenNoTaskManager(qtbot, pub):
    """fireAndForget=True without TaskManager must still deliver (inline fallback)."""
    received = []

    class _FiredSub(Subscriber):
        pubsubFireAndForget = True
        def __init__(self):
            super().__init__(['ffEvent'])
            self._homeThread = threading.Thread()  # fake child thread
        def onFfEvent(self):
            received.append(1)

    sub = _FiredSub()
    pub.subscribe(sub, 'ffEvent')
    pub.notify('ffEvent')
    assert _waitFor(qtbot, lambda: len(received) == 1, timeout=2000), 'fireAndForget inline fallback not called'
