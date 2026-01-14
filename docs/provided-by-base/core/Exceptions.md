# Exceptions

Custom exception classes and exception handling system.

## Overview

The exception system provides custom exception classes for different types of errors in the application, along with a centralized exception handler for displaying errors to users.

## API Reference

### Exception Classes

#### `AppException`
Base exception class for all application exceptions.

```python
class AppException(Exception):
    def __init__(self, message: str, title: str = 'Error'):
        self.title = title
        super().__init__(message)
```

**Properties:**
- `title` (str): Error title for display
- `message` (str): Error message

#### `ConfigError(AppException)`
Raised when there is a configuration error.

```python
class ConfigError(AppException):
    pass
```

#### `ServiceError(AppException)`
Raised when there is a service error.

```python
class ServiceError(AppException):
    pass
```

#### `UIError(AppException)`
Raised when there is a UI error.

```python
class UIError(AppException):
    pass
```

### Exception Handler

#### `ExceptionHandler`
Centralized exception handler for displaying errors to users.

```python
class ExceptionHandler:
    _instance = None
    _excludes = (SystemExit, KeyboardInterrupt)
```

**Methods:**

##### `registerHandler(self, exception_type: Type[Exception], handler) -> None`
Register a handler for an exception type.

**Parameters:**
- `exception_type` (Type[Exception]): The exception type to handle
- `handler`: The handler function

##### `handleException(self, e: Exception) -> bool`
Handle an exception using registered handlers or default handler.

**Parameters:**
- `e` (Exception): The exception to handle

**Returns:**
- `bool`: True if handled, False otherwise

##### `setupGlobalHandler(cls=None) -> None`
Setup global exception handler for `sys.excepthook`.

### Exception Event

#### `ExceptionEvent`
Event object for exceptions in the Observer pattern.

```python
class ExceptionEvent(QObject):
    raised = Signal(Exception)  # exception
```

**Signals:**
- `raised` (Exception): Emitted when an exception occurs

## Usage Examples

### Basic Exception Handling

```python
from core.Exceptions import AppException, ConfigError, ServiceError, UIError

# Raise custom exceptions
try:
    if not config_file:
        raise ConfigError("Configuration file not specified", "Config Error")
    
    if not service.is_available():
        raise ServiceError("Service is not available", "Service Error")
    
    if not widget.isVisible():
        raise UIError("Widget is not visible", "UI Error")
        
except AppException as e:
    print(f"{e.title}: {e}")
```

### Using Exception Handler

```python
from core.Exceptions import ExceptionHandler, AppException

# Create exception handler
handler = ExceptionHandler()

# Register custom handler
def custom_handler(e):
    print(f"Custom handler: {e}")
    return True

handler.registerHandler(ValueError, custom_handler)

# Handle exceptions
try:
    # Some operation that might fail
    risky_operation()
except Exception as e:
    handler.handleException(e)
```

### Custom Exception Classes

```python
from core.Exceptions import AppException

class DatabaseError(AppException):
    """Custom exception for database errors"""
    def __init__(self, message: str, query: str = None):
        super().__init__(message, "Database Error")
        self.query = query

class ValidationError(AppException):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: str = None):
        super().__init__(message, "Validation Error")
        self.field = field

# Usage
try:
    if not validate_email(email):
        raise ValidationError("Invalid email format", "email")
        
    if not database.connect():
        raise DatabaseError("Failed to connect to database", "SELECT * FROM users")
        
except ValidationError as e:
    print(f"Validation failed for {e.field}: {e}")
except DatabaseError as e:
    print(f"Database error in query '{e.query}': {e}")
```

### Global Exception Handler

```python
from core.Exceptions import ExceptionHandler

# Setup global handler at application startup
ExceptionHandler.setupGlobalHandler()

# Now unhandled exceptions will be caught and displayed
raise ValueError("This will be caught by global handler")
```

## Best Practices

1. **Use specific exception types**: Choose the most appropriate exception class
2. **Provide meaningful messages**: Include context and actionable information
3. **Use exception handler**: For centralized error handling
4. **Log exceptions**: Always log exceptions before handling them (handled by default handler)
5. **Handle gracefully**: Provide fallback behavior when possible
6. **Use custom exceptions**: For domain-specific errors

## Dependencies

- `PySide6.QtCore.QObject` - Base class for Qt objects
- `PySide6.QtWidgets.QApplication` - Application instance
- `core.Logging.logger` - Logging
- `core.Utils.WidgetUtils` - UI utilities

## Related Components

- [Logging](Logging.md) - Logging system
- [Observer](Observer.md) - Event system
- [Config](Config.md) - Configuration management
