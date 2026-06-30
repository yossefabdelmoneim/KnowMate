"""Logging setup.

Single `setup_logging()` call at app startup configures the root logger
once. Everything else just calls `logging.getLogger(__name__)` and gets
a consistently-formatted logger for free.
"""

from __future__ import annotations

import logging
import sys

from app.Back_End.core.config import settings

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Quiet down noisy third-party loggers that aren't useful at INFO level
# (urllib3 connection pool chatter on every Ollama call, sqlalchemy
# echo if accidentally left on, etc.).
_NOISY_LOGGERS = ("urllib3", "httpx", "httpcore", "asyncio", "matplotlib")


def setup_logging() -> None:
    """Configure root logging once at application startup.

    Safe to call multiple times (e.g. in tests) — clears existing
    handlers first to avoid duplicate log lines from repeated setup.
    """
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    root_logger.addHandler(handler)

    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)
