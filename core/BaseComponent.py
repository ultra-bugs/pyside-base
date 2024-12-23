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

from typing import Dict, Optional

from PySide6.QtWidgets import QWidget

from core.Observer import Publisher


class BaseComponent:
    """Base class for reusable UI components"""
    
    def __init__(self):
        """Initialize the component"""
        self.publisher = Publisher()
        self.widgets: Dict[str, QWidget] = {}
        self.parent: Optional[QWidget] = None
        
        # Setup UI
        self.setupUi()
    
    def setupUi(self):
        """Setup the UI components"""
        raise NotImplementedError("Subclasses must implement setupUi")
    
    def register_widget(self, name: str, widget: QWidget):
        """Register a widget for later access"""
        self.widgets[name] = widget
        setattr(self, name, widget)
    
    def get_widget(self, name: str) -> Optional[QWidget]:
        """Get a registered widget by name"""
        return self.widgets.get(name)
    
    def set_parent(self, parent: QWidget):
        """Set the parent widget"""
        self.parent = parent
        if hasattr(self, 'widget'):
            self.widget.setParent(parent)
    
    def show(self):
        """Show the main widget of the component"""
        if hasattr(self, 'widget'):
            self.widget.show()
    
    def hide(self):
        """Hide the main widget of the component"""
        if hasattr(self, 'widget'):
            self.widget.hide()
