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

from typing import Type

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication


class AppException(Exception):
    """Base exception class for application"""

    def __init__(self, message: str, title: str = 'Error'):
        self.title = title
        super().__init__(message)


class ConfigError(AppException):
    """Raised when there is a configuration error"""

    pass


class ServiceError(AppException):
    """Raised when there is a service error"""

    pass


class UIError(AppException):
    """Raised when there is a UI error"""

    pass


class ExceptionEvent(QObject):
    """Event object for exceptions"""

    raised = Signal(Exception)

    def __init__(self, exception: Exception):
        super().__init__()
        self.exception = exception


class ExceptionHandler:
    """Handles all exceptions in the application"""

    _instance = None
    _excludes = (SystemExit, KeyboardInterrupt)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        """Setup exception handler"""
        self._error_handlers = {}

    def registerHandler(self, exception_type: Type[Exception], handler):
        """Register a handler for an exception type"""
        self._error_handlers[exception_type] = handler

    def handleException(self, e: Exception):
        """Handle an exception"""
        if isinstance(e, self._excludes):
            return False
        handler = None
        for exc_type, h in self._error_handlers.items():
            if isinstance(e, exc_type):
                handler = h
                print('using specific handler', type(h))
                break
        if handler is None:
            handler = self._default_handler
            print('using default handler of ExceptionHandler')
        return handler(e)

    def _default_handler(self, e: Exception):
        """Default exception handler"""
        from PySide6.QtCore import QThread, QTimer
        from .Logging import logger
        from .Utils import WidgetUtils
        # Log the exception first
        if isinstance(e, AppException):
            logger.exception('App exception')
            logger.opt(exception=e).error(str(e))
            error_msg = str(e)
            error_title = e.title
        else:
            logger.exception('Unhandled exception', e)
            logger.opt(exception=e).error(str(e))
            error_msg = str(e)
            error_title = 'Unhandled Error'
        # Show messageBox only if we have a QApplication instance
        try:
            app = QApplication.instance()
            if app is None:
                return True
            # Determine parent widget
            try:
                parentWidget = app.centralWidget() if hasattr(app, 'centralWidget') else None
                if parentWidget is None and app.allWindows():
                    parentWidget = app.allWindows()[-1]
            except (AttributeError, IndexError):
                parentWidget = None
            # Check if we're on main thread
            if QThread.currentThread() == app.thread():
                # We're on main thread, show directly
                WidgetUtils.showErrorMsgBox(parentWidget, error_msg, error_title)
            else:
                # We're on worker thread, use QTimer to invoke on main thread
                # QTimer.singleShot with 0 delay schedules execution on main thread's event loop
                QTimer.singleShot(0, lambda: WidgetUtils.showErrorMsgBox(parentWidget, error_msg, error_title))
            return True
        except Exception as show_error:
            logger.error(f'Failed to show error dialog: {show_error}')
            return True

    @classmethod
    def setupGlobalHandler(cls=None):
        """Setup global exception handler"""
        import sys
        def globalExceptionHandler(exctype, value, traceback):
            """Global exception handler"""
            isHandled = False
            if exctype is not None and (not isinstance(exctype, ExceptionHandler._excludes)):
                handler = cls() if cls is not None else ExceptionHandler()
                isHandled = handler.handleException(value)
            not isHandled and sys.__excepthook__(exctype, value, traceback)
        sys.excepthook = globalExceptionHandler
