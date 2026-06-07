"""Generic audit data types."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AuditOutcome(StrEnum):
    REQUESTED = "requested"
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DENIED = "denied"


class AuditRecordCreate(BaseModel):
    event_type: str
    actor_id: str | None = None
    actor_name: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    outcome: AuditOutcome = AuditOutcome.REQUESTED
    metadata: dict[str, Any] = Field(default_factory=dict)
