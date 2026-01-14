from PySide6.QtNetwork import QNetworkAccessManager, QNetworkDiskCache
from PySide6.QtCore import QObject, QStandardPaths
from core.Config import Config
from core.Utils import PathHelper


class NetworkManager(QObject):
    """Manages QNetworkAccessManager and global network configurations."""

    def __init__(self, config: Config):
        super().__init__()
        self._manager = QNetworkAccessManager(self)
        self._config = config
        self._setupCache()

    @property
    def manager(self) -> QNetworkAccessManager:
        return self._manager

    def _setupCache(self):
        """Setup disk cache for network requests."""
        cache = QNetworkDiskCache(self)
        cachePath = PathHelper.joinPath(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), 'network_cache')
        cache.setCacheDirectory(str(cachePath))
        cache.setMaximumCacheSize(50 * 1024 * 1024)
        self._manager.setCache(cache)
