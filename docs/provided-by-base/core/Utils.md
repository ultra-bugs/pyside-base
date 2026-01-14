# Utils

Utility classes and helper functions for common operations.

## Overview

The Utils module provides a collection of utility classes and helper functions for common operations including path handling, URL manipulation, Python utilities, and widget operations.

## API Reference

### PathHelper

Utility class for path operations and file system management.

#### `PathHelper`

```python
class PathHelper:
    @staticmethod
    def buildDataPath(relative_path: Union[str, List[str]], *args: str) -> pathlib.Path
    @staticmethod
    def buildAssetPath(relative_path: Union[str, List[str]], *args: str) -> pathlib.Path
    @staticmethod
    def buildVendorPath(relative_path: Union[str, List[str]], *args: str) -> pathlib.Path
    @staticmethod
    def listDir(directory: Union[str, pathlib.Path], pattern: Optional[str] = None) -> List[pathlib.Path]
    @staticmethod
    def isFile(path: Union[str, pathlib.Path]) -> bool
    @staticmethod
    def isDir(path: Union[str, pathlib.Path]) -> bool
    @staticmethod
    def isFileExists(path: Union[str, pathlib.Path]) -> bool
    @staticmethod
    def isDirExists(path: Union[str, pathlib.Path]) -> bool
    @staticmethod
    def ensureDirExists(path: Union[str, pathlib.Path]) -> bool
    @staticmethod
    def ensureParentDirExists(path: Union[str, pathlib.Path]) -> bool
    @staticmethod
    def readJsonFile(jsonPath: Union[str, os.PathLike]) -> Union[Dict[str, Box], List[Box], Box]
    @staticmethod
    def joinPath(*paths: Union[str, pathlib.Path]) -> pathlib.Path
    @staticmethod
    def rootDir() -> pathlib.Path
    @staticmethod
    def dataDir() -> pathlib.Path
    @staticmethod
    def assetsDir() -> pathlib.Path
    @staticmethod
    def vendorDir() -> pathlib.Path
    @staticmethod
    def resolvePath(path: Union[str, os.PathLike]) -> Union[str, os.PathLike]
    @staticmethod
    def relativePathFromAbs(absolute_path: Union[str, pathlib.Path], base_path: Optional[Union[str, pathlib.Path]]=None) -> str
    @staticmethod
    def relativeModulePathFromAbs(absolute_path: Union[str, pathlib.Path], base_path: Optional[Union[str, pathlib.Path]]=None) -> str
    @staticmethod
    def isSymlink(path: Union[str, pathlib.Path]) -> bool
    @staticmethod
    def getSymlinkTarget(path: Union[str, pathlib.Path]) -> Optional[pathlib.Path]
    @staticmethod
    def isUsingSymlinkedCore() -> bool
    @staticmethod
    def debugPathInfo() -> str
```

**Methods:**

##### `buildDataPath(relative_path: Union[str, List[str]], *args: str) -> pathlib.Path`
Build path relative to data directory.

**Parameters:**
- `relative_path` (Union[str, List[str]]): Relative path from data directory
- `*args` (str): Additional path components

**Returns:**
- `pathlib.Path`: Absolute path

##### `buildAssetPath(relative_path: Union[str, List[str]], *args: str) -> pathlib.Path`
Build path relative to assets directory.

**Parameters:**
- `relative_path` (Union[str, List[str]]): Relative path from assets directory
- `*args` (str): Additional path components

**Returns:**
- `pathlib.Path`: Absolute path

##### `buildVendorPath(relative_path: Union[str, List[str]], *args: str) -> pathlib.Path`
Build path relative to vendor directory.

**Parameters:**
- `relative_path` (Union[str, List[str]]): Relative path from vendor directory
- `*args` (str): Additional path components

**Returns:**
- `pathlib.Path`: Absolute path

##### `listDir(directory: Union[str, pathlib.Path], pattern: Optional[str] = None) -> List[pathlib.Path]`
List files and directories in a directory.

**Parameters:**
- `directory` (Union[str, pathlib.Path]): Directory to list
- `pattern` (Optional[str]): Glob pattern to filter results

**Returns:**
- `List[pathlib.Path]`: List of paths

##### `isFile(path: Union[str, pathlib.Path]) -> bool`
Check if path is a file.

**Parameters:**
- `path` (Union[str, pathlib.Path]): Path to check

**Returns:**
- `bool`: True if path is a file

##### `isDir(path: Union[str, pathlib.Path]) -> bool`
Check if path is a directory.

**Parameters:**
- `path` (Union[str, pathlib.Path]): Path to check

**Returns:**
- `bool`: True if path is a directory

##### `isFileExists(path: Union[str, pathlib.Path]) -> bool`
Check if file exists.

**Parameters:**
- `path` (Union[str, pathlib.Path]): Path to check

**Returns:**
- `bool`: True if file exists

##### `isDirExists(path: Union[str, pathlib.Path]) -> bool`
Check if directory exists.

**Parameters:**
- `path` (Union[str, pathlib.Path]): Path to check

**Returns:**
- `bool`: True if directory exists

##### `ensureDirExists(path: Union[str, pathlib.Path]) -> bool`
Ensure directory exists, create if not.

**Parameters:**
- `path` (Union[str, pathlib.Path]): Directory path

**Returns:**
- `bool`: True if directory exists or was created

##### `ensureParentDirExists(path: Union[str, pathlib.Path]) -> bool`
Ensure parent directory exists, create if not.

**Parameters:**
- `path` (Union[str, pathlib.Path]): File path

**Returns:**
- `bool`: True if parent directory exists or was created

##### `readJsonFile(jsonPath: Union[str, os.PathLike]) -> Union[Dict[str, Box], List[Box], Box]`
Read JSON file and return content.

**Parameters:**
- `jsonPath` (Union[str, os.PathLike]): Path to JSON file

**Returns:**
- `Union[Dict[str, Box], List[Box], Box]`: JSON content

##### `joinPath(*paths: Union[str, pathlib.Path]) -> pathlib.Path`
Join multiple paths.

**Parameters:**
- `*paths` (Union[str, pathlib.Path]): Paths to join

**Returns:**
- `pathlib.Path`: Joined path

##### `rootDir() -> pathlib.Path`
Get project root directory.

**Returns:**
- `pathlib.Path`: Root directory path

##### `dataDir() -> pathlib.Path`
Get data directory.

**Returns:**
- `pathlib.Path`: Data directory path

##### `assetsDir() -> pathlib.Path`
Get assets directory.

**Returns:**
- `pathlib.Path`: Assets directory path

##### `vendorDir() -> pathlib.Path`
Get vendor directory.

**Returns:**
- `pathlib.Path`: Vendor directory path

##### `resolvePath(path: Union[str, os.PathLike]) -> Union[str, os.PathLike]`
Resolve path to absolute path.

**Parameters:**
- `path` (Union[str, os.PathLike]): Path to resolve

**Returns:**
- `Union[str, os.PathLike]`: Resolved path

##### `relativePathFromAbs(absolute_path: Union[str, pathlib.Path], base_path: Optional[Union[str, pathlib.Path]]=None) -> str`
Get the relative path from a base path to an absolute path.

**Parameters:**
- `absolute_path` (Union[str, pathlib.Path]): The absolute path to convert.
- `base_path` (Optional[Union[str, pathlib.Path]]): The base path to calculate the relative path from.

**Returns:**
- `str`: The relative path.

##### `relativeModulePathFromAbs(absolute_path: Union[str, pathlib.Path], base_path: Optional[Union[str, pathlib.Path]]=None) -> str`
Get the relative module path from a base path to an absolute path.

**Parameters:**
- `absolute_path` (Union[str, pathlib.Path]): The absolute path to convert.
- `base_path` (Optional[Union[str, pathlib.Path]]): The base path to calculate the relative path from.

**Returns:**
- `str`: The relative module path.

##### `isSymlink(path: Union[str, pathlib.Path]) -> bool`
Check if the path is a symlink.

**Parameters:**
- `path` (Union[str, pathlib.Path]): The path to check.

**Returns:**
- `bool`: True if path is a symlink, False otherwise.

##### `getSymlinkTarget(path: Union[str, pathlib.Path]) -> Optional[pathlib.Path]`
Get the target of a symlink.

**Parameters:**
- `path` (Union[str, pathlib.Path]): The symlink path to resolve.

**Returns:**
- `Optional[pathlib.Path]`: The target path of the symlink, or None if not a symlink.

##### `isUsingSymlinkedCore() -> bool`
Check if the current core directory is a symlink.

**Returns:**
- `bool`: True if the core directory is a symlink, False otherwise.

##### `debugPathInfo() -> str`
Get debug information about the current path configuration.

**Returns:**
- `str`: A formatted string with path information.

### UrlHelper

Utility class for URL manipulation and validation.

#### `UrlHelper`

```python
class UrlHelper:
    @staticmethod
    def getUriComponents(string: str, components: List[URIComponent]) -> Dict[URIComponent, str]
```

**Methods:**

##### `getUriComponents(string: str, components: List[URIComponent]) -> Dict[URIComponent, str]`
Get specified URI components from a string.

**Parameters:**
- `string` (str): The URI string to parse
- `components` (List[URIComponent]): List of URI components to extract

**Returns:**
- `Dict[URIComponent, str]`: Dictionary mapping components to their values

### WidgetUtils

Utility class for Qt widget operations.

#### `WidgetUtils`

```python
class WidgetUtils:
    @staticmethod
    def showAlertMsgBox(controller: None, msg: str = "", title: str = "INFO", icon: int = QMessageBox.Information, createOnly = False, placeCursorAtDefaultBtn=False)
    @staticmethod
    def showErrorMsgBox(controller = None, msg: str = "Opps. Something went wrong", title: str = "ERROR", icon: int = QMessageBox.Critical, createOnly = False, placeCursorAtDefaultBtn=False)
    @staticmethod
    def showYesNoMsgBox(controller: None, msg: str = "Are you sure?", title: str = "MESSAGE", icon: int = QMessageBox.Question, createOnly = False, defaultYes = False, escapeNo = False) -> bool
    @staticmethod
    def transQt(msg: str, name_space: str = None) -> str
```

**Methods:**

##### `showAlertMsgBox(controller: None, msg: str = "", title: str = "INFO", icon: int = QMessageBox.Information, createOnly = False, placeCursorAtDefaultBtn=False)`
Show an alert message box.

**Parameters:**
- `controller` (None): Controller instance
- `msg` (str): Message text
- `title` (str): Window title
- `icon` (int): Message box icon
- `createOnly` (bool): Only create, don't show
- `placeCursorAtDefaultBtn` (bool): Move cursor to default button

**Returns:**
- `QMessageBox`: Message box instance

##### `showErrorMsgBox(controller = None, msg: str = "Opps. Something went wrong", title: str = "ERROR", icon: int = QMessageBox.Critical, createOnly = False, placeCursorAtDefaultBtn=False)`
Show an error message box.

**Parameters:**
- `controller` (None): Controller instance
- `msg` (str): Error message
- `title` (str): Window title
- `icon` (int): Message box icon
- `createOnly` (bool): Only create, don't show
- `placeCursorAtDefaultBtn` (bool): Move cursor to default button

**Returns:**
- `QMessageBox`: Message box instance

##### `showYesNoMsgBox(controller: None, msg: str = "Are you sure?", title: str = "MESSAGE", icon: int = QMessageBox.Question, createOnly = False, defaultYes = False, escapeNo = False) -> bool`
Show a yes/no message box.

**Parameters:**
- `controller` (None): Controller instance
- `msg` (str): Message text
- `title` (str): Window title
- `icon` (int): Message box icon
- `createOnly` (bool): Only create, don't show
- `defaultYes` (bool): Default to Yes button
- `escapeNo` (bool): Escape key selects No

**Returns:**
- `bool`: True if Yes was selected

##### `transQt(msg: str, name_space: str = None) -> str`
Translate text using Qt translation system.

**Parameters:**
- `msg` (str): Text to translate
- `name_space` (str, optional): Translation namespace

**Returns:**
- `str`: Translated text

### PythonHelper

Utility class for Python-specific operations.

#### `PythonHelper`

```python
class PythonHelper:
    @staticmethod
    def is_type_compatible(value, annotation)
    @staticmethod
    def dataclass2Json(data_object: T, anotherDict: Optional[Dict[str, Any]]=None) -> str
    @staticmethod
    def dataclass2Dict(data_object: T, *anotherDict: Optional[Dict[str, Any]]) -> Dict[str, Any]
    @staticmethod
    def getEnvOfProcess(pid)
    @staticmethod
    def killProcessById(pid)
    @staticmethod
    def killAllProcessByName(name)
    @staticmethod
    def getProcessIdsByName(name)
    @staticmethod
    def getProcessListByName(name)
    @staticmethod
    def func_get_args()
    @staticmethod
    def env(key, type_, default=None)
    @staticmethod
    def mergeDicts(dict1, dict2)
    @staticmethod
    def strGetBetween(s: str, before: str, after: str) -> str
    @staticmethod
    def createFairRandomChooser(items: List[T]) -> Callable[[], T]
    @staticmethod
    def simpleFormatUuid(uuid: Union[str, UUID]) -> str
    @staticmethod
    def simpleFormatCcNumber(num) -> str
    @staticmethod
    def generateRandomString(length: int=8) -> str
```

**Methods:**

##### `is_type_compatible(value, annotation)`
Check if a value is compatible with a type annotation.

##### `dataclass2Json(data_object: T, anotherDict: Optional[Dict[str, Any]]=None) -> str`
Convert a dataclass object to a JSON string.

##### `dataclass2Dict(data_object: T, *anotherDict: Optional[Dict[str, Any]]) -> Dict[str, Any]`
Convert a dataclass object to a dictionary.

##### `getEnvOfProcess(pid)`
Get environment variables of a process.

##### `killProcessById(pid)`
Kill a process by ID.

##### `killAllProcessByName(name)`
Kill all processes by name.

##### `getProcessIdsByName(name)`
Get process IDs by name.

##### `getProcessListByName(name)`
Get process list by name.

##### `func_get_args()`
Get arguments of the current function.

##### `env(key, type_, default=None)`
Get environment variable with type conversion.

##### `mergeDicts(dict1, dict2)`
Merge two dictionaries recursively.

##### `strGetBetween(s: str, before: str, after: str) -> str`
Get string between two substrings.

##### `createFairRandomChooser(items: List[T]) -> Callable[[], T]`
Create a fair random chooser that ensures all items are picked once before repeating.

##### `simpleFormatUuid(uuid: Union[str, UUID]) -> str`
Format UUID to simple string (first 8 chars).

##### `simpleFormatCcNumber(num) -> str`
Format credit card number (first 4 and last 4 digits).

##### `generateRandomString(length: int=8) -> str`
Generate a random alphanumeric string.

### ProxyHelper

Utility class for proxy operations.

#### `ProxyHelper`

```python
class ProxyHelper:
    @staticmethod
    def parseProxyString(proxy_string: str) -> ProxyInfo
    @staticmethod
    def setChromiumProxy(proxy_string: str, chromium_options: 'DrissionPage._configs.chromium_options.ChromiumOptions') -> Any
    @staticmethod
    def checkProxyConnection(proxy_string: str, check_url: str='https://api.ipify.org/') -> ProxyCheckResult
```

**Methods:**

##### `parseProxyString(proxy_string: str) -> ProxyInfo`
Parse proxy string and return ProxyInfo object.

##### `setChromiumProxy(proxy_string: str, chromium_options: 'DrissionPage._configs.chromium_options.ChromiumOptions') -> Any`
Set proxy for ChromiumOptions.

##### `checkProxyConnection(proxy_string: str, check_url: str='https://api.ipify.org/') -> ProxyCheckResult`
Check proxy connection and return IP comparison result.

### OsHelper

Utility class for OS operations.

#### `OsHelper`

```python
class OsHelper:
    @staticmethod
    def openWithDefaultProgram(file_path: Union[str, pathlib.Path]) -> bool
```

**Methods:**

##### `openWithDefaultProgram(file_path: Union[str, pathlib.Path]) -> bool`
Opens a file with the default associated program based on the operating system.

### Utility Functions

#### `isInDebugEnv() -> bool`
Check if running in debug environment.

**Returns:**
- `bool`: True if debug environment

## Usage Examples

### Path Operations

```python
from core import PathHelper

# Build paths
data_path = PathHelper.buildDataPath('config/settings.json')
asset_path = PathHelper.buildAssetPath('images/logo.png')

# Check file system
if PathHelper.isFileExists(data_path):
    print(f"File exists: {data_path}")

# Create directory
PathHelper.ensureParentDirExists(data_path)

# Relative paths
rel_path = PathHelper.relativePathFromAbs(data_path)
```

### URL Operations

```python
from core import UrlHelper, URIComponent

# Parse URL
components = UrlHelper.getUriComponents(
    'https://user:pass@api.example.com:8080/users?page=1',
    [URIComponent.SCHEME, URIComponent.HOST, URIComponent.PORT]
)
print(components.host)  # api.example.com
```

### Python Utilities

```python
from core import PythonHelper

# Dataclass conversion
json_str = PythonHelper.dataclass2Json(my_dataclass)

# Environment variables
debug = PythonHelper.env('DEBUG', bool, False)

# Random string
random_str = PythonHelper.generateRandomString(16)
```

### Widget Operations

```python
from core import WidgetUtils

# Show alert
WidgetUtils.showAlertMsgBox(self, "Operation completed", "Success")

# Show confirmation
if WidgetUtils.showYesNoMsgBox(self, "Delete item?"):
    delete_item()
```

### Proxy Operations

```python
from core import ProxyHelper

# Check proxy
try:
    result = ProxyHelper.checkProxyConnection("socks5://127.0.0.1:1080")
    if result.isChanged:
        print(f"Proxy working. IP: {result.proxied}")
except ProxyDeadError:
    print("Proxy failed")
```

## Best Practices

1. **Use PathHelper for paths**: Always use PathHelper for path operations
2. **Validate URLs**: Always validate URLs before using them
3. **Check debug mode**: Use debug mode checks for conditional behavior
4. **Handle errors**: Always handle potential errors in utility operations
5. **Use type hints**: Leverage type hints for better code clarity
6. **Keep utilities focused**: Each utility class should have a specific purpose

## Dependencies

- `pathlib` - Path operations
- `urllib.parse` - URL parsing
- `inspect` - Python introspection
- `platform` - System information
- `PySide6.QtWidgets` - Widget operations
- `numpy` - Numerical operations
- `requests` - HTTP requests (for proxy check)
- `curl_cffi` - HTTP requests (for proxy check)

## Related Components

- [Config](Config.md) - Configuration management
- [Logging](Logging.md) - Logging system
- [WidgetManager](WidgetManager.md) - Widget management
