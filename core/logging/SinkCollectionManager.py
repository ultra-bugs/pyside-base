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
from __future__ import annotations
from contextlib import contextmanager
from loguru import logger as _loguru_logger
from core.SharedCollection import SharedCollection
from .SinkEntry import SinkEntry


class SinkCollectionManager:
    """
    Runtime sink manager for loguru.
    Maintains ordered SharedCollection[SinkEntry], commits to loguru on demand.
    """

    def __init__(self) -> None:
        self._col: SharedCollection[SinkEntry] = SharedCollection()

    # ------------------------------------------------------------------
    # Mutation API
    # ------------------------------------------------------------------

    def add(self, entry: SinkEntry) -> 'SinkCollectionManager':
        """Append sink entry. Auto-assign position if 0."""
        if entry.position == 0:
            entry.position = len(self._col) + 1
        self._col.addIfAbsent(entry)
        return self

    def remove(self, sink_id: str) -> 'SinkCollectionManager':
        self._col.removeWhere(lambda e: e.id == sink_id)
        return self

    def enable(self, sink_id: str) -> 'SinkCollectionManager':
        self._col.update(lambda e: e.id == sink_id, lambda e: setattr(e, 'enabled', True))
        return self

    def disable(self, sink_id: str) -> 'SinkCollectionManager':
        self._col.update(lambda e: e.id == sink_id, lambda e: setattr(e, 'enabled', False))
        return self

    def insertAt(self, position: int, entry: SinkEntry) -> 'SinkCollectionManager':
        """Insert and shift positions of existing entries >= position."""
        self._col.update(lambda e: e.position >= position, lambda e: setattr(e, 'position', e.position + 1))
        entry.position = position
        self._col.add(entry)
        return self

    def get(self, sink_id: str) -> SinkEntry | None:
        return self._col.first(lambda e: e.id == sink_id)

    # ------------------------------------------------------------------
    # Commit: rebuild loguru sinks in position order
    # ------------------------------------------------------------------

    def commit(self) -> 'SinkCollectionManager':
        """Remove all loguru handlers, re-add enabled sinks by position order."""
        _loguru_logger.remove()
        active = self._col.where(lambda e: e.enabled)
        active.sort(key=lambda e: e.position)
        for entry in active:
            kwargs = dict(entry.kwargs)
            kwargs['level'] = entry.level
            if entry.filter is not None:
                kwargs['filter'] = entry.filter
            new_id = _loguru_logger.add(entry.sink, **kwargs)
            entry.loguru_id = new_id
        return self

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def listSinks(self) -> list[SinkEntry]:
        return self._col.orderBy(lambda e: e.position)

    def __repr__(self) -> str:
        return f'SinkCollectionManager({self.listSinks()!r})'


class AutoCommitSinkManager(SinkCollectionManager):
    """SinkCollectionManager that commits after every mutation."""

    def __init__(self):
        super().__init__()
        self._batch_mode = False

    @contextmanager
    def batch(self):
        """Suppress auto-commit during block, commit once at end."""
        self._batch_mode = True
        try:
            yield self
        finally:
            self._batch_mode = False
            self.commit()

    def _auto_commit(self):
        if not self._batch_mode:
            self.commit()

    def _mutate(self, fn):
        fn()
        self.commit()
        return self

    def add(self, entry):
        return self._mutate(lambda: super(AutoCommitSinkManager, self).add(entry))

    def remove(self, sink_id):
        return self._mutate(lambda: super(AutoCommitSinkManager, self).remove(sink_id))

    def enable(self, sink_id):
        return self._mutate(lambda: super(AutoCommitSinkManager, self).enable(sink_id))

    def disable(self, sink_id):
        return self._mutate(lambda: super(AutoCommitSinkManager, self).disable(sink_id))

    def insertAt(self, position, entry):
        return self._mutate(lambda: super(AutoCommitSinkManager, self).insertAt(position, entry))
