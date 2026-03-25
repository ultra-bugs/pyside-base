# Observer Pattern - Publisher/Subscriber Event System

> **Queue-based, thread-aware, non-blocking event dispatch**

## Overview

The Observer pattern uses a Publisher/Subscriber model to:

- Decouple components (avoiding hard dependencies)
- Enable event-driven communication
- Provide **non-blocking** `notify()` via a background dispatcher thread
- Guarantee **UI thread safety** for main-thread subscribers via `_MainThreadBridge`
- Support **async I/O handlers** via TaskSystem integration (`pubsubFireAndForget`)
- Use smart parameter injection (type-hint aware matching)

## Architecture

```mermaid
flowchart TD
    A["Any Thread\n(UI / Worker)"] -->|"notify(event) — non-blocking"| Q["Dispatcher Queue\n(FIFO)"]
    Q --> D["PubSubDispatcher\n(DaemonWorker thread)"]
    D -->|homeThread == main| B["_MainThreadBridge\nQt QueuedConnection\n→ safe UI update ✅"]
    D -->|child thread, default| I["inline on Dispatcher"]
    D -->|"pubsubFireAndForget=True"| T["_CallableTask\n→ TaskManagerService\n→ QThreadPool"]
```

### Key Components

| Class | Role |
|---|---|
| `Publisher` (singleton) | Manages subscribers, queues events, routes delivery |
| `_PubSubDispatcher` | `DaemonWorker` thread draining the event queue |
| `_MainThreadBridge` | `QObject` relaying events to Qt main thread via `QueuedConnection` |
| `_CallableTask` | Wraps a callable as `AbstractTask` for TaskSystem delivery |
| `Subscriber` | Base observer; auto-subscribes; smart parameter injection |

## API Reference

### Publisher

```python
from core import Publisher

pub = Publisher.instance()   # or Publisher.globalInstance()

pub.notify('event.name', arg1, key=value)   # non-blocking ✅
pub.subscribe(sub, event='my.event')         # or event=None for global
pub.unsubscribe(sub, event='my.event')       # or event=None for all
pub.connect(widget, 'clicked', 'ui.click')  # Qt signal → event
pub.stop()                                   # graceful dispatcher shutdown
```

### Subscriber

```python
from core import Subscriber

class MyHandler(Subscriber):
    def __init__(self):
        super().__init__(events=['user.login', 'user.logout'])

    def onUserLogin(self, userId: int, username: str):
        pass

    def onUserLogout(self, userId: int):
        pass
```

**Event handler naming**: `on` + `PascalCase(event_name)`
- `user.login` → `onUserLogin`
- `task.progress` → `onTaskProgress`

## Thread Routing

Subscribers capture `_homeThread` at construction time:

| Subscriber registered on | Delivery mechanism |
|---|---|
| Main thread | `_MainThreadBridge` → Qt `QueuedConnection` (UI-safe) |
| Child thread (default) | Inline on Dispatcher thread |
| Child thread + `pubsubFireAndForget=True` | `TaskManagerService.addTask()` → QThreadPool |

### opt-in fire-and-forget

```python
class VndAutomationService(HandlerServiceWithAck):
    pubsubFireAndForget = True   # I/O-heavy: route via TaskSystem
```

## Smart Parameter Injection

`Subscriber.update()` dispatches to `onEventName()` using priority:

1. **By kwarg name**: `userId=123` → param `userId`
2. **By type hint**: `arg: int` → first unused `int` argument
3. **By position**: first unused arg → first unmatched param

```python
publisher.notify('complex.event', 123, 'john', {'key': 'value'})
publisher.notify('complex.event', userId=123, username='john')
```

## Shutdown

```python
# In QtAppContext._onExit():
publisher.notify('app.shutdown')
publisher.stop()   # gracefully drains and stops dispatcher thread
```

## Usage Examples

### Basic

```python
publisher = Publisher.instance()
publisher.notify('user.login', userId=123, username='john')
```

### Global Subscriber

```python
class GlobalHandler(Subscriber):
    def __init__(self):
        super().__init__(events=[], isGlobalSubscriber=True)

    def update(self, event: str, *args, **kwargs):
        print(f'Event: {event}')
```

### Qt Signal Integration

```python
publisher.connect(button, 'clicked', 'button.clicked', buttonId='submit')
```

### Task Progress

```python
class MyTask(AbstractTask):
    def handle(self):
        publisher = Publisher.instance()
        publisher.notify('task.progress', taskId=self.uuid, progress=50)
        publisher.notify('task.completed', taskId=self.uuid)
```

## Thread Safety

| Operation | Thread-safe? |
|---|---|
| `notify()` | ✅ — enqueue only, no lock needed |
| `subscribe()` / `unsubscribe()` | ✅ QMutex |
| Main-thread handler execution | ✅ via `_MainThreadBridge` + `QueuedConnection` |
| Child-thread handler (inline) | ✅ runs on Dispatcher thread, no Qt objects |

## Best Practices

### ✅ DO

```python
# Namespaced event names
publisher.notify('user.login', userId=123)

# Type hints for smart injection
def onUserLogin(self, userId: int, username: str): pass

# Subscribe specific events only
class MyHandler(Subscriber):
    def __init__(self):
        super().__init__(events=['user.login'])

# I/O-heavy service opts-in
class ApiSyncService(Subscriber):
    pubsubFireAndForget = True
```

### ❌ DON'T

```python
# Don't call handler methods directly
handler.onUserLogin(123, 'john')    # Wrong! Use publisher.notify()

# Don't create circular events
class A(Subscriber):
    def onEventA(self):
        publisher.notify('event.b')  # OK if B doesn't emit event.a

# Don't bypass Publisher with raw QThreadPool for I/O tasks
# Use pubsubFireAndForget = True instead
```

## Testing

```bash
pixi run ctests tests_core/observer/ -v
```

Tests verify:
- `notify()` returns before subscriber finishes (non-blocking)
- Main-thread subscribers receive events on main thread
- Child-thread subscribers receive events off main thread
- FIFO ordering guaranteed
- `unsubscribe()` stops delivery
- `fireAndForget` fallback when TaskManager unavailable

## Related

- [BaseController](04-controller-architecture.md) — auto-unsubscribes handler on destroy
- [QtAppContext](01-application-context.md) — publisher access, shutdown
- [Task System](12-task-system-overview.md) — `fireAndForget` concurrency
