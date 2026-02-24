#                  M""""""`M            dP
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

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from core.QtAppContext import QtAppContext


class ServiceProvider(ABC):
    """Base class for app-level service registration during bootstrap.

    Inspired by Laravel Service Providers + systemd unit ordering.

    Lifecycle:
        1. Build-time: ``scripts/compile_providers.py`` scans ``app/providers/``
           and generates ``_provider_manifest.py`` listing discoverable providers.
        2. Runtime: ``QtAppContext.bootstrap()`` loads the manifest, topologically
           sorts providers based on ordering attributes, then calls ``register()``
           followed by ``boot()`` on each provider.

    Class Attributes:
        discoverable (bool):
            If ``True`` (default), the build-time script includes this provider
            in the manifest.  Set to ``False`` for abstract base classes.
        after (List[str]):
            Provider class names that MUST run **before** this one.
            Equivalent to systemd ``After=``.
        requires (List[str]):
            Provider class names that MUST exist **and** succeed.
            If a required provider fails, this provider is skipped.
            Equivalent to systemd ``Requires=``.
        wants (List[str]):
            Provider class names that SHOULD run before this one,
            but whose failure is tolerated.
            Equivalent to systemd ``Wants=``.
    """

    discoverable: bool = True
    after: List[str] = []
    requires: List[str] = []
    wants: List[str] = []

    def __init__(self, ctx: 'QtAppContext'):
        self.ctx = ctx

    @abstractmethod
    def register(self):
        """Register services into ``self.ctx``.
        Called on the **main thread** during bootstrap.
        Use ``self.ctx.registerService(name, instance)`` here.
        """
        pass

    def boot(self):
        """Optional post-registration hook.
        Called after **all** providers have completed ``register()``.
        Use this when you need to wire services that depend on other
        providers already being registered.
        """
        pass
