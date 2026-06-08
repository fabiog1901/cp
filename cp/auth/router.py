"""CP auth router wiring."""

from typing import Any

from cpkit.audit import AuditRecorder
from cpkit.auth import create_oidc_router

from ..audit import build_log_msg
from ..infra import get_repo, request_id_ctx
from ..models import AuditEvent
from ..repos import Repo
from .dependencies import get_audit_actor, require_authenticated
from .oidc import oidc


def log_auth_event(
    repo: Repo,
    actor_id: str,
    action: str,
    details: dict[str, Any] | None = None,
) -> None:
    """Persist a login or logout event using the current request id context."""
    AuditRecorder(
        repo,
        lambda **kwargs: build_log_msg(**kwargs, default_metadata={}),
        request_id_provider=request_id_ctx.get,
    ).emit(
        AuditEvent(action),
        actor_id=actor_id,
        metadata=details,
    )


router = create_oidc_router(
    oidc,
    get_repo=get_repo,
    require_authenticated=require_authenticated,
    get_audit_actor=get_audit_actor,
    audit_event_hook=log_auth_event,
)
