# WidgetManager

Widget management system for UI components and controllers.

## Overview

`WidgetManager` provides a centralized way to manage and access widgets in controllers and UI components. It supports dot notation for widget access and provides type-safe widget retrieval.

## API Reference

### Class Definition

```python
class WidgetManager:
    def __init__(self, controller):
        self.controller = controller
        self.type = int  # 1 for controller, 2 for UI
        self.widgetClassName = str
        self.app = Union[QApplication, QCoreApplication]
```

### Properties

- `controller`: The controller/component that owns this manager
- `type` (int): Type of widget manager (1 for controller, 2 for UI)
- `widgetClassName` (str): Name of the controller/component class
- `app` (Union[QApplication, QCoreApplication]): Application instance

### Methods

#### `__init__(self, controller)`
Initialize widget manager.

**Parameters:**
- `controller`: Controller or component that owns this manager

**Features:**
- Automatically determines type based on controller class name
- Sets up application context

#### `get(self, widgetName: str) -> Union[QObject, QWidget, QTextEdit, QLabel, QLineEdit, QTableView, QTableWidget, QSpinBox]`
Get a widget by name using dot notation.

**Parameters:**
- `widgetName` (str): Widget name (e.g., "mainWindow.button1")

**Returns:**
- `Union[QObject, QWidget, ...]`: The requested widget

**Raises:**
- `Exception`: If widget not found

**Example:**
```python
# Access nested widgets
button = widget_manager.get("mainWindow.submitButton")
text_edit = widget_manager.get("content.textEdit")
```

#### `set(self, name: str, value, saveToConfig: bool = False) -> None`
Set a widget attribute value.

**Parameters:**
- `name` (str): Widget name (dot notation not allowed)
- `value`: Value to set
- `saveToConfig` (bool): Whether to save to config file

**Raises:**
- `NotImplementedError`: If name contains dots

**Example:**
```python
# Set widget attribute
widget_manager.set("submitButton", new_button)

# Set and save to config
widget_manager.set("windowTitle", "My App", saveToConfig=True)
```

#### `load(self, name: str, default=None) -> None`
Load value from config and apply to widget.

**Parameters:**
- `name` (str): Widget name
- `default`: Default value if not found in config

**Example:**
```python
# Load saved value for checkbox
widget_manager.load("rememberMeCheckbox", default=False)
```

#### `doActionSuppressSignal(self, widgetName: str, closure: Callable) -> None`
Execute action on widget with signals temporarily blocked.

**Parameters:**
- `widgetName` (str): Name of widget to act on
- `closure` (Callable): Action to execute

**Raises:**
- `ValueError`: If closure is not callable

**Example:**
```python
# Suppress signals during widget update
widget_manager.doActionSuppressSignal("textEdit", lambda w: w.setText("New text"))
```

## Usage Examples

### Basic Widget Access

```python
from core.BaseController import BaseController
from PySide6.QtWidgets import QPushButton, QLineEdit

class MyController(BaseController):
    slot_map = {}
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # widget_manager is automatically created by BaseController
    
    def access_widgets(self):
        # Access widgets using dot notation
        button = self.widget_manager.get("mainWindow.submitButton")
        line_edit = self.widget_manager.get("mainWindow.nameInput")
        
        # Set properties
        button.setText("Submit")
        line_edit.setPlaceholderText("Enter your name")
```

### Widget Attribute Management

```python
from core.BaseController import BaseController

class MyController(BaseController):
    slot_map = {}
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def manage_attributes(self):
        # Set widget attributes
        self.widget_manager.set("submitButton", new_button)
        self.widget_manager.set("windowTitle", "My App", saveToConfig=True)
        
        # Access widgets
        button = self.widget_manager.get("submitButton")
        button.setText("Updated Button")
```

### Signal Suppression

```python
from core.BaseController import BaseController

class MyController(BaseController):
    slot_map = {}
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def update_widget_silently(self):
        # Update widget without triggering signals
        self.widget_manager.doActionSuppressSignal("textEdit", lambda w: w.setText("New text"))
        
        # Multiple operations with suppressed signals
        self.widget_manager.doActionSuppressSignal("comboBox", lambda w: w.setCurrentIndex(0))
```

### Error Handling

```python
from core.BaseController import BaseController

class MyController(BaseController):
    slot_map = {}
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def safe_widget_access(self):
        try:
            # Try to access widget
            button = self.widget_manager.get("mainWindow.submitButton")
            button.setText("Success")
        except Exception as e:
            print(f"Widget not found: {e}")
            # Handle missing widget
            self.create_missing_widget()
    
    def create_missing_widget(self):
        # Create missing widget
        from PySide6.QtWidgets import QPushButton
        button = QPushButton("Submit")
        # Add to layout...
```

## Best Practices

1. **Use dot notation**: Leverage dot notation for clear widget hierarchy
2. **Handle errors**: Always handle Exception for missing widgets
3. **Use signal suppression**: Use `doActionSuppressSignal` when updating widgets programmatically
4. **Save to config**: Use `saveToConfig=True` for persistent settings
5. **Use consistent naming**: Use consistent naming conventions for widgets

## Dependencies

- `PySide6.QtCore.QCoreApplication` - Application instance
- `PySide6.QtWidgets.QApplication` - Application instance
- `PySide6.QtWidgets.QWidget` - Base widget class
- `core.QtAppContext` - Application context
- `core.Config` - Configuration management

## Related Components

- [BaseController](BaseController.md) - Uses WidgetManager
- [Observer](Observer.md) - Event system
