"""Generic audit record types and service helpers."""

from .events_service import AuditEventsService
from .recorder import (
    AuditRecorder,
    AuditRecordWriter,
    write_audit_record,
    write_audit_record_best_effort,
)
from .repository import AuditEventsRepositoryMixin, EVENT_LOG_TABLE
from .router import create_events_router
from .service import AuditService
from .types import (
    AuditEventCountResponse,
    AuditLogRecord,
    AuditOutcome,
    AuditRecordCreate,
)

__all__ = [
    "AuditEventCountResponse",
    "AuditEventsRepositoryMixin",
    "AuditEventsService",
    "AuditLogRecord",
    "AuditOutcome",
    "AuditRecorder",
    "AuditRecordCreate",
    "AuditRecordWriter",
    "AuditService",
    "EVENT_LOG_TABLE",
    "create_events_router",
    "write_audit_record",
    "write_audit_record_best_effort",
]
