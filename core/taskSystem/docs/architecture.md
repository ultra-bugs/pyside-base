# Architecture Documentation

## Project Overview

This is a PySide6-based application following Qt conventions with a clean architecture pattern using:

- **MVC Pattern**: Controllers, Handlers, Services
- **Observer Pattern**: Decoupled communication via Publisher/Subscriber
- **Qt Designer**: UI-first workflow with `.ui` files

## Coding Standards

### Naming Conventions (Qt Style)

**IMPORTANT**: This project follows Qt naming conventions, which is an **explicit exception** to PEP 8's snake_case
recommendation.

#### Files and Classes

- **PascalCase** for all files and classes
- Examples:
    - `TaskManagerService.py`
    - `AbstractTask.py`
    - `MainController.py`
    - `AndroidManagerService.py`

#### Methods and Variables

- **camelCase** for all methods, functions, and variables
- **NO snake_case** anywhere in the codebase
- Examples:
  ```python
  def addTask(self, task):  # ✅ Correct
      maxRetries = 5  # ✅ Correct
      deviceSerial = "ABC123"  # ✅ Correct
      
  def add_task(self, task):  # ❌ Wrong
      max_retries = 5  # ❌ Wrong
      device_serial = "ABC123"  # ❌ Wrong
  ```

#### Directories

- **lowercase with underscores** for directories
- Examples:
    - `core/taskSystem/`
    - `windows/main/`
    - `services/tasks/`

### PEP 8 Compliance (Except Naming)

We follow PEP 8 for everything **except** naming:

- ✅ 4 spaces for indentation
- ✅ Maximum line length: 120 characters (flexible)
- ✅ Blank lines between functions/classes
- ✅ Import organization (stdlib, third-party, local)
- ✅ Type hints for public functions
- ✅ Docstrings (PEP 257)
- ❌ **NOT** snake_case naming

### Logging Policy

**Mandatory**: Use `core.Logging.logger` everywhere. **Never use `print()`**.

```python
from ..Logging import logger

# Initialize logger with component name
logger = logger.bind(component="TaskSystem")

# Usage
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

#### Scoped Logging (Multithreaded/Async)

For concurrent systems, include contextual identifiers:

```python
import threading

# In multithreaded code
logger = logger.bind(
        component="TaskSystem",
        thread_id=threading.get_ident()
)

# In async/event code
logger = logger.bind(
        component="TaskSystem",
        task_uuid=task.uuid
)
```

## Architecture Layers

### 1. Core Layer (`core/`)

Foundation classes and utilities:

- **BaseController**: Base class for all controllers
- **Observer**: Publisher/Subscriber pattern implementation
- **Config**: Configuration management (thread-safe)
- **Logging**: Centralized logging with loguru
- **Exceptions**: Custom exception hierarchy
- **WidgetManager**: Widget access and signal-suppressed updates
- **TaskSystem**: Task management framework

### 2. Services Layer (`services/`)

Business logic, UI-agnostic:

- **AndroidManagerService**: Android device management
- **TaskManagerService**: Task orchestration
- **Task Implementations**: AdbCommandTask, RpaScriptTask, etc.

### 3. Windows Layer (`windows/`)

UI components:

- **Controllers**: Extend BaseController, wire UI to events
- **Handlers**: Extend Subscriber, implement business logic
- **Components**: Reusable UI widgets

Structure:

```
windows/
└── components/
    └── ComponentName/
        ├── ComponentName.ui          # Qt Designer file
        ├── ComponentName.py          # Generated (DO NOT EDIT)
        ├── ComponentNameWidget.py    # Controller
        ├── ComponentNameHandler.py   # Handler
        └── __init__.py
```

## UI-First Workflow

### Mandatory Process

1. **Design in Qt Designer**
    - Create/edit `.ui` files
    - Keep `.ui` as single source of truth
    - **Never add Python slots in `.ui` files**

2. **Compile UI to Python**
   ```bash
   python scripts/compile_ui.py
   ```

3. **Implement Controller**
    - Extend `BaseController`
    - Wire UI via `slot_map`
    - **Never edit generated `.py` files**

### Controller Pattern

```python
from ..BaseController import BaseController
from windows.main.Main import Ui_MainWindow


class MainController(Ui_MainWindow, BaseController):
    def __init__(self, parent = None):
        # Order matters: UI class first, then BaseController
        super().__init__(parent)
        # BaseController calls setupUi() automatically
        
        self.slot_map = {
            'btnStart.clicked': self.onStartClicked,
            'btnStop.clicked': self.onStopClicked,
        }
    
    def onStartClicked(self):
        # Emit event via Observer
        self.publisher.notify('StartRequested')
```

**CRITICAL**:

- Inherit order: `Ui_Class, BaseController`
- **Never call `setupUi()` in `__init__`** (BaseController does it)
- Use `slot_map` for signal connections
- Controllers should be thin - delegate to Handlers

### Handler Pattern

```python
from ..Observer import Subscriber


class MainHandler(Subscriber):
    def __init__(self):
        super().__init__(events=['StartRequested', 'StopRequested'])
    
    def onStartRequested(self):
        # Business logic here
        pass
```

## Observer Pattern

### Decoupled Communication

**Never** directly call other controllers. Use Observer pattern:

```python
# ❌ Wrong
otherController.doSomething()

# ✅ Correct
self.publisher.notify('SomethingRequested', data=myData)
```

### Publisher (Singleton)

```python
from ..Observer import Publisher

publisher = Publisher()

# Subscribe to specific event
publisher.subscribe(handler, event='TaskCompleted')

# Notify subscribers
publisher.notify('TaskCompleted', task=task, result=result)
```

### Subscriber

```python
from ..Observer import Subscriber


class MyHandler(Subscriber):
    def __init__(self):
        super().__init__(events=['TaskCompleted'])
    
    def onTaskCompleted(self, task, result):
        # Handle event
        pass
```

## TaskSystem Architecture

See [TaskSystem API Documentation](task-system-api.md) for details.

### Key Principles

1. **Qt Naming**: camelCase methods, PascalCase classes
2. **Logger**: All modules use `logger.bind(component="TaskSystem")`
3. **No snake_case**: Anywhere in TaskSystem code
4. **Thread-safe**: All public APIs are thread-safe
5. **Observable**: Integrates with Observer pattern

### Components

```
TaskManagerService (Orchestrator)
├── TaskQueue (FIFO + Concurrency)
│   └── QThreadPool
├── TaskTracker (Monitoring)
└── TaskScheduler (APScheduler)
```

## Exception Handling

### Custom Exceptions

All exceptions inherit from `core.Exceptions.AppException`:

```python
from ..Exceptions import AppException


class TaskSystemException(AppException):
    pass


class TaskNotFoundException(TaskSystemException):
    def __init__(self, uuid: str):
        super().__init__(f"Task {uuid} not found")
```

### Error Policy

- **Never catch silently** (unless `failSilently=True`)
- **Use typed exceptions** from `core.Exceptions`
- **Log errors** with context
- **Re-raise** when appropriate

## Configuration Management

### Config Singleton

```python
from ..Config import Config

config = Config()

# Get value
value = config.get('key.nested.path', default=None)

# Set value
config.set('key.nested.path', value)
config.save()
```

### Thread Safety

Config uses `QMutex` for thread-safe operations.

## Testing

### Test Structure

```
tests_core/
├── conftest.py           # Pytest fixtures
├── task_system/
│   ├── test_TaskStatus.py
│   ├── test_Exceptions.py
│   ├── test_AbstractTask.py
│   └── ...
└── integration/
    └── test_TaskFlow.py
```

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=core --cov=services --cov-report=html
```

## Scripts

### Code Generation

```bash
# Generate controller/handler/component
python scripts/generate.py component MyComponent

# Compile UI files
python scripts/compile_ui.py
```

### Workflow

1. Generate component scaffold
2. Design UI in Qt Designer
3. Compile UI
4. Implement controller logic
5. Implement handler logic
6. Write tests

## ACK Mechanism

For coordinated async operations requiring acknowledgment:

See `docs/provided-by-base/ACKNOWLEDGMENT_MECHANISM.md`

**When to use:**

- Task emits events requiring downstream processing
- Must wait for processing before cleanup
- Example: Browser automation with screenshot capture

**Pattern:**

```python
from ..ack import AcknowledgmentTracker, TaskServiceWithAck

tracker = AcknowledgmentTracker()

# Emit with ACK
await TaskServiceWithAck.emit_event_with_ack(
        tracker, publisher, 'TaskCompleted', task=task
)

# Wait for ACKs before cleanup
await tracker.wait_for_acknowledgments(timeout=5.0)
```

## Security

### Secrets Management

- **Never log** credentials, tokens, or PII
- **Centralize config** via `core.Config`
- **Never hardcode** secrets in code
- Use environment variables or secure config

### Example

```python
# ❌ Wrong
api_key = "sk-1234567890"

# ✅ Correct
api_key = config.get('api.key')
```

## Definition of Done (Feature/UI)

Before marking a feature complete:

- [ ] `.ui` file exists and compiles cleanly
- [ ] Controller/Handler implemented with proper wiring
- [ ] Service code covered by unit tests
- [ ] Integration tests for critical flows
- [ ] No direct edits to generated UI code
- [ ] Logging in place (no `print()` statements)
- [ ] Exceptions properly typed
- [ ] Documentation updated in `docs/`

## File Organization

```
project/
├── core/                   # Foundation
│   ├── taskSystem/        # Task management
│   ├── ack/               # ACK mechanism
│   └── ...
├── services/              # Business logic
│   ├── tasks/            # Task implementations
│   └── ...
├── windows/               # UI layer
│   ├── main/
│   └── components/
├── scripts/               # Dev tools
├── tests_core/            # Automated tests
├── docs/                  # Documentation
└── main.py               # Entry point
```

## External Libraries

### Documentation Policy

Before integrating a new library:

1. Review official docs (Context7/web search)
2. Add notes to `docs/` if behavior affects architecture
3. Document any Qt naming conflicts

### Existing Libraries

- **PySide6**: Qt for Python
- **loguru**: Logging
- **APScheduler**: Task scheduling
- **pytest**: Testing

## References

- [TaskSystem API](task-system-api.md)
- [Services Overview](services.md)
- [Task System Design](diagrams/task-system-architect-design.mermaid)
- [PySide6 Project Rules](.cursor/rules/)

## Summary

**Key Takeaways:**

1. **Qt Naming**: camelCase methods, PascalCase classes/files (NO snake_case)
2. **UI-First**: Design in Qt Designer, compile, never edit generated code
3. **Observer Pattern**: Decoupled communication, no direct controller calls
4. **Logger**: Use `core.Logging.logger`, never `print()`
5. **Architecture**: Controllers (thin) → Handlers (logic) → Services (business)
6. **Thread Safety**: Config, TaskSystem, and Observer are thread-safe
7. **Testing**: Unit tests for services, integration tests for flows

