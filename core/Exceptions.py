#              M""""""""`M            dP
#              Mmmmmm   .M            88
#              MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#              MMP  .MMMMM  88    88  88888"    88'  `88
#              M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#              M         M  `88888P'  dP   `YP  `88888P'
#              MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#              * * * * * * * * * * * * * * * * * * * * *
#              * -    - -   F.R.E.E.M.I.N.D   - -    - *
#              * -  Copyright © 2024 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

from typing import Type

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox


class AppException(Exception):
    """Base exception class for application"""
    
    def __init__(self, message: str, title: str = "Error"):
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
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup()
        return cls._instance
    
    def _setup(self):
        """Setup exception handler"""
        self._error_handlers = {}
    
    def register_handler(self, exception_type: Type[Exception], handler):
        """Register a handler for an exception type"""
        self._error_handlers[exception_type] = handler
    
    def handle_exception(self, e: Exception) -> None:
        """Handle an exception"""
        # Find most specific handler
        handler = None
        for exc_type, h in self._error_handlers.items():
            if isinstance(e, exc_type):
                handler = h
                break
        
        # Use default handler if no specific handler found
        if handler is None:
            handler = self._default_handler
        
        handler(e)
    
    def _default_handler(self, e: Exception) -> None:
        """Default exception handler"""
        if isinstance(e, AppException):
            QMessageBox.critical(None, e.title, str(e))
        else:
            QMessageBox.critical(None, "Error", str(e))
    
    @classmethod
    def setup_global_handler(cls):
        """Setup global exception handler"""
        import sys
        
        def global_exception_handler(exctype, value, traceback):
            """Global exception handler"""
            # Log the error
            from core.Logging import logger
            logger.opt(exception=(exctype, value, traceback)).error("Unhandled exception")
            
            # Handle the error
            handler = cls()
            handler.handle_exception(value)
            
            # Call original exception handler
            sys.__excepthook__(exctype, value, traceback)
        
        sys.excepthook = global_exception_handler
