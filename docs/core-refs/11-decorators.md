# Decorators

> **@singleton, @autoStrip, @catchExceptInMsgBox, SignalBlocker**

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
    # If exception occurs, shows message box
    raise ValueError('Something went wrong')

# With custom error message
@catchExceptInMsgBox(errorMsg='Operation failed')
def anotherOperation():
    raise ValueError('Error')

# Re-raise after showing
@catchExceptInMsgBox(reRaise=True)
def criticalOperation():
    raise ValueError('Critical error')
```

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
