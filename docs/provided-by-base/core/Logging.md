# Logging

Centralized logging system using loguru for the application.

## Overview

The logging system provides a centralized way to log messages throughout the application using loguru with different log levels, formatting options, and automatic log rotation.

## API Reference

### Logger Instance

```python
from core.Logging import logger
```

The logger is configured with:
- **Library**: loguru (not standard logging)
- **Level**: DEBUG for all logs
- **Format**: Timestamp, level, thread, module, function, line, message
- **Handlers**: Console (optional) and file handlers
- **Files**: 
  - `logs/app.log` - All logs with rotation
  - `logs/error.log` - Error logs only
- **Rotation**: Daily rotation with compression
- **Retention**: 7 days for app.log, 30 days for error.log

### Log Levels

- `DEBUG`: Detailed information for debugging
- `INFO`: General information about program execution
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for serious problems
- `CRITICAL`: Critical error messages

### Methods

#### `debug(message: str, *args, **kwargs) -> None`
Log debug message.

**Parameters:**
- `message` (str): Log message
- `*args`: Format arguments
- `**kwargs`: Additional keyword arguments

#### `info(message: str, *args, **kwargs) -> None`
Log info message.

**Parameters:**
- `message` (str): Log message
- `*args`: Format arguments
- `**kwargs`: Additional keyword arguments

#### `warning(message: str, *args, **kwargs) -> None`
Log warning message.

**Parameters:**
- `message` (str): Log message
- `*args`: Format arguments
- `**kwargs`: Additional keyword arguments

#### `error(message: str, *args, **kwargs) -> None`
Log error message.

**Parameters:**
- `message` (str): Log message
- `*args`: Format arguments
- `**kwargs`: Additional keyword arguments

#### `critical(message: str, *args, **kwargs) -> None`
Log critical message.

**Parameters:**
- `message` (str): Log message
- `*args`: Format arguments
- `**kwargs`: Additional keyword arguments

#### `exception(message: str, *args, **kwargs) -> None`
Log exception with traceback.

**Parameters:**
- `message` (str): Log message
- `*args`: Format arguments
- `**kwargs`: Additional keyword arguments

## Usage Examples

### Basic Logging

```python
from core.Logging import logger

# Log different levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Formatted Logging

```python
from core.Logging import logger

# Log with format arguments
user_id = 123
action = "login"
logger.info("User {} performed {}", user_id, action)

# Log with keyword arguments
logger.info("User {user_id} performed {action}", 
           user_id=user_id, action=action)
```

### Exception Logging

```python
from core.Logging import logger

try:
    # Some operation that might fail
    risky_operation()
except Exception as e:
    # Log exception with traceback
    logger.exception("Failed to perform risky operation: {}", str(e))
```

### Contextual Logging

```python
from core.Logging import logger

def process_user_data(user_data):
    logger.info("Processing user data for user: {}", user_data.get('id'))
    
    try:
        # Process data
        result = validate_and_process(user_data)
        logger.info("Successfully processed user data")
        return result
        
    except ValidationError as e:
        logger.error("Validation failed for user {}: {}", 
                    user_data.get('id'), str(e))
        raise
        
    except Exception as e:
        logger.exception("Unexpected error processing user {}: {}", 
                        user_data.get('id'), str(e))
        raise
```

### Scoped Logging (Binding)

```python
from core.Logging import logger

# Bind context to logger
task_logger = logger.bind(task_id="12345", user="john_doe")

task_logger.info("Starting task")
# Log output will include task_id and user in extra dict
```

## Best Practices

1. **Use appropriate log levels**: Choose the right level for each message
2. **Include context**: Provide relevant context in log messages
3. **Use structured logging**: Use format strings `{}` for better performance
4. **Log exceptions**: Always log exceptions with traceback using `logger.exception`
5. **Avoid sensitive data**: Don't log passwords or sensitive information
6. **Use binding**: Use `logger.bind()` for contextual logging in tasks/threads

## Dependencies

- `loguru` - Logging library
- `core.Utils.PathHelper` - Path utilities
- `core.Config` - Configuration management

## Related Components

- [Utils](Utils.md) - Utility functions
- [Config](Config.md) - Configuration management
- [Exceptions](Exceptions.md) - Exception handling
