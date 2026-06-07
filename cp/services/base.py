"""Shared service-layer helpers."""

import logging
from typing import Any

from cpkit.audit import AuditRecorder

from ..models import AuditEvent, LogMsg
from ..repos import Repo

logger = logging.getLogger(__name__)


def _build_log_msg(
    *,
    actor_id: str,
    event_type: str,
    metadata: dict[str, Any] | None,
    request_id: str | None,
) -> LogMsg:
    return LogMsg(
        user_id=actor_id,
        action=event_type,
        details=metadata,
        request_id=request_id,
    )


def log_event(
    repo: Repo,
    actor_id: str,
    action: AuditEvent | str,
    details: dict[str, Any] | None = None,
) -> None:
    """Best-effort audit logging for service-layer actions."""
    from ..main import request_id_ctx

    AuditRecorder(
        repo,
        _build_log_msg,
        request_id_provider=request_id_ctx.get,
        event_logger=logger,
    ).emit_best_effort(
        action,
        actor_id=actor_id,
        metadata=details,
    )
