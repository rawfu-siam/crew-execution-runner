"""
Production-grade structured logging utility module.
Provides dual-stream logging (Console and Rotating
File Handler) with timestamping and trace info.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from config.settings import settings


def setup_logger(name: str) -> logging.Logger:
    """
    Configures and returns a production-ready logger instance with dual-stream output.
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    # Define standard professional log format
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. Stream Handler (Console Output)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # 2. Rotating File Handler (Persistent Storage, max 50KB, 3 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=50 * 1024,  # 50 KB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Prevent log propagation to root logger to avoid duplicate entries
    logger.propagate = False
    return logger


# Default application logger instance
logger = setup_logger("crew_runner")
