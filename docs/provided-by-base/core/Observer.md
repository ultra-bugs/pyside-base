# Observer

Observer pattern implementation for event-driven communication.

## Overview

The Observer pattern provides a way to notify multiple objects about changes in state. This implementation includes a `Publisher` (Subject) class and a `Subscriber` (Observer) base class for handling events.

## API Reference

### Publisher Class

```python
class Publisher:
    def __init__(self):
        self.globalSubscribers = []
        self.eventSpecificSubscribers = {}
        self._lock = QMutex()
```

### Properties

- `globalSubscribers` (List[Subscriber]): List of global subscribers
- `eventSpecificSubscribers` (Dict[str, List[Subscriber]]): Event-specific subscribers
- `_lock` (QMutex): Thread safety lock

### Methods

#### `subscribe(self, subscriber: Subscriber, event: str = None) -> Publisher`
Subscribe to events.

**Parameters:**
- `subscriber` (Subscriber): Subscriber instance
- `event` (str, optional): Specific event name (None for all events)

**Returns:**
- `Publisher`: Self for chaining

#### `unsubscribe(self, subscriber: Subscriber, event: str = None) -> Publisher`
Unsubscribe from events.

**Parameters:**
- `subscriber` (Subscriber): Subscriber instance
- `event` (str, optional): Specific event name (None for all events)

**Returns:**
- `Publisher`: Self for chaining

#### `notify(self, event: str, *args, **kwargs) -> Publisher`
Notify subscribers of an event.

**Parameters:**
- `event` (str): Event name
- `*args`: Positional arguments
- `**kwargs`: Keyword arguments

**Returns:**
- `Publisher`: Self for chaining

#### `connect(self, widget, signalName: str, event: str, *args, **kwargs) -> Publisher`
Connect a Qt signal to an event.

**Parameters:**
- `widget`: Qt widget
- `signalName` (str): Signal name
- `event` (str): Event name
- `*args`: Positional arguments
- `**kwargs`: Keyword arguments

**Returns:**
- `Publisher`: Self for chaining

### Subscriber Class

```python
class Subscriber:
    def __init__(self, events: List[str], isGlobalSubscriber=False):
        self.events = events
        self.isGlobalSubscriber = isGlobalSubscriber
```

### Properties

- `events` (List[str]): List of events to subscribe to
- `isGlobalSubscriber` (bool): Whether subscriber listens to all events

### Methods

#### `update(self, event: str, *args, **kwargs) -> None`
Handle an event notification with smart parameter injection.

**Parameters:**
- `event` (str): Event name
- `*args`: Positional arguments
- `**kwargs`: Keyword arguments

## Usage Examples

### Basic Event Publishing

```python
from core.Observer import Publisher, Subscriber

# Create publisher
publisher = Publisher()

# Create subscriber
class MySubscriber(Subscriber):
    def __init__(self):
        super().__init__(['user_login', 'user_logout'])
    
    def onUserLogin(self, user_id, username):
        print(f"User {username} (ID: {user_id}) logged in")
    
    def onUserLogout(self, user_id):
        print(f"User {user_id} logged out")

# Subscribe to events (handled automatically in __init__)
subscriber = MySubscriber()

# Publish events
publisher.notify('user_login', user_id=123, username='john_doe')
publisher.notify('user_logout', user_id=123)
```

### Global Subscriber

```python
from core.Observer import Publisher, Subscriber

# Create publisher
publisher = Publisher()

# Create global subscriber
class GlobalSubscriber(Subscriber):
    def __init__(self):
        super().__init__([], isGlobalSubscriber=True)
    
    def update(self, event, *args, **kwargs):
        print(f"Global subscriber received event: {event}")
        print(f"Args: {args}, Kwargs: {kwargs}")

# Subscribe to all events
subscriber = GlobalSubscriber()
publisher.subscribe(subscriber)  # No event specified = global

# Publish events
publisher.notify('user_login', user_id=123)
publisher.notify('data_updated', data={'key': 'value'})
```

### Qt Signal Integration

```python
from core.Observer import Publisher
from PySide6.QtWidgets import QPushButton

# Create publisher
publisher = Publisher()

# Create Qt widget
button = QPushButton("Click Me")

# Connect Qt signal to event
publisher.connect(button, 'clicked', 'button_clicked', button_text='My Button')

# Subscribe to event
class ButtonSubscriber(Subscriber):
    def __init__(self):
        super().__init__(['button_clicked'])
    
    def onButtonClicked(self, button_text):
        print(f"Button clicked: {button_text}")

subscriber = ButtonSubscriber()

# When button is clicked, it will trigger the event
```

### Smart Parameter Injection

```python
from core.Observer import Publisher, Subscriber

# Create publisher
publisher = Publisher()

# Create subscriber with type hints
class SmartSubscriber(Subscriber):
    def __init__(self):
        super().__init__(['user_action'])
    
    def onUserAction(self, user_id: int, action: str, timestamp: float):
        print(f"User {user_id} performed {action} at {timestamp}")

# Subscribe to events
subscriber = SmartSubscriber()

# Publish event with mixed arguments
publisher.notify('user_action', 
                user_id=123, 
                action='login', 
                timestamp=1234567890.0,
                extra_data='ignored')
```

### Event Unsubscription

```python
from core.Observer import Publisher, Subscriber

# Create publisher
publisher = Publisher()

# Create subscriber
class MySubscriber(Subscriber):
    def __init__(self):
        super().__init__(['event1', 'event2'])
    
    def onEvent1(self, data):
        print(f"Event1: {data}")
    
    def onEvent2(self, data):
        print(f"Event2: {data}")

# Subscribe to events
subscriber = MySubscriber()

# Publish events
publisher.notify('event1', 'data1')
publisher.notify('event2', 'data2')

# Unsubscribe from all events
publisher.unsubscribe(subscriber)

# These won't be received anymore
publisher.notify('event1', 'data3')
publisher.notify('event2', 'data4')
```

### Error Handling

```python
from core.Observer import Publisher, Subscriber

# Create publisher
publisher = Publisher()

# Create subscriber with error handling
class ErrorHandlingSubscriber(Subscriber):
    def __init__(self):
        super().__init__(['error_event'])
    
    def onErrorEvent(self, error_message):
        print(f"Error handled: {error_message}")
        # Handle error appropriately

# Subscribe to events
subscriber = ErrorHandlingSubscriber()

# Publish error event
publisher.notify('error_event', error_message='Something went wrong')
```

## Best Practices

1. **Use descriptive event names**: Choose clear, descriptive names for events
2. **Handle errors gracefully**: Always handle potential errors in event handlers
3. **Use type hints**: Use type hints in event handler methods for better parameter matching
4. **Unsubscribe when done**: Always unsubscribe from events when no longer needed
5. **Use appropriate event granularity**: Don't make events too specific or too general
6. **Test thoroughly**: Test event handling thoroughly to ensure proper communication
7. **Naming Convention**: Event handlers should be named `onEventName` (camelCase) corresponding to event `event_name` (snake_case) or `eventName` (camelCase).

## Dependencies

- `PySide6.QtCore.QMutex` - Thread safety
- `PySide6.QtCore.QMutexLocker` - Mutex locking
- `inspect` - Method signature inspection
- `core.Utils.PythonHelper` - Type compatibility checking
- `core.Logging.logger` - Logging
- `core.Exceptions.ExceptionHandler` - Exception handling
- `caseconverter` - String case conversion

## Related Components

- [Logging](Logging.md) - Logging system
- [Exceptions](Exceptions.md) - Exception handling
- [Utils](Utils.md) - Utility functions
