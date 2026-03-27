"""Logging configuration for operational messages."""

import logging
import os
import sys
import time

from .util import RequestIDFilter, ShorthandFormatter


def configure_logging() -> None:
    """Configure app logging with journald when available."""

    if getattr(configure_logging, "_configured", False):
        return

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    logging.getLogger("uvicorn").setLevel(logging.ERROR)
    logging.getLogger("uvicorn.access").setLevel(logging.ERROR)

    if root_logger.handlers:
        configure_logging._configured = True
        return

    handler: logging.Handler
    formatter = ShorthandFormatter(
        "%(asctime)s [%(levelname)s] [%(request_id)s] %(message)s"
    )
    formatter.converter = time.gmtime
    formatter.default_msec_format = "%s.%06d"

    try:
        if sys.platform != "linux":
            raise RuntimeError("journald unavailable")

        from systemd.journal import JournalHandler

        handler = JournalHandler(
            SYSLOG_IDENTIFIER=os.getenv("JOURNALD_IDENTIFIER", "cp")
        )
    except Exception:
        handler = logging.StreamHandler()

    handler.addFilter(RequestIDFilter())
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    configure_logging._configured = True
