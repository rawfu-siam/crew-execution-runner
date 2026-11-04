"""
Production-grade structured logging utility module.
Provide dual-stream logging (Console and Rotating
File Handler) with timestamping and trace info.
"""

import logging
# import os
# from logging.handlers import RotatingFileHandler


def setup_logger(name: str) -> logging.Logger:
    """
    Configures and returns a production-ready logger instance with dula-stream output
    """
    logger = logging.getLogger(name)
    # Avoid duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger
