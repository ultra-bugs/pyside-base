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
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List, Optional

from PySide6.QtCore import QMutex, QMutexLocker, QObject, Qt, Signal

from .Decorators import singleton
from .Utils import PythonHelper
from .contracts.Message import Message
from .contracts.ReplyChannel import ReplyChannel
from .threading.DaemonWorker import DaemonWorker

_mainThread = threading.main_thread()


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
    """Single-thread FIFO dispatcher for Publisher events.

    Dequeues `Message` objects and routes delivery per thread-affinity and
    the `isAsync` flag set by the *sender* (Publisher.notifyAsync).
    """

    def __init__(self, publisher: 'Publisher'):
        super().__init__('PubSubDispatcher')
        self._pub = publisher

    def onItem(self, msg: Message) -> None:
        self._pub._deliver(msg)


class _CallableTask:
    """Lightweight AbstractTask adapter: wraps a zero-arg callable for TaskSystem."""

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

    `notify()` is non-blocking — events are enqueued as `Message` objects and
    dispatched FIFO by a background `_PubSubDispatcher` thread.

    Delivery routing per subscriber:
    - Registered on main thread           → `_MainThreadBridge` (QueuedConnection, UI-safe)
    - Child thread, `msg.isAsync=False`   → inline on Dispatcher thread
    - Child thread, `msg.isAsync=True`    → `TaskManagerService` (respects concurrency)

    Fire-and-Forget is a **sender** concern, set via `notifyAsync()`:
        publisher.notify(event)        # delivery may block Dispatcher
        publisher.notifyAsync(event)   # delivery offloaded to TaskSystem
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
        # Dedicated executor for async PubSub delivery — decoupled from TaskSystem pool
        self._pubsubExecutor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='PubSubExec')
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
        """Non-blocking: enqueue event for synchronous delivery on the Dispatcher thread.
        Delivery will block the Dispatcher while the subscriber processes it.
        Use `notifyAsync()` if the handler is I/O-heavy.
        """
        msg = Message(topic=event, payload={'args': args, 'kwargs': kwargs}, isAsync=False)
        self._dispatcher.enqueue(msg)
        return self

    def notifyAsync(self, event: str, *args, **kwargs) -> 'Publisher':
        """Non-blocking: enqueue event for async delivery via TaskManagerService.
        The *sender* declares this message as fire-and-forget — delivery is
        offloaded to the TaskSystem, freeing the Dispatcher immediately.
        Use when the handler performs I/O (API calls, DB writes, etc.).
        """
        msg = Message(topic=event, payload={'args': args, 'kwargs': kwargs}, isAsync=True)
        self._dispatcher.enqueue(msg)
        return self

    def connect(self, widget, signalName: str, event: str, *args, **kwargs) -> 'Publisher':
        """Connect a Qt signal to a Pub/Sub event."""
        slot = getattr(widget, signalName, None)
        if slot is None:
            self._logger.error(f"Signal '{signalName}' not found on widget '{widget.__class__.__name__}'")
            return self
        slot.connect(lambda *sArgs, **sKwargs: self.notify(event, *[*args, *sArgs], **{**kwargs, **sKwargs}))
        return self

    def stop(self) -> None:
        """Gracefully stop the dispatcher thread and PubSub executor."""
        self._dispatcher.stop()
        self._pubsubExecutor.shutdown(wait=False)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _deliver(self, msg: Message) -> None:
        with QMutexLocker(self._lock):
            targets = [*self._globalSubscribers, *self._eventSubscribers.get(msg.topic, [])]
        for sub in targets:
            self._logger.debug(f"Dispatching '{msg.topic}' → {sub.__class__.__name__} (async={msg.isAsync})")
            self._invokeSubscriber(sub, msg)

    def _invokeSubscriber(self, sub, msg: Message) -> None:
        args: tuple = msg.payload.get('args', ())
        kwargs: dict = msg.payload.get('kwargs', {})
        homeThread = getattr(sub, '_homeThread', None)
        if homeThread is _mainThread:
            self._bridge.deliver(sub, msg.topic, args, kwargs)
            return
        if msg.isAsync:
            self._dispatchToTaskSystem(sub, msg.topic, args, kwargs)
        else:
            sub.update(msg.topic, *args, **kwargs)

    def _dispatchToTaskSystem(self, sub, event: str, args: tuple, kwargs: dict) -> None:
        """Dispatch async PubSub delivery on a dedicated executor.
        Uses a separate ThreadPoolExecutor (2 threads) instead of the TaskSystem
        QThreadPool to prevent pool contention / deadlock when all task threads
        are occupied.
        """
        def _deliver():
            try:
                sub.update(event, *args, **kwargs)
            except Exception as e:
                self._logger.opt(exception=e).error(f'PubSub async delivery failed for {event}: {e}')
        try:
            self._pubsubExecutor.submit(_deliver)
        except RuntimeError:
            # Executor shut down — fall back to inline delivery
            self._logger.warning(f'PubSub executor shut down, delivering inline: {event}')
            sub.update(event, *args, **kwargs)


# ── UpdatableMixin ────────────────────────────────────────────────────────────


class UpdatableMixin:
    def update(self, event: str, *args, **kwargs):
        """Dispatch to on<EventName> method with smart parameter injection."""
        from caseconverter import pascalcase
        import re
        cleanEvent = re.sub(r'[\.\-_+/*]', ' ', event)
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
                logger.bind(component=self.__class__.__name__).opt(exception=e).exception(f'RuntimeError in event handler: {self.__class__.__name__}.{methodName}')
                return
            raise
        except Exception as e:
            from .Logging import logger
            logger.bind(component=self.__class__.__name__).opt(exception=e).exception(f'Exception in event handler: {self.__class__.__name__}.{methodName}')
            from .Exceptions import ExceptionHandler
            ExceptionHandler().handleException(e)


# ── Subscriber ────────────────────────────────────────────────────────────────


class Subscriber(UpdatableMixin):
    """Base class for subscribers (observers).

    Thread routing is determined by `_homeThread` (captured at construction).
    FnF vs sync delivery is decided by the **sender** via `notify()` / `notifyAsync()`.
    """

    def __init__(self, events: List[str], isGlobalSubscriber=False):
        self._homeThread = threading.current_thread()
        self.events = events
        self.isGlobalSubscriber = bool(isGlobalSubscriber)
        publisher = Publisher.instance()
        for event in events:
            publisher.subscribe(self, event)
        if isGlobalSubscriber:
            publisher.subscribe(self)
