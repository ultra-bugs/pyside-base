# Config

Configuration management system with thread-safe access and JSON persistence.

## Overview

`Config` is a singleton class that provides centralized configuration management for the application. It supports loading/saving configuration from JSON files, thread-safe access, and provides a convenient interface for accessing configuration values.

## API Reference

### Class Definition

```python
class Config:
    _instance: Config = None
    _config: Dict[str, Any] = {}
```

### Properties

- `isLoaded` (bool): Indicates if configuration has been loaded
- `_config` (Dict[str, Any]): Internal configuration storage
- `_config_file` (str): Path to configuration file

### Methods

#### `__new__(cls) -> Config`
Get singleton instance of Config.

**Returns:**
- `Config`: Singleton instance

#### `__call__(self, key: str = None) -> Any`
Get configuration value or entire config.

**Parameters:**
- `key` (str, optional): Configuration key

**Returns:**
- `Any`: Configuration value or entire config dict

#### `get(self, key: str, default: Any = None) -> Any`
Get configuration value with default fallback.

**Parameters:**
- `key` (str): Configuration key (supports dot notation)
- `default` (Any, optional): Default value if key not found

**Returns:**
- `Any`: Configuration value or default

#### `set(self, key: str, value: Any) -> None`
Set configuration value.

**Parameters:**
- `key` (str): Configuration key (supports dot notation)
- `value` (Any): Value to set

#### `load(self) -> Config`
Load configuration from file.

**Returns:**
- `Config`: Self for chaining

**Raises:**
- `ConfigError`: If file cannot be loaded

#### `save(self) -> None`
Save configuration to file.

**Raises:**
- `ConfigError`: If file cannot be saved

## Usage Examples

### Basic Configuration Access

```python
from core import Config

# Get singleton instance
config = Config()

# Access configuration values
app_name = config.get('app.name', 'Default App')
version = config.get('app.version', '1.0.0')

# Set configuration values
config.set('app.name', 'My Application')
config.set('database.host', 'localhost')
config.set('database.port', 5432)
```

### Nested Configuration

```python
from core import Config

config = Config()

# Access nested values using dot notation
db_config = config.get('database')
host = config.get('database.host')
port = config.get('database.port')

# Set nested values
config.set('database.connection.timeout', 30)
config.set('features.enable_logging', True)
```

### Configuration File Management

```python
from core import Config

config = Config()

# Load from default file (data/config/config.json)
config.load()

# Save current configuration
config.save()
```

### Thread-Safe Access

```python
from core import Config
import threading

config = Config()

def worker_thread():
    # Thread-safe access
    value = config.get('shared.value')
    config.set('shared.value', value + 1)

# Multiple threads can safely access config
threads = [threading.Thread(target=worker_thread) for _ in range(5)]
for thread in threads:
    thread.start()
```

### Configuration Validation

```python
from core import Config, ConfigError

config = Config()

try:
    # Load configuration
    config.load()
    
    # Validate required keys
    required_keys = ['app.name', 'app.version']
    for key in required_keys:
        if config.get(key) is None:
            raise ConfigError(f"Missing required configuration: {key}")
    
    print("Configuration loaded successfully")
    
except ConfigError as e:
    print(f"Configuration error: {e}")
```

## Configuration File Format

The configuration is stored in JSON format:

```json
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

## Best Practices

1. **Use dot notation**: For nested configuration keys
2. **Provide defaults**: Always provide default values for optional settings
3. **Validate on load**: Check for required configuration keys
4. **Handle errors**: Use try-catch blocks for configuration operations
5. **Save changes**: Call `save()` after modifying configuration
6. **Use singleton**: Access Config through singleton pattern

## Dependencies

- `PySide6.QtCore.QMutex` - Thread safety
- `core.Exceptions.ConfigError` - Error handling
- `core.Utils.PathHelper` - Path utilities
- `json` - JSON serialization

## Related Components

- [Exceptions](Exceptions.md) - Error handling
- [Utils](Utils.md) - Path utilities
- [Logging](Logging.md) - Logging system
