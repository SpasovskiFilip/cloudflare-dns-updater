"""
logger.py - Logging Utility for DNS Updater

This module provides a function to create and configure a logger for the DNS Updater application.
It ensures that log messages are output to both the console and a log file,
with appropriate formatting and log levels.

Functions:
    create_logger(level: int = logging.INFO, log_file: str = "dns_updater.log") -> logging.Logger
        Create and configure a logger with console and file handlers.
"""

import logging
import sys

def create_logger(level: int = logging.INFO, log_file: str = "dns_updater.log") -> logging.Logger:
    """
    Create and configure the logger object for the DNS Updater application.

    This logger outputs INFO and higher level logs to the console,
    and WARNING and higher to a log file.
    Duplicate handlers are avoided.

    Args:
        level (int, optional): The logging level for the console handler. Defaults to logging.INFO.
        log_file (str, optional): The filename for the log file. Defaults to 'dns_updater.log'.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger("MGE-Logs")
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        file_handler = logging.FileHandler(log_file)
        console_handler.setLevel(level)
        file_handler.setLevel(logging.WARNING)
        logger_format = logging.Formatter(
            "%(asctime)s | %(filename)s | %(levelname)s | %(message)s"
        )
        file_format = logging.Formatter(
            "%(asctime)s | %(filename)s(%(lineno)d) | %(levelname)s | %(message)s"
        )
        file_handler.setFormatter(file_format)
        console_handler.setFormatter(logger_format)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    logger.setLevel(level)
    return logger
