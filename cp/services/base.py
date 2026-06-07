"""Shared service-layer helpers."""

import logging
from typing import Any

from cpkit.audit import emit_legacy_event_best_effort

from ..models import AuditEvent, LogMsg
from ..repos import Repo

logger = logging.getLogger(__name__)


def log_event(
    repo: Repo,
    actor_id: str,
    action: AuditEvent | str,
    details: dict[str, Any] | None = None,
) -> None:
    """Best-effort audit logging for service-layer actions."""
    from ..main import request_id_ctx

    emit_legacy_event_best_effort(
        repo,
        LogMsg(
            user_id=actor_id,
            action=str(action),
            details=details,
            request_id=request_id_ctx.get(),
        ),
        event_type=str(action),
        event_logger=logger,
    )
