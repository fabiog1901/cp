"""Logging configuration for operational messages."""

import logging
import os


def configure_logging() -> None:
    """Configure app logging with journald when available."""

    if getattr(configure_logging, "_configured", False):
        return

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if root_logger.handlers:
        configure_logging._configured = True
        return

    handler: logging.Handler
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    try:
        from systemd.journal import JournalHandler

        handler = JournalHandler(
            SYSLOG_IDENTIFIER=os.getenv("JOURNALD_IDENTIFIER", "cp")
        )
    except Exception:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

    root_logger.addHandler(handler)
    configure_logging._configured = True
