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