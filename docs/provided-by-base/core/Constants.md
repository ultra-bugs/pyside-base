# Constants

Core constants and enumerations used throughout the application.

## Overview

The `Constants` module provides essential enumerations and constant values used across the application for type safety and consistency.

**Note:** The `URIComponent` enum is defined in `core.Utils` but documented here for reference.

## Enumerations

### URIComponent

Enumeration for URI component types, used for parsing and manipulating URLs.

```python
from core.Utils import URIComponent

# Available components
URIComponent.SCHEME    # Protocol (http, https, ftp, etc.)
URIComponent.HOST      # Domain name or IP address
URIComponent.PORT      # Port number
URIComponent.PATH      # Path portion of the URL
URIComponent.QUERY     # Query string parameters
URIComponent.FRAGMENT  # Fragment identifier (#section)
URIComponent.USERNAME  # Username for authentication
URIComponent.PASSWORD  # Password for authentication
```

**Usage Examples:**

```python
from core.Utils import URIComponent

# Check if a component is a scheme
if component_type == URIComponent.SCHEME:
    print("This is a protocol component")

# Use in URL parsing
def parse_url_component(url, component_type):
    if component_type == URIComponent.HOST:
        return extract_host(url)
    elif component_type == URIComponent.PORT:
        return extract_port(url)
    # ... other components
```

**Available Components:**
- `SCHEME` - Protocol identifier (http, https, ftp, etc.)
- `HOST` - Domain name or IP address
- `PORT` - Port number
- `PATH` - Path portion of the URL
- `QUERY` - Query string parameters
- `FRAGMENT` - Fragment identifier
- `USERNAME` - Username for authentication
- `PASSWORD` - Password for authentication

## Implementation Details

The enumeration uses Python's `auto()` function to automatically assign values, ensuring type safety and preventing magic numbers in the codebase.

```python
from enum import Enum, auto

class URIComponent(Enum):
    """URI component types"""
    SCHEME = auto()
    HOST = auto()
    PORT = auto()
    PATH = auto()
    QUERY = auto()
    FRAGMENT = auto()
    USERNAME = auto()
    PASSWORD = auto()
```

## Usage Patterns

### Type Checking

```python
from core.Utils import URIComponent
from typing import Union

def process_uri_component(component: URIComponent, value: str) -> str:
    """Process a URI component based on its type"""
    if component == URIComponent.SCHEME:
        return value.lower()
    elif component == URIComponent.HOST:
        return value.lower().strip()
    elif component == URIComponent.PORT:
        return str(int(value)) if value.isdigit() else "80"
    # ... handle other components
    return value
```

### URL Parsing

```python
from core.Utils import URIComponent

def extract_uri_components(url: str) -> dict:
    """Extract all URI components from a URL"""
    components = {}
    
    # Parse different components
    for component_type in URIComponent:
        components[component_type] = extract_component(url, component_type)
    
    return components
```

### Validation

```python
from core.Utils import URIComponent

def validate_uri_component(component: URIComponent, value: str) -> bool:
    """Validate a URI component value"""
    if component == URIComponent.SCHEME:
        return value.lower() in ['http', 'https', 'ftp', 'ftps']
    elif component == URIComponent.PORT:
        return value.isdigit() and 1 <= int(value) <= 65535
    elif component == URIComponent.HOST:
        return len(value) > 0 and '.' in value
    # ... other validations
    return True
```

## Notes

- All enumeration values are automatically assigned using `auto()`
- Use `URIComponent` for type hints to ensure type safety
- The enumeration is designed to be extensible for future URI components
- Values are guaranteed to be unique and consistent across application runs
