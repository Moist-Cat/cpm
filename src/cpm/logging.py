"""Logging methods"""
from typing import Callable
import logging
import logging.config

from cpm import settings

if settings.DEBUG:
    settings.LOGGERS["handlers"]["audit_file"] = settings.LOGGERS["handlers"]["console"]
logging.config.dictConfig(settings.LOGGERS)


def get_logger(name="audit.root"):
    return logging.getLogger(name)


def logged(cls) -> Callable:
    """Decorator to log certain methods of each class while giving
    each clas its own logger."""
    logger = logging.getLogger("audit." + cls.__qualname__)
    logger_user = logging.getLogger("user_info." + cls.__qualname__)

    cls.logger = logger
    cls.logger_user = logger_user
    cls.logger_error = logging.getLogger("error." + cls.__qualname__)
    cls.logger_mirror = logging.getLogger("user_info." + cls.__qualname__)

    def _log_mirror(self, *args, **kwargs):
        logging.Logger._log(self, *args, kwargs) # pylint: disable=W0212
        logger._log(*args, **kwargs)# pylint: disable=W0212

    cls.logger_mirror._log = _log_mirror.__get__(logger, logging.Logger) # pylint: disable=E1111,W0212

    return cls
