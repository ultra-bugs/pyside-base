import os
import sys
from PySide6.QtNetwork import QNetworkAccessManager
from typing import Any, Optional, Union
from core.taskSystem import TaskManagerService
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None
from PySide6.QtCore import QCoreApplication, QMutex, QMutexLocker, QObject, Signal, Slot
from PySide6.QtWidgets import QApplication
from core.Config import Config
from core.Logging import logger
from core.NetworkManager import NetworkManager
from core.Observer import Publisher
from core.ServiceLocator import ServiceLocator
from core.Exceptions import ExceptionHandler

class QtAppContext(QObject):
    """
    Central Application Context.
    Manages Lifecycle, Feature Flags, Services, and Scoped Resources.
    """
    appBooting = Signal()
    appReady = Signal()
    appClosing = Signal()
    _instance: 'QtAppContext' = None
    _lock = QMutex()

    @classmethod
    def globalInstance(cls) -> 'QtAppContext':
        if cls._instance is None:
            with QMutexLocker(cls._lock):
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._app: Union[QApplication, QCoreApplication] = QApplication.instance() or QApplication(sys.argv)
        self._isBootstrapped = False
        self._bootstrapLock = QMutex()
        self._sharedState: dict[str, Any] = {}
        self._stateLock = QMutex()
        self._services = ServiceLocator()
        self._config: Optional[Config] = None
        self._publisher: Optional[Publisher] = None
        self._networkManager: Optional[NetworkManager] = None
        self._taskManager = None
        self._app.aboutToQuit.connect(self._onExit)

    def _load_environment(self):
        """Load .env file and setup environment variables."""
        if load_dotenv:
            load_dotenv()

    def _get_env_bool(self, key: str, default: bool=True) -> bool:
        """Helper to parse boolean env vars (PSA_ prefix)."""
        val = os.getenv(f'PSA_{key}')
        if val is None:
            return default
        return val.lower() in ('true', '1', 'yes', 'on')

    def isFeatureEnabled(self, feature_name: str) -> bool:
        """Check if a specific feature is enabled via env vars."""
        keyMap = {'network': 'ENABLE_NETWORK', 'tasks': 'ENABLE_TASKS'}
        envKey = keyMap.get(feature_name.lower())
        if not envKey:
            return True
        return self._get_env_bool(envKey, default=True)

    def bootstrap(self):
        """
        Initialize the application context.
        Thread-safe and Idempotent (Runs only once).
        """
        with QMutexLocker(self._bootstrapLock):
            if self._isBootstrapped:
                logger.warning('QtAppContext is already bootstrapped. Skipping.')
                return
            logger.info('Bootstrapping Application Context...')
            self.appBooting.emit()
            self._load_environment()
            self._config = Config()
            self.registerService('config', self._config)
            self._publisher = Publisher.instance()
            self.registerService('publisher', self._publisher)
            try:
                ExceptionHandler.setupGlobalHandler()
                logger.info('Global Exception Handler installed.')
            except Exception as e:
                logger.error(f'Failed to install ExceptionHandler: {e}')
            if self.isFeatureEnabled('network'):
                logger.info('Feature [Network]: ENABLED')
                self._networkManager = NetworkManager(self._config)
                self.registerService('network', self._networkManager)
            else:
                logger.warning('Feature [Network]: DISABLED (via PSA_ENABLE_NETWORK)')
            if self.isFeatureEnabled('tasks'):
                logger.info('Feature [Tasks]: ENABLED')
                from core.taskSystem.TaskManagerService import TaskManagerService
                self._taskManager = TaskManagerService(self._publisher, self._config)
                self.registerService('task_manager', self._taskManager)
            else:
                logger.warning('Feature [Tasks]: DISABLED (via PSA_ENABLE_TASKS)')
            self._isBootstrapped = True
            self._publisher.notify('app.ready')
            self.appReady.emit()
            logger.info('Application Context Ready.')

    def run(self) -> int:
        """Start the Qt Event Loop."""
        if not self._isBootstrapped:
            self.bootstrap()
        return self._app.exec()

    @Slot()
    def _onExit(self):
        """Handle application shutdown."""
        self.appClosing.emit()
        if self._publisher:
            self._publisher.notify('app.shutdown')
        logger.info('Application shutting down.')

    def registerService(self, name: str, instance: Any) -> None:
        """Register a global service."""
        self._services.register(name, instance)

    def getService(self, name: str) -> Any:
        """Get a registered service."""
        return self._services.get(name)

    def registerScopedService(self, tag: str, instance: Any) -> None:
        """Register a scoped service (linked to a Job/Task UUID)."""
        self._services.registerScoped(tag, instance)

    def releaseScope(self, tag: str) -> None:
        """Cleanup all services associated with a tag."""
        self._services.releaseScope(tag)

    @property
    def config(self) -> Config:
        return self._config

    @property
    def publisher(self) -> Publisher:
        return self._publisher

    @property
    def network(self) -> Optional[QNetworkAccessManager]:
        """Returns QNetworkAccessManager or None if disabled."""
        if self._networkManager:
            return self._networkManager.manager
        logger.warning("Accessing 'network' but feature is disabled or not initialized.")
        return None

    @property
    def taskManager(self) -> Optional[TaskManagerService]:
        """Returns TaskManagerService or None if disabled."""
        if self._taskManager:
            return self._taskManager
        logger.warning("Accessing 'taskManager' but feature is disabled or not initialized.")
        return None

    def setState(self, key: str, value: Any) -> None:
        with QMutexLocker(self._stateLock):
            self._sharedState[key] = value

    def getState(self, key: str, default: Any=None) -> Any:
        with QMutexLocker(self._stateLock):
            return self._sharedState.get(key, default)