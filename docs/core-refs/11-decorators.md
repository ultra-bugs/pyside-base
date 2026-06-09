# Decorators

> **@singleton, @autoStrip, @catchExceptInMsgBox, @cachedWithTtl, SignalBlocker**
> **Last synced**: `2026-06-09`

## @singleton

Singleton pattern decorator:

```python
from core.Decorators import singleton

@singleton
class MyService:
    def __init__(self):
        self.data = []

# Always returns same instance
service1 = MyService()
service2 = MyService()
assert service1 is service2
```

## @autoStrip

Auto-strip strings in dataclass:

```python
from dataclasses import dataclass
from core.Decorators import autoStrip

@autoStrip
@dataclass
class UserData:
    name: str
    email: str

# Automatically strips whitespace
user = UserData(name='  John  ', email='  john@example.com  ')
print(user.name)  # 'John'
print(user.email)  # 'john@example.com'
```

## @catchExceptInMsgBox

Catch exceptions and show message box:

```python
from core.Decorators import catchExceptInMsgBox

@catchExceptInMsgBox
def riskyOperation():
    # If exception occurs, logs it and shows error message box
    raise ValueError('Something went wrong')
```

**Signature**: `catchExceptInMsgBox(func, errorMsg=None, onlyExceptions=None, reRaise=True, addExecInfo=True)`

- `reRaise` defaults to `True` — exception is re-raised after showing the dialog
- `addExecInfo` defaults to `True` — traceback is shown in the dialog's detail section
- `errorMsg` — custom message for the dialog; defaults to `'Runtime error in {func_name}: {exception}'`
- This decorator must be used **directly** (`@catchExceptInMsgBox`), not as a factory (`@catchExceptInMsgBox(errorMsg='...')` would fail since `func` is a required positional arg)

## @cachedWithTtl

Cache function results with a time-to-live expiry:

```python
from core.Decorators import cachedWithTtl

@cachedWithTtl(5000)  # Cache for 5000ms (5 seconds)
def expensiveQuery(userId: int):
    # Result is cached; re-executed only after TTL expires
    return db.fetchUser(userId)

# Inspect / clear cache
expensiveQuery.cache_info()   # {'size': N, 'ttlMs': 5000}
expensiveQuery.cache_clear()  # Invalidate all cached entries
```

Cache key is derived from `(*args, **kwargs)`. Each unique argument combination is cached separately.

## SignalBlocker

Context manager for blocking Qt signals:

```python
from core.Decorators import SignalBlocker

widget = self.widgetManager.get('slider')

# Block signals during update
with SignalBlocker(widget):
    widget.setValue(50)  # No valueChanged signal emitted
```

## Usage Examples

### Singleton Service

```python
from core.Decorators import singleton

@singleton
class CacheService:
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        self.cache[key] = value

# Use anywhere
cache = CacheService()
cache.set('key', 'value')
```

### Form Data with autoStrip

```python
from dataclasses import dataclass
from core.Decorators import autoStrip

@autoStrip
@dataclass
class FormData:
    username: str
    email: str
    phone: str

# User input with whitespace
form = FormData(
    username='  john_doe  ',
    email='  john@example.com  ',
    phone='  123-456-7890  '
)

# Automatically stripped
print(form.username)  # 'john_doe'
```

### Exception Handling

```python
from core.Decorators import catchExceptInMsgBox

class DataService:
    @catchExceptInMsgBox(errorMsg='Failed to save data')
    def saveData(self, data):
        # If error occurs, shows message box
        with open('data.json', 'w') as f:
            json.dump(data, f)
```

### Signal Blocking

```python
from core.Decorators import SignalBlocker

class MyHandler(BaseCtlHandler):
    def updateSliders(self, values):
        # Block signals for batch update
        for name, value in values.items():
            widget = self.widgetManager.get(name)
            with SignalBlocker(widget):
                widget.setValue(value)
```

## Best Practices

### ✅ DO

```python
# Use @singleton for services
@singleton
class DatabaseService:
    pass

# Use SignalBlocker for programmatic updates
with SignalBlocker(widget):
    widget.setValue(value)

# Use @autoStrip for user input
@autoStrip
@dataclass
class UserInput:
    name: str
```

### ❌ DON'T

```python
# Don't use @singleton on non-services
@singleton
class UserData:  # Wrong! Not a service
    pass

# Don't forget SignalBlocker
widget.setValue(value)  # Triggers signal!
```

## Related Documentation

- [WidgetManager](05-widget-management.md) - Signal suppression
- [Exceptions](09-exceptions.md) - Exception handling
