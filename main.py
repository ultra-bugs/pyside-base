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

import os
import sys
from pathlib import Path

import qdarktheme
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from core import Config, ExceptionHandler, logger
from windows.main.MainController import MainController


def config_init():
    """Load configuration"""
    config = Config()
    config.load()
    return config


def setup_environment(config):
    """Setup environment variables and paths"""
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.append(str(project_root))
    
    # Set Qt environment variables
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"


def setup_app(config):
    """Setup application components"""
    # Setup exception handling
    ExceptionHandler.setup_global_handler()
    logger.info("Application setup completed")


def setup_theme(config: Config):
    """Setup theme"""
    # Setup high DPI
    if config.get("ui.high_dpi", True):
        qdarktheme.enable_hi_dpi()
    
    # Setup theme
    qdarktheme.setup_theme(config.get("ui.theme", "auto"))


def main():
    """Main entry point"""
    try:
        # Setup environment and app
        config = config_init()
        setup_environment(config)
        setup_app(config)
        
        # Create application
        app = QApplication(sys.argv)
        app.setAttribute(Qt.AA_EnableHighDpiScaling)
        setup_theme(config)
        # Create and show main window
        main_controller = MainController()
        main_controller.show()
        
        # Start event loop
        sys.exit(app.exec())
    
    except Exception as e:
        logger.exception("Application failed to start")
        raise


if __name__ == "__main__":
    main()
