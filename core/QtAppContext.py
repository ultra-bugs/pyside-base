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
from typing import Optional, Union

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication


class QtAppContext:
    """Singleton class to access Qt application instance"""
    _instance: Optional[Union[QApplication, QCoreApplication]] = None
    _services: dict = {}
    def __new__(cls):
        if cls._instance is None:
            cls._instance = QApplication.instance() or QCoreApplication.instance()
        return cls._instance
    
    @classmethod
    def set_instance(cls, instance: Union[QApplication, QCoreApplication]) -> None:
        """Set the application instance"""
        cls._instance = instance
    
    @classmethod
    def set(cls, service, instance):
        """Set the service instance"""
        cls._services[service] = instance
    
    @classmethod
    def get(cls, service):
        """Get the service instance"""
        return cls._services[service]
