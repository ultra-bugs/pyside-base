#              M""""""""`M            dP
#              Mmmmmm   .M            88
#              MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#              MMP  .MMMMM  88    88  88888"    88'  `88
#              M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#              M         M  `88888P'  dP   `YP  `88888P'
#              MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#              * * * * * * * * * * * * * * * * * * * * *
#              * -    - -   F.R.E.E.M.I.N.D   - -    - *
#              * -  Copyright © 2024 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

import json
from pathlib import Path
from typing import Any, Dict

from core.Exceptions import ConfigError
from core.Logging import logger


class Config:
    """Configuration manager"""
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup()
        return cls._instance
    
    def _setup(self):
        """Setup configuration"""
        self._config = {}
        self._config_file = Path("data/config/config.json")
    
    def load(self) -> None:
        """Load configuration from file"""
        try:
            if not self._config_file.exists():
                self._create_default_config()
            
            with open(self._config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            
            logger.info("Configuration loaded successfully")
        
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ConfigError(f"Failed to load configuration: {e}")
    
    def save(self) -> None:
        """Save configuration to file"""
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4)
            
            logger.info("Configuration saved successfully")
        
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise ConfigError(f"Failed to save configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        try:
            value = self._config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        keys = key.split('.')
        config = self._config
        
        # Navigate to the correct nested level
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def _create_default_config(self) -> None:
        """Create default configuration"""
        default_config = {
            "app": {
                "name": "Base Qt Application",
                "version": "1.0.0",
                "debug": False
            },
            "ui": {
                "theme": "auto",  # auto, light, dark
                "language": "en",
                "high_dpi": True
            },
            "logging": {
                "level": "INFO",
                "file": "app.log"
            }
        }
        
        self._config = default_config
        self.save()
