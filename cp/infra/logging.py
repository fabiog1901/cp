"""Logging configuration for operational messages."""

import logging
import sys
import time

from ..models import SettingKey
from .util import RequestIDFilter, ShorthandFormatter


def configure_logging(repo=None, *, force: bool = False) -> None:
    """Configure app logging with journald when available."""

    if getattr(configure_logging, "_configured", False) and not force:
        return

    if repo is None:
        level_name = "INFO"
        journald_identifier = "cp"
    else:
        level_name = repo.get_setting(SettingKey.logging_level).value.upper()
        journald_identifier = repo.get_setting(
            SettingKey.logging_journald_identifier
        ).value
    level = getattr(logging, level_name, logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    logging.getLogger("uvicorn").setLevel(logging.ERROR)
    logging.getLogger("uvicorn.access").setLevel(logging.ERROR)

    if force:
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass
    elif root_logger.handlers:
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

        handler = JournalHandler(SYSLOG_IDENTIFIER=journald_identifier)
    except Exception:
        handler = logging.StreamHandler()

    handler.addFilter(RequestIDFilter())
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    configure_logging._configured = True
