# Logging - Loguru-based Logging System

> **Structured logging with file rotation, console output, and thread context**

## Overview

The Core utilizes `loguru` for logging, providing:

- File rotation (daily)
- Separate error log
- Console logging (configurable)
- Thread context
- Colored output
- Auto-cleanup (retention policy)

## API Reference

### Logger Access

```python
from core.Logging import logger

logger.debug('Debug message')
logger.info('Info message')
logger.warning('Warning message')
logger.error('Error message')
logger.exception('Exception with traceback')
```

### Log Levels

- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages (potential issues)
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

### Contextual Logging

```python
# Bind context
logger = logger.bind(component='TaskSystem')
logger.info('Task started')  # Includes component='TaskSystem'

# Exception logging
try:
    # Code...
    pass
except Exception as e:
    logger.opt(exception=e).error('Operation failed')
```

## Configuration

### Config Keys

```json
{
    "logging": {
        "level": "INFO",
        "file": "app.log"
    },
    "consolelog": {
        "enable": true,
        "level": "DEBUG"
    }
}
```

### Log Files

**Location:** `{PROJECT_ROOT}/data/logs/`

**Files:**
- `app.log`: All logs (DEBUG+)
- `error.log`: Errors only (ERROR+)

**Rotation:** Daily  
**Retention:**
- `app.log`: 7 days
- `error.log`: 30 days

**Compression:** ZIP after rotation

## Usage Examples

### Basic Logging

```python
from core.Logging import logger

logger.debug('Starting operation...')
logger.info('Operation completed successfully')
logger.warning('Deprecated feature used')
logger.error('Operation failed')
```

### Exception Logging

```python
from core.Logging import logger

try:
    result = risky_operation()
except Exception as e:
    logger.opt(exception=e).error('Risky operation failed')
    # Logs full traceback
```

### Contextual Logging

```python
from core.Logging import logger

# Component-specific logger
taskLogger = logger.bind(component='TaskSystem')
taskLogger.info('Task started')
taskLogger.info('Task completed')

# Thread-specific logger
threadLogger = logger.bind(thread_id=threading.get_ident())
threadLogger.debug('Processing in thread')
```

### Structured Logging

```python
from core.Logging import logger

logger.info('User login', userId=123, username='john', ip='192.168.1.1')
logger.error('Database query failed', query='SELECT * FROM users', error=str(e))
```

## Best Practices

### ✅ DO

```python
# Use appropriate log levels
logger.debug('Variable value: {}', value)  # Development
logger.info('User logged in: {}', username)  # Important events
logger.warning('Deprecated API used')  # Potential issues
logger.error('Failed to save data: {}', error)  # Errors

# Include context
logger.info('Task completed', taskId=uuid, duration=elapsed)

# Use exception logging
try:
    # Code...
    pass
except Exception as e:
    logger.opt(exception=e).error('Operation failed')

# Bind component context
logger = logger.bind(component='MyComponent')
```

### ❌ DON'T

```python
# Don't use print()
print('Debug message')  # Wrong! Use logger.debug()

# Don't log sensitive data
logger.info('User password: {}', password)  # Security risk!

# Don't catch exceptions silently
try:
    # Code...
    pass
except:
    pass  # Wrong! At least log it

# Don't log in tight loops
for i in range(10000):
    logger.debug('Processing {}', i)  # Performance issue!
```

## Log Format

### Console Format

```
<green>2026-01-21 18:00:00</green> | <level>INFO    </level> | <green>T:MainThread</green>|<cyan>core.QtAppContext</cyan>:<cyan>bootstrap</cyan>:<cyan>115</cyan> | <level>Application Context Ready.</level>
```

### File Format

```
2026-01-21 18:00:00 | INFO     | T:MainThread | core.QtAppContext:bootstrap:115 | Application Context Ready.
```

## Common Patterns

### Task Logging

```python
from core.taskSystem import AbstractTask
from core.Logging import logger

class MyTask(AbstractTask):
    def handle(self):
        taskLogger = logger.bind(taskId=self.uuid)
        
        taskLogger.info('Task started')
        
        try:
            # Do work...
            taskLogger.debug('Processing step 1')
            taskLogger.debug('Processing step 2')
            
            taskLogger.info('Task completed successfully')
        except Exception as e:
            taskLogger.opt(exception=e).error('Task failed')
            raise
```

### Service Logging

```python
from core.Logging import logger

class DatabaseService:
    def __init__(self):
        self.logger = logger.bind(component='DatabaseService')
    
    def connect(self):
        self.logger.info('Connecting to database...')
        try:
            # Connect...
            self.logger.info('Database connected')
        except Exception as e:
            self.logger.opt(exception=e).error('Database connection failed')
            raise
```

### Performance Logging

```python
import time
from core.Logging import logger

def expensive_operation():
    start = time.time()
    logger.debug('Starting expensive operation')
    
    try:
        # Do work...
        elapsed = time.time() - start
        logger.info('Operation completed', duration=f'{elapsed:.2f}s')
    except Exception as e:
        elapsed = time.time() - start
        logger.opt(exception=e).error('Operation failed', duration=f'{elapsed:.2f}s')
        raise
```

## Related Documentation

- [QtAppContext](01-application-context.md) - Bootstrap logging
- [Config](06-configuration.md) - Logging configuration
- [Exceptions](09-exceptions.md) - Exception handling

## Troubleshooting

**Q: Logs not appearing in console**

```python
# Check config
from core import Config
config = Config()
print(config.get('consolelog.enable'))  # Should be True
print(config.get('consolelog.level'))   # Should be DEBUG or INFO
```

**Q: Log files not created**

```python
# Check data directory
from core.Utils import PathHelper
logDir = PathHelper.buildDataPath('logs')
print(logDir)  # Should exist
```

**Q: Too many log files**

```python
# Adjust retention in core/Logging.py
# app.log: retention='7 days'
# error.log: retention='30 days'
```
