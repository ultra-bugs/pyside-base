import traceback
import typing
from functools import wraps
from dataclasses import fields, is_dataclass
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

def catchExceptInMsgBox(func: typing.Callable, errorMsg: str | None=None, onlyExceptions: typing.List[typing.Type[Exception]] | None=None, reRaise: bool=True, addExecInfo: bool=True):
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