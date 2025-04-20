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
#              * -  Copyright © 2025 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

#
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow

from core import BaseController, Config
from windows.main.main_window import Ui_MainWindow


class MainController(Ui_MainWindow, BaseController, QMainWindow):
    slot_map = {
    
    }
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initialize_ui()
    
    def initialize_ui(self):
        """Khởi tạo các thành phần UI"""
        config = Config()
        self.setWindowTitle(config.get("app.name", "Base Qt Application"))
        # Set window icon
        icon_path = Path("assets/icon.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        # Khởi tạo UI
        self.label.setText(f'Hello from {config.get("app.name", "Base Qt Application")}')
