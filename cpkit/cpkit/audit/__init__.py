"""Generic audit record types and service helpers."""

from .legacy import emit_legacy_event_best_effort, write_legacy_event
from .service import AuditService
from .types import AuditOutcome, AuditRecordCreate

__all__ = [
    "AuditOutcome",
    "AuditRecordCreate",
    "AuditService",
    "emit_legacy_event_best_effort",
    "write_legacy_event",
]
