import json
from typing import Any, Dict, List
from PySide6.QtCore import QMutex, QMutexLocker
from core.Exceptions import ConfigError
from core.Utils import PathHelper


class Config:
    """Configuration manager"""

    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup()
            cls._instance.load()
        return cls._instance
    
    @classmethod
    def getInstance(cls):
        cls()
        return cls._instance
    
    def __init__(self):
        self.isLoaded = False

    def __call__(self, key: str = None) -> 'Any':
        return self.get(key) if key else self

    def _setup(self):
        """Setup configuration"""
        self._config = {}
        self._config_file = PathHelper.buildDataPath('config/config.json')
        self._lock = QMutex()
        self.isLoaded = False

    def load(self) -> 'Config':
        """Load configuration from file"""
        with QMutexLocker(self._lock):
            from .Logging import logger
            if self.isLoaded:
                return self
            try:
                if not PathHelper.isFileExists(self._config_file):
                    self._create_default_config()
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logger.info('Configuration loaded successfully')
                self.isLoaded = True
                return self
            except Exception as e:
                logger.error(f'Failed to load configuration: {e}')
                raise ConfigError(f'Failed to load configuration: {e}')

    def save(self) -> None:
        """Save configuration to file"""
        with QMutexLocker(self._lock):
            from .Logging import logger
            try:
                PathHelper.ensureParentDirExists(self._config_file)
                with open(self._config_file, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, indent=4)
                logger.info('Configuration saved successfully')
            except Exception as e:
                logger.error(f'Failed to save configuration: {e}')
                raise ConfigError(f'Failed to save configuration: {e}')

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        with QMutexLocker(self._lock):
            try:
                value = self._config
                for k in key.split('.'):
                    value = value[k]
                return value
            except (KeyError, TypeError):
                return default

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        with QMutexLocker(self._lock):
            keys = key.split('.')
            config = self._config
            if key == 'raffle_id':
                if config['raffle_id']:
                    config['raffleHistories']: List[str] = config['raffleHistory'] if hasattr(config, 'raffleHistories') else []
                    if not value not in config['raffleHistories']:
                        config['raffleHistories'].append(value)
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value

    def _create_default_config(self) -> None:
        """Create default configuration"""
        defaultConfig = {
            'app': {'name': 'Base Qt Application', 'version': '1.0.0', 'debug': False},
            'ui': {'theme': 'auto', 'language': 'en', 'high_dpi': True},
            'logging': {'level': 'INFO', 'file': 'app.log'},
            'consolelog': {'enable': True, 'level': 'DEBUG'},
        }
        locker = QMutexLocker(self._lock)
        self._config = defaultConfig
        locker.unlock()
        self.save()
