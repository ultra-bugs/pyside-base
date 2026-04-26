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
import sys
from contextlib import contextmanager
from functools import wraps

from loguru import logger as _loguru


from core.logging.SinkCollectionManager import AutoCommitSinkManager, SinkCollectionManager
from core.logging.SinkEntry import SinkEntry
from core.Utils import PathHelper
from core.logging.FilterFactory import FilterFactory


def _setupBetterException():
    import better_exceptions
    better_exceptions.hook()
    _original_exception = _loguru.exception
    @wraps(_original_exception)
    def better_exception_wrapper(*args, **kwargs):
        exc_type, exc_value, tb = sys.exc_info()
        print(exc_type)
        print(exc_value)
        if not isinstance(exc_type, (KeyboardInterrupt, SystemExit)):
            formatted = ''.join(better_exceptions.format_exception(exc_type, exc_value, tb))
            _loguru.opt(exception=exc_value).error('BetterException Stacktrace:\n{}', formatted)
        return _original_exception(*args, **kwargs)
    _loguru.exception = better_exception_wrapper


class _LoguruWrappedLogger:
    """
    Transparent proxy to loguru logger.
    - getSinkManager() -> SinkCollectionManager|AutoCommitSinkManager (must CALL, not access as prop)
    - Everything else delegates to internal loguru logger
    """

    _initialized = False
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self.__class__._initialized:
            return
        self.__class__._initialized = True
        self.__dict__['_logger'] = _loguru
        self.__dict__['warn'] = _loguru.warning
        from core.Config import Config
        cfg = Config()
        if cfg.get('logging.sinkManAutoCommit', False):
            self.__dict__['_sink_manager'] = SinkCollectionManager()
            self._setup()
        else:
            self.__dict__['_sink_manager'] = AutoCommitSinkManager()
            self._setupUseAutoCommit()

    def _setupUseAutoCommit(self):
        from core.Config import Config
        cfg = Config()
        logDir = PathHelper.buildDataPath('logs')
        PathHelper.ensureDirExists(logDir)
        module_levels = cfg.get('logging.module_levels', {})
        default_level = cfg.get('logging.level', 'DEBUG')
        mod_filter = FilterFactory.make(module_levels, default_level) if module_levels else None
        LOG_FMT = '{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | T:{thread} | {name}:{function}:{line} | {message}'
        CON_FMT = (
            '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | '
            '<green>T:{thread.name}</green>|<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | '
            '<level>{message}</level>'
        )
        sm = self.__dict__['_sink_manager']
        with sm.batch():
            if cfg.get('consolelog.enable', False):
                sm.add(
                    SinkEntry(
                        id='console', sink=sys.stderr, position=1, level=cfg.get('consolelog.level', 'DEBUG'), filter=mod_filter, kwargs={'format': CON_FMT, 'colorize': True}
                    )
                )
            else:
                sm.add(SinkEntry(id='console.error', sink=sys.stderr, position=1, level='ERROR', kwargs={'format': LOG_FMT}))
            sm.add(
                SinkEntry(
                    id='file.app',
                    sink=PathHelper.joinPath(logDir, 'app.log'),
                    level='DEBUG',
                    position=2,
                    filter=mod_filter,
                    kwargs={'format': LOG_FMT, 'rotation': '1 day', 'retention': '7 days', 'compression': 'zip'},
                )
            )
            sm.add(
                SinkEntry(
                    id='file.error',
                    sink=PathHelper.joinPath(logDir, 'error.log'),
                    level='ERROR',
                    position=3,
                    kwargs={'format': LOG_FMT, 'rotation': '1 day', 'retention': '30 days', 'compression': 'zip'},
                )
            )

    def _setup(self) -> None:
        from core.Config import Config
        cfg = Config()
        logDir = PathHelper.buildDataPath('logs')
        PathHelper.ensureDirExists(logDir)
        module_levels = cfg.get('logging.module_levels', {})
        default_level = cfg.get('logging.level', 'DEBUG')
        mod_filter = FilterFactory.make(module_levels, default_level) if module_levels else None
        LOG_FMT = '{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | T:{thread} | {name}:{function}:{line} | {message}'
        CON_FMT = (
            '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | '
            '<green>T:{thread.name}</green>|<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | '
            '<level>{message}</level>'
        )
        sm = self.__dict__['_sink_manager']
        if cfg.get('consolelog.enable', False):
            sm.add(
                SinkEntry(id='console', sink=sys.stderr, position=1, level=cfg.get('consolelog.level', 'DEBUG'), filter=mod_filter, kwargs={'format': CON_FMT, 'colorize': True})
            )
        else:
            sm.add(SinkEntry(id='console.error', sink=sys.stderr, position=1, level='ERROR', kwargs={'format': LOG_FMT}))
        sm.add(
            SinkEntry(
                id='file.app',
                sink=PathHelper.joinPath(logDir, 'app.log'),
                level='DEBUG',
                position=2,
                filter=mod_filter,
                kwargs={'format': LOG_FMT, 'rotation': '1 day', 'retention': '7 days', 'compression': 'zip'},
            )
        )
        sm.add(
            SinkEntry(
                id='file.error',
                sink=PathHelper.joinPath(logDir, 'error.log'),
                level='ERROR',
                position=3,
                kwargs={'format': LOG_FMT, 'rotation': '1 day', 'retention': '30 days', 'compression': 'zip'},
            )
        )
        sm.commit()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def getSinkManager(self) -> SinkCollectionManager:
        """Returns SinkCollectionManager. Must be CALLED, not accessed as property."""
        return self.__dict__['_sink_manager']

    # ------------------------------------------------------------------
    # Transparent delegation
    # ------------------------------------------------------------------

    def __getattr__(self, name: str):
        return getattr(self.__dict__['_logger'], name)

    def __setattr__(self, name: str, value):
        # Intercept only internal attrs; rest goes to loguru
        if name.startswith('_') or name in ('warn',):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['_logger'], name, value)

    def __call__(self, *args, **kwargs):
        return self.__dict__['_logger'](*args, **kwargs)


@contextmanager
def logContext(**kwargs):
    """
    Temporary logging context.
        with logContext(taskId=uuid, userId=123):
            logger.info('Processing')
    """
    yield logger.bind(**kwargs)


logger = _LoguruWrappedLogger()

__all__ = ['logger', 'logContext']
