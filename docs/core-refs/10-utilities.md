# Utilities - Helper Classes

> **PathHelper, OsHelper, PythonHelper, WidgetUtils**

## PathHelper

Symlink-aware path management:

### Key Methods

```python
from core.Utils import PathHelper

# Root directory
root = PathHelper.rootDir()

# Data directory
dataDir = PathHelper.dataDir()
configPath = PathHelper.buildDataPath('config/config.json')

# Assets directory
assetsDir = PathHelper.assetsDir()
iconPath = PathHelper.buildAssetPath('icons/app.png')

# Vendor directory
vendorDir = PathHelper.vendorDir()

# File operations
exists = PathHelper.isFileExists(path)
isDir = PathHelper.isDirExists(path)
PathHelper.ensureDirExists(path)
PathHelper.ensureParentDirExists(filePath)

# JSON
data = PathHelper.readJson('config.json')
```

### Symlink Support

```python
# Detects symlinked core directory
isSymlinked = PathHelper.isUsingSymlinkedCore()

# Debug info
print(PathHelper.debugPathInfo())
```

## OsHelper

OS operations:

```python
from core.Utils import OsHelper

# Open file with default program
OsHelper.openWithDefaultProgram('document.pdf')
```

## PythonHelper

Python utilities:

```python
from core.Utils import PythonHelper

# Type checking
isCompatible = PythonHelper.is_type_compatible(value, int)

# Dataclass to JSON
jsonStr = PythonHelper.dataclass2Json(dataObject)
dictData = PythonHelper.dataclass2Dict(dataObject)

# Environment variables
value = PythonHelper.env('KEY', str, default='default')
debugMode = PythonHelper.env('DEBUG', bool, default=False)

# UUID formatting
shortId = PythonHelper.simpleFormatUuid(uuid)  # First 8 chars

# Random string
randomStr = PythonHelper.generateRandomString(length=16)

# Async to Sync conversion
result = PythonHelper.Async2Sync(myAsyncFunction())
```

### Async2Sync Helper

> [!IMPORTANT]
> **Use qasync Event Loop**
> 
> `Async2Sync` uses the qasync loop bootstrapped by `QtAppContext`.
> **Do NOT** create new event loops with `asyncio.new_event_loop()`.

```python
from core.Utils import PythonHelper

# Run async coroutine synchronously
async def fetchData():
    # ... async code ...
    return data

result = PythonHelper.Async2Sync(fetchData())
```

**Common use case:**
```python
from core.Utils import PythonHelper
from app.services.AsyncAdbExecutor import AsyncAdbExecutor

class MyService:
    def someMethod(self, deviceId: str):
        executor = AsyncAdbExecutor.GetInstance(deviceId)
        
        # Run async ADB command synchronously
        result = PythonHelper.Async2Sync(
            executor.Exec('shell pm list packages')
        )
        
        return result.StdOut
```

## WidgetUtils

Qt widget helpers:

```python
from core.Utils import WidgetUtils

# Message boxes
WidgetUtils.showErrorMsgBox(parent, 'Error message', 'Error Title')
WidgetUtils.showInfoMsgBox(parent, 'Info message', 'Info Title')
WidgetUtils.showWarningMsgBox(parent, 'Warning message', 'Warning Title')
```

## Usage Examples

### Path Management

```python
from core.Utils import PathHelper

# Build paths
configFile = PathHelper.buildDataPath('config/settings.json')
iconFile = PathHelper.buildAssetPath('icons/logo.png')

# Ensure directories exist
logDir = PathHelper.buildDataPath('logs')
PathHelper.ensureDirExists(logDir)

# Read JSON
config = PathHelper.readJson(configFile)
```

### Environment Variables

```python
from core.Utils import PythonHelper

# String
apiKey = PythonHelper.env('API_KEY', str, default='')

# Boolean
debugMode = PythonHelper.env('DEBUG', bool, default=False)

# Integer
port = PythonHelper.env('PORT', int, default=8080)
```

## Best Practices

### ✅ DO

```python
# Use PathHelper for all paths
dataPath = PathHelper.buildDataPath('data.json')

# Ensure directories exist
PathHelper.ensureParentDirExists(filePath)

# Use type-safe env vars
debugMode = PythonHelper.env('DEBUG', bool, default=False)
```

### ❌ DON'T

```python
# Don't hardcode paths
path = 'C:/Users/data/config.json'  # Wrong!

# Don't use os.path directly
import os
path = os.path.join('data', 'config.json')  # Use PathHelper

# Don't parse env vars manually
debug = os.getenv('DEBUG') == 'true'  # Use PythonHelper.env
```

## Related Documentation

- [Config](06-configuration.md) - Configuration paths
- [Logging](07-logging.md) - Log file paths
