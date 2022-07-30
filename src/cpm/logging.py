"""Logging methods"""
from typing import Callable
import logging
import logging.config

from cpm import settings

if settings.DEBUG is True:
    settings.LOGGERS["handlers"]["audit_file"] = settings.LOGGERS["handlers"]["console"]
logging.config.dictConfig(settings.LOGGERS)

def get_logger(name="audit.root"):
    return logging.getLogger(name)

def logged(cls) -> Callable:
    """Decorator to log certain methods of each class while giving
    each clas its own logger."""
    cls.logger = logging.getLogger("user_info." + cls.__qualname__)
    cls.logger_error = logging.getLogger("error." + cls.__qualname__)
    logger_audit = logging.getLogger("audit." + cls.__qualname__)
    cls.logger_audit = logger_audit

    def _log_mirror(self, *args, **kwargs):
        logging.Logger._log(self, *args, **kwargs)
        logger_audit._log(*args, **kwargs)
    cls.logger_mirror = cls.logger
    cls.logger_mirror._log = _log_mirror.__get__(cls.logger, logging.Logger)

    return cls
