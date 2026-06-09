# Extends - Extensions

> **Anti-detection HTTP session using curl_cffi**
> **Last synced**: `2026-06-09`

## CurlSslAntiDetectSession module

Module: `core/extends/CurlSslAntiDetectSession.py`

Provides an anti-detection HTTP session built on `curl_cffi`. It can be used in two ways:

1. **Monkey-patch `requests`** — drop-in replacement; all `requests.get/post/...` calls use curl_cffi transparently.
2. **Direct session** — instantiate `AntiDetectSession` or use `createAntiDetectSession()`.

## installAntiDetectSession (monkey-patcher)

Exported from `core.extends`. Patches `requests` module in-place so all existing `requests.*` calls use curl_cffi automatically.

```python
from core.extends import installAntiDetectSession

# Call once at bootstrap
installAntiDetectSession()

# After patching, just use requests normally
import requests
response = requests.get('https://example.com')
print(response.status_code)
```

**Signature**: `installAntiDetectSession(autoRotate=False, profilePool=None)`

- `autoRotate` — rotate browser profile on each request
- `profilePool` — custom list of profile strings to rotate through

## AntiDetectSession

Direct session class. Subclasses `curl_cffi.requests.Session`.

```python
from core.extends.CurlSslAntiDetectSession import AntiDetectSession

# Random profile from default pool
session = AntiDetectSession()

# Specific profile
session = AntiDetectSession(impersonate='chrome120')

# Auto-rotate on every request
session = AntiDetectSession(autoRotate=True)

response = session.get('https://example.com')
print(response.status_code)
```

**Constructor**: `AntiDetectSession(impersonate=None, autoRotate=False, profilePool=None, disableIpv6=True, **kwargs)`

- `impersonate` — profile string; if `None`, picks next from rotation pool
- `autoRotate` — rotate profile before each request
- `profilePool` — custom rotation pool
- `disableIpv6` — force IPv4-only (`True` by default; prevents SOCKS5 IPv6 errors)

### Methods

```python
session.rotateProfile()             # rotate to next profile, returns new profile name
session.rotateProfile('chrome124')  # rotate to specific profile
profile = session.currentProfile    # str — currently active profile
```

## createAntiDetectSession (factory)

```python
from core.extends.CurlSslAntiDetectSession import createAntiDetectSession

session = createAntiDetectSession(impersonate='chrome120', autoRotate=True)
```

## BrowserProfile

Available profile constants:

```python
from core.extends.CurlSslAntiDetectSession import BrowserProfile

BrowserProfile.chromeVersions   # ['chrome110', 'chrome116', ...]
BrowserProfile.edgeVersions     # ['edge101', 'edge99']
BrowserProfile.safariVersions   # ['safari15_3', 'safari15_5', 'safari17_0']
BrowserProfile.allProfiles      # all profiles combined

random_profile = BrowserProfile.getRandomProfile()
random_chrome  = BrowserProfile.getRandomChrome()
random_safari  = BrowserProfile.getRandomSafari()
```

## Usage Examples

### Bootstrap (monkey-patch at startup)

```python
# In ServiceProvider.boot() or app entry point
from core.extends import installAntiDetectSession

installAntiDetectSession(autoRotate=True)

# Elsewhere in the app — no import changes needed
import requests
response = requests.get('https://example.com')
```

### In Background Task

```python
from core.taskSystem import AbstractTask
from core.extends.CurlSslAntiDetectSession import AntiDetectSession

class ScrapingTask(AbstractTask):
    def handle(self):
        session = AntiDetectSession(impersonate='chrome120')

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
# Monkey-patch once at bootstrap, use requests everywhere
from core.extends import installAntiDetectSession
installAntiDetectSession()

# Or use direct session in tasks
from core.extends.CurlSslAntiDetectSession import AntiDetectSession
session = AntiDetectSession(impersonate='chrome120')

# Use in background tasks, not UI thread
class MyTask(AbstractTask):
    def handle(self):
        session = AntiDetectSession()
        response = session.get(url)
```

### ❌ DON'T

```python
# Don't use in UI thread
class MyHandler(BaseCtlHandler):
    def onButtonClicked(self):
        session = AntiDetectSession()  # Wrong! Use in task

# Don't import using the wrong class name
from core.extends import CurlSslAntiDetectSession  # Wrong! That's the module
```

## Related Documentation

- [AbstractTask](13-abstract-task.md) - Background tasks
- [NetworkManager](08-network-manager.md) - UI thread networking
