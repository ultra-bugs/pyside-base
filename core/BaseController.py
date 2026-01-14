import importlib
from abc import ABC, abstractmethod
from typing import Dict, List
from PySide6 import QtCore
from box import Box
from core.Observer import Publisher
from core.WidgetManager import WidgetManager


class ControllerMeta(type(QtCore.QObject), type(ABC)):
    required_attrs = ['slot_map']

    def __new__(mcs, name, bases, dct):
        if name == 'BaseController':
            return super().__new__(mcs, name, bases, dct)
        klass = super().__new__(mcs, name, bases, dct)
        combined_slotmap = {}
        for base in reversed(klass.__mro__):
            slotmap = getattr(base, 'slot_map', None)
            if slotmap:
                combined_slotmap.update(slotmap)
        missing = []
        for attr in mcs.required_attrs:
            if not any((hasattr(base, attr) for base in klass.__mro__)):
                missing.append(attr)
        if missing:
            raise TypeError(f"Class '{name}' must define the following attributes: {', '.join(missing)}.\n Nothing defined in {klass.__mro__}")
        klass.slot_map = Box(combined_slotmap)
        return klass


class BaseController(metaclass=ControllerMeta):
    """Base class for all controllers"""

    slot_map: Dict[str, List[str]] = {}
    signal_connected = False
    is_auto_connect_signal = True

    def __init__(self, parent=None):
        super().__init__()
        self.widgetManager = WidgetManager(self)
        self.controllerName = self.__class__.__name__
        self.publisher = Publisher()
        self.setupUi(self)
        if not self.is_auto_connect_signal:
            return
        self.setupHandler()

    def setupHandler(self):
        """Setup handler and connect signals"""
        searchModules = ['app.windows.handlers', '.'.join(self.__module__.split('.')[:-1])]
        if searchModules[-1] == '__main__' or searchModules[-1] == '':
            searchModules.pop()
        searchCls = [self.controllerName, self.controllerName.replace('Controller', ''), self.controllerName.replace('Widget', '')]
        for module in searchModules:
            for cls in searchCls:
                if importlib.util.find_spec(f'{module}.{cls}Handler') is None:
                    continue
                handlerModule = importlib.import_module(f'{module}.{cls}Handler')
                self.handler = getattr(handlerModule, f'{cls}Handler')(widgetManager=self.widgetManager, events=list(self.slot_map.keys()))
                break
        if self.is_auto_connect_signal and hasattr(self, 'handler'):
            self._connect_signals()

    @abstractmethod
    def setupUi(self, widget):
        """Set up the UI components"""
        pass

    def _connect_signals(self):
        if not hasattr(self, 'slot_map'):
            raise ValueError(f'{self.__class__.__name__} must define slot_map to use auto connect signals')
        subscriber = self.handler
        for event in self.handler.events:
            if event in self.slot_map.keys():
                t = self.slot_map.get(event)
                if t is None:
                    continue
                if callable(t):
                    t(self.handler, self.publisher)
                    continue
                    pass
                try:
                    self.publisher.connect(self.widgetManager.get(t[0]), t[1], event, data={'widget_manager': self.widgetManager})
                except AttributeError:
                    wd = self.widgetManager.get(t[0])
                    from .Logging import logger
                    logger.debug('widget "%s" does not have attribute "%s". Abort connecting event: %s' % (wd, t[1], event))
                    pass
                self.publisher.subscribe(subscriber=subscriber, event=event)
        self.signal_connected = True
