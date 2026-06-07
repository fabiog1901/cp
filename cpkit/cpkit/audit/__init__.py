"""Generic audit record types and service helpers."""

from .recorder import (
    AuditRecorder,
    AuditRecordWriter,
    write_audit_record,
    write_audit_record_best_effort,
)
from .service import AuditService
from .types import AuditOutcome, AuditRecordCreate

__all__ = [
    "AuditOutcome",
    "AuditRecorder",
    "AuditRecordCreate",
    "AuditRecordWriter",
    "AuditService",
    "write_audit_record",
    "write_audit_record_best_effort",
]
