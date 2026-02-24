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

import traceback
import typing
from dataclasses import fields, is_dataclass
from functools import wraps

from PySide6 import QtCore, QtWidgets


def autoStrip(cls):
    if not is_dataclass(cls):
        raise TypeError('@auto_strip is only applicable to dataclass')
    originalPostInit = getattr(cls, '__post_init__', None)
    @wraps(originalPostInit)
    def newPostInit(self, *args, **kwargs):
        if originalPostInit:
            originalPostInit(self, *args, **kwargs)
        for f in fields(self):
            if f.type == str:
                value = getattr(self, f.name)
                if isinstance(value, str):
                    setattr(self, f.name, value.strip())
    setattr(cls, '__post_init__', newPostInit)
    return cls


class SignalBlocker(QtCore.QObject):
    """Implements a signal blocker which can be used to temporarily block qt signals
    of a qt object using the with statement.
    Classes can extend this class then able to use the with statement to block signals
    """

    def __init__(self, qtObject: QtCore.QObject) -> None:
        super().__init__()
        self._qt_object = qtObject

    def __enter__(self):
        self._qt_object.blockSignals(True)

    def __exit__(self, exc_type, exc_value, traceback):
        self._qt_object.blockSignals(False)


def singleton(cls):
    """Singleton decorator"""
    instances = {}
    @wraps(cls)
    def getInstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getInstance


def catchExceptInMsgBox(
    func: typing.Callable, errorMsg: str | None = None, onlyExceptions: typing.List[typing.Type[Exception]] | None = None, reRaise: bool = True, addExecInfo: bool = True
):
    """Decorator that catches ALL exceptions and logs them. Also shows a message box if the app is running.
    TODO: second argument with list of exceptions to catch?
    Args:
        func (callable): The function which should be called
        reRaise (bool, optional): If True, the exception will be re-raised after being logged. Defaults to True.
    """
    def showExceptInMsgBox(*args, **kwargs):
        from core.Logging import logger as log
        try:
            return func(*args, **kwargs)
        except Exception as exception:
            log.exception(f'Exception in {func.__name__}: {exception}', addExecInfo=addExecInfo)
            if QtWidgets.QApplication.instance() is not None:
                err = errorMsg
                if err is None:
                    err = f'Runtime error in {func.__name__}: {exception}'
                from core import WidgetUtils
                msg = WidgetUtils.showErrorMsgBox(None, errorMsg, createOnly=True)
                msg.setInformativeText(f'{type(exception).__name__}: {exception}')
                trace_msg = f'Traceback:\n{traceback.format_exc()}'
                if addExecInfo:
                    msg.setDetailedText(trace_msg)
                msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
                msg.exec()
            if reRaise:
                raise
    return showExceptInMsgBox


import time
from typing import Any, Callable, ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')


def cachedWithTtl(ttlMs: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator that caches function results with a time-to-live (TTL) boundary.
    Args:
        ttlMs: Time-to-live in milliseconds. Cache is invalidated after this duration.
    Returns:
        Decorated function with time-bounded caching.
    Example:
        @cachedWithTtl(5000)  # Cache for 5 seconds
        def expensive_function(x):
            return x * 2
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        cache: dict[tuple, tuple[float, Any]] = {}
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Create cache key from arguments
            key = (args, tuple(sorted(kwargs.items())))
            current_time = time.time() * 1000  # Convert to milliseconds
            # Check if cached result exists and is still valid
            if key in cache:
                cached_time, cached_value = cache[key]
                if current_time - cached_time < ttlMs:
                    return cached_value
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[key] = (current_time, result)
            return result
        # Add cache inspection methods
        wrapper.cache_info = lambda: {'size': len(cache), 'ttlMs': ttlMs}
        wrapper.cache_clear = lambda: cache.clear()
        return wrapper
    return decorator
