"""Settings go here"""
import os
from pathlib import Path
import sys
import uuid

BASE_DIR = Path(__file__).parent

DEBUG = os.environ.get("CPM_DEBUG", False)

# client settings
RETRIES = 3
URL = (
    "https://moistcat.pythonanywhere.com/"
    if DEBUG is False
    else "http://localhost:5050/"
)
ITEM_SCHEME = {
    "name": "",
    "deps": [],
    "tags": [],
    "image": "",
    "desc": "",
    "file": "",
    "service": "NAI",
    "date_created": "",
    "date_updated": "",
}

# secrets
def get_keys():
    """Get the auth token of the user from a file"""
    try:
        with open(BASE_DIR / "token.key") as file:
            token = file.read()
    except FileNotFoundError:
        token = str(uuid.uuid4())
        with open(BASE_DIR / "token.key", "w") as file:
            file.write(token)
    return token


# logger settings
LOG_FILE = BASE_DIR / "logs/client.audit"
ERROR_FILE = BASE_DIR / "logs/client.error"
LOGGERS = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stderr,
            "formatter": "basic",
        },
        "audit_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 5000000,
            "backupCount": 1,
            "filename": LOG_FILE,
            "encoding": "utf-8",
            "formatter": "basic",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 5000000,
            "backupCount": 1,
            "filename": ERROR_FILE,
            "encoding": "utf-8",
            "formatter": "basic",
        },
    },
    "formatters": {
        "basic": {
            "style": "{",
            "format": "{asctime:s} [{levelname:s}] -- {name:s}: {message:s}",
        }
    },
    "loggers": {
        "user_info": {
            "handlers": ("console",),
            "level": "INFO" if DEBUG is False else "DEBUG",
        },
        "error": {"handlers": ("error_file",), "level": "ERROR"},
        "audit": {"handlers": ("audit_file",), "level": "DEBUG"},
    },
}
