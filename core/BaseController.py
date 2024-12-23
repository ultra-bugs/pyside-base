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

from typing import Dict, List, Optional

from PySide6.QtWidgets import QWidget

from core.Observer import Publisher


class BaseController:
    """Base class for all controllers"""
    
    def __init__(self):
        """Initialize the controller"""
        self.publisher = Publisher()
        self.widgets: Dict[str, QWidget] = {}
        self.slot_map: Dict[str, List[str]] = {}
        
        # Setup UI and connect signals
        self.setupUi()
        self._connect_signals()
    
    def setupUi(self):
        """Setup the UI components"""
        raise NotImplementedError("Subclasses must implement setupUi")
    
    def _connect_signals(self):
        """Connect Qt signals to event system"""
        if not hasattr(self, 'slot_map'):
            raise ValueError(f"{self.__class__.__name__} must define slot_map")
        
        for event, (widget_name, signal_name) in self.slot_map.items():
            if not hasattr(self, widget_name):
                continue
            
            widget = getattr(self, widget_name)
            self.publisher.connect(widget, signal_name, event)
    
    def register_widget(self, name: str, widget: QWidget):
        """Register a widget for later access"""
        self.widgets[name] = widget
        setattr(self, name, widget)
    
    def get_widget(self, name: str) -> Optional[QWidget]:
        """Get a registered widget by name"""
        return self.widgets.get(name)
    
    def show(self):
        """Show the main widget of the controller"""
        if hasattr(self, 'widget'):
            self.widget.show()
    
    def hide(self):
        """Hide the main widget of the controller"""
        if hasattr(self, 'widget'):
            self.widget.hide()
