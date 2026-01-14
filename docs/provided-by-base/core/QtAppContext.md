# QtAppContext

Application Context and Lifecycle Management.

## Overview

`QtAppContext` is the central application context manager that handles:
- Application lifecycle (booting, ready, closing)
- Core service bootstrapping (Config, Publisher, ExceptionHandler)
- Feature flags via environment variables
- Service Locator / Dependency Injection
- Shared state management
- Quick access to core services

## API Reference

### Class Definition

```python
class QtAppContext(QObject):
    appBooting = Signal()
    appReady = Signal()
    appClosing = Signal()
    
    @classmethod
    def globalInstance(cls) -> 'QtAppContext': ...
```

### Signals

- `appBooting`: Emitted when bootstrap starts
- `appReady`: Emitted when bootstrap completes
- `appClosing`: Emitted when application is shutting down

### Methods

#### `bootstrap(self) -> None`
Initialize the application context. Thread-safe and idempotent (runs only once).
- Loads environment variables
- Initializes Config
- Initializes Publisher
- Sets up Global Exception Handler
- Initializes NetworkManager (if enabled)
- Initializes TaskManagerService (if enabled)

#### `run(self) -> int`
Start the Qt Event Loop. Automatically calls bootstrap if not already done.

#### `registerService(self, name: str, instance: Any) -> None`
Register a global service instance.

#### `getService(self, name: str) -> Any`
Get a registered service instance.

#### `registerScopedService(self, tag: str, instance: Any) -> None`
Register a scoped service linked to a specific tag (e.g., task UUID).

#### `releaseScope(self, tag: str) -> None`
Cleanup all services associated with a tag.

#### `setState(self, key: str, value: Any) -> None`
Set a value in the thread-safe shared state.

#### `getState(self, key: str, default: Any = None) -> Any`
Get a value from the thread-safe shared state.

#### `isFeatureEnabled(self, feature_name: str) -> bool`
Check if a feature is enabled via environment variables.

### Properties

- `config`: Access the Config instance
- `publisher`: Access the Publisher instance
- `network`: Access the QNetworkAccessManager (or None)
- `taskManager`: Access the TaskManagerService (or None)

## Feature Flags

Features can be enabled/disabled via environment variables (prefix `PSA_`):

| Feature | Env Variable | Default | Description |
|---------|--------------|---------|-------------|
| Network | `PSA_ENABLE_NETWORK` | `True` | Enables NetworkManager |
| Tasks | `PSA_ENABLE_TASKS` | `True` | Enables TaskManagerService |

Values can be: `true`, `1`, `yes`, `on` (case-insensitive).

## Usage Examples

### Basic Setup (main.py)

```python
import sys
from core.QtAppContext import QtAppContext
from windows.main.MainController import MainController

def main():
    # 1. Get Context
    ctx = QtAppContext.globalInstance()
    
    # 2. Bootstrap (Initialize core services)
    ctx.bootstrap()
    
    # 3. Setup UI
    window = MainController()
    window.show()
    
    # 4. Run App
    sys.exit(ctx.run())

if __name__ == "__main__":
    main()
```

### Accessing Services

```python
from core.QtAppContext import QtAppContext

ctx = QtAppContext.globalInstance()

# Quick access properties
config = ctx.config
publisher = ctx.publisher

# Service Locator
network = ctx.getService('network')
task_manager = ctx.getService('task_manager')
```

### Shared State

```python
# Set state in one component
ctx.setState('current_user', {'id': 1, 'name': 'Admin'})

# Get state in another component
user = ctx.getState('current_user')
```

### Scoped Services (e.g., in a Task)

```python
def execute_task(self):
    ctx = QtAppContext.globalInstance()
    task_id = self.uuid
    
    # Register service for this task only
    browser_service = ChromeBrowserService()
    ctx.registerScopedService(task_id, browser_service)
    
    try:
        # Do work...
        pass
    finally:
        # Cleanup services for this task
        ctx.releaseScope(task_id)
```

## Dependencies

- `PySide6.QtWidgets.QApplication`
- `core.Config`
- `core.Observer.Publisher`
- `core.Exceptions.ExceptionHandler`
- `core.NetworkManager`
- `core.taskSystem.TaskManagerService`
- `core.ServiceLocator`
- `python-dotenv` (optional, for .env loading)

## Related Components

- [Config](Config.md)
- [Observer](Observer.md)
- [Exceptions](Exceptions.md)
- [TaskSystem](TaskSystem.md)
