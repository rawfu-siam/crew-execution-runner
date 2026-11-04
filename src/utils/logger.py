"""
Production-grade structured logging utility module.
Provide dual-stream logging (Console and Rotating
File Handler) with timestamping and trace info.
"""

import logging
import os
# from logging.handlers import RotatingFileHandler

from config.settings import settings


def setup_logger(name: str) -> logging.Logger:
    """
    Configures and returns a production-ready logger instance with dula-stream output
    """
    logger = logging.getLogger(name)
    # Avoid duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create logs directory if it doesn't exists
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    # Define standard professional log format
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
