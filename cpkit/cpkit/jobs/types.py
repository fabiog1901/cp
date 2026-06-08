"""Generic job queue data types."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QueueMessage(BaseModel):
    """Message claimed from the framework queue."""

    msg_id: int
    start_after: datetime
    msg_type: str
    msg_data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    created_by: str
