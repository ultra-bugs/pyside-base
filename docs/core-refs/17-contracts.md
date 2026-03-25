# Contracts - Interfaces

> **Interface definitions for core components**

## DisposableInterface

Interface for resources requiring cleanup:

```python
from core.contracts import DisposableInterface

class MyResource(DisposableInterface):
    def cleanup(self):
        """Called by ServiceLocator.releaseScope()"""
        # Cleanup logic
        self._releaseResources()
        self._closeConnections()
```

## Usage

### With ServiceLocator

```python
from core import QtAppContext
from core.contracts import DisposableInterface

class DatabaseConnection(DisposableInterface):
    def __init__(self):
        self.connection = self._connect()
    
    def cleanup(self):
        if self.connection:
            self.connection.close()
            self.connection = None

# Register as scoped service
ctx = QtAppContext.globalInstance()
taskId = self.uuid

db = DatabaseConnection()
ctx.registerScopedService(taskId, db)

try:
    # Use database...
    pass
finally:
    ctx.releaseScope(taskId)  # Calls db.cleanup()
```

### Cleanup Priority

ServiceLocator checks methods in order:

1. `cleanup()` (highest priority - DisposableInterface)
2. `close()`
3. `dispose()`

```python
class MyResource(DisposableInterface):
    def cleanup(self):  # ✅ Preferred
        # Cleanup logic
        pass
    
    def close(self):  # Alternative if cleanup() not found
        pass
    
    def dispose(self):  # Fallback
        pass
```

## Best Practices

### ✅ DO

```python
# Implement DisposableInterface for scoped resources
class BrowserService(DisposableInterface):
    def cleanup(self):
        self.driver.quit()

# Use with scoped services
ctx.registerScopedService(taskId, resource)
```

### ❌ DON'T

```python
# Don't forget to implement cleanup
class MyResource(DisposableInterface):
    pass  # Missing cleanup()!

# Don't raise exceptions in cleanup
def cleanup(self):
    raise Exception('Error')  # Will be logged but won't stop other cleanups
```

## Related Documentation

- [ServiceProvider](25-service-providers.md) - App service bootstrap
- [ServiceLocator](02-dependency-injection.md) - Scoped services
- [AbstractTask](13-abstract-task.md) - Task resources

## ServiceProvider

Interface for app-level service registration during bootstrap.
Provides a declarative way to register services, handle boot initialization, and hook into post-application start events.

```python
from core.contracts.ServiceProvider import ServiceProvider
from core import QtAppContext

class MyServiceProvider(ServiceProvider):
    # Optional flags for ordering and dependency management
    discoverable: bool = True
    after: list[str] = []
    requires: list[str] = []
    wants: list[str] = []

    def __init__(self, ctx: QtAppContext):
        self.ctx = ctx

    def register(self):
        # Register services into self.ctx
        # Automatically called during bootstrap
        pass

    def boot(self):
        # Optional post-registration hook
        pass

    def booted(self):
        # Optional hook executed after the application is fully bootstrapped.
        pass
```

See the [ServiceProvider Documentation](25-service-providers.md) for full architectural details.
