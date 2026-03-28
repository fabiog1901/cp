from typing import Any

from fastapi import Depends, Request, Security
from fastapi.security import APIKeyCookie, APIKeyHeader

from ..infra import get_repo
from ..models import CPRole
from ..repos.base import BaseRepo
from .common import claims_groups
from .oidc import oidc

cookie_scheme = APIKeyCookie(name=oidc.config.session_cookie_name, auto_error=False)
access_key_scheme = APIKeyHeader(
    name="X-CP-Access-Key",
    scheme_name="XAccessKey",
    auto_error=False,
)
signature_scheme = APIKeyHeader(
    name="X-CP-Signature",
    scheme_name="XSignature",
    auto_error=False,
)
timestamp_scheme = APIKeyHeader(
    name="X-Timestamp",
    scheme_name="XTimestamp",
    auto_error=False,
)


async def require_authenticated(
    request: Request,
    repo: BaseRepo = Depends(get_repo),
    session_token: str | None = Security(cookie_scheme),
    access_key: str | None = Security(access_key_scheme),
    signature: str | None = Security(signature_scheme),
    timestamp: str | None = Security(timestamp_scheme),
) -> dict[str, Any]:
    """Return claims for the current caller, regardless of auth transport."""
    return await oidc.current_claims(
        request,
        repo,
        session_token=session_token,
        access_key=access_key,
        signature=signature,
        timestamp=timestamp,
    )


def require_user(
    claims: dict[str, Any] = Security(require_authenticated),
) -> dict[str, Any]:
    """Require a role that permits mutating compute-unit operations."""
    return oidc.ensure_any_role(claims, CPRole.CP_USER, CPRole.CP_ADMIN)


def require_readonly(
    request: Request,
    claims: dict[str, Any] = Security(require_authenticated),
) -> dict[str, Any]:
    """Allow read-only users on GET, and require user/admin on write operations."""
    if request.method.upper() == "GET":
        return oidc.ensure_any_role(
            claims,
            CPRole.CP_READONLY,
            CPRole.CP_USER,
            CPRole.CP_ADMIN,
        )
    return oidc.ensure_any_role(claims, CPRole.CP_USER, CPRole.CP_ADMIN)


def require_admin(
    claims: dict[str, Any] = Security(require_authenticated),
) -> dict[str, Any]:
    """Require the admin role."""
    return oidc.ensure_any_role(claims, CPRole.CP_ADMIN)


def get_access_scope(claims: dict[str, Any]) -> tuple[list[str], bool]:
    """Return normalized caller groups plus whether the caller has CP_ADMIN."""
    groups_claim_name = str(
        claims.get("_groups_claim_name", oidc.config.groups_claim_name)
    )
    groups = sorted(claims_groups(claims, groups_claim_name))

    effective_roles = (
        claims.get("_role_groups")
        if isinstance(claims.get("_role_groups"), dict)
        else oidc.config.role_groups
    )
    admin_role_groups = effective_roles.get(CPRole.CP_ADMIN, set())
    is_admin = bool(admin_role_groups) and not admin_role_groups.isdisjoint(groups)

    return groups, is_admin


def get_audit_actor(
    claims: dict[str, Any] = Security(require_authenticated),
) -> str:
    """Return the identifier that should be written into audit logs."""
    if claims.get("auth_type") == "api_key":
        return str(claims.get("access_key") or "anonymous")

    username = claims.get(oidc.config.ui_username_claim) or claims.get("sub")
    return str(username or "anonymous")
