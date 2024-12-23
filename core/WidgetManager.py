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

from typing import Callable, Union

from PySide6.QtCore import QCoreApplication, QObject
from PySide6.QtWidgets import QApplication, QWidget


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
        cls_name = controller.__class__.__name__
        self.type = 1 if "Controller" in cls_name else 2
        self.widget_class_name = cls_name
        
        # Get app instance
        from core.QtAppContext import QtAppContext
        self.app: Union[QApplication, QCoreApplication] = QtAppContext()
    
    def get(self, widget_name: str) -> Union[QObject, QWidget]:
        """Get a widget by name
        
        Supports nested widget names using dot notation (e.g. 'parent.child')
        
        Args:
            widget_name: Name of widget to get
            
        Returns:
            The widget instance
            
        Raises:
            Exception: If widget not found
        """
        keys = widget_name.split(".")
        resolved = []
        current_parent = self.controller
        
        for key in keys:
            if not hasattr(current_parent, key):
                raise Exception(
                        f"Widget {key} not found in {self.controller}.\n"
                        f"Was resolved: {'.'.join(resolved)}"
                )
            if key != keys[-1]:
                resolved.append(key)
                current_parent = getattr(current_parent, key)
        
        return getattr(current_parent, keys[-1])
    
    def set(self, name: str, value, save_to_config: bool = False) -> None:
        """Set a widget attribute value
        
        Args:
            name: Widget name
            value: Value to set
            save_to_config: Whether to save to config file
            
        Raises:
            NotImplementedError: If name contains dots
        """
        if "." in name:
            raise NotImplementedError("Dot notation not allowed in widget names for set()")
        
        setattr(self.controller, name, value)
        
        if save_to_config:
            from core.Config import Config
            config = Config()
            config_key = f"{self.widget_class_name}.{name}"
            config.set(config_key, value)
            config.save()
    
    def do_action_suppress_signal(self, widget_name: str, closure: Callable) -> None:
        """Execute action on widget with signals temporarily blocked
        
        Args:
            widget_name: Name of widget to act on
            closure: Action to execute
            
        Raises:
            ValueError: If closure is not callable
        """
        if not callable(closure):
            raise ValueError("closure must be callable")
        
        widget = self.get(widget_name)
        widget.blockSignals(True)
        try:
            closure(widget)
        except TypeError:
            closure()
        widget.blockSignals(False)
