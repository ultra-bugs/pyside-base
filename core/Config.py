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
import json
from typing import Any, Dict, List, Tuple

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
            from loguru import logger
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
            from loguru import logger
            try:
                PathHelper.ensureParentDirExists(self._config_file)
                with open(self._config_file, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, indent=4)
                logger.info('Configuration saved successfully')
            except Exception as e:
                logger.error(f'Failed to save configuration: {e}')
                raise ConfigError(f'Failed to save configuration: {e}')

    def _traverse(self, config: Dict[str, Any], keys: List[str], create_missing: bool = False) -> Tuple[Dict[str, Any], str]:
        """Traverse configuration to find parent dict and key, supporting dotted keys"""
        current = config
        i = 0
        while i < len(keys):
            if not isinstance(current, dict):
                raise TypeError(f"Expected dict, got {type(current).__name__}")
            
            remainder_key = '.'.join(keys[i:])
            if remainder_key in current:
                return current, remainder_key
            
            if i == len(keys) - 1:
                return current, keys[i]
            
            matched = False
            for length in range(len(keys) - i - 1, 0, -1):
                part = '.'.join(keys[i : i + length])
                if part in current:
                    current = current[part]
                    i += length
                    matched = True
                    break
            
            if not matched:
                k = keys[i]
                if k not in current:
                    if create_missing:
                        current[k] = {}
                    else:
                        raise KeyError(k)
                current = current[k]
                i += 1
        
        return current, keys[-1]

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        with QMutexLocker(self._lock):
            try:
                parent, k = self._traverse(self._config, key.split('.'))
                return parent[k]
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
            
            parent, k = self._traverse(self._config, keys, create_missing=True)
            parent[k] = value

    def _create_default_config(self) -> None:
        """Create default configuration"""
        defaultConfig = {
            'app': {'name': 'Base Qt Application', 'version': '1.0.0', 'debug': False, 'disableGui': False},
            'ui': {'theme': 'auto', 'language': 'en', 'high_dpi': True},
            'logging': {
                'level': 'INFO',
                'file': 'app.log',
                'moduleLvs': {'app': 'DEBUG', 'core': 'INFO'},
                'customLevels': []
            },
            'consolelog': {'enable': True, 'level': 'DEBUG', 'moduleLvs': {'app': 'DEBUG', 'core': 'INFO'}},
        }
        locker = QMutexLocker(self._lock)
        self._config = defaultConfig
        locker.unlock()
        self.save()
