# Decorators

Core decorators for common functionality patterns.

## Overview

The `Decorators` module provides utility decorators for common patterns like singleton, error handling, and data processing.

## Classes

### SignalBlocker

Context manager for temporarily blocking Qt signals.

```python
from core.Decorators import SignalBlocker

# Block signals during operations
with SignalBlocker(widget):
    widget.setValue(100)
    widget.setText("Updated")
# Signals are automatically unblocked here
```

**Methods:**
- `__init__(qtObject: QtCore.QObject)` - Initialize with Qt object
- `__enter__()` - Block signals
- `__exit__(exc_type, exc_value, traceback)` - Unblock signals

## Decorators

### @autoStrip

Automatically strips whitespace from string fields in dataclasses.

```python
from dataclasses import dataclass
from core.Decorators import autoStrip

@autoStrip
@dataclass
class User:
    name: str
    email: str
    age: int

user = User("  John  ", "  john@example.com  ", 25)
print(user.name)  # "John" (whitespace stripped)
print(user.email)  # "john@example.com" (whitespace stripped)
```

**Parameters:**
- `cls` - Dataclass to apply auto-stripping to

**Raises:**
- `TypeError` - If applied to non-dataclass

### @singleton

Ensures only one instance of a class exists.

```python
from core.Decorators import singleton

@singleton
class DatabaseConnection:
    def __init__(self):
        self.connected = False

# Multiple instantiations return the same instance
db1 = DatabaseConnection()
db2 = DatabaseConnection()
print(db1 is db2)  # True
```

### @catchExceptInMsgBox

Catches exceptions and displays them in a message box.

```python
from core.Decorators import catchExceptInMsgBox

@catchExceptInMsgBox(
    errorMsg="Custom error message",
    onlyExceptions=[ValueError, TypeError],
    reRaise=True,
    addExecInfo=True
)
def risky_operation():
    # Code that might raise exceptions
    pass
```

**Parameters:**
- `func` - Function to wrap
- `errorMsg` - Custom error message (optional)
- `onlyExceptions` - List of exception types to catch (optional)
- `reRaise` - Whether to re-raise the exception (default: True)
- `addExecInfo` - Whether to include execution info (default: True)

**Features:**
- Logs exceptions using core logging
- Shows message box if Qt application is running
- Includes detailed traceback information
- Configurable exception filtering

## Usage Examples

### Basic Error Handling

```python
from core.Decorators import catchExceptInMsgBox

@catchExceptInMsgBox(errorMsg="Failed to process data")
def process_user_data(data):
    # Processing logic that might fail
    return processed_data
```

### Singleton Service

```python
from core.Decorators import singleton

@singleton
class ConfigService:
    def __init__(self):
        self.settings = {}
    
    def get_setting(self, key):
        return self.settings.get(key)
```

### Data Processing with Auto-strip

```python
from dataclasses import dataclass
from core.Decorators import autoStrip

@autoStrip
@dataclass
class ContactInfo:
    name: str
    phone: str
    address: str
    
    def __post_init__(self):
        # Additional validation after auto-stripping
        if not self.name:
            raise ValueError("Name cannot be empty")
```

## Notes

- `@autoStrip` only works with dataclasses
- `@singleton` instances are shared across the entire application
- `@catchExceptInMsgBox` requires Qt application to be running for message box display
- All decorators preserve original function signatures and metadata
