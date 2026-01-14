"""
ChainContext

Thread-safe context manager for sharing data between tasks in a TaskChain.
Provides serialization support for persistence across application restarts.
"""

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
#              * -  Copyright © 2025 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *
import json
import threading
from typing import Any, Dict, Optional

from ..Logging import logger

# Initialize logger for TaskSystem
logger = logger.bind(component='TaskSystem')


class ChainContext:
    """
    Thread-safe context manager for sharing data between tasks in a chain.

    This class provides a centralized way to share business data between
    sequential tasks in a TaskChain. All data must be JSON serializable
    to support persistence across application restarts.

    Attributes:
        _chainUuid (str): UUID of the parent chain
        _data (dict): Dictionary storing shared data
        _lock (threading.Lock): Lock for thread-safe operations
    """

    def __init__(self, chainUuid: str, initialData: Optional[Dict[str, Any]] = None):
        """
        Initialize ChainContext.
        Args:
            chainUuid: UUID of the parent TaskChain
            initialData: Optional initial data dictionary
        """
        self._chainUuid = chainUuid
        self._data = initialData if initialData is not None else {}
        self._lock = threading.Lock()
        logger.debug(f'ChainContext initialized for chain {chainUuid}')

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the context.
        Args:
            key: Key to retrieve
            default: Default value if key doesn't exist
        Returns:
            Value associated with key, or default if not found
        """
        with self._lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the context.
        The value must be JSON serializable to support persistence.
        Args:
            key: Key to set
            value: Value to store (must be JSON serializable)
        Raises:
            TypeError: If value is not JSON serializable
        """
        # Validate JSON serializability
        try:
            json.dumps(value)
        except (TypeError, ValueError) as e:
            raise TypeError(f"Value for key '{key}' is not JSON serializable: {e}")
        with self._lock:
            self._data[key] = value
            logger.debug(f"ChainContext[{self._chainUuid}] set key '{key}'")

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize context to dictionary for persistence.
        Returns:
            Dictionary containing chainUuid and data
        """
        with self._lock:
            return {
                'chainUuid': self._chainUuid,
                'data': self._data.copy(),  # Return copy to avoid external modification
            }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'ChainContext':
        """
        Deserialize context from dictionary.
        Args:
            data: Dictionary containing serialized context data
        Returns:
            Reconstructed ChainContext instance
        """
        chainUuid = data.get('chainUuid')
        initialData = data.get('data', {})
        if not chainUuid:
            raise ValueError('chainUuid is required for deserialization')
        logger.debug(f'Deserializing ChainContext for chain {chainUuid}')
        return cls(chainUuid=chainUuid, initialData=initialData)

    def clear(self) -> None:
        """
        Clear all data from the context.
        """
        with self._lock:
            self._data.clear()
            logger.debug(f'ChainContext[{self._chainUuid}] cleared')

    def keys(self) -> list:
        """
        Get all keys in the context.
        Returns:
            List of keys
        """
        with self._lock:
            return list(self._data.keys())

    def has(self, key: str) -> bool:
        """
        Check if a key exists in the context.
        Args:
            key: Key to check
        Returns:
            True if key exists, False otherwise
        """
        with self._lock:
            return key in self._data
