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

from typing import Callable, Union
from PySide6.QtCore import QCoreApplication, QObject
from PySide6.QtWidgets import QApplication, QCheckBox, QDoubleSpinBox, QLabel, QLineEdit, QRadioButton, QSpinBox, QTableView, QTableWidget, QTextEdit, QWidget


class WidgetManager:
    """Manages widgets in controllers and UI components

    Attributes:
        type (int): Type of widget manager (1 for controller, 2 for UI)
        controller: The controller/component that owns this manager
        widget_class_name (str): Name of the controller/component class
    """

    def __init__(self, controller):
        """Initialize widget manager
        Args:
            controller: Controller or component that owns this manager
        """
        self.controller = controller
        clsName = controller.__class__.__name__
        self.type = 1 if 'Controller' in clsName else 2
        self.widgetClassName = clsName
        from core.QtAppContext import QtAppContext
        self.app: Union[QApplication, QCoreApplication] = QtAppContext()

    def get(self, widgetName: str) -> Union[QObject, QWidget, QTextEdit, QLabel, QLineEdit, QTableView, QTableWidget, QSpinBox]:
        """Get a widget by name
        Supports nested widget names using dot notation (e.g. 'parent.child')
        Args:
            widget_name: Name of widget to get
        Returns:
            The widget instance
        Raises:
            Exception: If widget not found
        """
        keys = widgetName.split('.')
        resolved = []
        currentParent = self.controller
        for key in keys:
            if not hasattr(currentParent, key):
                raise Exception(f'Widget {key} not found in {self.controller}.\nWas resolved: {".".join(resolved)}')
            attr = getattr(currentParent, key)
            if key != keys[-1]:
                resolved.append(key)
                currentParent = attr
                continue
            if callable(attr):
                try:
                    return attr()
                except TypeError:
                    return attr
            return attr

    def set(self, name: str, value, saveToConfig: bool = False) -> None:
        """Set a widget attribute value
        Args:
            name: Widget name
            value: Value to set
            save_to_config: Whether to save to config file
        Raises:
            NotImplementedError: If name contains dots
        """
        if '.' in name:
            raise NotImplementedError('Dot notation not allowed in widget names for set()')
        if hasattr(self.controller, name):
            widget = getattr(self.controller, name)
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.setValue(float(value) if isinstance(widget, QDoubleSpinBox) else int(value))
            elif isinstance(widget, (QLineEdit, QLabel)):
                widget.setText(str(value))
            elif isinstance(widget, (QCheckBox, QRadioButton)):
                widget.setChecked(bool(value))
            else:
                setattr(self.controller, name, value)
        else:
            setattr(self.controller, name, value)
        if saveToConfig:
            from core.Config import Config
            config = Config()
            configKey = f'{self.widgetClassName}.{name}'
            config.set(configKey, value)
            config.save()

    def load(self, name: str, default=None) -> None:
        """Load value from config and apply to widget
        Args:
            name: Widget name
            default: Default value if not found in config
        """
        from core.Config import Config
        config = Config()
        configKey = f'{self.widgetClassName}.{name}'
        value = config.get(configKey, default)
        if value is not None and hasattr(self.controller, name):
            widget = getattr(self.controller, name)
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.setValue(float(value) if isinstance(widget, QDoubleSpinBox) else int(value))
            elif isinstance(widget, (QLineEdit, QLabel)):
                widget.setText(str(value))
            elif isinstance(widget, (QCheckBox, QRadioButton)):
                widget.setChecked(bool(value))

    def doActionSuppressSignal(self, widgetName: str, closure: Callable) -> None:
        """Execute action on widget with signals temporarily blocked
        Args:
            widget_name: Name of widget to act on
            closure: Action to execute
        Raises:
            ValueError: If closure is not callable
        """
        if not callable(closure):
            raise ValueError('closure must be callable')
        widget = self.get(widgetName)
        widget.blockSignals(True)
        try:
            closure(widget)
        except TypeError:
            closure()
        widget.blockSignals(False)
