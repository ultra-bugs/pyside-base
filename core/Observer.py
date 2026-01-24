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
from typing import List, Optional

from PySide6.QtCore import QMutex, QMutexLocker

from .Decorators import singleton
from .Utils import PythonHelper


@singleton
class Publisher:
    """Publisher (Subject) in Observer pattern"""

    _instance: 'Publisher' = None

    @staticmethod
    def instance():
        cls = Publisher
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.globalSubscribers = []
        self.eventSpecificSubscribers = {}
        self._lock = QMutex()

    def subscribe(self, subscriber, event: Optional[str] = None) -> 'Publisher':
        """Subscribe to all events or a specific event"""
        locker = QMutexLocker(self._lock)
        if event is None:
            self.globalSubscribers.append(subscriber)
        else:
            if event not in self.eventSpecificSubscribers:
                self.eventSpecificSubscribers[event] = []
            if subscriber not in self.eventSpecificSubscribers[event]:
                self.eventSpecificSubscribers[event].append(subscriber)
        return self

    def unsubscribe(self, subscriber, event: Optional[str] = None) -> 'Publisher':
        """Unsubscribe from all events or a specific event"""
        locker = QMutexLocker(self._lock)
        if event is None:
            if subscriber in self.globalSubscribers:
                self.globalSubscribers.remove(subscriber)
            for subscribers in self.eventSpecificSubscribers.values():
                if subscriber in subscribers:
                    subscribers.remove(subscriber)
        elif event in self.eventSpecificSubscribers and subscriber in self.eventSpecificSubscribers[event]:
            self.eventSpecificSubscribers[event].remove(subscriber)
        return self

    def notify(self, event: str, *args, **kwargs) -> 'Publisher':
        """Notify subscribers of an event"""
        from .Logging import logger
        locker = QMutexLocker(self._lock)
        globalSubscribers = self.globalSubscribers.copy()
        eventSubscribers = self.eventSpecificSubscribers.get(event, []).copy()
        locker.unlock()
        for subscriber in globalSubscribers:
            logger.debug(f"Notifying {subscriber} of event '{event}'")
            logger.debug(f'Args: {args}, Kwargs: {kwargs}')
            subscriber.update(event, *args, **kwargs)
        for subscriber in eventSubscribers:
            logger.debug(f"Notifying {subscriber} of event '{event}'")
            logger.debug(f'Args: {args}, Kwargs: {kwargs}')
            subscriber.update(event, *args, **kwargs)
        return self

    def connect(self, widget, signalName: str, event: str, *args, **kwargs) -> 'Publisher':
        """Connect a Qt signal to an event"""
        slot = getattr(widget, signalName, None)
        if slot is None:
            from core.Logging import logger
            logger.error(f"Signal '{signalName}' not found on widget '{widget.__class__.__name__}'")
            return self
        slot.connect(lambda *s_args, **signalKwargs: self.notify(event, *[*args, *s_args], **{**kwargs, **signalKwargs}))
        return self


class Subscriber:
    """Base class for subscribers (observers)"""

    def __init__(self, events: List[str], isGlobalSubscriber=False):
        self.events = events
        self.isGlobalSubscriber = bool(isGlobalSubscriber)
        publisher = Publisher()
        for event in events:
            publisher.subscribe(self, event)

    def update(self, event: str, *args, **kwargs):
        """Handle an event using smart parameter injection with type hint priority"""
        from caseconverter import pascalcase
        method_name = f'on{pascalcase(event)}'
        sig = None
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            try:
                sig = inspect.signature(method)
                params_dict = {}
                used_args = set()
                used_kwargs = set()
                all_params = {}
                for i, arg in enumerate(args):
                    all_params[f'arg{i}'] = arg
                for k, v in kwargs.items():
                    if not k.startswith('*'):
                        all_params[k] = v
                for param_name, param in sig.parameters.items():
                    if param_name == 'self':
                        continue
                    matched = False
                    if param_name in kwargs and param_name not in used_kwargs:
                        params_dict[param_name] = kwargs[param_name]
                        used_kwargs.add(param_name)
                        matched = True
                        continue
                    if param.annotation != inspect.Parameter.empty:
                        for i, arg in enumerate(args):
                            if i not in used_args and PythonHelper.is_type_compatible(arg, param.annotation):
                                params_dict[param_name] = arg
                                used_args.add(i)
                                matched = True
                                break
                        if not matched:
                            for key, value in kwargs.items():
                                if key not in used_kwargs and PythonHelper.is_type_compatible(value, param.annotation):
                                    params_dict[param_name] = value
                                    used_kwargs.add(key)
                                    matched = True
                                    break
                    if not matched and param.default is inspect.Parameter.empty:
                        for i, arg in enumerate(args):
                            if i not in used_args:
                                params_dict[param_name] = arg
                                used_args.add(i)
                                matched = True
                                break
                        if not matched:
                            for key, value in kwargs.items():
                                if key not in used_kwargs:
                                    params_dict[param_name] = value
                                    used_kwargs.add(key)
                                    matched = True
                                    break
                return method(**params_dict)
            except (TypeError, AttributeError) as e:
                if not sig:
                    sig = inspect.signature(method)
                errorMsg = str(e)
                if 'argument' in errorMsg and ('got an unexpected' in errorMsg or 'missing' in errorMsg):
                    try:
                        param_count = len(sig.parameters)
                        has_self = 'self' in sig.parameters
                        if has_self:
                            param_count -= 1
                        if param_count == 0:
                            return method()
                        elif param_count == 1 and args:
                            return method(args[0])
                        elif param_count == 2 and len(args) >= 2:
                            return method(args[0], args[1])
                        elif args:
                            return method(*args)
                        else:
                            raise TypeError(f'Could not match parameters for {method_name}. Original error: {errorMsg}')
                    except TypeError:
                        raise TypeError(f'Could not match parameters for {method_name}. Original error: {errorMsg}')
                else:
                    raise
            except Exception as e:
                from .Logging import logger
                logger.opt(exception=e).exception(f'Exception in event handler: {self.__class__.__name__}.{method_name}')
                from .Exceptions import ExceptionHandler
                handler = ExceptionHandler()
                handler.handle_exception(e)
