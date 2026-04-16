import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Security
from fastapi.responses import RedirectResponse

from ..infra import get_repo, request_id_ctx, safe_next_path
from ..models import AuditEvent, LogMsg
from ..repos.base import BaseRepo
from .dependencies import get_audit_actor, require_authenticated
from .oidc import oidc

router = APIRouter(prefix="/auth", tags=["auth"])


def oidc_cookie_kwargs() -> dict[str, Any]:
    """Return the shared cookie settings used across the OIDC browser flow."""
    return {
        "httponly": True,
        "secure": oidc.config.cookie_secure,
        "samesite": oidc.config.cookie_samesite,
        "domain": oidc.config.cookie_domain,
        "path": "/",
    }


def log_auth_event(
    repo: BaseRepo,
    actor_id: str,
    action: AuditEvent,
    details: dict[str, Any] | None = None,
) -> None:
    """Persist a login or logout event using the current request id context."""
    repo.log_event(
        LogMsg(
            user_id=actor_id,
            action=str(action),
            details=details or {},
            request_id=request_id_ctx.get(),
        )
    )


@router.get("/login")
def oidc_login(request: Request, next: str = "/"):  # noqa: A002
    """Start the browser OIDC login flow and store anti-CSRF cookies."""
    if not oidc.enabled:
        raise HTTPException(
            status_code=404,
            detail="OIDC is disabled.",
        )

    state = secrets.token_urlsafe(24)
    nonce = secrets.token_urlsafe(24)
    next_path = safe_next_path(next)
    redirect_uri = oidc.config.redirect_uri or str(request.url_for("oidc_callback"))
    auth_url = oidc.build_authorization_url(redirect_uri, state, nonce)

    resp = RedirectResponse(auth_url, status_code=302)
    cookie_kwargs = oidc_cookie_kwargs()
    resp.set_cookie(oidc.config.state_cookie_name, state, max_age=300, **cookie_kwargs)
    resp.set_cookie(oidc.config.nonce_cookie_name, nonce, max_age=300, **cookie_kwargs)
    resp.set_cookie(
        oidc.config.next_cookie_name, next_path, max_age=300, **cookie_kwargs
    )
    return resp


@router.get("/callback", name="oidc_callback")
def oidc_callback(
    request: Request,
    repo: BaseRepo = Depends(get_repo),
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
):
    """Finish the OIDC login flow, validate the ID token, and set the session cookie."""
    if not oidc.enabled:
        raise HTTPException(
            status_code=404,
            detail="OIDC is disabled.",
        )

    if error:
        desc = error_description or "OIDC authorization failed."
        raise HTTPException(status_code=401, detail=f"{error}: {desc}")

    expected_state = request.cookies.get(oidc.config.state_cookie_name)
    expected_nonce = request.cookies.get(oidc.config.nonce_cookie_name)
    next_path = safe_next_path(request.cookies.get(oidc.config.next_cookie_name))

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")
    if not state or not expected_state or state != expected_state:
        raise HTTPException(status_code=401, detail="Invalid OIDC state.")
    if not expected_nonce:
        raise HTTPException(status_code=401, detail="Missing OIDC nonce.")

    redirect_uri = oidc.config.redirect_uri or str(request.url_for("oidc_callback"))
    token_payload = oidc.exchange_code(code, redirect_uri)

    id_token = token_payload.get("id_token")
    if not id_token or not isinstance(id_token, str):
        raise HTTPException(
            status_code=401, detail="Token endpoint response missing id_token."
        )
    refresh_token = token_payload.get("refresh_token")
    refresh_token_value = (
        refresh_token if isinstance(refresh_token, str) and refresh_token else None
    )

    claims = oidc.validate_jwt(
        id_token,
        expected_nonce=expected_nonce,
        strict_client_audience=True,
    )
    oidc.ensure_authorized(claims)
    session_id = secrets.token_urlsafe(32)
    repo.create_oidc_session(
        oidc.build_session_record(
            session_id,
            id_token=id_token,
            refresh_token=refresh_token_value,
            claims=claims,
        )
    )
    actor_id = str(claims.get(oidc.config.ui_username_claim) or claims.get("sub"))
    log_auth_event(
        repo,
        actor_id,
        AuditEvent.LOGIN,
        {
            "auth_type": "oidc",
            "refresh_token_present": bool(refresh_token_value),
        },
    )

    resp = RedirectResponse(next_path, status_code=302)
    cookie_kwargs = oidc_cookie_kwargs()
    resp.set_cookie(
        oidc.config.session_cookie_name,
        session_id,
        max_age=oidc.config.session_max_age_seconds,
        **cookie_kwargs,
    )
    resp.delete_cookie(
        oidc.config.state_cookie_name, path="/", domain=oidc.config.cookie_domain
    )
    resp.delete_cookie(
        oidc.config.nonce_cookie_name, path="/", domain=oidc.config.cookie_domain
    )
    resp.delete_cookie(
        oidc.config.next_cookie_name, path="/", domain=oidc.config.cookie_domain
    )
    return resp


@router.post("/logout")
def oidc_logout(
    repo: BaseRepo = Depends(get_repo),
    actor_id: str = Depends(get_audit_actor),
    claims: dict[str, Any] = Security(require_authenticated),
):
    """Clear the OIDC session cookie and write a logout audit event."""
    session_id = str(claims.get("_session_id") or "").strip()
    if session_id:
        repo.delete_oidc_session(session_id)
    log_auth_event(
        repo,
        actor_id,
        AuditEvent.LOGOUT,
        {"auth_type": str(claims.get("auth_type") or "oidc")},
    )
    resp = Response(status_code=204)
    resp.delete_cookie(
        oidc.config.session_cookie_name, path="/", domain=oidc.config.cookie_domain
    )
    return resp


@router.get("/me")
def oidc_me(
    request: Request, claims: dict[str, Any] = Security(require_authenticated)
) -> dict[str, Any]:
    """Return the current caller's claims plus CP-specific auth metadata."""
    payload = oidc.enrich_claims(claims)
    payload["cookies"] = request.cookies
    return payload
