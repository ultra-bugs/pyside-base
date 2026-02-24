"""
JsonStorage

JSON file-based implementation of BaseStorage.
Stores data in a JSON file separate from the main application config.
"""

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
import os
from threading import Lock
from typing import Any, Dict

from core.Logging import logger
from core.model.DictSerializable import DictSerializable
from core.Utils import PathHelper

from .BaseStorage import BaseStorage


class CustomJsonEncoder(json.JSONEncoder):
    """
    Custom JSON Encoder that handles DictSerializable objects.
    """

    def default(self, o):
        if isinstance(o, DictSerializable):
            return o.toDict()
        # Fallback: convert non-serializable objects to repr string
        try:
            return super().default(o)
        except TypeError:
            return repr(o)


logger = logger.bind(component='TaskSystem')


class JsonStorage(BaseStorage):
    """
    JSON file-based storage backend.
    """

    def __init__(self, filePath: str = 'config/task_storage.json'):
        """
        Initialize JsonStorage.
        Args:
            file_path: Relative path to the JSON storage file.
        """
        self._file_path = PathHelper.buildDataPath(filePath)
        self._data: Dict[str, Any] = {}
        self._lock = Lock()
        self._load_file()

    def _load_file(self) -> None:
        """Load data from the JSON file."""
        with self._lock:
            try:
                if os.path.exists(self._file_path):
                    with open(self._file_path, 'r', encoding='utf-8') as f:
                        self._data = json.load(f)
                else:
                    self._data = {}
            except Exception as e:
                logger.opt(exception=e).error(f'Failed to load task storage from {self._file_path}: {e}')
                self._data = {}

    def _save_file(self) -> None:
        """Save data to the JSON file."""
        with self._lock:
            try:
                PathHelper.ensureParentDirExists(self._file_path)
                with open(self._file_path, 'w', encoding='utf-8') as f:
                    json.dump(self._data, f, indent=4, cls=CustomJsonEncoder)
            except Exception as e:
                logger.opt(exception=e).error(f'Failed to save task storage to {self._file_path}: {e}')

    def load(self, key: str, default: Any = None) -> Any:
        """
        Load data associated with a key.
        Args:
            key: The key to retrieve data for.
            default: Default value if key is not found.
        Returns:
            The stored data or default value.
        """
        with self._lock:
            return self._data.get(key, default)

    def save(self, key: str, value: Any) -> None:
        """
        Save data associated with a key.
        Args:
            key: The key to store data under.
            value: The data to store.
        """
        with self._lock:
            self._data[key] = value
        self._save_file()

    def clear(self, key: str) -> None:
        """
        Clear data associated with a key.
        Args:
            key: The key to clear data for.
        """
        with self._lock:
            if key in self._data:
                del self._data[key]
        self._save_file()
