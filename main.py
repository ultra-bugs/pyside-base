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

import os
import sys
from pathlib import Path

import qdarktheme
from PySide6.QtCore import Qt

from app.windows.main.MainController import MainController
from core import Config, ExceptionHandler, logger
from core.QtAppContext import QtAppContext


def configInit():
    """Load configuration"""
    config = Config()
    config.load()
    return config

def setupEnvironment(config):
    """Setup environment variables and paths"""
    projectRoot = Path(__file__).parent
    sys.path.append(str(projectRoot))
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

def setupApp(config):
    """Setup application components"""
    ExceptionHandler.setupGlobalHandler()
    logger.info('Application setup completed')

def setupTheme(config: Config):
    """Setup theme"""
    if config.get('ui.high_dpi', True):
        qdarktheme.enable_hi_dpi()
    qdarktheme.setup_theme(config.get('ui.theme', 'auto'))

def main():
    """Main entry point"""
    try:
        config = configInit()
        setupEnvironment(config)
        setupApp(config)
        ctx = QtAppContext.globalInstance()
        try:
            app = ctx._app
            app.setAttribute(Qt.AA_EnableHighDpiScaling)
        except Exception:
            pass
        setupTheme(config)
        ctx.bootstrap()
        mainController = MainController()
        mainController.show()
        sys.exit(ctx.run())
    except Exception:
        logger.exception('Application failed to start')
        raise
if __name__ == '__main__':
    main()
