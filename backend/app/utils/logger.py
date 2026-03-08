"""
Centralised logging configuration.

Usage:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Hello from %s", __name__)
"""

import logging
import sys
from app.config import settings


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a pre-configured logger with the application log level."""
    logger = logging.getLogger(name or "threat_intel")

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    return logger
