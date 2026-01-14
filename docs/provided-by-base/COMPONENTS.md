# Component Architecture Guide

## Overview

Tất cả UI components trong App nên tuân theo pattern nhất quán với:
- File `.ui` cho giao diện (Qt Designer)
- File `Widget.py` cho logic UI và Controller
- File `Handler.py` cho xử lý events (Observer pattern)
## Benefits

### 1. **Separation of Concerns**
- UI logic (Widget) tách biệt với business logic (Handler)
- Dễ maintain và test từng layer riêng biệt

### 2. **Consistent Pattern**
- Tất cả components tuân theo cùng một pattern
- Developer dễ hiểu và implement

### 3. **Observer Pattern**
- Loose coupling giữa UI và logic
- Dễ extend và modify behavior

### 4. **Qt Designer Integration**
- UI được thiết kế bằng visual tool
- Tự động compile và sync

### 5. **Reusability**
- Components có thể tái sử dụng ở nhiều nơi
- Parameterizable và configurable


## Quick Start

### 1. Tạo Component Mới

```bash
# Tạo thư mục component
mkdir windows/components/MyComponent

# Tạo các files cần thiết:
# - MyComponent.ui (Qt Designer)
# - MyComponent.py (compiled UI)
# - MyComponentWidget.py (Widget + Controller)
# - MyComponentHandler.py (Event Handler)
# - __init__.py (Module exports)
```

### 2. Thiết Kế UI (.ui file)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <author>Zuko</author>
 <class>MyComponent</class>
 <widget class="QWidget" name="MyComponent">
  <!-- UI elements here -->
 </widget>
</ui>
```

### 3. Compile UI to Python

```bash
# Manual compile (nếu có pyside6-uic)
pyside6-uic MyComponent.ui -o MyComponent.py

# Hoặc dùng script
python scripts/compile_ui.py
```

### 4. Implement Widget

```python
from core import BaseController
from .MyComponent import Ui_MyComponent

class MyComponentWidget(BaseController, QWidget, Ui_MyComponent):
    # Observer pattern mapping
    slot_map = {
        'button_clicked': ['myButton', 'clicked'],
    }
    
    # External signals
    dataChanged = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        # Setup logic here
```

### 5. Implement Handler

```python
from core.Observer import Subscriber

class MyComponentHandler(Subscriber):
    def __init__(self, widget, events):
        super().__init__(events)
        self.widget = widget
    
    def on_button_clicked(self, data=None):
        # Handle event here
        pass
```

### 6. Sử Dụng Component

```python
from windows.components.MyComponent import MyComponentWidget

class ParentController(BaseController):
    def setup_components(self):
        # Tạo widget
        self.my_comp = MyComponentWidget(parent=self)
        
        # Connect signals
        self.my_comp.dataChanged.connect(self.on_data_changed)
        
        # Add to layout
        self.layout.addWidget(self.my_comp)
```

## Examples

### AccountTableWidget

```python
# UI: AccountTable.ui - Table với columns cho accounts
# Widget: AccountTableWidget.py - Hiển thị accounts, handle selection
# Handler: AccountTableHandler.py - Xử lý refresh, export, context menu

# Usage:
account_table = AccountTableWidget(site=site, parent=self)
account_handler = AccountTableHandler(account_table, account_table.events)
account_table.accountSelected.connect(self.on_account_selected)
```

### TaskSelectorWidget

```python
# UI: TaskSelector.ui - ComboBox với refresh button
# Widget: TaskSelectorWidget.py - Load tasks, manage selection
# Handler: TaskSelectorHandler.py - Xử lý selection change, refresh

# Usage:
task_selector = TaskSelectorWidget(parent=self)
task_handler = TaskSelectorHandler(task_selector, task_selector.events)
task_selector.taskSelected.connect(self.on_task_selected)
```

## Development Patterns

### Observer Pattern

Tất cả components sử dụng Observer pattern:

```python
# Widget định nghĩa slot_map
slot_map = {
    'event_name': ['widgetName', 'signalName'],
}

# Handler implement on_event_name methods
def on_event_name(self, data=None):
    # Handle event logic
    pass
```

### Signal Emission

Components emit signals cho external communication:

```python
class MyWidget(BaseController):
    # Define signals
    dataChanged = Signal(dict)
    itemSelected = Signal(object)
    
    def some_method(self):
        # Emit signals với data
        self.dataChanged.emit({'key': 'value'})
        self.itemSelected.emit(selected_item)
```

### Configuration Management

Components có thể save/load settings:

```python
def save_settings_to_config(self):
    config = Config()
    config.set('component.setting', self.get_setting(), True)

def load_settings_from_config(self):
    config = Config()
    setting = config.get('component.setting', default_value)
    self.set_setting(setting)
```

## Best Practices

### 1. UI Design
- Sử dụng meaningful object names
- Set tooltips và status tips
- Configure sane defaults
- `ComponentName.ui` - UI definition
- `ComponentName.py` - Generated UI code (DON'T EDIT)
- `ComponentNameWidget.py` - Widget implementation
- `ComponentNameHandler.py` - Event handler
- `__init__.py` - Module exports

### 2. Widget Implementation
- Kế thừa: `BaseController`, `QWidget`, `Ui_ComponentName`. Đúng thứ tự
- Định nghĩa `slot_map` đầy đủ
- Setup UI trong `__init__`
- Emit signals cho external communication
- Implement data getters/setters

### 3. Handler Implementation
- Kế thừa từ `Subscriber`
- Prefix methods với `on_`
- Handle exceptions properly
- Log important events
- Keep methods focused

### 4. Error Handling
- Wrap event handlers trong try-catch
- Log errors với context
- Graceful degradation
```python
def on_some_event(self, data=None):
    try:
        # Event handling logic
        pass
    except Exception as e:
        from core.Logging import logger
        logger.error(f"Error handling event: {e}")
```

### 5. Signal Management
- Emit typed signals với meaningful data
- Document signal parameters
- Use descriptive signal names

### 6. Logging
```python
from core.Logging import logger

logger.info("Component initialized")
logger.debug("Debug information")
logger.warning("Warning message")
logger.error("Error message")
```

## Testing Components

### Unit Testing
```python
def test_component_widget():
    widget = MyComponentWidget()
    assert widget.some_property == expected_value

def test_component_handler():
    widget = MyComponentWidget()
    handler = MyComponentHandler(widget, widget.events)
    handler.on_some_event()
    # Assert expected behavior
```

### Integration Testing
```python
def test_component_integration():
    parent = ParentController()
    parent.setup_components()
    # Test component interaction
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Check `__init__.py` exports
   - Verify file names match class names

2. **Slot Map Not Working**
   - Check widget object names trong `.ui` file
   - Verify signal names are correct

3. **Handler Not Receiving Events**
   - Ensure handler created với correct events
   - Check `BaseController.__init__` called

4. **UI Not Loading**
   - Verify `.py` file generated từ `.ui`
   - Check import paths

### Debug Tips

- Enable debug logging để trace events
- Use breakpoints trong event handlers
- Test components independently trước khi integrate
- Check Qt object names trong Designer

## Migration từ Old Pattern

Để migrate component cũ sang pattern mới:

1. **Tạo .ui file** từ existing UI code
2. **Generate .py file** từ .ui
3. **Extract Widget logic** từ old component
4. **Extract Handler logic** sang separate handler
5. **Update usage** trong parent controllers
6. **Test functionality** thoroughly
