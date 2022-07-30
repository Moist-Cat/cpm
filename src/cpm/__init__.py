"""
The CPM module
"""
from cpm import settings
from cpm.logging import get_logger

logger = get_logger()

if settings.DEBUG:
    logger.warning("Debug is turned on. All audit logs are being sent to stderr.")
