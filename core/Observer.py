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
import inspect
import queue
import threading
from typing import Callable, Dict, List, Optional

from PySide6.QtCore import QMutex, QMutexLocker, QObject, Qt, Signal

from .Decorators import singleton
from .threading.DaemonWorker import DaemonWorker
from .Utils import PythonHelper

_mainThread = threading.main_thread()
_STOP = object()


# ── Internal helpers ──────────────────────────────────────────────────────────

class _MainThreadBridge(QObject):
    """Relay subscriber.update() calls to the Qt main thread via QueuedConnection."""
    _sig = Signal(object, str, object, object)

    def __init__(self):
        super().__init__()
        self._sig.connect(self._onDeliver, Qt.QueuedConnection)

    def deliver(self, sub, event: str, args: tuple, kwargs: dict) -> None:
        self._sig.emit(sub, event, args, kwargs)

    def _onDeliver(self, sub, event: str, args, kwargs) -> None:
        sub.update(event, *args, **kwargs)


class _PubSubDispatcher(DaemonWorker):
    """Single-thread FIFO dispatcher for Publisher events."""

    def __init__(self, publisher: 'Publisher'):
        super().__init__('PubSubDispatcher')
        self._pub = publisher

    def onItem(self, msg) -> None:
        event, args, kwargs = msg
        self._pub._deliver(event, args, kwargs)


class _CallableTask:
    """Lightweight AbstractTask adapter: wraps a zero-arg callable for TaskSystem."""
    _isCallableTask = True

    def __init__(self, fn: Callable, name: str = 'PubSubTask'):
        self._fn = fn
        self._taskName = name

    def _asAbstractTask(self):
        from core.taskSystem.AbstractTask import AbstractTask

        fn = self._fn
        taskName = self._taskName

        class _Task(AbstractTask):
            serializables = ()

            def __init__(self):
                super().__init__(name=taskName, failSilently=True)

            def handle(self):
                fn()

            def _performCancellationCleanup(self):
                pass

            @classmethod
            def deserialize(cls, data):
                return None

        return _Task()


# ── Publisher ─────────────────────────────────────────────────────────────────

@singleton
class Publisher:
    """Queue-based, thread-aware Pub/Sub Publisher (Singleton).

    notify() is non-blocking — events are enqueued and dispatched by a
    single background daemon thread (PubSubDispatcher), preserving FIFO order.

    Delivery routing per subscriber:
    - Registered on main thread  → _MainThreadBridge (Qt QueuedConnection, UI-safe)
    - Child thread, default      → inline on Dispatcher thread
    - Child thread, pubsubFireAndForget=True → TaskManagerService (respects concurrency)
    """

    _instance: 'Publisher' = None
    _logger = None
    _isInited = False

    @staticmethod
    def instance() -> 'Publisher':
        return Publisher()

    @staticmethod
    def globalInstance() -> 'Publisher':
        return Publisher()

    def __init__(self):
        if Publisher._isInited:
            return
        self._lock = QMutex()
        self._globalSubscribers: list = []
        self._eventSubscribers: dict = {}
        self._bridge = _MainThreadBridge()
        self._dispatcher = _PubSubDispatcher(self)
        self._dispatcher.start()
        from .Logging import logger
        self._logger = logger.bind(component='core.Observer.Publisher')
        Publisher._isInited = True

    @property
    def logger(self):
        return self._logger

    def subscribe(self, subscriber, event: Optional[str] = None) -> 'Publisher':
        """Subscribe to all events or a specific event."""
        with QMutexLocker(self._lock):
            if event is None:
                self._globalSubscribers.append(subscriber)
            else:
                self._eventSubscribers.setdefault(event, [])
                if subscriber not in self._eventSubscribers[event]:
                    self._eventSubscribers[event].append(subscriber)
        return self

    def unsubscribe(self, subscriber, event: Optional[str] = None) -> 'Publisher':
        """Unsubscribe from all events or a specific event."""
        with QMutexLocker(self._lock):
            if event is None:
                self._globalSubscribers = [s for s in self._globalSubscribers if s is not subscriber]
                for lst in self._eventSubscribers.values():
                    if subscriber in lst:
                        lst.remove(subscriber)
            elif event in self._eventSubscribers:
                self._eventSubscribers[event] = [s for s in self._eventSubscribers[event] if s is not subscriber]
        return self

    def notify(self, event: str, *args, **kwargs) -> 'Publisher':
        """Non-blocking: enqueue event and return immediately."""
        self._dispatcher.enqueue((event, args, kwargs))
        return self

    def connect(self, widget, signalName: str, event: str, *args, **kwargs) -> 'Publisher':
        """Connect a Qt signal to a Pub/Sub event."""
        slot = getattr(widget, signalName, None)
        if slot is None:
            self._logger.error(f"Signal '{signalName}' not found on widget '{widget.__class__.__name__}'")
            return self
        slot.connect(lambda *s_args, **signalKwargs: self.notify(event, *[*args, *s_args], **{**kwargs, **signalKwargs}))
        return self

    def stop(self) -> None:
        """Gracefully stop the dispatcher thread."""
        self._dispatcher.stop()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _deliver(self, event: str, args: tuple, kwargs: dict) -> None:
        with QMutexLocker(self._lock):
            targets = [*self._globalSubscribers, *self._eventSubscribers.get(event, [])]
        for sub in targets:
            self._logger.debug(f"Dispatching '{event}' → {sub.__class__.__name__}")
            self._invokeSubscriber(sub, event, args, kwargs)

    def _invokeSubscriber(self, sub, event: str, args: tuple, kwargs: dict) -> None:
        homeThread = getattr(sub, '_homeThread', None)
        if homeThread is _mainThread:
            self._bridge.deliver(sub, event, args, kwargs)
            return
        if getattr(sub, 'pubsubFireAndForget', False):
            self._dispatchToTaskSystem(sub, event, args, kwargs)
        else:
            sub.update(event, *args, **kwargs)

    def _dispatchToTaskSystem(self, sub, event: str, args: tuple, kwargs: dict) -> None:
        try:
            from core.QtAppContext import QtAppContext
            tm = QtAppContext.globalInstance().taskManager
            if tm:
                ct = _CallableTask(lambda: sub.update(event, *args, **kwargs), name=f'PubSub:{event}')
                tm.addTask(ct._asAbstractTask())
                return
        except Exception as e:
            self._logger.warning(f'TaskSystem unavailable for fireAndForget, falling back inline: {e}')
        sub.update(event, *args, **kwargs)


# ── Subscriber ────────────────────────────────────────────────────────────────

class Subscriber:
    """Base class for subscribers (observers).

    Thread routing flags:
    - pubsubFireAndForget (class-level bool): Set True for I/O-heavy handlers
      that should be dispatched via TaskManagerService instead of blocking
      the Dispatcher thread.
    """

    pubsubFireAndForget: bool = False

    def __init__(self, events: List[str], isGlobalSubscriber=False):
        self._homeThread = threading.current_thread()
        self.events = events
        self.isGlobalSubscriber = bool(isGlobalSubscriber)
        publisher = Publisher()
        for event in events:
            publisher.subscribe(self, event)
        if isGlobalSubscriber:
            publisher.subscribe(self)

    def update(self, event: str, *args, **kwargs):
        """Dispatch to on<EventName> method with smart parameter injection."""
        from caseconverter import pascalcase
        import re
        cleanEvent = re.sub(r'[.\-_+/*]', ' ', event)
        methodName = f'on{pascalcase(cleanEvent)}'
        sig = None
        if not hasattr(self, methodName):
            return
        method = getattr(self, methodName)
        try:
            sig = inspect.signature(method)
            paramsDict: Dict = {}
            usedArgs: set = set()
            usedKwargs: set = set()
            for paramName, param in sig.parameters.items():
                if paramName == 'self':
                    continue
                matched = False
                if paramName in kwargs and paramName not in usedKwargs:
                    paramsDict[paramName] = kwargs[paramName]
                    usedKwargs.add(paramName)
                    matched = True
                    continue
                if param.annotation != inspect.Parameter.empty:
                    for i, arg in enumerate(args):
                        if i not in usedArgs and PythonHelper.is_type_compatible(arg, param.annotation):
                            paramsDict[paramName] = arg
                            usedArgs.add(i)
                            matched = True
                            break
                    if not matched:
                        for key, value in kwargs.items():
                            if key not in usedKwargs and PythonHelper.is_type_compatible(value, param.annotation):
                                paramsDict[paramName] = value
                                usedKwargs.add(key)
                                matched = True
                                break
                if not matched and param.default is inspect.Parameter.empty:
                    for i, arg in enumerate(args):
                        if i not in usedArgs:
                            paramsDict[paramName] = arg
                            usedArgs.add(i)
                            matched = True
                            break
                    if not matched:
                        for key, value in kwargs.items():
                            if key not in usedKwargs:
                                paramsDict[paramName] = value
                                usedKwargs.add(key)
                                matched = True
                                break
            return method(**paramsDict)
        except (TypeError, AttributeError) as e:
            if not sig:
                sig = inspect.signature(method)
            errorMsg = str(e)
            if 'argument' in errorMsg and ('got an unexpected' in errorMsg or 'missing' in errorMsg):
                try:
                    paramCount = len([p for p in sig.parameters if p != 'self'])
                    if paramCount == 0:
                        return method()
                    elif paramCount == 1 and args:
                        return method(args[0])
                    elif paramCount == 2 and len(args) >= 2:
                        return method(args[0], args[1])
                    elif args:
                        return method(*args)
                    else:
                        raise TypeError(f'Could not match parameters for {methodName}. Original: {errorMsg}')
                except TypeError:
                    raise TypeError(f'Could not match parameters for {methodName}. Original: {errorMsg}')
            else:
                raise
        except RuntimeError as e:
            if 'signal' in str(e).lower():
                from .Logging import logger
                logger.bind(component=self.__class__.__name__).opt(exception=e).exception(
                    f'RuntimeError in event handler: {self.__class__.__name__}.{methodName}')
                return
            raise
        except Exception as e:
            from .Logging import logger
            logger.bind(component=self.__class__.__name__).opt(exception=e).exception(
                f'Exception in event handler: {self.__class__.__name__}.{methodName}')
            from .Exceptions import ExceptionHandler
            ExceptionHandler().handleException(e)
