"""Shared service-layer helpers."""

import logging
from typing import Any

from cpkit.audit import AuditRecorder
from cpkit.logging import request_id_ctx

from ..audit import build_log_msg
from ..models import AuditEvent
from ..repos import Repo

logger = logging.getLogger(__name__)


def log_event(
    repo: Repo,
    actor_id: str,
    action: AuditEvent | str,
    details: dict[str, Any] | None = None,
) -> None:
    """Best-effort audit logging for service-layer actions."""
    AuditRecorder(
        repo,
        build_log_msg,
        request_id_provider=request_id_ctx.get,
        event_logger=logger,
    ).emit_best_effort(
        action,
        actor_id=actor_id,
        metadata=details,
    )
