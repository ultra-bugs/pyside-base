import sys
from functools import wraps
from loguru import logger
from core.Utils import PathHelper
if False:
    import better_exceptions
    better_exceptions.hook()
    _original_exception = logger.exception

    @wraps(_original_exception)
    def better_exception_wrapper(*args, **kwargs):
        exc_type, exc_value, tb = sys.exc_info()
        print(exc_type)
        print(exc_value)
        if not isinstance(exc_type, (KeyboardInterrupt, SystemExit)):
            formatted = ''.join(better_exceptions.format_exception(exc_type, exc_value, tb))
            logger.opt(exception=exc_value).error('BetterException Stacktrace:\n{}', formatted)
        return _original_exception(*args, **kwargs)
    logger.exception = better_exception_wrapper

def setupLogging():
    """Setup application logging"""
    logger.remove()
    isHasStdErrHandler = False
    logDir = PathHelper.buildDataPath('logs')
    PathHelper.ensureDirExists(logDir)
    from core.Config import Config
    if Config().get('consolelog.enable', False):
        logger.add(sys.stderr, format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <green>T:{thread.name}</green>|<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>', level=Config().get('consolelog.level', 'DEBUG'))
        isHasStdErrHandler = True
    logger.add(PathHelper.joinPath(logDir, 'app.log'), rotation='1 day', retention='7 days', compression='zip', format='{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | T:{thread} | {name}:{function}:{line} | {message}', level='DEBUG')
    logger.add(PathHelper.joinPath(logDir, 'error.log'), rotation='1 day', retention='30 days', compression='zip', format='{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | T:{thread} | {name}:{function}:{line} | {message}', level='ERROR')
    if not isHasStdErrHandler:
        logger.add(sys.stderr, format='{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | T:{thread} | {name}:{function}:{line} | {message}', level='ERROR')
    return logger
logger = setupLogging()