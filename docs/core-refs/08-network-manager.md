# NetworkManager - Qt Network Integration

> **QNetworkAccessManager wrapper with disk cache and feature flag integration**

## Overview

`NetworkManager` provides:

- A `QNetworkAccessManager` instance
- Disk cache (50MB)
- Feature flag integration (`PSA_ENABLE_NETWORK`)
- UI thread execution only (Qt limitation)

## API Reference

### Access

```python
from core import QtAppContext

ctx = QtAppContext.globalInstance()

# Check feature enabled
if ctx.isFeatureEnabled('network'):
    network = ctx.network  # QNetworkAccessManager | None
```

### QNetworkAccessManager

```python
from PySide6.QtNetwork import QNetworkRequest
from PySide6.QtCore import QUrl

request = QNetworkRequest(QUrl('https://api.example.com'))
reply = network.get(request)
reply.finished.connect(lambda: handleResponse(reply))
```

## Usage Examples

### Basic GET Request

```python
from core import QtAppContext
from PySide6.QtNetwork import QNetworkRequest
from PySide6.QtCore import QUrl

ctx = QtAppContext.globalInstance()

if ctx.isFeatureEnabled('network'):
    network = ctx.network
    
    request = QNetworkRequest(QUrl('https://api.example.com/data'))
    reply = network.get(request)
    reply.finished.connect(lambda: onReplyFinished(reply))

def onReplyFinished(reply):
    if reply.error() == QNetworkReply.NoError:
        data = reply.readAll()
        print(data.data().decode('utf-8'))
    else:
        print(f'Error: {reply.errorString()}')
    reply.deleteLater()
```

### POST Request

```python
from PySide6.QtNetwork import QNetworkRequest
from PySide6.QtCore import QUrl, QByteArray

network = ctx.network
request = QNetworkRequest(QUrl('https://api.example.com/users'))
request.setHeader(QNetworkRequest.ContentTypeHeader, 'application/json')

data = QByteArray(b'{"name": "John", "email": "john@example.com"}')
reply = network.post(request, data)
reply.finished.connect(lambda: onPostFinished(reply))
```

## UI Thread vs Background Thread

### ✅ UI Thread (NetworkManager)

```python
# In controller/handler (UI thread)
class MyHandler(BaseCtlHandler):
    def onLoadDataClicked(self):
        ctx = QtAppContext.globalInstance()
        network = ctx.network
        
        request = QNetworkRequest(QUrl('https://api.example.com'))
        reply = network.get(request)
        reply.finished.connect(self.onDataLoaded)
```

### ❌ Background Thread (Use requests)

```python
# In task (background thread)
import requests

class DataFetchTask(AbstractTask):
    def handle(self):
        # Don't use NetworkManager here!
        # Use requests library instead
        response = requests.get('https://api.example.com')
        data = response.json()
```

## Feature Flag

### Enable/Disable

```bash
# .env file
PSA_ENABLE_NETWORK=true   # Enable NetworkManager
PSA_ENABLE_NETWORK=false  # Disable NetworkManager
```

### Check Before Use

```python
ctx = QtAppContext.globalInstance()

if ctx.isFeatureEnabled('network'):
    # Use NetworkManager
    network = ctx.network
else:
    # Fallback to requests
    import requests
    response = requests.get('https://api.example.com')
```

## Disk Cache

**Location:** `{CACHE_DIR}/network_cache`  
**Size:** 50MB  
**Auto-managed:** Qt handles cache eviction

## Best Practices

### ✅ DO

```python
# Check feature flag
if ctx.isFeatureEnabled('network'):
    network = ctx.network

# Use in UI thread only
class MyHandler(BaseCtlHandler):
    def onButtonClicked(self):
        network = ctx.network
        # Make request...

# Delete replies
def onFinished(reply):
    # Process reply...
    reply.deleteLater()  # Don't forget!
```

### ❌ DON'T

```python
# Don't use in background threads
class MyTask(AbstractTask):
    def handle(self):
        network = ctx.network  # Wrong! Use requests

# Don't forget to delete replies
def onFinished(reply):
    data = reply.readAll()
    # Missing: reply.deleteLater()  # Memory leak!

# Don't assume network enabled
network = ctx.network  # May be None!
```

## Related Documentation

- [QtAppContext](01-application-context.md) - Feature flags
- [AbstractTask](13-abstract-task.md) - Background tasks
