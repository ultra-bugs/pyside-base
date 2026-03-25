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
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from PySide6.QtCore import QMutex, QMutexLocker, QObject

from core.Logging import logger

T = TypeVar('T')

# Sentinel to distinguish "no instance passed" from None
_SENTINEL = object()


class ServiceLocator(QObject):
    """
    Advanced Dependency Injection & Lifecycle Manager.
    Supports:
    1. Global Singletons  – keyed by string or class FQN
    2. Scoped Instances   – tag-based grouping & auto-cleanup
    """

    def __init__(self):
        super().__init__()
        # Global singletons: { key_str: instance }
        self._singletons: Dict[str, Any] = {}
        self._backCompatibleMaps: Dict[str, str] = {}
        # Scoped instances: { 'tag_id': [instance1, instance2, ...] }
        self._scopes: Dict[str, List[Any]] = {}
        self._lock = QMutex()

    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================

    def _resolveKey(self, interface: Union[str, Type]) -> str:
        """Resolve a string key from a string or a class/type."""
        if isinstance(interface, str):
            if interface in self._backCompatibleMaps.keys():
                return self._backCompatibleMaps[interface]
            return interface
        if isinstance(interface, type):
            return f'{interface.__module__}.{interface.__qualname__}'
        raise TypeError(f'ServiceLocator key must be a str or a class, got {type(interface)!r}')

    # =========================================================================
    # GLOBAL / SINGLETON MANAGEMENT
    # =========================================================================

    def register(self, interfaceOrInstance: Union[str, Type, Any], instance: Any = _SENTINEL) -> None:
        """Register a global singleton.

        Overloads (inspired by Laravel Container):
            register(instance)           → key = FQN of type(instance)
            register(MyClass, instance)  → key = FQN of MyClass
            register('my_key', instance) → key = 'my_key'  (legacy)
        """
        if instance is _SENTINEL:
            # Single-arg form: register(instance)
            actualInstance = interfaceOrInstance
            key = self._resolveKey(type(actualInstance))
        else:
            # Two-arg form: register(str|Type, instance)
            try:
                key = self._resolveKey(type(instance))
                self._backCompatibleMaps[interfaceOrInstance] = key
            except TypeError:
                key = self._resolveKey(interfaceOrInstance)
                del self._backCompatibleMaps[interfaceOrInstance]
            actualInstance = instance

        with QMutexLocker(self._lock):
            if key in self._singletons:
                logger.warning(f'Overwriting existing singleton service: {key}')
            self._singletons[key] = actualInstance

    def get(self, interface: Union[str, Type[T]], default: Optional[T] = None) -> Optional[T]:
        """Retrieve a global singleton by string key or class.

        Examples:
            get('my_key')         → legacy string lookup
            get(MyClass)          → lookup by class FQN
            get(MyClass, default) → returns default if not found
        """
        key = self._resolveKey(interface)
        with QMutexLocker(self._lock):
            return self._singletons.get(key, default)

    # =========================================================================
    # SCOPED / TAGGED MANAGEMENT (Factory Instances)
    # =========================================================================

    def registerScoped(self, tag: str, instance: Any) -> None:
        """Register an instance under a specific tag/scope.

        Keeps the instance alive until releaseScope is called.
        Duplicate objects in the same scope are silently ignored.
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

    def getScopedByType(self, tag: str, cls: Type[T]) -> Optional[T]:
        """Get the first scoped instance matching the given class under a tag.

        Args:
            tag: Scope identifier (e.g. task UUID).
            cls: Class to filter by (uses isinstance check).

        Returns:
            First matched instance or None.
        """
        with QMutexLocker(self._lock):
            for instance in self._scopes.get(tag, []):
                if isinstance(instance, cls):
                    return instance
        return None

    def releaseScope(self, tag: str) -> None:
        """Cleanup all instances under a tag.

        Cleanup priority per instance:
            1. cleanup()  (highest)
            2. close()
            3. dispose()
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
                    logger.opt(exception=e).error(f"Error cleaning up instance {instance} in scope '{tag}': {e}")
            # Remove the key entirely.
            # This drops the ServiceLocator's reference to the list and the objects.
            # Python's GC will now reclaim memory assuming no other strong refs exist.
            del self._scopes[tag]
