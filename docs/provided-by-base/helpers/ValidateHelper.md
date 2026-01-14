# ValidateHelper

Input validation helper utilities.

## Overview

`ValidateHelper` provides static methods for validating various types of input data including hostnames, domains, and other common data formats.

## API Reference

### Class Definition

```python
class ValidateHelper:
    @staticmethod
    def validateHostname(hostname: str, raiseEx: bool = False) -> Tuple[bool, str]
    @staticmethod
    def isTopLevelDomain(domain: str, raiseEx: bool = False) -> bool
    @staticmethod
    def validateMultipleHostnames(hostnames: str, raiseEx: bool = False) -> Tuple[bool, str, List[str]]
```

### Methods

#### `validateHostname(hostname: str, raiseEx: bool = False) -> Tuple[bool, str]`
Validate hostname format.

**Parameters:**
- `hostname` (str): Hostname to validate
- `raiseEx` (bool): Whether to raise exception on validation failure

**Returns:**
- `Tuple[bool, str]`: (is_valid, error_message)

**Raises:**
- `InputError`: If validation fails and raiseEx is True

#### `isTopLevelDomain(domain: str, raiseEx: bool = False) -> bool`
Check if domain is a top-level domain (has only one dot).

**Parameters:**
- `domain` (str): Domain to check
- `raiseEx` (bool): Whether to raise exception on validation failure

**Returns:**
- `bool`: True if domain is top-level

**Raises:**
- `InputError`: If validation fails and raiseEx is True

#### `validateMultipleHostnames(hostnames: str, raiseEx: bool = False) -> Tuple[bool, str, List[str]]`
Validate multiple hostnames from a comma-separated string.

**Parameters:**
- `hostnames` (str): Comma-separated hostnames to validate
- `raiseEx` (bool): Whether to raise exception on validation failure

**Returns:**
- `Tuple[bool, str, List[str]]`: (is_valid, error_message, validated_hostnames)

**Raises:**
- `InputError`: If validation fails and raiseEx is True

## Usage Examples

### Basic Hostname Validation

```python
from core.helpers.ValidateHelper import ValidateHelper

# Validate single hostname
is_valid, error = ValidateHelper.validateHostname("example.com")
if is_valid:
    print("Valid hostname")
else:
    print(f"Invalid hostname: {error}")

# Validate with exception
try:
    ValidateHelper.validateHostname("invalid..hostname", raiseEx=True)
except InputError as e:
    print(f"Validation error: {e}")
```

### Top-Level Domain Check

```python
from core.helpers.ValidateHelper import ValidateHelper

# Check if domain is top-level
is_tld = ValidateHelper.isTopLevelDomain("example.com")
print(f"Is TLD: {is_tld}")  # True

is_tld = ValidateHelper.isTopLevelDomain("sub.example.com")
print(f"Is TLD: {is_tld}")  # False
```

### Multiple Hostnames Validation

```python
from core.helpers.ValidateHelper import ValidateHelper

# Validate multiple hostnames
hostnames = "example.com, sub.example.com, invalid..hostname"
is_valid, error, validated = ValidateHelper.validateMultipleHostnames(hostnames)

if is_valid:
    print(f"All hostnames valid: {validated}")
else:
    print(f"Validation error: {error}")
    print(f"Valid hostnames: {validated}")
```

### Error Handling

```python
from core.helpers.ValidateHelper import ValidateHelper, InputError


def validate_input(hostname):
    try:
        is_valid, error = ValidateHelper.validateHostname(hostname, raiseEx=True)
        return True, "Valid"
    except InputError as e:
        return False, str(e)


# Test validation
result = validate_input("example.com")
print(result)  # (True, "Valid")

result = validate_input("invalid..hostname")
print(result)  # (False, "Invalid hostname format...")
```

### Batch Processing

```python
from core.helpers.ValidateHelper import ValidateHelper


def process_hostnames(hostname_list):
    valid_hostnames = []
    invalid_hostnames = []
    
    for hostname in hostname_list:
        is_valid, error = ValidateHelper.validateHostname(hostname)
        if is_valid:
            valid_hostnames.append(hostname)
        else:
            invalid_hostnames.append((hostname, error))
    
    return valid_hostnames, invalid_hostnames


# Process list of hostnames
hostnames = ["example.com", "sub.example.com", "invalid..hostname", "test.org"]
valid, invalid = process_hostnames(hostnames)

print(f"Valid: {valid}")
print(f"Invalid: {invalid}")
```

## Best Practices

1. **Use appropriate validation**: Choose the right validation method for your data type
2. **Handle errors gracefully**: Always handle validation errors appropriately
3. **Use raiseEx parameter**: Use `raiseEx=True` when you want exceptions for invalid input
4. **Validate early**: Validate input as early as possible in your application
5. **Provide clear error messages**: Use the error messages to provide user feedback

## Dependencies

- `core.Exceptions.AppException` - Base exception class
- `re` - Regular expressions for pattern matching

## Related Components

- [AppHelper](AppHelper.md) - Application helper utilities
- [Exceptions](core/Exceptions.md) - Exception handling
