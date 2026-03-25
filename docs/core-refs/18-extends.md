# Extends - Extensions

> **Extended functionality and specialized implementations**

## CurlSslAntiDetectSession

Anti-detection HTTP session using `curl_cffi`:

```python
from core.extends import CurlSslAntiDetectSession

session = CurlSslAntiDetectSession(
    impersonate='chrome110',
    timeout=30
)

# GET request
response = session.get('https://api.example.com')
print(response.text)

# POST request
response = session.post(
    'https://api.example.com/data',
    json={'key': 'value'}
)

# With headers
response = session.get(
    'https://api.example.com',
    headers={'User-Agent': 'Custom'}
)
```

## Features

- Browser impersonation (Chrome, Firefox, Safari)
- TLS fingerprint randomization
- Anti-bot detection
- Session persistence

## Usage Examples

### Basic Request

```python
from core.extends import CurlSslAntiDetectSession

session = CurlSslAntiDetectSession()

# Simple GET
response = session.get('https://example.com')
print(response.status_code)
print(response.text)
```

### With Impersonation

```python
# Impersonate Chrome 110
session = CurlSslAntiDetectSession(impersonate='chrome110')

# Impersonate Firefox
session = CurlSslAntiDetectSession(impersonate='firefox')

# Impersonate Safari
session = CurlSslAntiDetectSession(impersonate='safari')
```

### In Background Task

```python
from core.taskSystem import AbstractTask
from core.extends import CurlSslAntiDetectSession

class ScrapingTask(AbstractTask):
    def handle(self):
        session = CurlSslAntiDetectSession(impersonate='chrome110')
        
        try:
            response = session.get('https://example.com')
            data = response.json()
            
            # Process data...
            
        except Exception as e:
            self.fail(f'Request failed: {e}')
    
    def _performCancellationCleanup(self):
        pass
```

## Best Practices

### ✅ DO

```python
# Use in background tasks
class MyTask(AbstractTask):
    def handle(self):
        session = CurlSslAntiDetectSession()
        response = session.get(url)

# Set appropriate timeout
session = CurlSslAntiDetectSession(timeout=30)

# Handle exceptions
try:
    response = session.get(url)
except Exception as e:
    logger.error(f'Request failed: {e}')
```

### ❌ DON'T

```python
# Don't use in UI thread
class MyHandler(BaseCtlHandler):
    def onButtonClicked(self):
        session = CurlSslAntiDetectSession()  # Wrong! Use in task

# Don't forget timeout
session = CurlSslAntiDetectSession()  # No timeout!
```

## Related Documentation

- [AbstractTask](13-abstract-task.md) - Background tasks
- [NetworkManager](08-network-manager.md) - UI thread networking
