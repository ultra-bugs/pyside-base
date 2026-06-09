# Logging - Loguru-based Logging System

> **Structured logging with file rotation, console output, and thread context**
> **Last synced**: `2026-06-09`

## Overview

The Core utilizes `loguru` for logging, providing:

- File rotation (daily)
- Separate error log
- Console logging (configurable)
- Custom log levels (e.g. `BLOCKING`)
- Per-module level filtering
- Thread context
- Colored output
- Auto-cleanup (retention policy)

## Architecture

### Initialization Flow

`logger` is a singleton `_LoguruWrappedLogger` instance created at module load. Init sequence:

1. Load config → merge `FilterFactory._CUSTOM_LEVELS` + `logging.customLevels` from config → register all levels with loguru inline in `__init__`
2. Read `logging.sinkManAutoCommit` config to choose sink manager:
   - `false` (default) → `AutoCommitSinkManager` → `_setupUseAutoCommit()`
   - `true` → `SinkCollectionManager` → `_setup()` + explicit `commit()`
3. Configure default sinks (console + file.app + file.error)

### SinkEntry

`core.logging.SinkEntry` — dataclass representing a single loguru sink.

| Field | Type | Default | Description |
|---|---|---|---|
| `id` | `str` | *(required)* | Unique sink identifier |
| `sink` | `Any` | *(required)* | Path string, callable, `sys.stderr`, etc. |
| `level` | `str` | `'DEBUG'` | Minimum log level |
| `enabled` | `bool` | `True` | Whether sink is active |
| `position` | `int` | `0` | Ordering priority (lower = first) |
| `filter` | `Optional[Callable]` | `None` | Filter function (from `FilterFactory.make()`) |
| `kwargs` | `dict` | `{}` | Extra kwargs passed to `loguru.add()` (format, rotation, etc.) |
| `loguru_id` | `Optional[int]` | `None` | Internal loguru handler ID (set after commit) |

### SinkCollectionManager

`core.logging.SinkCollectionManager` — manages an ordered collection of `SinkEntry` objects. Changes are staged until `commit()` rebuilds all loguru handlers.

**Methods:**

| Method | Returns | Description |
|---|---|---|
| `add(entry)` | `self` | Append sink entry. Auto-assigns position if 0 |
| `remove(sink_id)` | `self` | Remove sink by ID |
| `enable(sink_id)` | `self` | Enable a disabled sink |
| `disable(sink_id)` | `self` | Disable a sink (excluded from commit) |
| `insertAt(position, entry)` | `self` | Insert at position, shifting existing entries |
| `get(sink_id)` | `SinkEntry \| None` | Lookup sink by ID |
| `commit()` | `self` | Remove all loguru handlers, re-add enabled sinks by position order |
| `listSinks()` | `list[SinkEntry]` | All sinks ordered by position |

### AutoCommitSinkManager

Subclass of `SinkCollectionManager` that commits after every mutation (`add`, `remove`, `enable`, `disable`, `insertAt`). Use `batch()` context manager to suppress auto-commit and commit once at end:

```python
sm = logger.getSinkManager()
with sm.batch():
    sm.add(SinkEntry(id='custom', sink='/tmp/custom.log', level='INFO'))
    sm.disable('console')
```

### Default Sinks

| Sink ID | Sink | Level | Condition |
|---|---|---|---|
| `console` | `sys.stderr` | `consolelog.level` | `consolelog.enable = true` (default) |
| `console.error` | `sys.stderr` | `ERROR` | `consolelog.enable = false` |
| `file.app` | `data/logs/app.log` | `DEBUG` | Always |
| `file.error` | `data/logs/error.log` | `ERROR` | Always |

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

**Built-in (loguru):**

- `TRACE` (5): Fine-grained tracing
- `DEBUG` (10): Detailed diagnostic information
- `INFO` (20): General informational messages
- `SUCCESS` (25): Operation success confirmations
- `WARNING` (30): Warning messages (potential issues)
- `ERROR` (40): Error messages
- `CRITICAL` (50): Critical errors

**Custom levels** — registered at logger init by merging `FilterFactory._CUSTOM_LEVELS` (hardcoded) with `logging.customLevels` from config:

- `BLOCKING` (35): Blocking/gate-wait events (between WARNING and ERROR) — defined in `FilterFactory._CUSTOM_LEVELS`

`_LEVEL_NO` is built from `_BUILTIN_LEVELS` + all resolved custom levels and is used by `FilterFactory.make()` for per-module filtering.

**Declaring custom levels in config** (`logging.customLevels`) — adds extra log levels beyond the hardcoded defaults. Each entry is a dict of kwargs accepted by loguru's `level()` method (`name` and `no` are required; `color` and `icon` are optional):

```json
{
    "logging": {
        "customLevels": [
            {"name": "GATE_WAIT", "no": 36, "color": "<blue>", "icon": "⏳"},
            {"name": "SLOW", "no": 38}
        ]
    }
}
```

**Supported entry formats** (same as `FilterFactory._CUSTOM_LEVELS` entries):

| Format | Example | Behavior |
|---|---|---|
| `str` | `'MY_LEVEL'` | Auto-assigns `no` (increments from `_AUTO_NO_BASE` or previous entry) |
| `dict` | `{'name': 'X', 'no': 35, 'color': '<blue>', 'icon': '⏳'}` | Explicit params. `no` required, `color`/`icon` optional |
| Level namedtuple | `loguru.level('ERROR')` result | Uses `name`, `no`, `color`, `icon` from the namedtuple |

Usage: `logger.log('BLOCKING', 'message')`

### Runtime Sink Management

```python
from core.Logging import logger

sm = logger.getSinkManager()

# Add a custom sink at runtime
from core.logging.SinkEntry import SinkEntry
sm.add(SinkEntry(id='custom.debug', sink='/tmp/debug.log', level='DEBUG', position=10,
                 kwargs={'format': '{time} | {level} | {message}', 'rotation': '10 MB'}))

# Disable/enable sinks
sm.disable('console')
sm.enable('console')

# List current sinks
for entry in sm.listSinks():
    print(f'{entry.id}: enabled={entry.enabled}, level={entry.level}')
```

### Contextual Logging

```python
# Bind context
logger = logger.bind(component='TaskSystem')
logger.info('Task started')  # Includes component='TaskSystem'

# Context manager (temporary binding) — use the yielded bound logger
from core.Logging import logContext
with logContext(taskId=uuid, userId=123) as ctxLogger:
    ctxLogger.info('Processing')  # Includes taskId + userId

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
        "sinkManAutoCommit": false,
        "customLevels": [],
        "moduleLvs": {
            "app.tasks": "INFO",
            "core.taskSystem": "WARNING"
        }
    },
    "consolelog": {
        "enable": true,
        "level": "DEBUG"
    }
}
```

| Key | Default | Description |
|---|---|---|
| `logging.level` | `"DEBUG"` | Default log level applied to all modules that have no matching rule in `moduleLvs` |
| `logging.sinkManAutoCommit` | `false` | `false` → `AutoCommitSinkManager` (commits per mutation); `true` → `SinkCollectionManager` (manual commit) |
| `logging.customLevels` | `[]` | Declare additional custom log levels to register with loguru. Merged with the hardcoded `FilterFactory._CUSTOM_LEVELS` at init. Each entry: `{"name": "...", "no": N}` (plus optional `color`, `icon`) |
| `logging.moduleLvs` | `{}` | Per-module log level overrides, matched by Python module namespace prefix. Longest-prefix match wins (e.g. `"app.services.http"` takes priority over `"app"`). Processed by `FilterFactory.make()` |
| `consolelog.enable` | `true` | Enable colored console output to stderr. When `false`, a stderr ERROR-only sink is added instead |
| `consolelog.level` | `"DEBUG"` | Console log level (only when `consolelog.enable` is true) |

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
