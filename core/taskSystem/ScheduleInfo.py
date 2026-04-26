"""
ScheduleInfo

Type-safe container hierarchy for task scheduling configuration.
Replaces raw dict-based scheduleInfo, provides trigger-specific helper methods.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, Literal, Optional, Union, overload

# QTimer's maximum interval (signed 32-bit ms) ≈ 24.8 days
_QTIMER_MAX_MS: int = 2_147_483_647
_QTIMER_MAX_SECONDS: int = _QTIMER_MAX_MS // 1000


# ── Base ──────────────────────────────────────────────────────────────────────


class ScheduleInfo(ABC):
    """
    Abstract base for all schedule containers.

    Internally stores `nextRuntime` as a Unix timestamp (float).
    Subclasses carry trigger-specific data and helper methods.
    All subclasses are compatible with TaskScheduler.addScheduledTask().
    """

    @property
    @abstractmethod
    def trigger(self) -> str:
        """Trigger type string: 'date' | 'interval' | 'cron'"""

    @property
    @abstractmethod
    def nextRuntime(self) -> float:
        """Next execution time as Unix timestamp."""

    @property
    def nextRun(self) -> datetime:
        """Next execution time as datetime (local)."""
        return datetime.fromtimestamp(self.nextRuntime)

    @property
    def delaySeconds(self) -> float:
        """Seconds until next execution. Negative if overdue."""
        return self.nextRuntime - time.time()

    @property
    def needsCheckpointRearm(self) -> bool:
        """True if delay exceeds QTimer's 32-bit ms limit (~24.8 days)."""
        return self.delaySeconds > _QTIMER_MAX_SECONDS

    @abstractmethod
    def toDict(self) -> Dict[str, Any]:
        """Serialize to dict (backward-compat with existing storage)."""

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(trigger={self.trigger!r}, nextRun={self.nextRun.isoformat()})'


# ── Date ──────────────────────────────────────────────────────────────────────


class DateScheduleInfo(ScheduleInfo):
    """
    One-time execution at a specific datetime.

    Example:
        info = DateScheduleInfo(datetime(2026, 5, 1, 9, 0))
        info.changeWhen(datetime(2026, 5, 10, 9, 0))
    """

    trigger = 'date'

    def __init__(self, runDate: datetime) -> None:
        self._validate(runDate)
        self._runDate = runDate

    @staticmethod
    def _validate(runDate: datetime) -> None:
        if not isinstance(runDate, datetime):
            raise TypeError(f'runDate must be datetime, got {type(runDate).__name__}')
        if runDate <= datetime.now():
            raise ValueError(f'runDate must be in the future (got {runDate})')

    @property
    def nextRuntime(self) -> float:
        return self._runDate.timestamp()

    @property
    def runDate(self) -> datetime:
        return self._runDate

    def changeWhen(self, runDate: datetime) -> 'DateScheduleInfo':
        """Change the target run datetime. Fluent."""
        self._validate(runDate)
        self._runDate = runDate
        return self

    def toDict(self) -> Dict[str, Any]:
        return {'trigger': self.trigger, 'runDate': self._runDate}


# ── Interval ─────────────────────────────────────────────────────────────────


class IntervalScheduleInfo(ScheduleInfo):
    """
    Recurring execution at a fixed interval.

    `startDate` is the anchor for the first run (optional).
    `setInterval()` changes the cadence without touching `startDate`.

    Example:
        info = IntervalScheduleInfo(intervalSeconds=3600)
        info.setInterval(1800)          # change to 30 min
        info.everyHours(2)              # fluent alias
        info.everyMinutes(45)           # fluent alias
    """

    trigger = 'interval'

    def __init__(self, intervalSeconds: int, startDate: Optional[datetime] = None) -> None:
        self._validate_interval(intervalSeconds)
        if startDate is not None and startDate <= datetime.now():
            raise ValueError('startDate must be in the future if provided')
        self._intervalSeconds = intervalSeconds
        self._startDate = startDate

    @staticmethod
    def _validate_interval(seconds: int) -> None:
        if not isinstance(seconds, int) or seconds <= 0:
            raise ValueError(f'intervalSeconds must be a positive int, got {seconds!r}')

    @property
    def intervalSeconds(self) -> int:
        return self._intervalSeconds

    @property
    def startDate(self) -> Optional[datetime]:
        return self._startDate

    @property
    def nextRuntime(self) -> float:
        if self._startDate and self._startDate > datetime.now():
            return self._startDate.timestamp()
        # Next tick from now
        return (datetime.now() + timedelta(seconds=self._intervalSeconds)).timestamp()

    def setInterval(self, seconds: int) -> 'IntervalScheduleInfo':
        """Change interval cadence without affecting startDate. Fluent."""
        self._validate_interval(seconds)
        self._intervalSeconds = seconds
        return self

    def everyMinutes(self, minutes: int) -> 'IntervalScheduleInfo':
        """Fluent alias: set interval in minutes."""
        return self.setInterval(minutes * 60)

    def everyHours(self, hours: int) -> 'IntervalScheduleInfo':
        """Fluent alias: set interval in hours."""
        return self.setInterval(hours * 3600)

    def everyDays(self, days: int) -> 'IntervalScheduleInfo':
        """Fluent alias: set interval in days."""
        return self.setInterval(days * 86400)

    def startAt(self, startDate: datetime) -> 'IntervalScheduleInfo':
        """Set or change the first-run anchor. Fluent."""
        if startDate <= datetime.now():
            raise ValueError('startDate must be in the future')
        self._startDate = startDate
        return self

    def toDict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {'trigger': self.trigger, 'intervalSeconds': self._intervalSeconds}
        if self._startDate:
            result['startDate'] = self._startDate
        return result


# ── Cron ─────────────────────────────────────────────────────────────────────


class CronScheduleInfo(ScheduleInfo):
    """
    Daily execution at a specific local time (hour:minute).

    Example:
        info = CronScheduleInfo(hour=9, minute=30)
        info.every(hour=18, minute=0)   # change to 18:00 daily. Fluent.
    """

    trigger = 'cron'

    def __init__(self, hour: int, minute: int = 0) -> None:
        self._validate(hour, minute)
        self._hour = hour
        self._minute = minute

    @staticmethod
    def _validate(hour: int, minute: int) -> None:
        if not (0 <= hour <= 23):
            raise ValueError(f'hour must be 0-23, got {hour}')
        if not (0 <= minute <= 59):
            raise ValueError(f'minute must be 0-59, got {minute}')

    @property
    def hour(self) -> int:
        return self._hour

    @property
    def minute(self) -> int:
        return self._minute

    @property
    def nextRuntime(self) -> float:
        now = datetime.now()
        candidate = now.replace(hour=self._hour, minute=self._minute, second=0, microsecond=0)
        if candidate <= now:
            candidate += timedelta(days=1)
        return candidate.timestamp()

    def every(self, hour: int, minute: int = 0) -> 'CronScheduleInfo':
        """Change the daily trigger time. Fluent."""
        self._validate(hour, minute)
        self._hour = hour
        self._minute = minute
        return self

    def toDict(self) -> Dict[str, Any]:
        return {'trigger': self.trigger, 'hour': self._hour, 'minute': self._minute}


# ── Factory ───────────────────────────────────────────────────────────────────


class ScheduleInfoFactory:
    """
    Creates ScheduleInfo instances from dicts or kwargs.
    Used internally by TaskManagerService for backward-compat dict → container conversion.

    Usage:
        info = ScheduleInfoFactory.fromDict({'trigger': 'interval', 'intervalSeconds': 3600})
        info = ScheduleInfoFactory.create('cron', hour=9, minute=0)
        info = ScheduleInfoFactory.create('date', runDate=datetime(2026, 6, 1))
    """

    _registry: Dict[str, type] = {'date': DateScheduleInfo, 'interval': IntervalScheduleInfo, 'cron': CronScheduleInfo}

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> ScheduleInfo:
        """Create ScheduleInfo from a plain dict (legacy scheduleInfo format)."""
        if not isinstance(data, dict):
            raise TypeError(f'Expected dict, got {type(data).__name__}')
        data = dict(data)  # shallow copy — do not mutate caller's dict
        trigger = data.pop('trigger', None)
        if not trigger:
            raise KeyError("scheduleInfo dict must contain 'trigger' key")
        return cls.create(trigger, **data)

    @overload
    @classmethod
    def create(cls, trigger: Literal['date'], **kwargs: Any) -> DateScheduleInfo: ...
    @overload
    @classmethod
    def create(cls, trigger: Literal['interval'], **kwargs: Any) -> IntervalScheduleInfo: ...
    @overload
    @classmethod
    def create(cls, trigger: Literal['cron'], **kwargs: Any) -> CronScheduleInfo: ...
    @classmethod
    def create(cls, trigger: Literal['cron', 'date', 'interval'], **kwargs: Any) -> ScheduleInfo:
        """Create ScheduleInfo by trigger type + keyword args."""
        klass = cls._registry.get(trigger)
        if klass is None:
            raise ValueError(f'Unknown trigger {trigger!r}. Valid: {list(cls._registry)}')
        return klass(**kwargs)

    @classmethod
    def date(cls, **kwargs: Any) -> DateScheduleInfo:
        """Create ScheduleInfo by trigger date + keyword args."""
        return cls.create(trigger='date', **kwargs)

    @classmethod
    def interval(cls, **kwargs: Any) -> IntervalScheduleInfo:
        """Create ScheduleInfo by trigger interval + keyword args."""
        return cls.create(trigger='interval', **kwargs)

    @classmethod
    def cron(cls, **kwargs: Any) -> CronScheduleInfo:
        """Create ScheduleInfo by trigger cron + keyword args."""
        return cls.create(trigger='cron', **kwargs)

    @classmethod
    def ensure(cls, info: Union[ScheduleInfo, Dict[str, Any]]) -> ScheduleInfo:
        """
        Idempotent coerce: pass-through ScheduleInfo, or convert dict.
        Use at facade boundary so internal code always works with typed objects.
        """
        if isinstance(info, ScheduleInfo):
            return info
        if isinstance(info, dict):
            return cls.fromDict(info)
        raise TypeError(f'scheduleInfo must be ScheduleInfo or dict, got {type(info).__name__}')
