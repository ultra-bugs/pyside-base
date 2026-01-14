# TextLinesHelpers

Utility class for processing and manipulating text lines with comprehensive functionality.

## Overview

The `TextLinesHelper` class provides static methods for processing text lines, including parsing, filtering, sorting, and transformation operations. It's particularly useful for handling credit card data, text processing, and line-based operations.

## Core Methods

### Basic Operations

#### `getLines(text: str) -> List[str]`
Split text into lines, removing empty lines and stripping whitespace.

```python
from core.helpers import TextLinesHelper

text = "line1\n\nline2\n  line3  \n"
lines = TextLinesHelper.getLines(text)
# Result: ['line1', 'line2', 'line3']
```

#### `ensureLines(input: LineInput) -> List[str]`
Ensure input is a list of lines, converting string if necessary.

```python
lines = TextLinesHelper.ensureLines("line1\nline2")  # Returns ['line1', 'line2']
lines = TextLinesHelper.ensureLines(['line1', 'line2'])  # Returns ['line1', 'line2']
```

#### `getLineCount(text: LineInput) -> int`
Get the number of lines in text.

```python
count = TextLinesHelper.getLineCount("line1\nline2\nline3")  # Returns 3
```

### Credit Card Operations

#### `getCardsByLines(text: LineInput) -> List[C]`
Parse credit card data from lines.

```python
text = "1234567890123456|12|2025|123\n9876543210987654|01|2026|456"
cards = TextLinesHelper.getCardsByLines(text)
# Returns list of C objects
```

#### `parseCardLine(line: str) -> Optional[C]`
Parse a single credit card line.

```python
card = TextLinesHelper.parseCardLine("1234567890123456|12|2025|123")
# Returns C object or None if invalid
```

#### `isValidCardLine(line: str) -> bool`
Check if a line contains valid credit card data.

```python
is_valid = TextLinesHelper.isValidCardLine("1234567890123456|12|2025|123")  # True
is_valid = TextLinesHelper.isValidCardLine("invalid line")  # False
```

#### `cardsToLinesText(cards: List[C]) -> str`
Convert credit card objects back to text format.

```python
cards = [C(num=1234567890123456, exp_month=12, exp_year=2025, cvv=123)]
text = TextLinesHelper.cardsToLinesText(cards)
# Returns "1234567890123456|12|2025|123"
```

### Duplicate Management

#### `uniqueLines(input: LineInput) -> List[str]`
Remove duplicate lines while preserving order.

```python
lines = ["line1", "line2", "line1", "line3"]
unique = TextLinesHelper.uniqueLines(lines)
# Result: ['line1', 'line2', 'line3']
```

#### `duplicateLines(input: LineInput) -> List[str]`
Return only duplicate lines, preserving order of first occurrence.

```python
lines = ["line1", "line2", "line1", "line3", "line2"]
duplicates = TextLinesHelper.duplicateLines(lines)
# Result: ['line1', 'line2']
```

#### `duplicatesWithCount(input: LineInput) -> Dict[str, int]`
Return dictionary of duplicate lines with their counts.

```python
lines = ["line1", "line2", "line1", "line3", "line2", "line1"]
counts = TextLinesHelper.duplicatesWithCount(lines)
# Result: {'line1': 3, 'line2': 2}
```

### Attribute-based Operations

#### `uniqueByAttr(lines: List[str], attr: str) -> List[str]`
Remove duplicates based on an attribute extracted from each line.

```python
lines = ["user=john id=1", "user=jane id=2", "user=john id=3"]
unique = TextLinesHelper.uniqueByAttr(lines, "user")
# Result: ["user=john id=1", "user=jane id=2"]
```

#### `duplicatesByAttr(lines: List[str], attr: str) -> List[str]`
Return lines with duplicate attribute values.

```python
lines = ["user=john id=1", "user=jane id=2", "user=john id=3"]
duplicates = TextLinesHelper.duplicatesByAttr(lines, "user")
# Result: ["user=john id=1", "user=john id=3"]
```

### Callback-based Operations

#### `uniqueByCallback(input: LineInput, callback: Callable) -> List[str]`
Remove items based on a callback function.

```python
def keep_even_length(line, index, all_lines):
    return len(line) % 2 == 0

lines = ["ab", "abc", "abcd", "abcde"]
filtered = TextLinesHelper.uniqueByCallback(lines, keep_even_length)
# Result: ["ab", "abcd"]
```

#### `duplicatesByCallback(input: LineInput, callback: Callable) -> List[str]`
Find duplicates based on a callback function.

```python
def is_duplicate(line, index, all_lines):
    return line in all_lines[:index]

lines = ["line1", "line2", "line1", "line3"]
duplicates = TextLinesHelper.duplicatesByCallback(lines, is_duplicate)
# Result: ["line1"]
```

### Sorting Operations

#### `sort(input: LineInput) -> List[str]`
Sort lines alphabetically.

```python
lines = ["zebra", "apple", "banana"]
sorted_lines = TextLinesHelper.sort(lines)
# Result: ["apple", "banana", "zebra"]
```

#### `sortByDesc(input: LineInput) -> List[str]`
Sort lines in reverse alphabetical order.

```python
lines = ["apple", "banana", "zebra"]
sorted_lines = TextLinesHelper.sortByDesc(lines)
# Result: ["zebra", "banana", "apple"]
```

#### `sortKeys(input: LineInput, key: Callable) -> List[str]`
Sort lines using a key function.

```python
lines = ["apple", "banana", "zebra"]
sorted_lines = TextLinesHelper.sortKeys(lines, len)
# Result: ["apple", "zebra", "banana"] (by length)
```

#### `sortKeyDesc(input: LineInput, key: Callable) -> List[str]`
Sort lines using a key function in reverse order.

```python
lines = ["apple", "banana", "zebra"]
sorted_lines = TextLinesHelper.sortKeyDesc(lines, len)
# Result: ["banana", "zebra", "apple"] (by length, descending)
```

### Search Operations

#### `firstKey(input: LineInput, value: str) -> int`
Find the first index of a line that matches the given value.

```python
lines = ["apple", "banana", "apple", "cherry"]
index = TextLinesHelper.firstKey(lines, "apple")  # Returns 0
index = TextLinesHelper.firstKey(lines, "grape")  # Returns -1
```

#### `keys(input: LineInput, value: str) -> List[int]`
Find all indices of lines that match the given value.

```python
lines = ["apple", "banana", "apple", "cherry"]
indices = TextLinesHelper.keys(lines, "apple")  # Returns [0, 2]
```

#### `has(input: LineInput, value: str) -> bool`
Check if lines contain a specific value.

```python
lines = ["apple", "banana", "cherry"]
has_apple = TextLinesHelper.has(lines, "apple")  # True
has_grape = TextLinesHelper.has(lines, "grape")  # False
```

#### `hasAny(input: LineInput, values: List[str]) -> bool`
Check if lines contain any of the specified values.

```python
lines = ["apple", "banana", "cherry"]
has_fruit = TextLinesHelper.hasAny(lines, ["apple", "grape"])  # True
has_vegetable = TextLinesHelper.hasAny(lines, ["carrot", "lettuce"])  # False
```

### Filtering Operations

#### `where(input: LineInput, condition: Callable) -> List[str]`
Filter lines based on a condition.

```python
def is_long(line):
    return len(line) > 5

lines = ["apple", "banana", "cherry", "kiwi"]
long_lines = TextLinesHelper.where(lines, is_long)
# Result: ["banana", "cherry"]
```

#### `reject(input: LineInput, condition: Callable) -> List[str]`
Return lines that don't pass the given condition.

```python
def is_short(line):
    return len(line) <= 5

lines = ["apple", "banana", "cherry", "kiwi"]
long_lines = TextLinesHelper.reject(lines, is_short)
# Result: ["banana", "cherry"]
```

### Collection Operations

#### `pull(input: LineInput, value: str) -> List[str]`
Remove all occurrences of a value.

```python
lines = ["apple", "banana", "apple", "cherry"]
filtered = TextLinesHelper.pull(lines, "apple")
# Result: ["banana", "cherry"]
```

#### `push(input: LineInput, value: str) -> List[str]`
Add a value to the end of the list.

```python
lines = ["apple", "banana"]
new_lines = TextLinesHelper.push(lines, "cherry")
# Result: ["apple", "banana", "cherry"]
```

#### `merge(input1: LineInput, input2: LineInput) -> List[str]`
Merge two inputs of lines.

```python
lines1 = ["apple", "banana"]
lines2 = ["cherry", "date"]
merged = TextLinesHelper.merge(lines1, lines2)
# Result: ["apple", "banana", "cherry", "date"]
```

### Transformation Operations

#### `prependMap(input: LineInput, callback: Callable) -> List[str]`
Apply a callback to each line and prepend the result.

```python
def add_number(line, index, all_lines):
    return f"{index + 1}. "

lines = ["apple", "banana", "cherry"]
numbered = TextLinesHelper.prependMap(lines, add_number)
# Result: ["1. apple", "2. banana", "3. cherry"]
```

#### `appendMap(input: LineInput, callback: Callable) -> List[str]`
Apply a callback to each line and append the result.

```python
def add_length(line, index, all_lines):
    return f" ({len(line)} chars)"

lines = ["apple", "banana", "cherry"]
with_length = TextLinesHelper.appendMap(lines, add_length)
# Result: ["apple (5 chars)", "banana (6 chars)", "cherry (6 chars)"]
```

#### `map(input: LineInput, callback: Callable) -> List[Any]`
Apply a callback to each line and return the results.

```python
def get_length(line, index, all_lines):
    return len(line)

lines = ["apple", "banana", "cherry"]
lengths = TextLinesHelper.map(lines, get_length)
# Result: [5, 6, 6]
```

#### `reduce(input: LineInput, callback: Callable, initial: Any = None) -> Any`
Reduce collection to a single value.

```python
def concatenate(acc, line, index, all_lines):
    return acc + " " + line

lines = ["apple", "banana", "cherry"]
result = TextLinesHelper.reduce(lines, concatenate, "")
# Result: " apple banana cherry"
```

### Selection Operations

#### `except_(input: LineInput, values: List[str]) -> List[str]`
Return all lines except those in the given list.

```python
lines = ["apple", "banana", "cherry", "date"]
filtered = TextLinesHelper.except_(lines, ["banana", "date"])
# Result: ["apple", "cherry"]
```

#### `only(input: LineInput, values: List[str]) -> List[str]`
Return only the lines that are in the given list.

```python
lines = ["apple", "banana", "cherry", "date"]
filtered = TextLinesHelper.only(lines, ["apple", "cherry"])
# Result: ["apple", "cherry"]
```

### Utility Operations

#### `toGenerator(input: LineInput) -> Generator[str, None, None]`
Convert lines to a generator.

```python
lines = ["apple", "banana", "cherry"]
gen = TextLinesHelper.toGenerator(lines)
for line in gen:
    print(line)  # Prints each line
```

## Type Definitions

```python
from typing import List, Callable, Any, Union

LineInput = Union[str, List[str]]  # Either string or list of strings
```

## Usage Examples

### Credit Card Processing

```python
from core.helpers import TextLinesHelper

# Process credit card data
card_text = """
1234567890123456|12|2025|123
9876543210987654|01|2026|456
1234567890123456|12|2025|123
"""

# Get unique cards
cards = TextLinesHelper.getCardsByLines(card_text)
unique_cards = TextLinesHelper.uniqueLines(card_text)

# Find duplicates
duplicates = TextLinesHelper.duplicateLines(card_text)
```

### Text Processing

```python
# Process log lines
log_text = """
[INFO] Application started
[ERROR] Connection failed
[INFO] Application started
[WARN] Low memory
"""

# Get unique log entries
unique_logs = TextLinesHelper.uniqueLines(log_text)

# Filter by log level
error_logs = TextLinesHelper.where(log_text, lambda line: "[ERROR]" in line)
```

### Data Analysis

```python
# Analyze user data
user_data = """
user=john age=25 city=NYC
user=jane age=30 city=LA
user=john age=25 city=NYC
user=bob age=35 city=Chicago
"""

# Find unique users
unique_users = TextLinesHelper.uniqueByAttr(user_data, "user")

# Find duplicate users
duplicate_users = TextLinesHelper.duplicatesByAttr(user_data, "user")
```

## Notes

- All methods are static and can be called without instantiation
- The class handles both string and list inputs automatically
- Credit card parsing expects format: `number|month|year|cvv`
- Attribute-based operations support key-value, pipe-separated, and space-separated formats
- Callback functions receive `(line, index, all_lines)` parameters
- All operations preserve original order unless explicitly sorting
