# Exception Handling

> **Custom exception types and global exception handler**

## Overview

The Core provides:

- Custom exception types
- A global exception handler
- Handler registration mechanics
- Auto message box display support

## Exception Types

### AppException

Base exception for the application:

```python
from core import AppException

raise AppException('Error message', title='Custom Title')
```

### ConfigError

Configuration errors:

```python
from core import ConfigError

raise ConfigError('Invalid config value')
```

### ServiceError

Service-related errors:

```python
from core import ServiceError

raise ServiceError('Service initialization failed')
```

### UIError

UI-related errors:

```python
from core import UIError

raise UIError('Widget not found')
```

## ExceptionHandler

### Global Handler

```python
from core import ExceptionHandler

# Setup (auto-called by QtAppContext)
ExceptionHandler.setupGlobalHandler()
```

### Custom Handlers

```python
handler = ExceptionHandler()

def customHandler(e: MyException):
    # Handle exception
    return True  # Handled

handler.registerHandler(MyException, customHandler)
```

## Usage Examples

### Raising Exceptions

```python
from core import AppException, ConfigError

# Application exception
if not valid:
    raise AppException('Validation failed', title='Validation Error')

# Config exception
if not config_file_exists:
    raise ConfigError('Config file not found')
```

### Exception Logging

```python
from core.Logging import logger

try:
    risky_operation()
except Exception as e:
    logger.opt(exception=e).error('Operation failed')
    raise
```

## Best Practices

### ✅ DO

```python
# Use specific exception types
raise ConfigError('Invalid value')

# Log exceptions
try:
    # Code...
    pass
except Exception as e:
    logger.opt(exception=e).error('Failed')
    raise

# Provide context
raise AppException(f'Failed to load user {userId}', title='Load Error')
```

### ❌ DON'T

```python
# Don't catch silently
try:
    # Code...
    pass
except:
    pass  # Wrong!

# Don't use generic Exception
raise Exception('Error')  # Use AppException instead
```

## Related Documentation

- [Logging](07-logging.md) - Exception logging
- [Decorators](11-decorators.md) - @catchExceptInMsgBox
