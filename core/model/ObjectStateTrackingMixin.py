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

import copy
from dataclasses import dataclass, is_dataclass, asdict


# noinspection PyUnresolvedReferences
class ObjectStateTrackingMixin:
    """
    Mixin to track property changes in a Python object.
    High performance, low memory footprint.
    Flow: Init Object -> Set Default Values -> Start Tracking
    """

    # Internal attributes to ignore during tracking
    _IGNORE_TRACKING = {'_originalState', '_dirtyMap', '_isTracking'}
    _IGNORE_UNDERSCORE = True
    def __init__(self):
        # Using direct dict access to avoid triggering __setattr__ recursively
        self.__dict__['_originalState'] = {}
        self.__dict__['_dirtyMap'] = {}
        self.__dict__['_isTracking'] = False

    def startTracking(self):
        """
        Snapshots the current state and enables change detection.
        Call this after your object is fully initialized.
        """
        current_state = self._getCurrentState()
        self.__dict__['_originalState'] = copy.deepcopy(current_state)
        self.__dict__['_dirtyMap'] = {}
        self.__dict__['_isTracking'] = True

    def commit(self):
        """
        Accepts current changes as the new baseline.
        """
        if not self._isTracking:
            return

        self.__dict__['_originalState'] = copy.deepcopy(self._getCurrentState())
        self.__dict__['_dirtyMap'].clear()

    def rollback(self):
        """
        Reverts object properties to the last committed state.
        """
        if not self._isTracking:
            return

        original = self.__dict__['_originalState']
        # Stop tracking to avoid triggering events during rollback
        temp_tracking = self._isTracking
        self.__dict__['_isTracking'] = False

        for key, value in original.items():
            if hasattr(self, key):
                setattr(self, key, copy.deepcopy(value))

        self.__dict__['_dirtyMap'].clear()
        self.__dict__['_isTracking'] = temp_tracking

    def getDirtyData(self) -> dict:
        """
        Returns a dict of changed fields: {field_name: {'oldValue': val, 'newValue': val}}
        """
        return self._dirtyMap

    def isDirty(self) -> bool:
        return bool(self._dirtyMap)

    def _getCurrentState(self) -> dict:
        """Helper to extract current values based on object type."""
        if is_dataclass(self):
            # noinspection PyDataclass
            return asdict(self)

        # Filter out internal methods and private variables
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_') and not callable(v)}
    def onDataModified(self, key, oldValue, newValue):
        """
        Callback method to be overridden in the subclass.
        Called when data is modified.
        """
        pass
    def __setattr__(self, key, value):
        # 1. Standard assignment
        super().__setattr__(key, value)

        # 2. Tracking Logic
        # Skip if not tracking or if it's an internal attribute
        if not getattr(self, '_isTracking', False) or key in self._IGNORE_TRACKING or (self._IGNORE_UNDERSCORE and key.startswith('_')):
            return

        # 3. Compare with original
        original_val = self._originalState.get(key)

        # If value is same as original, remove from dirty map (revert case)
        if original_val == value:
            if key in self._dirtyMap:
                del self._dirtyMap[key]
        else:
            # Record the change
            self._dirtyMap[key] = {'oldValue': original_val, 'newValue': value}
            self.onDataModified(key, original_val, value)
