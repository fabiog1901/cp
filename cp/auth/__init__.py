"""CP's cpkit OIDC integration.

The framework owns the OIDC flow, API-key authentication headers, FastAPI
dependencies, and `/auth` routes. CP supplies only application-specific wiring:
the repository dependency, session record model, secret crypto helpers, role
names, audit event persistence, and the browser session cookie name.
"""

from typing import Any

from cpkit.audit import AuditRecorder
from cpkit.auth import (
    OIDC_NEXT_COOKIE_NAME,
    OIDC_NONCE_COOKIE_NAME,
    OIDC_STATE_COOKIE_NAME,
    OIDCConfig,
    OIDCManager as CpkitOIDCManager,
    access_key_scheme,
    api_key_signature,
    build_api_key_signature_payload,
    claim_groups,
    claims_groups,
    create_auth_dependencies,
    create_oidc_router,
    jsonable_role_groups,
    parse_api_key_timestamp,
    request_target_bytes,
    signature_scheme,
    timestamp_scheme,
)

from ..audit import build_log_msg
from ..infra import decrypt_secret, encrypt_secret, get_repo, request_id_ctx
from ..infra import validate_secret_crypto_config
from ..models import AuditEvent, CPRole, OIDCSessionRecord
from ..repos import Repo

OIDC_SESSION_COOKIE_NAME = "cp_session"


class OIDCManager(CpkitOIDCManager):
    """Configure CP-specific dependencies for cpkit OIDC auth."""

    def __init__(self) -> None:
        super().__init__(
            encrypt_secret=encrypt_secret,
            decrypt_secret=decrypt_secret,
            session_record_factory=OIDCSessionRecord,
            session_cookie_name=OIDC_SESSION_COOKIE_NAME,
            validate_secret_crypto_config=validate_secret_crypto_config,
            missing_api_key_headers_detail=(
                "X-CP-Access-Key, X-CP-Signature, and X-Timestamp are required."
            ),
        )


oidc = OIDCManager()

_auth_dependencies = create_auth_dependencies(
    oidc,
    get_repo=get_repo,
    session_cookie_name=OIDC_SESSION_COOKIE_NAME,
    readonly_roles=(CPRole.CP_READONLY,),
    user_roles=(CPRole.CP_USER, CPRole.CP_ADMIN),
    admin_roles=(CPRole.CP_ADMIN,),
)

require_authenticated = _auth_dependencies.require_authenticated
require_user = _auth_dependencies.require_user
require_readonly = _auth_dependencies.require_readonly
require_admin = _auth_dependencies.require_admin
get_access_scope = _auth_dependencies.get_access_scope
get_audit_actor = _auth_dependencies.get_audit_actor


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

__all__ = [
    "OIDC_NEXT_COOKIE_NAME",
    "OIDC_NONCE_COOKIE_NAME",
    "OIDC_SESSION_COOKIE_NAME",
    "OIDC_STATE_COOKIE_NAME",
    "OIDCConfig",
    "OIDCManager",
    "access_key_scheme",
    "api_key_signature",
    "build_api_key_signature_payload",
    "claim_groups",
    "claims_groups",
    "get_access_scope",
    "get_audit_actor",
    "jsonable_role_groups",
    "oidc",
    "parse_api_key_timestamp",
    "require_admin",
    "require_authenticated",
    "require_readonly",
    "require_user",
    "request_target_bytes",
    "router",
    "signature_scheme",
    "timestamp_scheme",
]
