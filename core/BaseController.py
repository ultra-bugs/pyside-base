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
import importlib
from abc import ABC, abstractmethod
from typing import Dict, List

from PySide6.QtWidgets import QWidget

from core.Observer import Publisher
from core.WidgetManager import WidgetManager


class ControllerMeta(type(QWidget), type(ABC)):
    required_attrs = ["slot_map"]
    
    def __new__(cls, name, bases, dct):
        required_attrs = cls.required_attrs
        for attr in required_attrs:
            if attr not in dct:
                raise ValueError(f"Attribute: {attr} is required but not defined in {name}")
        return super().__new__(cls, name, bases, dct)


class BaseController(metaclass=ControllerMeta):
    """Base class for all controllers"""
    slot_map: Dict[str, List[str]] = {}
    signal_connected = False
    is_auto_connect_signal = True
    
    def __init__(
            self,
            parent = None,
    ):
        super().__init__()
        self.widget_manager = WidgetManager(self)
        self.controller_name = self.__class__.__name__
        self.publisher = Publisher()
        self.setupUi(self)
        if not self.is_auto_connect_signal:
            return
        # Prepare modules,classes to search
        search_modules = ["windows.handlers", ".".join(self.__module__.split(".")[:-1])]
        search_cls = [self.controller_name, self.controller_name.replace("Controller", "")]
        # Auto-loading handler
        for module in search_modules:
            for cls in search_cls:
                if importlib.util.find_spec(f"{module}.{cls}Handler") is None:
                    continue
                # If the module is found, import it
                handler_module = importlib.import_module(f"{module}.{cls}Handler")
                self.handler = getattr(handler_module, f"{cls}Handler")(
                        widget_manager=self.widget_manager, events=self.slot_map.keys()
                )
                break
        if self.is_auto_connect_signal:
            self._connect_signals()
    
    @abstractmethod
    def setupUi(self, widget):
        """Set up the UI components"""
        pass
    
    def _connect_signals(self):
        if not hasattr(self, 'slot_map'):
            raise ValueError(f"{self.__class__.__name__} must define slot_map to use auto connect signals")
        subscriber = self.handler
        for event in self.handler.events:
            if event in self.slot_map.keys():
                t = self.slot_map.get(event)
                if t is None:
                    continue
                if callable(t):
                    t(self.handler, self.publisher)
                    continue
                    # TODO: find a better way to do this
                    pass
                try:
                    
                    self.publisher.connect(
                            self.widget_manager.get(t[0]),
                            t[1],
                            event,
                            data={"widget": self.widget_manager.get(t[0])},
                    )
                except AttributeError:
                    wd = self.widget_manager.get(t[0])
                    print('widget "%s" does not have attribute "%s"' % (wd, t[1]))
                    print("x")
                    pass
                self.publisher.subscribe(subscriber=subscriber, event=event)
        self.signal_connected = True
