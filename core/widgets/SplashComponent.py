'''
SplashComponent - Custom splash screen component for PySide6
'''
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import QSplashScreen, QProgressBar, QLabel, QVBoxLayout, QWidget, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont


class SplashComponent(QSplashScreen):
    '''Custom splash screen with text, progress bar, and configurable options'''

    def __init__(self, pixmap: QPixmap, opacity: float = 1.0, alwaysOnTop: bool = True, autoClose: Optional[int] = None):
        '''
        Initialize splash screen component

        Args:
            pixmap: QPixmap to display as background
            opacity: Window opacity (0.0 to 1.0)
            alwaysOnTop: Keep window on top of other windows
            autoClose: Auto close after this many milliseconds (None to disable)
        '''
        flags = Qt.WindowStaysOnTopHint if alwaysOnTop else Qt.WindowType(0)
        super().__init__(pixmap, flags)

        self.setWindowOpacity(opacity)

        # Create overlay widget for text and progress bar
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet('background: transparent;')

        layout = QVBoxLayout(self.overlay)
        layout.setContentsMargins(20, 0, 20, 30)
        layout.setSpacing(10)

        # Add spacer to push content to bottom
        layout.addStretch()

        # Status label
        self.statusLabel = QLabel('Loading...')
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setFont(QFont('Arial', 12, QFont.Bold))
        self.statusLabel.setStyleSheet('''
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 150);
                padding: 10px;
                border-radius: 5px;
            }
        ''')
        layout.addWidget(self.statusLabel)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setStyleSheet('''
            QProgressBar {
                border: 2px solid rgba(255, 255, 255, 200);
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 100);
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        ''')
        layout.addWidget(self.progress)

        # Resize overlay to match splash screen
        self.overlay.setGeometry(self.rect())

        # Setup auto-close timer if specified
        if autoClose is not None and autoClose > 0:
            self._autoCloseTimer = QTimer()
            self._autoCloseTimer.setSingleShot(True)
            self._autoCloseTimer.timeout.connect(self.close)
            self._autoCloseTimer.start(autoClose)
        else:
            self._autoCloseTimer = None


    def resizeEvent(self, event):
        '''Handle resize event to keep overlay in sync'''
        super().resizeEvent(event)
        self.overlay.setGeometry(self.rect())


    def setProgress(self, value: int):
        '''Set progress bar value (0-100)'''
        self.progress.setValue(value)


    def setStatus(self, text: str):
        '''Set status label text'''
        self.statusLabel.setText(text)


    def close(self):
        '''Override close to cleanup timer'''
        if self._autoCloseTimer is not None:
            self._autoCloseTimer.stop()
        super().close()


def loadSplashPixmap(path: str, maxWidthRatio: float = 0.5, maxHeightRatio: float = 0.6) -> Optional[QPixmap]:
    '''
    Load and scale pixmap from file path or Qt resource

    Args:
        path: Absolute file path or Qt resource path (e.g., ":/splash.jpeg")
        maxWidthRatio: Maximum width as ratio of screen width (default 0.5 = 50%)
        maxHeightRatio: Maximum height as ratio of screen height (default 0.6 = 60%)

    Returns:
        Scaled QPixmap or None if loading failed
    '''
    pixmap = QPixmap()

    # Try loading from resource or file
    if path.startswith(':/'):
        # Qt resource path
        pixmap = QPixmap(path)
    else:
        # File path - resolve and normalize
        filePath = Path(path).resolve()
        pathStr = str(filePath).replace('\\', '/')
        pixmap = QPixmap(pathStr)

    if pixmap.isNull():
        return None

    # Get screen dimensions
    app = QApplication.instance()
    if app is None:
        # No QApplication instance, return pixmap as-is
        return pixmap

    screen = app.primaryScreen().geometry()
    maxWidth = int(screen.width() * maxWidthRatio)
    maxHeight = int(screen.height() * maxHeightRatio)

    # Scale if needed
    if pixmap.width() > maxWidth or pixmap.height() > maxHeight:
        pixmap = pixmap.scaled(maxWidth, maxHeight, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    return pixmap


def createSplash(imagePath: str, opacity: float = 1.0, alwaysOnTop: bool = True, autoClose: Optional[int] = None, maxWidthRatio: float = 0.5, maxHeightRatio: float = 0.6) -> Optional[SplashComponent]:
    '''
    Helper method to create configured SplashComponent

    Args:
        imagePath: Absolute file path or Qt resource path (e.g., ":/splash.jpeg")
        opacity: Window opacity (0.0 to 1.0)
        alwaysOnTop: Keep window on top of other windows
        autoClose: Auto close after this many milliseconds (None to disable)
        maxWidthRatio: Maximum width as ratio of screen width
        maxHeightRatio: Maximum height as ratio of screen height

    Returns:
        SplashComponent instance or None if image loading failed
    '''
    pixmap = loadSplashPixmap(imagePath, maxWidthRatio, maxHeightRatio)

    if pixmap is None:
        return None

    return SplashComponent(pixmap=pixmap, opacity=opacity, alwaysOnTop=alwaysOnTop, autoClose=autoClose)
