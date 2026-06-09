# Model - Data Models

> **Base models and mixins for data tracking**
> **Last synced**: `2026-06-09`

## BaseAttributeModel

Base model with attribute access:

```python
from core.model import BaseAttributeModel

class UserModel(BaseAttributeModel):
    def __init__(self, data: dict):
        super().__init__(data)
    
    @property
    def name(self):
        return self.get('name')
    
    @property
    def email(self):
        return self.get('email')

# Usage
user = UserModel({'name': 'John', 'email': 'john@example.com'})
print(user.name)  # 'John'
print(user.email)  # 'john@example.com'
```

## DataTrackingMixin

Row/column dirty-tracking mixin for Qt item models. Tracks which cells have changed since the last `commitData()` call.

```python
from core.model import DataTrackingMixin
from PySide6.QtCore import QAbstractTableModel

class MyTableModel(DataTrackingMixin, QAbstractTableModel):
    def __init__(self):
        super().__init__()

    def setData(self, index, value, role=Qt.EditRole):
        # Calls DataTrackingMixin.setData internally — records dirty state
        super().setData(index, value)
        return True
```

### Key methods

```python
model.setData(index, value)   # record new value; marks cell dirty if changed
model.commitData()            # snapshot current data as "last committed" — clears dirty state
model.isDirty()               # bool — True if any cell changed since last commitData()
model.getDirtyData()          # dict[key, {'old_value': ..., 'new_value': ...}]
```

### Override callbacks

```python
class MyModel(DataTrackingMixin, QAbstractTableModel):
    def onDataModified(self, key, oldValue, newValue):
        # Called when an existing cell's value changes
        print(f'{key}: {oldValue} → {newValue}')

    def onDataAdded(self, key, value):
        # Called when a new cell is first set
        print(f'{key} added: {value}')
```

The cell key is derived from the row/column pattern `_key_pattern` (default `'{row}_{column}'`). Change via `DataTrackingMixin.setKeyPattern('{row}')` for row-only models.

## Usage Examples

### User Model

```python
from core.model import BaseAttributeModel

class User(BaseAttributeModel):
    @property
    def id(self):
        return self.get('id')
    
    @property
    def username(self):
        return self.get('username')
    
    @property
    def isActive(self):
        return self.get('is_active', default=False)

# Create from API response
userData = {'id': 123, 'username': 'john', 'is_active': True}
user = User(userData)

print(user.id)  # 123
print(user.username)  # 'john'
print(user.isActive)  # True
```

### Tracked Table Model

```python
from core.model import DataTrackingMixin
from PySide6.QtCore import QAbstractTableModel, Qt

class EditableTableModel(DataTrackingMixin, QAbstractTableModel):
    def __init__(self):
        super().__init__()

    def setData(self, index, value, role=Qt.EditRole):
        super().setData(index, value)  # records dirty
        self.dataChanged.emit(index, index)
        return True

    def onDataModified(self, key, oldValue, newValue):
        print(f'Cell {key} changed: {oldValue} → {newValue}')

model = EditableTableModel()
# After edits...
if model.isDirty():
    dirty = model.getDirtyData()   # {'0_1': {'old_value': 'A', 'new_value': 'B'}, ...}
    model.commitData()             # accept edits, clear dirty state
```

## Best Practices

### ✅ DO

```python
# Use BaseAttributeModel for API responses
class ApiResponse(BaseAttributeModel):
    @property
    def status(self):
        return self.get('status')

# Use DataTrackingMixin for Qt table models needing dirty-detection
class MyModel(DataTrackingMixin, QAbstractTableModel):
    def setData(self, index, value, role=Qt.EditRole):
        super().setData(index, value)
        return True

# Commit after accepting edits
if model.isDirty():
    model.commitData()
```

### ❌ DON'T

```python
# Don't access dict directly
class User(BaseAttributeModel):
    @property
    def name(self):
        return self._data['name']  # Use self.get('name')

# DataTrackingMixin is not a generic key-value change tracker
# It requires Qt model indices (row/column), not plain string keys
```

## Related Documentation

- [Config](06-configuration.md) - Configuration management
- [Utilities](10-utilities.md) - Data helpers
