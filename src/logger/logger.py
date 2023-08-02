import logging
import os
from datetime import datetime as dt

from logger.qt_handler import QtLogHandler


LOG_FILE = f"{dt.now().strftime('%d_%m_%Y')}.log"
logs_dir = os.path.join(os.getcwd(), "logs")

os.makedirs(logs_dir, exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_dir, LOG_FILE)

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler for the logger
file_handler = logging.FileHandler(LOG_FILE_PATH)
# Don't log debug messages to file
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    "[ %(asctime)s ] %(lineno)d - %(levelname)s: %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Create a stream handler for the logger
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_formatter = logging.Formatter("%(levelname)s: %(message)s")
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)

# Create a Qt handler for the logger
qt_log_handler = QtLogHandler()
logger.addHandler(qt_log_handler)
