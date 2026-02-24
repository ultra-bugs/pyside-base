"""
DictSerializable Protocol - Reusable interface for object-to-dict conversion.

Provides a standard interface for objects that can be converted to dictionary format,
useful for serialization, API responses, and data transfer between components.

Usage:
    class MyModel(DictSerializable):
        def toDict(self) -> Dict[str, Any]:
            return {'id': self.id, 'name': self.name}

    # Type checking
    def processSerializable(obj: DictSerializable):
        data = obj.toDict()
        ...
"""

#              M\"\"\"\"\"\"\"`M            dP
#              Mmmmmm   .M            88
#              MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#              MMP  .MMMMM  88    88  88888\"    88'  `88
#              M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#              M         M  `88888P'  dP   `YP  `88888P'
#              MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#              * * * * * * * * * * * * * * * * * * * * *
#              * -    - -   F.R.E.E.M.I.N.D   - -    - *
#              * -  Copyright © 2025 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *
from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class DictSerializable(Protocol):
    """Protocol for objects that can be converted to dictionary format.

    Implementing classes should provide a toDict() method that returns
    a dictionary representation of the object suitable for serialization,
    JSON export, or table display.

    Example:
        class Device(DictSerializable):
            def toDict(self) -> Dict[str, Any]:
                return {
                    'deviceId': self.deviceId,
                    'model': self.model,
                    'status': self.status
                }
    """

    def toDict(self) -> Dict[str, Any]:
        """Convert object to dictionary representation.
        Returns:
            Dictionary containing object's data in serializable format.
            Keys should be strings, values should be JSON-compatible types.
        """
        ...
