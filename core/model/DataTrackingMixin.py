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

import collections
from collections import defaultdict
from copy import deepcopy

from PySide6.QtCore import QAbstractItemModel


class DataTrackingMixin:
    _key_pattern = '{row}_{column}'

    def __init__(self, initialData=None):
        self._data = {}
        self._last_committed_data = {}
        self._dirty_data = defaultdict(dict)
        if isinstance(self, QAbstractItemModel) and initialData is not None:
            self.initDataFromModel(initialData)

    def initDataFromModel(self, model):
        for row in range(model.rowCount()):
            if 'column' in self._key_pattern:
                for column in range(model.columnCount()):
                    index = model.index(row, column)
                    key = self._get_key(index)
                    value = model.data(index, role='dataTrackingRole')
                    self._set_value_obj(key, value)
            else:
                index = model.createIndex(row, 0)
                key = self._get_key(index)
                value = model.data(index, role='dataTrackingRole')
                self._set_value_obj(key, value)
        self.commitData()

    def _set_value_obj(self, key, value):
        if isinstance(value, collections.abc.MutableMapping):
            value = deepcopy(value)
        elif isinstance(value, collections.abc.MutableSequence):
            value = deepcopy(value)
        elif isinstance(value, collections.abc.MutableSet):
            value = deepcopy(value)
        elif hasattr(value, '__dict__'):
            value = deepcopy(value)
        elif hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
            value = deepcopy(value.toDict())
        self._data[key] = value

    def setData(self, index, value):
        key = self._get_key(index)
        if key not in self._data or not self._compare_objects(self._data[key], value):
            self._set_value_obj(key, value)
            self._on_data_modified(key, value)

    def commitData(self):
        isinstance(self, QAbstractItemModel) and self.beginResetModel()
        self._last_committed_data = self._data.copy()
        self._dirty_data.clear()
        isinstance(self, QAbstractItemModel) and self.endResetModel()

    def _on_data_modified(self, key, value):
        if key in self._last_committed_data:
            oldValue = self._last_committed_data[key]
            self._dirty_data[key]['old_value'] = oldValue
            self._dirty_data[key]['new_value'] = value
            self.onDataModified(key, oldValue, value)
        else:
            self.onDataAdded(key, value)

    def onDataModified(self, key, oldValue, newValue):
        """
        Callback method to be overridden in the subclass.
        Called when data is modified.
        """
        pass

    def onDataAdded(self, key, value):
        """
        Callback method to be overridden in the subclass.
        Called when new data is added.
        """
        pass

    def _get_key(self, index):
        if isinstance(index, tuple):
            row, column = index
        else:
            row, column = (index.row(), index.column())
        return self._key_pattern.format(row=row, column=column)

    def isDirty(self):
        return bool(self._dirty_data)

    def getDirtyData(self):
        return self._dirty_data

    @staticmethod
    def setKeyPattern(pattern):
        DataTrackingMixin._key_pattern = pattern

    def _compare_objects(self, obj1, obj2):
        """
        Compares two objects based on their properties.
        This method can be overridden in the subclass to provide a custom comparison logic.
        """
        if isinstance(obj1, dict) and isinstance(obj2, dict):
            return obj1 == obj2
        if hasattr(obj1, '__dict__') and hasattr(obj2, '__dict__'):
            return obj1.__dict__ == obj2.__dict__
        if hasattr(obj1, 'to_dict') and hasattr(obj2, 'to_dict') and callable(obj1.toDict) and callable(obj2.toDict):
            obj1 = obj1.toDict()
            obj2 = obj2.toDict()
        return obj1 == obj2
