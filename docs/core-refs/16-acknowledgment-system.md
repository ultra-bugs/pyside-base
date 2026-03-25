# Acknowledgment System

> **ACK/NACK protocol for task coordination and event synchronization**

## Overview

The ACK system provides:

- Acknowledgment tracking
- Timeout handling
- Success/error callbacks
- Thread-safe coordination

## Components

### AcknowledgmentTracker

Core coordinator:

```python
from core.ack import AcknowledgmentTracker

tracker = AcknowledgmentTracker()

# Register pending ack
tracker.registerPending(
    ackId='task-123',
    successCallback=onSuccess,
    errorCallback=onError,
    timeoutCallback=onTimeout,
    timeout=30.0
)

# Acknowledge
tracker.acknowledge('task-123', result={'data': 'value'})

# Or error
tracker.acknowledgeError('task-123', Exception('Failed'))
```

### AcknowledgmentSender

Emit events with ACK:

```python
from core.ack import AcknowledgmentSender

sender = AcknowledgmentSender(tracker, publisher)

# Emit with ACK
sender.emitWithAck(
    event='data.process',
    ackId='process-123',
    successCallback=onSuccess,
    timeout=30.0,
    data={'key': 'value'}
)
```

### AcknowledgmentReceiver

Handle events with ACK:

```python
from core.ack import AcknowledgmentReceiver

receiver = AcknowledgmentReceiver(tracker, publisher)

# Handle with ACK
def processData(ackId, data):
    try:
        # Process data...
        receiver.acknowledge(ackId, result={'status': 'ok'})
    except Exception as e:
        receiver.acknowledgeError(ackId, e)

receiver.handleWithAck('data.process', processData)
```

## Usage Examples

### Basic ACK Flow

```python
from core.ack import AcknowledgmentTracker, AcknowledgmentSender, AcknowledgmentReceiver
from core import Publisher

tracker = AcknowledgmentTracker()
publisher = Publisher.instance()

sender = AcknowledgmentSender(tracker, publisher)
receiver = AcknowledgmentReceiver(tracker, publisher)

# Sender
def onSuccess(ackId, result):
    print(f'Success: {result}')

def onTimeout(ackId):
    print(f'Timeout: {ackId}')

sender.emitWithAck(
    event='task.execute',
    ackId='task-123',
    successCallback=onSuccess,
    timeoutCallback=onTimeout,
    timeout=10.0,
    taskData={'action': 'process'}
)

# Receiver
def handleTask(ackId, taskData):
    try:
        # Process task...
        result = {'status': 'completed'}
        receiver.acknowledge(ackId, result)
    except Exception as e:
        receiver.acknowledgeError(ackId, e)

receiver.handleWithAck('task.execute', handleTask)
```

### Task Coordination

```python
class TaskWithAck(AbstractTask):
    def handle(self):
        tracker = AcknowledgmentTracker()
        sender = AcknowledgmentSender(tracker, Publisher.instance())
        
        # Emit event and wait for ACK
        ackReceived = threading.Event()
        
        def onSuccess(ackId, result):
            print(f'Handler completed: {result}')
            ackReceived.set()
        
        def onTimeout(ackId):
            print('Handler timeout!')
            ackReceived.set()
        
        sender.emitWithAck(
            event='data.process',
            ackId=f'task-{self.uuid}',
            successCallback=onSuccess,
            timeoutCallback=onTimeout,
            data={'items': [1, 2, 3]}
        )
        
        # Wait for acknowledgment
        ackReceived.wait(timeout=30)
```

## Best Practices

### ✅ DO

```python
# Always provide timeout
tracker.registerPending(
    ackId='id',
    successCallback=onSuccess,
    timeout=30.0  # Don't forget!
)

# Handle timeouts
def onTimeout(ackId):
    logger.warning(f'ACK timeout: {ackId}')
    # Cleanup or retry

# Acknowledge in try-except
def handler(ackId, data):
    try:
        # Process...
        receiver.acknowledge(ackId, result)
    except Exception as e:
        receiver.acknowledgeError(ackId, e)
```

### ❌ DON'T

```python
# Don't forget to acknowledge
def handler(ackId, data):
    # Process...
    pass  # Missing: receiver.acknowledge()!

# Don't use infinite timeout
tracker.registerPending(
    ackId='id',
    successCallback=onSuccess,
    timeout=0  # Wrong! Will never timeout
)
```

## Related Documentation

- [Observer Pattern](03-observer-pattern.md) - Event system
- [AbstractTask](13-abstract-task.md) - Task integration
