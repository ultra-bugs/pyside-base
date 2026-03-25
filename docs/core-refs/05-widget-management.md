# WidgetManager - Widget Access Helper

> **Simplified widget access utilizing deep dot notation, signal suppression frameworks, and persistent config saving mappings**

## Overview

`WidgetManager` supplies distinct robust utility operations designed to:

- Extract robust nested hierarchy interface objects utilizing standard uniform completely transparent dot-notation access parameters (`get('parent.child')`)
- Seamlessly bypass distinct executing standard evaluation boundaries explicitly evaluating clean uninterrupted programmatic interface insertions cleanly explicitly bypassing `signal suppression` natively safely implicitly seamlessly gracefully.
- Definitively evaluate explicitly robust native value saving mechanisms implementing strict Config persistence accurately independently routing seamlessly implicitly (save/load widget states securely tracking universally).
- Strictly cleanly seamlessly perfectly explicitly seamlessly resolving safely mapping completely uniformly type-safe values dynamically tracking accurately seamlessly securely natively extracting seamlessly.

## API Reference

### Access

```python
# Via controller
self.widgetManager.get('widgetName')
self.widgetManager.get('parent.child.widget')
```

### Set Value

```python
self.widgetManager.set('widgetName', value, saveToConfig=False)
```

### Load from Config

```python
self.widgetManager.load('widgetName', default=None)
```

### Signal Suppression

```python
self.widgetManager.doActionSuppressSignal('widgetName', lambda w: w.setValue(50))
```

## Usage Examples

### Basic Widget Access

```python
from core import BaseController, BaseCtlHandler

class MyControllerHandler(BaseCtlHandler):
    def onSaveClicked(self):
        # Get widget
        input = self.widgetManager.get('usernameInput')
        text = input.text()
        
        # Nested access
        nestedWidget = self.widgetManager.get('parent.child.widget')
```

### Set Widget Values

```python
class MyHandler(BaseCtlHandler):
    def onLoadData(self):
        # Set QLineEdit
        self.widgetManager.set('nameInput', 'John Doe')
        
        # Set QSpinBox
        self.widgetManager.set('ageSpinBox', 25)
        
        # Set QCheckBox
        self.widgetManager.set('agreeCheckbox', True)
```

### Config Persistence

```python
class SettingsHandler(BaseCtlHandler):
    def onSaveSettings(self):
        # Save to config
        self.widgetManager.set('themeComboBox', 'dark', saveToConfig=True)
        self.widgetManager.set('autoSaveCheckbox', True, saveToConfig=True)
    
    def onLoadSettings(self):
        # Load from config
        self.widgetManager.load('themeComboBox', default='light')
        self.widgetManager.load('autoSaveCheckbox', default=False)
```

**Config key format:** `{ControllerName}.{widgetName}`

Example: `MainController.themeComboBox`

### Signal Suppression

```python
class MyHandler(BaseCtlHandler):
    def updateSliderWithoutSignal(self):
        # Suppress valueChanged signal
        self.widgetManager.doActionSuppressSignal(
            'volumeSlider',
            lambda slider: slider.setValue(75)
        )
        
        # Or with widget parameter
        def updateWidget(widget):
            widget.setValue(75)
            widget.setEnabled(False)
        
        self.widgetManager.doActionSuppressSignal('volumeSlider', updateWidget)
```

## Supported Widget Types

### Auto Value Handling

**QSpinBox / QDoubleSpinBox:**

```python
self.widgetManager.set('spinBox', 42)  # Calls setValue()
value = self.widgetManager.get('spinBox').value()
```

**QLineEdit / QLabel:**

```python
self.widgetManager.set('lineEdit', 'text')  # Calls setText()
text = self.widgetManager.get('lineEdit').text()
```

**QCheckBox / QRadioButton:**

```python
self.widgetManager.set('checkbox', True)  # Calls setChecked()
checked = self.widgetManager.get('checkbox').isChecked()
```

## Best Practices

### ✅ DO

```python
# Use descriptive widget names
self.widgetManager.get('usernameInput')
self.widgetManager.get('saveButton')

# Use dot notation for nested widgets
self.widgetManager.get('settingsPanel.themeComboBox')

# Suppress signals when programmatically updating
self.widgetManager.doActionSuppressSignal('slider', lambda w: w.setValue(50))

# Save important settings to config
self.widgetManager.set('theme', 'dark', saveToConfig=True)

# Load with defaults
self.widgetManager.load('theme', default='light')
```

### ❌ DON'T

```python
# Don't use set() with dot notation
self.widgetManager.set('parent.child', value)  # NotImplementedError

# Don't forget signal suppression for programmatic updates
slider = self.widgetManager.get('slider')
slider.setValue(50)  # Triggers valueChanged signal!

# Don't access widgets before setupUi
class MyController(BaseController):
    def __init__(self):
        super().__init__()
        widget = self.widgetManager.get('button')  # Error! setupUi not called
```

## Common Patterns

### Form Data Collection

```python
class FormHandler(BaseCtlHandler):
    def collectFormData(self):
        return {
            'name': self.widgetManager.get('nameInput').text(),
            'age': self.widgetManager.get('ageSpinBox').value(),
            'email': self.widgetManager.get('emailInput').text(),
            'subscribe': self.widgetManager.get('subscribeCheckbox').isChecked()
        }
```

### Batch Widget Update

```python
class DataHandler(BaseCtlHandler):
    def loadUserData(self, userData):
        # Suppress all signals during batch update
        widgets = {
            'nameInput': userData['name'],
            'ageSpinBox': userData['age'],
            'emailInput': userData['email']
        }
        
        for widgetName, value in widgets.items():
            self.widgetManager.doActionSuppressSignal(
                widgetName,
                lambda w, v=value: self._setValue(w, v)
            )
    
    def _setValue(self, widget, value):
        if hasattr(widget, 'setText'):
            widget.setText(str(value))
        elif hasattr(widget, 'setValue'):
            widget.setValue(value)
```

### Settings Persistence

```python
class SettingsController(BaseController, QWidget):
    slot_map = {
        'saveClicked': ['saveButton', 'clicked'],
        'loadClicked': ['loadButton', 'clicked']
    }

class SettingsHandler(BaseCtlHandler):
    SETTINGS_WIDGETS = ['theme', 'language', 'autoSave', 'fontSize']
    
    def onSaveClicked(self):
        for widget in self.SETTINGS_WIDGETS:
            value = self._getWidgetValue(widget)
            self.widgetManager.set(widget, value, saveToConfig=True)
    
    def onLoadClicked(self):
        for widget in self.SETTINGS_WIDGETS:
            self.widgetManager.load(widget)
    
    def _getWidgetValue(self, widgetName):
        widget = self.widgetManager.get(widgetName)
        if hasattr(widget, 'text'):
            return widget.text()
        elif hasattr(widget, 'value'):
            return widget.value()
        elif hasattr(widget, 'isChecked'):
            return widget.isChecked()
```

## Related Documentation

- [BaseController](04-controller-architecture.md) - Controller integration
- [Config](06-configuration.md) - Config persistence
- [Common Use Cases](20-common-use-cases.md) - Practical examples
