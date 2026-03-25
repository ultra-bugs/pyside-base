# Model - Data Models

> **Base models and mixins for data tracking**

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

Track data changes:

```python
from core.model import DataTrackingMixin

class TrackedModel(DataTrackingMixin):
    def __init__(self):
        super().__init__()
        self.data = {}
    
    def updateData(self, key, value):
        self._trackChange(key, value)
        self.data[key] = value

# Usage
model = TrackedModel()
model.updateData('name', 'John')
model.updateData('name', 'Jane')

changes = model.getChanges()
print(changes)  # History of changes
```

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

### Tracked Configuration

```python
from core.model import DataTrackingMixin

class AppConfig(DataTrackingMixin):
    def __init__(self):
        super().__init__()
        self.settings = {}
    
    def setSetting(self, key, value):
        oldValue = self.settings.get(key)
        self._trackChange(key, oldValue, value)
        self.settings[key] = value
    
    def getSetting(self, key, default=None):
        return self.settings.get(key, default)

# Usage
config = AppConfig()
config.setSetting('theme', 'light')
config.setSetting('theme', 'dark')

# Get change history
changes = config.getChanges()
```

## Best Practices

### ✅ DO

```python
# Use BaseAttributeModel for API responses
class ApiResponse(BaseAttributeModel):
    @property
    def status(self):
        return self.get('status')

# Use DataTrackingMixin for audit trails
class AuditedModel(DataTrackingMixin):
    def update(self, key, value):
        self._trackChange(key, value)
```

### ❌ DON'T

```python
# Don't access dict directly
class User(BaseAttributeModel):
    @property
    def name(self):
        return self._data['name']  # Use self.get('name')
```

## Related Documentation

- [Config](06-configuration.md) - Configuration management
- [Utilities](10-utilities.md) - Data helpers
