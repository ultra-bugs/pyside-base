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
if os.getenv('PYTHONUNBUFFERED', False) == '1':
    from core.extends.pycharm_pydevd_qasync_fix_patch import \
        patch_qasync_for_pycharm_debugger
    patch_qasync_for_pycharm_debugger()
# noinspection PyUnusedImports
from _loader_ import *
from core.QtAppContext import QtAppContext
from app.windows.main.MainController import MainController


def main():
    """Main entry point"""
    try:
        ctx = QtAppContext.globalInstance()
        ctx.bootstrap()
        # App services now registered via ServiceProviders (app/providers/)
        mainController = MainController()
        mainController.show()
        exitCode = ctx.run()
        sys.exit(exitCode)
    except Exception as e:
        from core.Logging import logger
        logger.exception('Application failed to start')
        from core.Utils import WidgetUtils
        WidgetUtils.showAlertMsgBox(None, 'Application failed to start', f'Exception: {e.__class__.__name__}::{e}')
        raise


if __name__ == '__main__':
    main()
