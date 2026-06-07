"""Compatibility helpers for applications with existing audit record models."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def write_legacy_event(
    writer: Any,
    record: Any,
    *,
    method_name: str = "log_event",
) -> Any:
    """Write an application-owned audit record through a repository-like writer."""
    return getattr(writer, method_name)(record)


def emit_legacy_event_best_effort(
    writer: Any,
    record: Any,
    *,
    event_type: str | None = None,
    method_name: str = "log_event",
    event_logger: logging.Logger | None = None,
) -> bool:
    """Write an audit record without letting audit failures fail the caller."""
    active_logger = event_logger or logger

    try:
        write_legacy_event(writer, record, method_name=method_name)
    except Exception:
        active_logger.exception("Failed to write audit event %s", event_type or record)
        return False

    return True
