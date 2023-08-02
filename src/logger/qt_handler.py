import logging

from PyQt6.QtCore import pyqtSignal, QObject


class QtLogHandler(logging.Handler):
    """Custom logging handler to redirect logs to Qt's signal slot."""

    class Signals(QObject):
        """Signals to be emitted by the QtLogHandler"""

        # signal to emit the log message
        log = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._initialSetup()
        self.signals = self.Signals()

    def _initialSetup(self):
        """Initial setup of the QtLogHandler"""
        # set the log level and formatter
        self.setLevel(logging.INFO)
        formatter = logging.Formatter("> %(levelname)s: %(message)s")
        self.setFormatter(formatter)

    def emit(self, record):
        """Emit the log message"""
        msg = self.format(record)
        self.signals.log.emit(msg)
