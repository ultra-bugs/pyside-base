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
from typing import Any, Dict, List, Optional, Type, TypeVar
from PySide6.QtCore import QMutex, QMutexLocker, QObject
from core.Logging import logger

T = TypeVar('T')


class ServiceLocator(QObject):
    """
    Advanced Dependency Injection & Lifecycle Manager.
    Supports:
    1. Global Singletons
    2. Scoped Instances (Tag-based grouping & Auto-cleanup)
    """

    def __init__(self):
        super().__init__()
        # Global singletons: { 'interface_name': instance }
        self._singletons: Dict[str, Any] = {}
        # Scoped instances: { 'tag_id': [instance1, instance2, ...] }
        self._scopes: Dict[str, List[Any]] = {}
        self._lock = QMutex()

    # =========================================================================
    # GLOBAL / SINGLETON MANAGEMENT
    # =========================================================================

    def register(self, interface: str, instance: Any) -> None:
        """Register a global singleton."""
        with QMutexLocker(self._lock):
            if interface in self._singletons:
                logger.warning(f'Overwriting existing singleton service: {interface}')
            self._singletons[interface] = instance

    def get(self, interface: str, default: Optional[T] = None, serviceType: Type[T] = None) -> Optional[T]:
        """Retrieve a global singleton."""
        with QMutexLocker(self._lock):
            return self._singletons.get(interface, default)

    # =========================================================================
    # SCOPED / TAGGED MANAGEMENT (Factory Instances)
    # =========================================================================

    def registerScoped(self, tag: str, instance: Any) -> None:
        """
        Register an instance under a specific tag/scope.
        This keeps the instance alive until releaseScope is called.
        """
        with QMutexLocker(self._lock):
            if tag not in self._scopes:
                self._scopes[tag] = []
            # Avoid duplicate registration of the exact same object in the same scope
            if instance not in self._scopes[tag]:
                self._scopes[tag].append(instance)
            logger.debug(f"Registered scoped instance {instance.__class__.__name__} under tag '{tag}'")

    def getScoped(self, tag: str) -> List[Any]:
        """Get all instances associated with a tag."""
        with QMutexLocker(self._lock):
            return list(self._scopes.get(tag, []))

    def releaseScope(self, tag: str) -> None:
        """
        1. Retrieve all instances under the tag.
        2. Call .cleanup() / .dispose() / .close() if available.
        3. Remove references from registry to allow GC.
        """
        with QMutexLocker(self._lock):
            if tag not in self._scopes:
                return
            instances = self._scopes[tag]
            logger.info(f"Releasing scope '{tag}' with {len(instances)} instances.")
            for instance in instances:
                try:
                    # Priority 1: standard cleanup() method (IDisposable)
                    if hasattr(instance, 'cleanup') and callable(instance.cleanup):
                        instance.cleanup()
                    # Priority 2: generic close() method
                    elif hasattr(instance, 'close') and callable(instance.close):
                        instance.close()
                    # Priority 3: generic dispose() method
                    elif hasattr(instance, 'dispose') and callable(instance.dispose):
                        instance.dispose()
                except Exception as e:
                    logger.error(f"Error cleaning up instance {instance} in scope '{tag}': {e}")
            # Remove the key entirely.
            # This drops the ServiceLocator's reference to the list and the objects.
            # Python's GC will now reclaim memory assuming no other strong refs exist.
            del self._scopes[tag]
