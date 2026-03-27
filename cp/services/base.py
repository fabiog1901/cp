"""Shared service-layer helpers."""

import logging
from typing import Any

from ..models import LogMsg
from ..repos.base import BaseRepo

logger = logging.getLogger(__name__)


def log_event(
    repo: BaseRepo,
    actor_id: str,
    action: Any,
    details: dict[str, Any] | None = None,
) -> None:
    """Best-effort audit logging for service-layer actions."""
    from ..main import request_id_ctx

    try:
        repo.log_event(
            LogMsg(
                user_id=actor_id,
                action=str(action),
                details=details,
                request_id=request_id_ctx.get(),
            )
        )
    except Exception:
        logger.exception("Failed to write audit event %s", action)
