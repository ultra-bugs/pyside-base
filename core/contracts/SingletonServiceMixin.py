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
#              * -  Copyright © 2026 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

class SingletonServiceMixin:
    '''Mixin enforcing singleton construction — child classes need zero boilerplate.

    Mechanism:
        * ``__new__`` always returns the same instance per class.
        * ``__init_subclass__`` automatically wraps each subclass ``__init__``
          so it only runs on the first construction. Subsequent calls to
          ``SomeService()`` return the cached instance without re-running ``__init__``.

    Compatible with plain Python classes (no QObject in MRO required).
    Signal decoupling via composition (separate QObject signal containers) must
    be applied before using this mixin with former QObject subclasses.

    Usage — just inherit, nothing else::

        class MyService(SingletonServiceMixin):
            def __init__(self):
                # runs exactly once — no guard call needed
                self.data = loadHeavyData()
    '''

    _singletonInstance = None
    _singletonInitialized: bool = False

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        # Per-class reset so each leaf class has its own singleton state
        cls._singletonInstance = None
        cls._singletonInitialized = False
        # Auto-wrap __init__ defined directly on this subclass
        if '__init__' in cls.__dict__:
            _original = cls.__dict__['__init__']

            def _guarded(self, *args, _orig=_original, **kwargs):
                if type(self)._singletonInitialized:
                    return
                type(self)._singletonInitialized = True
                _orig(self, *args, **kwargs)

            cls.__init__ = _guarded

    def __new__(cls, *args, **kwargs):
        if cls._singletonInstance is None:
            cls._singletonInstance = super().__new__(cls)
        return cls._singletonInstance
