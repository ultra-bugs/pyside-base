# StealthBrowserHelper

Helper class for implementing stealth techniques to avoid detection by anti-bot systems.

## Overview

The `StealthBrowserHelper` class provides methods to modify browser behavior and properties to make automated browsing appear more like human interaction. It integrates with DrissionPage and ChromeBrowser services to apply various stealth techniques.

## Initialization

```python
from core.helpers import StealthBrowserHelper
from services.ChromeBrowserServices import ChromeBrowser

# Initialize with ChromeBrowser
browser = ChromeBrowser()
stealth = StealthBrowserHelper(browser)

# Or initialize with DrissionPage objects
from DrissionPage import WebPage

page = WebPage()
stealth = StealthBrowserHelper(page)
```

**Parameters:**
- `browser` - ChromeBrowser, WebPage, or ChromiumPage instance
- `objectUid` - Optional unique identifier (auto-generated if not provided)

## Stealth Techniques

### Navigator Webdriver

#### `patchNavigatorWebdriver()`
Hides the `navigator.webdriver` property to avoid detection.

```python
stealth.patchNavigatorWebdriver()
# Sets navigator.webdriver to false
```

#### `isNavigatorWebdriverOn() -> bool`
Check if navigator webdriver patching is active.

```python
if stealth.isNavigatorWebdriverOn():
    print("Navigator webdriver is patched")
```

### User Agent Spoofing

#### `spoofUserAgent(ua: str)`
Spoof the user agent string.

```python
stealth.spoofUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
```

#### `isUserAgentOn() -> bool`
Check if user agent spoofing is active.

```python
if stealth.isUserAgentOn():
    print("User agent is spoofed")
```

### Chrome Runtime

#### `patchChromeRuntime()`
Adds a fake `window.chrome.runtime` object.

```python
stealth.patchChromeRuntime()
# Creates window.chrome = { runtime: {} }
```

#### `isChromeRuntimeOn() -> bool`
Check if Chrome runtime patching is active.

```python
if stealth.isChromeRuntimeOn():
    print("Chrome runtime is patched")
```

### Canvas Fingerprinting

#### `hookCanvas()`
Modifies canvas rendering to avoid fingerprinting.

```python
stealth.hookCanvas()
# Returns fake canvas data
```

#### `isCanvasOn() -> bool`
Check if canvas hooking is active.

```python
if stealth.isCanvasOn():
    print("Canvas is hooked")
```

### WebGL Fingerprinting

#### `hookWebgl()`
Modifies WebGL properties to avoid fingerprinting.

```python
stealth.hookWebgl()
# Spoofs WebGL vendor and renderer
```

#### `isWebGLOn() -> bool`
Check if WebGL hooking is active.

```python
if stealth.isWebGLOn():
    print("WebGL is hooked")
```

### Function toString

#### `hookFunctionToString()`
Modifies `Function.prototype.toString` to hide automation.

```python
stealth.hookFunctionToString()
# Returns native code for Object.defineProperty
```

#### `isFnToStringOn() -> bool`
Check if function toString hooking is active.

```python
if stealth.isFnToStringOn():
    print("Function toString is hooked")
```

### Internationalization

#### `spoofIntlLocales(locales: list)`
Spoofs internationalization locales.

```python
stealth.spoofIntlLocales(['en-US', 'en-GB'])
# Modifies Intl.DateTimeFormat
```

#### `isIntlLocalesOn() -> bool`
Check if Intl locales spoofing is active.

```python
if stealth.isIntlLocalesOn():
    print("Intl locales are spoofed")
```

## Convenience Methods

### `applyAll(ua: str = None, intl_locales: list = None)`
Apply all stealth techniques at once.

```python
# Apply all techniques with custom user agent
stealth.applyAll(
    ua="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    intl_locales=['en-US', 'en-GB']
)
```

**Parameters:**
- `ua` - Optional custom user agent string
- `intl_locales` - Optional list of locales for Intl spoofing

## State Management

The helper tracks the state of each stealth technique:

```python
# Check individual technique states
stealth_states = {
    'NavigatorWebdriver': False,
    'UserAgent': False,
    'ChromeRuntime': False,
    'Canvas': False,
    'WebGL': False,
    'FnToString': False,
    'IntlLocales': False,
}
```

## Integration Examples

### With ChromeBrowser

```python
from services.ChromeBrowserServices import ChromeBrowser
from core.helpers import StealthBrowserHelper

# Create browser instance
browser = ChromeBrowser()
browser.startChromeProcess()

# Apply stealth techniques
stealth = StealthBrowserHelper(browser)
stealth.applyAll(
        ua="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        intl_locales=['en-US']
)

# Navigate to target site
browser.navigate("https://example.com")
```

### With DrissionPage

```python
from DrissionPage import WebPage
from core.helpers import StealthBrowserHelper

# Create page instance
page = WebPage()

# Apply stealth techniques
stealth = StealthBrowserHelper(page)
stealth.patchNavigatorWebdriver()
stealth.spoofUserAgent("Custom User Agent")
stealth.patchChromeRuntime()

# Navigate to target site
page.get("https://example.com")
```

### Selective Stealth Application

```python
# Apply only specific techniques
stealth.patchNavigatorWebdriver()
stealth.hookCanvas()
stealth.hookWebgl()

# Check what's active
print(f"Navigator patched: {stealth.isNavigatorWebdriverOn()}")
print(f"Canvas hooked: {stealth.isCanvasOn()}")
print(f"WebGL hooked: {stealth.isWebGLOn()}")
```

## Advanced Usage

### Custom Stealth Configuration

```python
# Create stealth helper
stealth = StealthBrowserHelper(browser)

# Apply techniques based on requirements
if needs_user_agent_spoofing:
    stealth.spoofUserAgent(custom_ua)
    
if needs_canvas_protection:
    stealth.hookCanvas()
    
if needs_webgl_protection:
    stealth.hookWebgl()

# Always patch navigator webdriver
stealth.patchNavigatorWebdriver()
```

### State Monitoring

```python
# Monitor stealth state
def check_stealth_status(stealth):
    status = {
        'navigator': stealth.isNavigatorWebdriverOn(),
        'user_agent': stealth.isUserAgentOn(),
        'chrome_runtime': stealth.isChromeRuntimeOn(),
        'canvas': stealth.isCanvasOn(),
        'webgl': stealth.isWebGLOn(),
        'function_toString': stealth.isFnToStringOn(),
        'intl_locales': stealth.isIntlLocalesOn(),
    }
    return status

# Check current status
status = check_stealth_status(stealth)
print(f"Active stealth techniques: {[k for k, v in status.items() if v]}")
```

## Notes

- All stealth techniques are applied via JavaScript injection
- Techniques are applied to the current page context
- State is tracked per instance
- Integration with ChromeBrowser automatically sets up the stealth relationship
- Some techniques may conflict with certain websites or security measures
- Use `applyAll()` for comprehensive stealth coverage
- Individual techniques can be applied selectively based on requirements
