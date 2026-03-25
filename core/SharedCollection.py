#                  M"""""""`M            dP
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

from __future__ import annotations

from typing import Callable, Generic, Iterator, Optional, TypeVar, overload

from PySide6.QtCore import QMutex, QMutexLocker

K = TypeVar('K')
R = TypeVar('R')
T = TypeVar('T')


class SharedCollection(Generic[T]):
    """
    Thread-safe global shared collection with LINQ-inspired query helpers.

    All mutations are guarded by a QMutex. Query methods take a snapshot
    before releasing the lock, so user-supplied predicates/mappers are
    never called while the lock is held — avoiding deadlock potential.

    Usage::

        col = ctx.getCollection('myItems')
        col.add(item).add(item2)          # fluent mutation
        results = col.where(lambda x: x.active).orderBy(lambda x: x.name)
    """

    def __init__(self) -> None:
        self._items: list[T] = []
        self._lock = QMutex()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _snapshot(self) -> list[T]:
        """Return a shallow copy of items under lock."""
        with QMutexLocker(self._lock):
            return list(self._items)

    # ------------------------------------------------------------------
    # Mutation methods  (return Self for fluent chaining)
    # ------------------------------------------------------------------

    def add(self, item: T) -> 'SharedCollection[T]':
        """Append a single item."""
        with QMutexLocker(self._lock):
            self._items.append(item)
        return self

    def addIfAbsent(self, item: T) -> bool:
        """Atomically add *item* only if it is not already present.

        Returns:
            True if item was added, False if it already existed.
        """
        with QMutexLocker(self._lock):
            if item in self._items:
                return False
            self._items.append(item)
            return True

    def addMany(self, items: list[T]) -> 'SharedCollection[T]':
        """Extend collection with multiple items."""
        with QMutexLocker(self._lock):
            self._items.extend(items)
        return self

    def remove(self, item: T) -> 'SharedCollection[T]':
        """Remove first occurrence of item (identity equality)."""
        with QMutexLocker(self._lock):
            try:
                self._items.remove(item)
            except ValueError:
                pass
        return self

    def removeWhere(self, predicate: Callable[[T], bool]) -> 'SharedCollection[T]':
        """Remove all items matching predicate."""
        with QMutexLocker(self._lock):
            self._items = [x for x in self._items if not predicate(x)]
        return self

    def update(self, predicate: Callable[[T], bool], updater: Callable[[T], None]) -> 'SharedCollection[T]':
        """
        Call *updater* in-place for every item matching *predicate*.
        Useful for mutable objects (dataclasses, dicts, etc.).
        """
        with QMutexLocker(self._lock):
            for item in self._items:
                if predicate(item):
                    updater(item)
        return self

    def replace(self, items: list[T]) -> 'SharedCollection[T]':
        """Replace entire collection contents."""
        with QMutexLocker(self._lock):
            self._items = list(items)
        return self

    def clear(self) -> 'SharedCollection[T]':
        """Remove all items."""
        with QMutexLocker(self._lock):
            self._items.clear()
        return self

    # ------------------------------------------------------------------
    # Query methods  (snapshot-based — lock released before user calls)
    # ------------------------------------------------------------------

    def where(self, predicate: Callable[[T], bool]) -> list[T]:
        """Filter items by predicate (LINQ Where)."""
        snap = self._snapshot()
        return [x for x in snap if predicate(x)]

    def select(self, mapper: Callable[[T], R]) -> list[R]:
        """Map items to a new type (LINQ Select)."""
        snap = self._snapshot()
        return [mapper(x) for x in snap]

    def first(self, predicate: Optional[Callable[[T], bool]] = None, default: Optional[T] = None) -> Optional[T]:
        """Return first item matching predicate, or *default*."""
        snap = self._snapshot()
        for item in snap:
            if predicate is None or predicate(item):
                return item
        return default

    def last(self, predicate: Optional[Callable[[T], bool]] = None, default: Optional[T] = None) -> Optional[T]:
        """Return last item matching predicate, or *default*."""
        snap = self._snapshot()
        for item in reversed(snap):
            if predicate is None or predicate(item):
                return item
        return default

    def any(self, predicate: Optional[Callable[[T], bool]] = None) -> bool:
        """Return True if any item matches predicate (or collection non-empty)."""
        snap = self._snapshot()
        if predicate is None:
            return len(snap) > 0
        return any(predicate(x) for x in snap)

    def all(self, predicate: Callable[[T], bool]) -> bool:
        """Return True if all items match predicate."""
        snap = self._snapshot()
        return all(predicate(x) for x in snap)

    def count(self, predicate: Optional[Callable[[T], bool]] = None) -> int:
        """Count items matching predicate, or total count."""
        snap = self._snapshot()
        if predicate is None:
            return len(snap)
        return sum(1 for x in snap if predicate(x))

    def groupBy(self, keyFn: Callable[[T], K]) -> dict[K, list[T]]:
        """Group items by key function (LINQ GroupBy)."""
        snap = self._snapshot()
        result: dict[K, list[T]] = {}
        for item in snap:
            k = keyFn(item)
            result.setdefault(k, []).append(item)
        return result

    def orderBy(self, keyFn: Callable[[T], any], reverse: bool = False) -> list[T]:
        """Return sorted list by key function (LINQ OrderBy / OrderByDescending)."""
        snap = self._snapshot()
        return sorted(snap, key=keyFn, reverse=reverse)

    def distinct(self, keyFn: Optional[Callable[[T], any]] = None) -> list[T]:
        """Return list with duplicates removed, preserving first-seen order."""
        snap = self._snapshot()
        seen: set = set()
        result: list[T] = []
        for item in snap:
            key = keyFn(item) if keyFn else item
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result

    def toList(self) -> list[T]:
        """Return a snapshot copy as a plain list."""
        return self._snapshot()

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        with QMutexLocker(self._lock):
            return len(self._items)

    def __iter__(self) -> Iterator[T]:
        """Iterate over a snapshot (safe for concurrent modifications)."""
        return iter(self._snapshot())

    def __contains__(self, item: object) -> bool:
        snap = self._snapshot()
        return item in snap

    def __repr__(self) -> str:
        snap = self._snapshot()
        return f'SharedCollection({snap!r})'
