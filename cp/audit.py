"""CP-specific audit record construction helpers."""

from typing import Any

from .models import LogMsg


def build_log_msg(
    *,
    actor_id: str,
    event_type: str,
    metadata: dict[str, Any] | None,
    request_id: str | None,
    default_metadata: dict[str, Any] | None = None,
) -> LogMsg:
    return LogMsg(
        user_id=actor_id,
        action=event_type,
        details=metadata if metadata is not None else default_metadata,
        request_id=request_id,
    )
