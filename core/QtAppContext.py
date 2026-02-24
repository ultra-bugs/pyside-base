#                  M""""""""`M            dP
#                  Mmmmmm   .M            88
#                  MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#                  MMP  .MMMMM  88    88  88888"    88'  `88
#                  M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#                  M         M  `88888P'  dP   `YP  `88888P'
#                  MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#                  * * * * * * * * * * * * * * * * * * * * *
#                  * -    - -   F.R.E.E.M.I.N.D   - -    - *
#                  * -  Copyright © 2026 (Z) Programing  - *
#                  *    -  -  All Rights Reserved  -  -    *
#                  * * * * * * * * * * * * * * * * * * * * *

import os
import sys
from typing import Any, Optional, Self, Union

from PySide6.QtNetwork import QNetworkAccessManager

from core.taskSystem import TaskManagerService
from core.Utils import PathHelper

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None
from PySide6.QtCore import QCoreApplication, QMutex, QMutexLocker, QObject, Signal, Slot
from PySide6.QtWidgets import QApplication

from core.Config import Config
from core.Exceptions import ExceptionHandler
from core.Logging import logger
from core.NetworkManager import NetworkManager
from core.Observer import Publisher
from core.ServiceLocator import ServiceLocator


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

    @staticmethod
    def _ensurePyPath():
        """Setup environment variables and paths"""
        projectRoot = PathHelper.rootDir()
        sys.path.append(str(projectRoot))
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

    def __init__(self):
        self._ensurePyPath()
        super().__init__()
        self._app: Union[QApplication, QCoreApplication] = QApplication.instance() or QApplication(sys.argv)
        self._isBootstrapped = False
        self.loop = None  # qasync QEventLoop, set during bootstrap()
        self._bootstrapLock = QMutex()
        self._sharedState: dict[str, Any] = {}
        self._stateLock = QMutex()
        self._services = ServiceLocator()
        self._config: Optional[Config] = None
        self._publisher: Optional[Publisher] = None
        self._networkManager: Optional[NetworkManager] = None
        self._taskManager = None
        self._app.aboutToQuit.connect(self._onExit)

    def _load_environment(self) -> Self:
        """Load .env file and setup environment variables."""
        if load_dotenv:
            load_dotenv()
        return self

    def _get_env_bool(self, key: str, default: bool = True) -> bool:
        """Helper to parse boolean env vars (PSA_ prefix)."""
        val = os.getenv(f'PSA_{key}')
        if val is None:
            return default
        return val.lower() in ('true', '1', 'yes', 'on')

    def _setupAppNameIcon(self) -> Self:
        from core.Utils import AppHelper
        app_name = AppHelper.getAppName()
        app_version = AppHelper.getAppVersion()
        self._app.setApplicationName(f'{app_name}')
        self._app.setApplicationVersion(app_version)
        self._app.setOrganizationName('Z-Programming')
        self._app.setOrganizationDomain('zuko.pro')
        self._app.setWindowIcon(AppHelper.getAppIcon())
        return self

    def isFeatureEnabled(self, feature_name: str) -> bool:
        """Check if a specific feature is enabled via env vars."""
        keyMap = {'network': 'ENABLE_NETWORK', 'tasks': 'ENABLE_TASKS'}
        envKey = keyMap.get(feature_name.lower())
        if not envKey:
            return True
        return self._get_env_bool(envKey, default=True)

    def _setupTheme(self) -> Self:
        """Setup theme"""
        import qdarktheme
        config = self.config()
        if config.get('ui.high_dpi', True):
            qdarktheme.enable_hi_dpi()
        qdarktheme.setup_theme(config.get('ui.theme', 'auto'))
        return self

    def bootstrap(self) -> Self:
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
            import asyncio
            from qasync import QEventLoop
            self.loop = QEventLoop(self._app)
            asyncio.set_event_loop(self.loop)
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
                self.registerService('taskManager', self._taskManager)
            else:
                logger.warning('Feature [Tasks]: DISABLED (via PSA_ENABLE_TASKS)')
            self._setupTheme()._setupAppNameIcon()
            self._isBootstrapped = True
            self._loadAppProviders()
            self._publisher.notify('app.ready')
            self.appReady.emit()
            logger.info('Application Context Ready.')
            return self

    def _loadAppProviders(self) -> Self:
        """Load and execute app ServiceProviders from build-time manifest."""
        try:
            from app.providers._provider_manifest import PROVIDERS
        except ImportError:
            logger.debug('No _provider_manifest.py found — skipping app providers.')
            return
        if not PROVIDERS:
            return
        import importlib
        from core.contracts.ServiceProvider import ServiceProvider
        from core.Utils import WidgetUtils
        # --- Phase 0: Import and instantiate ---
        providerInstances = {}  # className -> instance
        providerClasses = {}  # className -> class
        for fqn in PROVIDERS:
            modulePath, className = fqn.rsplit('.', 1)
            try:
                mod = importlib.import_module(modulePath)
                cls = getattr(mod, className)
                if not (isinstance(cls, type) and issubclass(cls, ServiceProvider)):
                    logger.warning(f'[Providers] {fqn} is not a ServiceProvider subclass, skipping.')
                    continue
                providerClasses[className] = cls
            except Exception as e:
                msg = f'Failed to import provider {fqn}: {e}'
                logger.error(f'[Providers] {msg}')
                WidgetUtils.showAlertMsgBox(None, msg, 'Provider Import Error')
        # --- Phase 1: Topological sort (Kahn's algorithm) ---
        # Build graph: after + requires + wants all contribute edges
        inDegree = {name: 0 for name in providerClasses}
        graph = {name: [] for name in providerClasses}  # name -> list of dependents
        for name, cls in providerClasses.items():
            deps = set(getattr(cls, 'after', []) + getattr(cls, 'requires', []) + getattr(cls, 'wants', []))
            for dep in deps:
                if dep in providerClasses:
                    graph[dep].append(name)
                    inDegree[name] += 1
        queue = [n for n in providerClasses if inDegree[n] == 0]
        sortedNames = []
        while queue:
            queue.sort()  # deterministic order
            node = queue.pop(0)
            sortedNames.append(node)
            for dependent in graph[node]:
                inDegree[dependent] -= 1
                if inDegree[dependent] == 0:
                    queue.append(dependent)
        if len(sortedNames) != len(providerClasses):
            cycle = set(providerClasses) - set(sortedNames)
            msg = f'Circular dependency detected among providers: {cycle}'
            logger.error(f'[Providers] {msg}')
            WidgetUtils.showAlertMsgBox(title='Provider Dependency Error', msg=msg)
            # Still load what we can
            for name in providerClasses:
                if name not in sortedNames:
                    sortedNames.append(name)
        # --- Phase 2: register() ---
        failedProviders = set()
        for name in sortedNames:
            cls = providerClasses[name]
            # Check requires
            requiredDeps = getattr(cls, 'requires', [])
            missingReqs = [r for r in requiredDeps if r in failedProviders]
            if missingReqs:
                logger.warning(f'[Providers] Skipping {name}: required providers failed: {missingReqs}')
                failedProviders.add(name)
                continue
            try:
                instance = cls(self)
                instance.register()
                providerInstances[name] = instance
                logger.info(f'[Providers] ✓ Registered: {name}')
            except Exception as e:
                failedProviders.add(name)
                msg = f'Provider {name}.register() failed: {e}'
                logger.error(f'[Providers] {msg}')
                WidgetUtils.showAlertMsgBox(title='Provider Registration Error', msg=msg)
        # --- Phase 3: boot() ---
        for name in sortedNames:
            instance = providerInstances.get(name)
            if not instance:
                continue
            try:
                instance.boot()
            except Exception as e:
                msg = f'Provider {name}.boot() failed: {e}'
                logger.error(f'[Providers] {msg}')
                WidgetUtils.showAlertMsgBox(title='Provider Boot Error', msg=msg)
        logger.info(f'[Providers] Loaded {len(providerInstances)}/{len(PROVIDERS)} providers.')
        return self

    def getMainWindowCtl(self) -> QMainWindow:
        for widget in self._app.topLevelWidgets():
            if type(widget).__name__ == 'MainController':
                return widget
        return None

    def run(self) -> int:
        """Start the qasync event loop (replaces QApplication.exec())."""
        if not self._isBootstrapped:
            self.bootstrap()
        with self.loop:
            self.loop.run_forever()
            return 0

    @Slot()
    def _onExit(self):
        """Handle application shutdown."""
        self.appClosing.emit()
        if self._publisher:
            self._publisher.notify('app.shutdown')
        logger.info('Application shutting down.')

    def registerService(self, name: str, instance: Any) -> Self:
        """Register a global service."""
        self._services.register(name, instance)
        return self

    def getService(self, name: str) -> Any:
        """Get a registered service."""
        return self._services.get(name)

    def registerScopedService(self, tag: str, instance: Any) -> Self:
        """Register a scoped service (linked to a Job/Task UUID)."""
        self._services.registerScoped(tag, instance)
        return self

    def releaseScope(self, tag: str) -> Self:
        """Cleanup all services associated with a tag."""
        self._services.releaseScope(tag)
        return self

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

    def setState(self, key: str, value: Any) -> Self:
        with QMutexLocker(self._stateLock):
            self._sharedState[key] = value
        return self

    def getState(self, key: str, default: Any = None) -> Any:
        with QMutexLocker(self._stateLock):
            return self._sharedState.get(key, default)
