# BaseController

Base controller class for UI components following the Observer pattern.

## Overview

`BaseController` is the foundation for all UI controllers in the application. It provides a standardized way to handle UI events, widget management, and follows the Observer pattern for event handling. It uses a metaclass to enforce required attributes and automatically connects signals.

## API Reference

### Class Definition

```python
class BaseController(metaclass=ControllerMeta):
    slot_map: Dict[str, List[str]] = {}  # Required: Maps event names to widget/signal pairs
    signal_connected = False
    is_auto_connect_signal = True
```

### Properties

- `slot_map` (Dict[str, List[str]]): **Required** - Maps event names to [widget_name, signal_name] pairs
- `widgetManager` (WidgetManager): Widget management instance
- `publisher` (Publisher): Event publisher for Observer pattern
- `controllerName` (str): Name of the controller class
- `signal_connected` (bool): Whether signals are connected
- `is_auto_connect_signal` (bool): Whether to auto-connect signals on init

### Methods

#### `__init__(self, parent=None)`
Initialize the controller.

**Parameters:**
- `parent` (QObject, optional): Parent object

**Features:**
- Automatically sets up widget manager and publisher
- Auto-loads handler classes from `app.windows.handlers` or current module
- Connects signals if `is_auto_connect_signal` is True

#### `setupUi(self, widget)`
Abstract method to set up UI components.

**Parameters:**
- `widget`: Widget to set up

**Note:** Must be implemented by subclasses

#### `setupHandler(self)`
Setup handler and connect signals.
Searches for handler classes in:
- `app.windows.handlers.{ControllerName}Handler`
- `{current_module}.{ControllerName}Handler`
- `{current_module}.{ControllerNameWithoutController}Handler`
- `{current_module}.{ControllerNameWithoutWidget}Handler`

#### `_connect_signals(self)`
Internal method to connect signals to handlers.

**Note:** Called automatically during initialization if `is_auto_connect_signal` is True

## Usage Examples

### Basic Controller Implementation

```python
from core.BaseController import BaseController
from PySide6.QtWidgets import QPushButton, QTextEdit

class MyController(BaseController):
    # Required: Define event to widget/signal mapping
    slot_map = {
        'button_clicked': ['submitButton', 'clicked'],
        'text_changed': ['textEdit', 'textChanged']
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def setupUi(self, widget):
        """Set up UI components"""
        # Initialize UI widgets
        self.submitButton = QPushButton("Submit")
        self.textEdit = QTextEdit()
        # ... other UI setup
```

### Widget Access

```python
class MyController(BaseController):
    slot_map = {}
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def access_widgets(self):
        # Access widgets using widget manager
        button = self.widgetManager.get("submitButton")
        text_edit = self.widgetManager.get("textEdit")
        
        # Set properties
        button.setText("Submit")
        text_edit.setPlainText("Hello World")
```

### Handler Integration

```python
# The controller automatically looks for handlers in:
# - app.windows.handlers.{ControllerName}Handler
# - {current_module}.{ControllerName}Handler

# Example handler file: app/windows/handlers/MyControllerHandler.py
from core.Observer import Subscriber

class MyControllerHandler(Subscriber):
    def __init__(self, widgetManager, events):
        super().__init__(events)
        self.widgetManager = widgetManager

    # Standard: the "onEventName" method will be called automatically when signal fired.
    def onButtonClicked(self, *args, **kwargs):
        print("Button clicked!")
    
    def onTextChanged(self, *args, **kwargs):
        print("Text changed!")
```

## Best Practices

1. **Always define slot_map**: This is required and maps events to [widget_name, signal_name] pairs
2. **Implement setupUi**: Required abstract method for UI initialization
3. **Use widgetManager.get()**: For accessing widgets by name
4. **Create handler classes**: Place handlers in `app.windows.handlers` or current module
5. **Handle errors gracefully**: Use try-catch blocks in handler methods

## Metaclass Features

The `ControllerMeta` metaclass provides:
- **Required attribute enforcement**: Ensures `slot_map` is defined
- **Slot map inheritance**: Combines slot maps from parent classes
- **Automatic handler loading**: Searches for handler classes automatically

## Dependencies

- `core.WidgetManager` - Widget management utilities
- `core.Observer.Publisher` - Event publishing system
- `abc.ABC` - Abstract base class functionality
- `PySide6.QtCore` - Qt core functionality
- `box` - Box library for dictionary access

## Related Components

- [WidgetManager](WidgetManager.md) - Widget management utilities
- [Observer](Observer.md) - Event publishing system
- [Exceptions](Exceptions.md) - Error handling
