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

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from core import BaseController, Config
from windows.main.handlers.MainHandler import MainHandler


class MainController(BaseController):
    """Main window controller"""
    
    def __init__(self):
        # Define slot map before calling parent's __init__
        self.slot_map = {
            # Add your slot mappings here
            # 'event_name': ['widget_name', 'signal_name']
        }
        
        # Initialize handler
        self.handler = MainHandler(self)
        
        super().__init__()
    
    def setupUi(self):
        """Setup the UI components"""
        # Create main window
        self.widget = QMainWindow()
        
        # Set window properties
        config = Config()
        self.widget.setWindowTitle(config.get("app.name", "Base Qt Application"))
        self.widget.resize(800, 600)
        
        # Set window icon
        icon_path = Path("assets/icon.png")
        if icon_path.exists():
            self.widget.setWindowIcon(QIcon(str(icon_path)))
        
        # Create central widget and layout
        central_widget = QWidget()
        self.widget.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add hello text
        hello_label = QLabel(
            f"Welcome to {config.get('app.name', 'Base Qt Application')} v{config.get('app.version', '1.0.0')}")
        hello_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(hello_label)
        
        # Register widgets
        self.register_widget('mainWindow', self.widget)
        self.register_widget('helloLabel', hello_label)
