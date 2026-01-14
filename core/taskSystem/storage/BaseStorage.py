"""
BaseStorage

Abstract base class for TaskSystem storage backends.
Defines the interface for storing and retrieving task data.
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
#              * -  Copyright © 2026 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

import abc
from typing import Any, Dict, List, Optional

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
    def clear(self, key: str) -> None:
        """
        Clear data associated with a key.
        Args:
            key: The key to clear data for.
        """
        pass
