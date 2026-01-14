# AppHelper

Application helper utilities for common app operations.

## Overview

`AppHelper` provides static utility methods for accessing application information, configuration, and common app-related operations.

## API Reference

### Class Definition

```python
class AppHelper:
    @staticmethod
    def getConfig() -> 'core.Config'
    @staticmethod
    def getAppName() -> str
    @staticmethod
    def getAppVersion() -> str
    @staticmethod
    def getAppDisplayName() -> str
    @staticmethod
    def getAppIconPath() -> str
    @staticmethod
    def getAppIcon() -> QIcon
```

### Methods

#### `getConfig() -> 'core.Config'`
Get the application configuration instance.

**Returns:**
- `core.Config`: Configuration instance

#### `getAppName() -> str`
Get the application name from configuration.

**Returns:**
- `str`: Application name (default: 'Qt Base App - by Zuko')

#### `getAppVersion() -> str`
Get the application version from configuration.

**Returns:**
- `str`: Application version (default: '0.0.01')

#### `getAppDisplayName() -> str`
Get the formatted application display name.

**Returns:**
- `str`: Formatted display name (e.g., 'My App | v1.0.0')

#### `getAppIconPath() -> str`
Get the path to the application icon.

**Returns:**
- `str`: Path to icon file

#### `getAppIcon() -> QIcon`
Get the application icon as QIcon.

**Returns:**
- `QIcon`: Application icon

## Usage Examples

### Basic App Information

```python
from core.Utils import AppHelper

# Get app information
app_name = AppHelper.getAppName()
app_version = AppHelper.getAppVersion()
display_name = AppHelper.getAppDisplayName()

print(f"App: {app_name}")
print(f"Version: {app_version}")
print(f"Display: {display_name}")
```

### Configuration Access

```python
from core.Utils import AppHelper

# Get configuration instance
config = AppHelper.getConfig()

# Access configuration values
app_name = config.get('app.name', 'Default App')
app_version = config.get('app.version', '1.0.0')
debug_mode = config.get('app.debug', False)

print(f"App: {app_name}")
print(f"Version: {app_version}")
print(f"Debug: {debug_mode}")
```

### Icon Management

```python
from core.Utils import AppHelper
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel

app = QApplication([])
window = QMainWindow()

# Get app icon
icon_path = AppHelper.getAppIconPath()
print(f"Icon path: {icon_path}")

# Set window icon
icon = AppHelper.getAppIcon()
window.setWindowIcon(icon)

# Display icon in label
label = QLabel()
label.setPixmap(icon.pixmap(64, 64))
window.setCentralWidget(label)

window.show()
app.exec()
```

### Window Title Setup

```python
from core.Utils import AppHelper
from PySide6.QtWidgets import QApplication, QMainWindow

app = QApplication([])
window = QMainWindow()

# Set window title with app name and version
display_name = AppHelper.getAppDisplayName()
window.setWindowTitle(display_name)

# Set window icon
window.setWindowIcon(AppHelper.getAppIcon())

window.show()
app.exec()
```

### Configuration Updates

```python
from core.Utils import AppHelper

# Get configuration
config = AppHelper.getConfig()

# Update app information
config.set('app.name', 'My Custom App')
config.set('app.version', '2.0.0')
config.set('app.debug', True)

# Save configuration
config.save()

# Verify changes
app_name = AppHelper.getAppName()
app_version = AppHelper.getAppVersion()
print(f"Updated app: {app_name} v{app_version}")
```

### Error Handling

```python
from core.Utils import AppHelper
from core.Exceptions import ConfigError

try:
    # Get app information
    app_name = AppHelper.getAppName()
    app_version = AppHelper.getAppVersion()
    
    print(f"App: {app_name} v{app_version}")

except ConfigError as e:
    print(f"Configuration error: {e}")
    # Use defaults
    app_name = "Default App"
    app_version = "1.0.0"
```

## Best Practices

1. **Use static methods**: All methods are static, no need to instantiate
2. **Handle configuration errors**: Always handle potential ConfigError exceptions
3. **Use for UI setup**: Perfect for setting up window titles and icons
4. **Cache when possible**: Cache frequently accessed values for performance
5. **Provide fallbacks**: Always have fallback values for missing configuration

## Dependencies

- `core.Config` - Configuration management
- `core.Utils.PathHelper` - Path utilities
- `PySide6.QtGui.QIcon` - Icon handling

## Related Components

- [Config](core/Config.md) - Configuration management
- [PathHelper](core/Utils.md) - Path utilities
