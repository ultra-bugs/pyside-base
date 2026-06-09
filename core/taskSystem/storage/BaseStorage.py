"""
BaseStorage

Abstract base class for TaskSystem storage backends.
Defines the interface for storing and retrieving task data.
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
import abc
from typing import Any, Dict, Set


class BaseStorage(abc.ABC):
    """
    Abstract base class for storage backends.
    """

    @abc.abstractmethod
    def load(self, key: str, default: Any = None) -> Any:
        """
        Load data associated with a key.
        Args:
            key: The key to retrieve data for.
            default: Default value if key is not found.
        Returns:
            The stored data or default value.
        """
        pass

    @abc.abstractmethod
    def save(self, key: str, value: Any) -> None:
        """
        Save data associated with a key.
        Args:
            key: The key to store data under.
            value: The data to store.
        """
        pass

    @abc.abstractmethod
    def saveBatch(self, items: Dict[str, Any]) -> None:
        """
        Save multiple key-value pairs in a single operation.
        Adapter responsibility: HOW to persist (JSON/SQL/etc).
        Args:
            items: Dictionary of key-value pairs to save.
        """
        pass

    @abc.abstractmethod
    def clear(self, key: str) -> None:
        """
        Clear data associated with a key.
        Args:
            key: The key to clear data for.
        """
        pass

    def beginWork(self) -> 'WorkingSet':
        """
        Returns working set for batched operations.
        Returns:
            A WorkingSet instance for Unit of Work pattern operations.
        """
        return self.WorkingSet(self)

    class WorkingSet:
        """
        Inner class: Unit of Work logic as core storage capability.
        Tracks dirty state and batches operations until commit.
        """

        def __init__(self, storage: 'BaseStorage'):
            self._storage = storage
            self._pending: Dict[str, Any] = {}
            self._dirty: Set[str] = set()

        def save(self, key: str, value: Any) -> None:
            """
            Save data with dirty detection - only marks dirty if value changed.
            Args:
                key: The key to store data under.
                value: The data to store.
            """
            _SENTINEL = object()
            current = self._storage.load(key, _SENTINEL)
            if current is _SENTINEL or current != value:
                self._pending[key] = value
                self._dirty.add(key)

        @property
        def isDirty(self) -> bool:
            """
            Check if any data has been modified.
            Returns:
                True if there are pending changes, False otherwise.
            """
            return bool(self._dirty)

        def commit(self) -> int:
            """
            Commit all pending changes to storage.
            Returns:
                Number of keys written, 0 if no changes.
            """
            if not self._dirty:
                return 0
            self._storage.saveBatch(self._pending)
            count = len(self._dirty)
            self._dirty.clear()
            self._pending.clear()
            return count
