"""Logging methods"""
from typing import Callable
import logging
import logging.config

from cpm import settings

logging.config.dictConfig(settings.LOGGERS)


def logged(cls) -> Callable:
    """Decorator to log certain methods of each class while giving
    each clas its own logger."""
    cls.logger = logging.getLogger("user_info." + cls.__qualname__)
    cls.logger_error = logging.getLogger("error." + cls.__qualname__)
    cls.logger_audit = logging.getLogger("audit." + cls.__qualname__)

    return cls
