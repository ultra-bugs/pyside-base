# Core Components Index

This document provides a comprehensive index of all core components available in the base framework.

## Quick Reference

### Core Components (`core/`)
| Component | Description | Key Features |
|-----------|-------------|--------------|
| [BaseController](../../core/BaseController.md) | Base controller for UI components | Observer pattern, widget management, signal handling |
| [Config](../../core/Config.md) | Configuration management | JSON persistence, thread-safe access, dot notation |
| [Exceptions](../../core/Exceptions.md) | Exception handling system | Custom exceptions, error dialogs, event system |
| [Observer](../../core/Observer.md) | Observer pattern implementation | Event publishing, subscriptions, thread-safe |
| [TaskSystem](../../core/TaskSystem.md) | Task management system | Task execution, steps, monitoring, signals |
| [Utils](../../core/Utils.md) | Utility classes and functions | Path handling, URL manipulation, Python utilities |
| [WidgetManager](../../core/WidgetManager.md) | Widget management system | Dot notation access, type-safe retrieval |
| [Logging](../../core/Logging.md) | Logging system | Centralized logging, multiple levels, file output |
| [CURL SSL Anti Fingerprinting](../../core/CurlSslAntiDetectSession.md) | Extends/Patching | Prevent SSL fingerprinting for `requests` library |

### Helper Components (`helpers/`)
| Component | Description | Key Features |
|-----------|-------------|--------------|
| [AppHelper](../../helpers/AppHelper.md) | Application utilities | App info, configuration access, icon management |
| [ValidateHelper](../../helpers/ValidateHelper.md) | Input validation | Hostname, email, URL validation, error handling |
| [TextLinesHelpers](../../helpers/TextLinesHelpers.md) | Text processing | Line manipulation, text analysis, formatting |
| [StealthBrowserHelper](../../helpers/StealthBrowserHelper.md) | Browser stealth utilities | Anti-detection, stealth features, browser automation |

## Component Relationships

Refer to specific component documentation for detailed usage patterns and relationships.

### Core Architecture
- **BaseController** relies on **WidgetManager**, **Observer**, and **Config**.
- **TaskSystem** orchestrates **Task** and **TaskStep** execution.

See component docs for more diagrams.

## Common Usage Patterns

### 1. Controller Implementation
```python
from core import BaseController, Config, logger

class MyController(BaseController):
    slot_map = {
        'buttonClicked': ['pushSampleButton', 'clicked']
        #event name: [widget property name, signal name]
        'forced_camel_case': ['pushSampleButton', 'clicked']
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        
### 2. Handler Implement
```python
from core.Observer import Observer
from core.WidgetManager import WidgetManager
from typing import List

class MyHandler(Observer):
    def __init__(self, widgetManager: WidgetManager, events: List[str]):
        super().__init__(events=events)
        self.widgetManager = widgetManager
    
    # camelCase of event name. Prefixed with `on`
    def onButtonClickedButtonClicked(self):
        pass
    # forced_camel_case
    # Even you already snaked evt name. You still must define evt handler = onForcedCamelCase
    def onForcedCamelCase(self):
        pass
``` 

### 4. Configuration Usage
from core import Config
from core.helpers import AppHelper

# Direct config access
config = Config()
app_name = config.get('app.name', 'Default App')

# Helper access
app_name = AppHelper.getAppName()
app_version = AppHelper.getAppVersion()
```

### 5. Validation Usage

```python
from core.helpers import ValidateHelper

# Validate input
is_valid, error = ValidateHelper.validateEmail("user@example.com")
if not is_valid:
    print(f"Invalid email: {error}")

# Validate with exception
try:
    ValidateHelper.validateHostname("invalid..hostname", raiseEx=True)
except InputError as e:
    print(f"Validation error: {e}")
```

## Getting Started

### 1. Choose Your Components
- **UI Development**: Use `BaseController`, `WidgetManager`, `Observer`
- **Configuration**: Use `Config`, `AppHelper`
- **Task Management**: Use `TaskSystem`, `TaskSchedulerService`
- **Browser Automation**: Use `AbstractCheckerService`, `ChromeBrowserServices`
- **Input Validation**: Use `ValidateHelper`

### 2. Follow the Patterns
- Read the component documentation
- Follow the usage examples
- Implement error handling
- Use appropriate logging

### 3. Test Your Implementation
- Test with different scenarios
- Handle edge cases
- Monitor performance
- Check error handling

## Best Practices

### General
1. **Read the documentation**: Always read component docs before use
2. **Follow patterns**: Use the provided examples as templates
3. **Handle errors**: Implement proper error handling
4. **Use logging**: Log important events and errors
5. **Test thoroughly**: Test with various scenarios

### Performance
1. **Use singletons**: Access shared resources through singletons
2. **Cache frequently used data**: Avoid repeated expensive operations
3. **Use appropriate data structures**: Choose the right data structure for your use case
4. **Monitor resource usage**: Keep track of memory and CPU usage

### Security
1. **Validate input**: Always validate user input
2. **Handle sensitive data**: Don't log sensitive information
3. **Use secure defaults**: Choose secure default configurations
4. **Follow security best practices**: Implement proper security measures

## Troubleshooting

### Common Issues
1. **Import errors**: Check if components are properly imported
2. **Configuration errors**: Verify configuration files and paths
3. **Thread safety**: Ensure thread-safe access to shared resources
4. **Memory leaks**: Properly clean up resources and connections

### Getting Help
1. **Check logs**: Look at application logs for error messages
2. **Read documentation**: Refer to component-specific documentation
3. **Test components**: Test components in isolation
4. **Debug step by step**: Use debugging tools to trace issues

## Contributing

When adding new components or modifying existing ones:

1. **Follow naming conventions**: Use consistent naming patterns
2. **Add documentation**: Document all public methods and properties
3. **Include examples**: Provide usage examples
4. **Test thoroughly**: Test with various scenarios
5. **Update this index**: Keep the index up to date
