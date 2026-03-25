# Config - Configuration Management

> **Singleton configuration manager with JSON persistence and nested key access**

## Overview

`Config` manages application configuration:

- Singleton pattern (one instance per application)
- JSON file persistence (`data/config/config.json`)
- Nested key access with dot notation
- Thread-safe operations (QMutex)
- Auto-create default config

## API Reference

### Singleton Access

```python
from core import Config

config = Config()  # Always returns same instance
# Or via QtAppContext
from core import QtAppContext
config = QtAppContext.globalInstance().config
```

### Get Value

```python
value = config.get('key.nested.path', default=None)
```

### Set Value

```python
config.set('key.nested.path', value)
```

### Save to Disk

```python
config.save()
```

### Load from Disk

```python
config.load()  # Auto-called on first access
```

## Usage Examples

### Basic Usage

```python
from core import Config

config = Config()

# Get values
appName = config.get('app.name')
theme = config.get('ui.theme', default='auto')

# Set values
config.set('ui.theme', 'dark')
config.set('app.debug', True)

# Save to disk
config.save()
```

### Nested Keys

```python
config = Config()

# Set nested values
config.set('database.host', 'localhost')
config.set('database.port', 5432)
config.set('database.credentials.username', 'admin')

# Get nested values
host = config.get('database.host')
username = config.get('database.credentials.username')
```

### Default Configuration

```python
# Default config created automatically if file doesn't exist
{
    "app": {
        "name": "Base Qt Application",
        "version": "1.0.0",
        "debug": false
    },
    "ui": {
        "theme": "auto",
        "language": "en",
        "high_dpi": true
    },
    "logging": {
        "level": "INFO",
        "file": "app.log"
    },
    "consolelog": {
        "enable": true,
        "level": "DEBUG"
    }
}
```

### Application Settings

```python
from core import Config

class AppSettings:
    def __init__(self):
        self.config = Config()
    
    def getTheme(self):
        return self.config.get('ui.theme', default='auto')
    
    def setTheme(self, theme):
        self.config.set('ui.theme', theme)
        self.config.save()
    
    def isDebugMode(self):
        return self.config.get('app.debug', default=False)
```

### WidgetManager Integration

```python
# WidgetManager automatically uses Config for persistence
from core import BaseCtlHandler

class SettingsHandler(BaseCtlHandler):
    def onSaveSettings(self):
        # Saves to config automatically
        self.widgetManager.set('theme', 'dark', saveToConfig=True)
        
        # Config key: "SettingsController.theme"
```

## File Location

**Path:** `{PROJECT_ROOT}/data/config/config.json`

**Auto-created:** If file doesn't exist, default config is created

**Format:** JSON with indentation (4 spaces)

## Best Practices

### ✅ DO

```python
# Use descriptive nested keys
config.set('database.connection.timeout', 30)
config.set('api.endpoints.users', '/api/v1/users')

# Provide defaults
theme = config.get('ui.theme', default='auto')

# Save after important changes
config.set('user.preferences.language', 'vi')
config.save()

# Use constants for keys
class ConfigKeys:
    APP_NAME = 'app.name'
    UI_THEME = 'ui.theme'

theme = config.get(ConfigKeys.UI_THEME)
```

### ❌ DON'T

```python
# Don't use flat keys
config.set('database_host', 'localhost')  # Use 'database.host'

# Don't forget to save
config.set('important.setting', value)
# Missing: config.save()

# Don't catch ConfigError silently
try:
    config.load()
except:
    pass  # Wrong! Handle properly

# Don't modify config file manually while app running
# Use config.set() and config.save() instead
```

## Thread Safety

- ✅ `get()`: Thread-safe (QMutex)
- ✅ `set()`: Thread-safe (QMutex)
- ✅ `save()`: Thread-safe (QMutex)
- ✅ `load()`: Thread-safe (QMutex)

## Common Patterns

### Application Configuration

```python
from core import Config

class AppConfig:
    def __init__(self):
        self.config = Config()
    
    @property
    def appName(self):
        return self.config.get('app.name', default='My App')
    
    @property
    def version(self):
        return self.config.get('app.version', default='1.0.0')
    
    @property
    def isDebug(self):
        return self.config.get('app.debug', default=False)
    
    def setDebug(self, enabled):
        self.config.set('app.debug', enabled)
        self.config.save()
```

### User Preferences

```python
class UserPreferences:
    def __init__(self):
        self.config = Config()
    
    def getPreference(self, key, default=None):
        return self.config.get(f'user.preferences.{key}', default=default)
    
    def setPreference(self, key, value):
        self.config.set(f'user.preferences.{key}', value)
        self.config.save()

# Usage
prefs = UserPreferences()
prefs.setPreference('theme', 'dark')
prefs.setPreference('language', 'vi')
theme = prefs.getPreference('theme', default='auto')
```

### Feature Flags

```python
class FeatureFlags:
    def __init__(self):
        self.config = Config()
    
    def isEnabled(self, feature):
        return self.config.get(f'features.{feature}.enabled', default=False)
    
    def enable(self, feature):
        self.config.set(f'features.{feature}.enabled', True)
        self.config.save()
    
    def disable(self, feature):
        self.config.set(f'features.{feature}.enabled', False)
        self.config.save()

# Usage
flags = FeatureFlags()
if flags.isEnabled('experimental_ui'):
    # Use experimental UI
    pass
```

## Related Documentation

- [QtAppContext](01-application-context.md) - Config access
- [WidgetManager](05-widget-management.md) - Widget persistence
- [PathHelper](10-utilities.md) - Path management

## Troubleshooting

**Q: Config file not found**

```python
# Auto-created with defaults
config = Config()
config.load()  # Creates default config if missing
```

**Q: Nested key not working**

```python
# Ensure parent keys exist
config.set('a.b.c', value)  # Auto-creates a.b if missing

# Get with default
value = config.get('a.b.c', default=None)
```

**Q: Changes not persisted**

```python
# Must call save()
config.set('key', 'value')
config.save()  # Don't forget!
```
