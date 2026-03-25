# Common Use Cases

> **Practical recipes for common scenarios**

## Creating a New Controller

```python
# 1. Create UI file in Qt Designer
# app/windows/settings/Settings.ui

# 2. Compile UI
# pixi run python scripts/compile_ui.py

# 3. Create controller
from core import BaseController
from app.windows.settings.Settings import Ui_Settings

class SettingsController(Ui_Settings, BaseController):
    slot_map = {
        'saveClicked': ['saveButton', 'clicked'],
        'cancelClicked': ['cancelButton', 'clicked']
    }
    
    def setupUi(self, widget):
        super().setupUi(widget)

# 4. Create handler
from core import BaseCtlHandler

class SettingsHandler(BaseCtlHandler):
    def onSaveClicked(self):
        # Get values
        theme = self.widgetManager.get('themeComboBox').currentText()
        
        # Save to config
        from core import Config
        config = Config()
        config.set('ui.theme', theme)
        config.save()
        
        # Close window
        self.controller.close()
    
    def onCancelClicked(self):
        self.controller.close()
```

## Creating a Background Task

```python
from core.taskSystem import AbstractTask
from core import QtAppContext

class DataProcessTask(AbstractTask):
    def __init__(self, dataPath):
        super().__init__(name=f'Process {dataPath}')
        self.dataPath = dataPath
    
    def handle(self):
        # Read data
        with open(self.dataPath, 'r') as f:
            data = json.load(f)
        
        total = len(data)
        
        # Process with progress
        for i, item in enumerate(data):
            if self.isStopped():
                return
            
            # Process item...
            self._processItem(item)
            
            # Update progress
            self.setProgress(int(i / total * 100))
    
    def _performCancellationCleanup(self):
        # Cleanup partial results
        pass

# Add to queue
ctx = QtAppContext.globalInstance()
task = DataProcessTask('data.json')
ctx.taskManager.addTask(task)
```

## Using Scoped Services

```python
from core.taskSystem import AbstractTask
from core import QtAppContext

class BrowserTask(AbstractTask):
    def __init__(self, url):
        super().__init__(name=f'Browse {url}')
        self.url = url
    
    def handle(self):
        ctx = QtAppContext.globalInstance()
        taskId = self.uuid
        
        # Create scoped resources
        browser = ChromeBrowserService()
        tempFiles = TempFileHandler()
        
        # Register for auto cleanup
        ctx.registerScopedService(taskId, browser)
        ctx.registerScopedService(taskId, tempFiles)
        
        try:
            # Use resources
            browser.navigate(self.url)
            
            # Do work...
            if self.isStopped():
                return
            
            # Save screenshot
            screenshot = browser.screenshot()
            tempFiles.save('screenshot.png', screenshot)
            
        finally:
            # Auto cleanup: calls cleanup() on all scoped services
            ctx.releaseScope(taskId)
    
    def _performCancellationCleanup(self):
        # Cleanup handled by releaseScope
        pass
```

## Implementing Event Handlers

```python
from core import Subscriber, Publisher

# Define events
class AppEvents:
    USER_LOGIN = 'user.login'
    DATA_CHANGED = 'data.changed'

# Create handler
class DataHandler(Subscriber):
    def __init__(self):
        super().__init__(events=[
            AppEvents.USER_LOGIN,
            AppEvents.DATA_CHANGED
        ])
    
    def onUserLogin(self, userId: int, username: str):
        print(f'User {username} logged in')
        # Load user data...
    
    def onDataChanged(self, dataType: str, data: dict):
        print(f'Data changed: {dataType}')
        # Update UI...

# Register handler
handler = DataHandler()

# Publish events
publisher = Publisher.instance()
publisher.notify(AppEvents.USER_LOGIN, userId=123, username='john')
publisher.notify(AppEvents.DATA_CHANGED, dataType='users', data={...})
```

## Configuration Management

```python
from core import Config

class AppSettings:
    def __init__(self):
        self.config = Config()
    
    # Theme
    def getTheme(self):
        return self.config.get('ui.theme', default='auto')
    
    def setTheme(self, theme):
        self.config.set('ui.theme', theme)
        self.config.save()
    
    # Language
    def getLanguage(self):
        return self.config.get('ui.language', default='en')
    
    def setLanguage(self, lang):
        self.config.set('ui.language', lang)
        self.config.save()
    
    # Debug mode
    def isDebugMode(self):
        return self.config.get('app.debug', default=False)
    
    def setDebugMode(self, enabled):
        self.config.set('app.debug', enabled)
        self.config.save()

# Usage
settings = AppSettings()
settings.setTheme('dark')
settings.setLanguage('vi')
theme = settings.getTheme()
```

## Error Handling Patterns

```python
from core import AppException
from core.Logging import logger

# Custom exception
class ValidationError(AppException):
    def __init__(self, message):
        super().__init__(message, title='Validation Error')

# In service
class UserService:
    def createUser(self, userData):
        try:
            # Validate
            if not userData.get('email'):
                raise ValidationError('Email is required')
            
            # Create user...
            logger.info('User created', userId=userId)
            
        except ValidationError as e:
            logger.warning(f'Validation failed: {e}')
            raise
        except Exception as e:
            logger.opt(exception=e).error('Failed to create user')
            raise AppException(f'Failed to create user: {e}')

# In handler
class UserHandler(BaseCtlHandler):
    def onCreateUserClicked(self):
        try:
            userData = self._collectFormData()
            userService = UserService()
            userService.createUser(userData)
            
            # Success
            self.widgetManager.get('statusLabel').setText('User created!')
            
        except ValidationError as e:
            # Show validation error
            self.widgetManager.get('errorLabel').setText(str(e))
        except AppException as e:
            # Show error dialog
            from core.Utils import WidgetUtils
            WidgetUtils.showErrorMsgBox(self.controller, str(e), e.title)
```

## Task Chain Pipeline

```python
from core.taskSystem import AbstractTask, ChainRetryBehavior
from core import QtAppContext

# Step 1: Fetch data
class FetchDataTask(AbstractTask):
    def handle(self):
        import requests
        response = requests.get('https://api.example.com/data')
        
        # Share with next task
        self._chainContext.set('raw_data', response.json())

# Step 2: Process data
class ProcessDataTask(AbstractTask):
    def handle(self):
        rawData = self._chainContext.get('raw_data')
        
        # Process...
        processed = self._transform(rawData)
        
        # Share with next task
        self._chainContext.set('processed_data', processed)

# Step 3: Save data
class SaveDataTask(AbstractTask):
    def handle(self):
        data = self._chainContext.get('processed_data')
        
        # Save to database
        with open('output.json', 'w') as f:
            json.dump(data, f)

# Create chain
ctx = QtAppContext.globalInstance()
chain = ctx.taskManager.addChainTask(
    name='Data Pipeline',
    tasks=[
        FetchDataTask(name='Fetch'),
        ProcessDataTask(name='Process'),
        SaveDataTask(name='Save')
    ],
    retryBehaviorMap={
        'Fetch': ChainRetryBehavior.RETRY_TASK,
        'Process': ChainRetryBehavior.SKIP_TASK,
        'Save': ChainRetryBehavior.FAIL_CHAIN
    }
)
```

## Scheduled Tasks

```python
from datetime import datetime, timedelta
from core import QtAppContext

ctx = QtAppContext.globalInstance()

# Run once at specific time
task = MyTask(name='Scheduled Task')
ctx.taskManager.addTask(task, scheduleInfo={
    'trigger': 'date',
    'runDate': datetime(2026, 1, 22, 9, 0)  # 9:00 AM tomorrow
})

# Run every hour
task = MyTask(name='Hourly Task')
ctx.taskManager.addTask(task, scheduleInfo={
    'trigger': 'interval',
    'intervalSeconds': 3600
})

# Run daily at 9:00 AM
task = MyTask(name='Daily Task')
ctx.taskManager.addTask(task, scheduleInfo={
    'trigger': 'cron',
    'hour': 9,
    'minute': 0
})

# Run on weekdays at 9:00 AM
task = MyTask(name='Weekday Task')
ctx.taskManager.addTask(task, scheduleInfo={
    'trigger': 'cron',
    'hour': 9,
    'minute': 0,
    'day_of_week': 'mon-fri'
})
```

## Related Documentation

- [BaseController](04-controller-architecture.md)
- [AbstractTask](13-abstract-task.md)
- [ServiceLocator](02-dependency-injection.md)
- [Observer Pattern](03-observer-pattern.md)
- [Config](06-configuration.md)
