# Core Components Index

This document provides a comprehensive index of all core components available in the base framework.

## Quick Reference

### Core Components (`core/`)
| Component                                                        | Description                       | Key Features                                         |
|------------------------------------------------------------------|-----------------------------------|------------------------------------------------------|
| [BaseController](core/BaseController.md)                         | Base controller for UI components | Observer pattern, widget management, signal handling |
| [Config](core/Config.md)                                         | Configuration management          | JSON persistence, thread-safe access, dot notation   |
| [Exceptions](core/Exceptions.md)                                 | Exception handling system         | Custom exceptions, error dialogs, event system       |
| [Observer](core/Observer.md)                                     | Observer pattern implementation   | Event publishing, subscriptions, thread-safe         |
| [TaskSystem](core/TaskSystem.md)                                 | Task management system            | Task execution, steps, monitoring, signals           |
| [Utils](core/Utils.md)                                           | Utility classes and functions     | Path handling, URL manipulation, Python utilities    |
| [WidgetManager](core/WidgetManager.md)                           | Widget management system          | Dot notation access, type-safe retrieval             |
| [Logging](core/Logging.md)                                       | Logging system                    | Centralized logging, multiple levels, file output    |
| [CURL SSL Anti Fingerprinting](core/CurlSslAntiDetectSession.md) | Extends/Patching                  | Prevent SSL fingerprinting for `requests` library    |

### Helper Components (`helpers/`)
| Component | Description | Key Features |
|-----------|-------------|--------------|
| [AppHelper](helpers/AppHelper.md) | Application utilities | App info, configuration access, icon management |
| [ValidateHelper](helpers/ValidateHelper.md) | Input validation | Hostname, email, URL validation, error handling |
| [TextLinesHelpers](helpers/TextLinesHelpers.md) | Text processing | Line manipulation, text analysis, formatting |
| [StealthBrowserHelper](helpers/StealthBrowserHelper.md) | Browser stealth utilities | Anti-detection, stealth features, browser automation |

### Service Components (`services/`)
| Component                                                          | Description               | Key Features                                           |
|--------------------------------------------------------------------|---------------------------|--------------------------------------------------------|
| [AbstractCheckerService](services/AbstractCheckerService.md)       | Base checker service      | Browser automation, profile management, error handling |
| [InstancesContainerService](services/InstancesContainerService.md) | Instance management       | Thread-safe container, UUID-based identification       |
| [TaskSchedulerService](services/TaskSchedulerService.md)           | Task scheduling           | One-time and recurring tasks, time-based execution     |
| [ChromeBrowserServices](services/ChromeBrowserServices.md)         | Chrome browser management | Browser automation, profile handling, stealth features |
| [ChromeProfileServices](services/ChromeProfileServices.md)         | Profile management        | Profile creation, management, import/export            |
| [DomWatcherService](services/DomWatcherService.md)                 | DOM monitoring            | Element watching, change detection, event handling     |
| [NetworkWatcherService](services/NetworkWatcherService.md)         | Network monitoring        | Request/response tracking, network analysis            |

## Component Relationships

### Core Architecture
```
BaseController
├── WidgetManager (widget access)
├── Observer (event system)
└── Config (configuration)

TaskSystem
├── TaskManager (task execution)
├── Task (individual tasks)
└── TaskStep (task steps)

Utils
├── PathHelper (file operations)
├── UrlHelper (URL manipulation)
├── PythonHelper (Python utilities)
└── WidgetUtils (widget operations)
```

### Service Layer
```
AbstractCheckerService
├── ChromeBrowserServices (browser automation)
├── ChromeProfileServices (profile management)
└── InstancesContainerService (instance management)

TaskSchedulerService
├── TaskSystem (task execution)
└── InstancesContainerService (instance management)
```

### Helper Layer
```
AppHelper
├── Config (configuration access)
└── PathHelper (path utilities)

ValidateHelper
├── AppException (error handling)
└── InputError (validation errors)
```

## Common Usage Patterns

### 1. Controller Implementation
```python
from core import BaseController, Config, logger

class MyController(BaseController):
    slot_map = {
        'button_clicked': 'on_button_clicked'
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.connect_signals()
    
    def on_button_clicked(self):
        logger.info("Button clicked")
        # Handle button click
```

### 2. Service Implementation
```python
from services import AbstractCheckerService
from core import logger

class MyCheckerService(AbstractCheckerService):
    def __init__(self):
        super().__init__()
        self.BASE_URL = 'https://example.com'
    
    def check_account(self, account_data):
        try:
            result = self.initializeBrowser()
            if result['status'] == 'success':
                # Perform check
                return {'status': 'success'}
        except Exception as e:
            logger.error(f"Check failed: {e}")
            return {'status': 'error', 'message': str(e)}
```

### 3. Task Implementation
```python
from core import TaskManager, Task, PrintStep, SleepStep

def create_my_task():
    manager = TaskManager()
    task = manager.create_task("my_task", "My Task")
    
    task.add_step(PrintStep("Starting task"))
    task.add_step(SleepStep(2.0))
    task.add_step(PrintStep("Task completed"))
    
    return manager, task
```

### 4. Configuration Usage

```python
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
