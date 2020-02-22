"""Logger Module"""
import logging
import os


LEVELS = dict(CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10)
ENV_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

LOGGER = logging.getLogger()
LOGGER.setLevel(LEVELS.get(ENV_LEVEL, 20))


def log_debug(msg):
    """Logs debug messages"""
    LOGGER.debug(msg)


def log_info(msg):
    """Logs info messages"""
    LOGGER.info(msg)


def log_warning(msg):
    """Logs warning messages"""
    LOGGER.warning(msg)


def log_error(msg):
    """Logs error messages"""
    LOGGER.error(msg)


def log_exception(msg):
    """Logs exception messages"""
    LOGGER.exception(msg)
