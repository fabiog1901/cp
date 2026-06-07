"""Audit recording helpers for application-owned audit record models."""

import logging
from collections.abc import Callable
from enum import StrEnum
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class AuditRecordWriter(Protocol):
    """Repository-like object that can persist an application audit record."""

    def log_event(self, record: Any) -> Any: ...


def write_audit_record(
    writer: Any,
    record: Any,
    *,
    method_name: str = "log_event",
) -> Any:
    """Write an application-owned audit record through a repository-like writer."""
    return getattr(writer, method_name)(record)


def write_audit_record_best_effort(
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
        write_audit_record(writer, record, method_name=method_name)
    except Exception:
        active_logger.exception("Failed to write audit event %s", event_type or record)
        return False

    return True


class AuditRecorder:
    """Build and persist application-owned audit records with common mechanics."""

    def __init__(
        self,
        writer: AuditRecordWriter,
        record_factory: Callable[..., Any],
        *,
        request_id_provider: Callable[[], str | None] | None = None,
        method_name: str = "log_event",
        event_logger: logging.Logger | None = None,
    ) -> None:
        self.writer = writer
        self.record_factory = record_factory
        self.request_id_provider = request_id_provider
        self.method_name = method_name
        self.logger = event_logger or logger

    def emit(
        self,
        event_type: str | StrEnum,
        *,
        actor_id: str,
        metadata: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> Any:
        """Create and write an application-owned audit record."""
        record = self._build_record(
            event_type,
            actor_id=actor_id,
            metadata=metadata,
            request_id=request_id,
        )
        return write_audit_record(
            self.writer,
            record,
            method_name=self.method_name,
        )

    def emit_best_effort(
        self,
        event_type: str | StrEnum,
        *,
        actor_id: str,
        metadata: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> bool:
        """Create and write an audit record without failing the caller."""
        record = self._build_record(
            event_type,
            actor_id=actor_id,
            metadata=metadata,
            request_id=request_id,
        )
        return write_audit_record_best_effort(
            self.writer,
            record,
            event_type=str(event_type),
            method_name=self.method_name,
            event_logger=self.logger,
        )

    def _build_record(
        self,
        event_type: str | StrEnum,
        *,
        actor_id: str,
        metadata: dict[str, Any] | None,
        request_id: str | None,
    ) -> Any:
        effective_request_id = request_id
        if effective_request_id is None and self.request_id_provider is not None:
            effective_request_id = self.request_id_provider()

        return self.record_factory(
            actor_id=actor_id,
            event_type=str(event_type),
            metadata=metadata,
            request_id=effective_request_id,
        )
