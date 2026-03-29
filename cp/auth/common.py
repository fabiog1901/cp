import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from hmac import new as hmac_new
from typing import Any

from fastapi import Request

from ..infra import as_bool, safe_csv_set, safe_json_string_dict
from ..models import CPRole


def claim_groups(claim_value: Any) -> set[str]:
    """Normalize a groups claim into a trimmed set of group names."""
    if claim_value is None:
        return set()
    if isinstance(claim_value, str):
        return (
            safe_csv_set(claim_value)
            if "," in claim_value
            else ({claim_value.strip()} if claim_value.strip() else set())
        )
    if isinstance(claim_value, (list, tuple, set)):
        return {str(v).strip() for v in claim_value if str(v).strip()}
    return set()


def claims_groups(
    claims: dict[str, Any], groups_claim_name: str = "groups"
) -> set[str]:
    """Extract the configured groups claim from a JWT or synthetic claims payload."""
    return claim_groups(claims.get(groups_claim_name))


def jsonable_role_groups(role_groups: dict[str, Any]) -> dict[str, list[str]]:
    """Convert role-to-groups mappings into JSON-friendly sorted lists."""
    normalized: dict[str, list[str]] = {}
    for role_name, groups in role_groups.items():
        normalized[str(role_name)] = sorted(claim_groups(groups))
    return normalized


def cookie_secure_default() -> bool:
    """Return the configured secure-cookie default for OIDC session cookies."""
    return as_bool(os.getenv("OIDC_COOKIE_SECURE"), default=False)


def api_key_signature_ttl_seconds() -> int:
    """Return the maximum allowed age for signed API key requests."""
    try:
        return max(0, int(os.getenv("API_KEY_SIGNATURE_TTL_SECONDS", "300")))
    except ValueError:
        return 300


def parse_api_key_timestamp(timestamp: str) -> datetime:
    """Parse either epoch seconds or an ISO-8601 timestamp into UTC."""
    raw_timestamp = timestamp.strip()
    if not raw_timestamp:
        raise ValueError("empty timestamp")

    try:
        parsed = datetime.fromtimestamp(float(raw_timestamp), tz=timezone.utc)
    except (OSError, OverflowError, ValueError):
        normalized = (
            f"{raw_timestamp[:-1]}+00:00"
            if raw_timestamp.endswith("Z")
            else raw_timestamp
        )
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        else:
            parsed = parsed.astimezone(timezone.utc)

    return parsed


def request_target_bytes(request: Request) -> bytes:
    """Return the exact path and query bytes that are covered by the request signature."""
    raw_path = request.scope.get("raw_path")
    if isinstance(raw_path, bytes) and raw_path:
        path = raw_path
    else:
        path = request.url.path.encode("utf-8")

    query_string = request.scope.get("query_string")
    if isinstance(query_string, bytes) and query_string:
        return path + b"?" + query_string
    return path


def build_api_key_signature_payload(
    request: Request, timestamp: str, body: bytes
) -> bytes:
    """Build the canonical payload used for HMAC request signing."""
    return b"\n".join(
        [
            request.method.upper().encode("utf-8"),
            request_target_bytes(request),
            timestamp.strip().encode("utf-8"),
            body,
        ]
    )


def api_key_signature(
    secret_key: bytes, request: Request, timestamp: str, body: bytes
) -> str:
    """Return the expected HMAC signature for an API-key-authenticated request."""
    return hmac_new(
        secret_key,
        build_api_key_signature_payload(request, timestamp, body),
        sha256,
    ).hexdigest()


@dataclass(frozen=True)
class OIDCConfig:
    """Configuration derived from environment variables for OIDC login and authz."""

    enabled: bool = field(
        default_factory=lambda: as_bool(os.getenv("OIDC_ENABLED"), default=False)
    )
    issuer_url: str = field(
        default_factory=lambda: os.getenv("OIDC_ISSUER_URL", "").strip().rstrip("/")
    )
    client_id: str = field(
        default_factory=lambda: os.getenv("OIDC_CLIENT_ID", "").strip()
    )
    client_secret: str = field(
        default_factory=lambda: os.getenv("OIDC_CLIENT_SECRET", "").strip()
    )
    scopes: str = field(
        default_factory=lambda: os.getenv("OIDC_SCOPES", "openid profile email").strip()
    )
    audience: str = field(
        default_factory=lambda: os.getenv("OIDC_AUDIENCE", "").strip()
    )
    extra_auth_params_raw: str = field(
        default_factory=lambda: os.getenv("OIDC_EXTRA_AUTH_PARAMS", "{}")
    )
    redirect_uri: str = field(
        default_factory=lambda: os.getenv("OIDC_REDIRECT_URI", "").strip()
    )
    login_path: str = field(
        default_factory=lambda: os.getenv("OIDC_LOGIN_PATH", "/api/auth/login").strip()
    )
    session_cookie_name: str = field(
        default_factory=lambda: os.getenv(
            "OIDC_SESSION_COOKIE_NAME", "cp_session"
        ).strip()
    )
    state_cookie_name: str = field(
        default_factory=lambda: os.getenv(
            "OIDC_STATE_COOKIE_NAME", "cp_oidc_state"
        ).strip()
    )
    nonce_cookie_name: str = field(
        default_factory=lambda: os.getenv(
            "OIDC_NONCE_COOKIE_NAME", "cp_oidc_nonce"
        ).strip()
    )
    next_cookie_name: str = field(
        default_factory=lambda: os.getenv(
            "OIDC_NEXT_COOKIE_NAME", "cp_oidc_next"
        ).strip()
    )
    cookie_secure: bool = field(default_factory=cookie_secure_default)
    cookie_samesite: str = field(
        default_factory=lambda: os.getenv("OIDC_COOKIE_SAMESITE", "lax").strip().lower()
    )
    cookie_domain: str | None = field(
        default_factory=lambda: os.getenv("OIDC_COOKIE_DOMAIN")
    )
    verify_audience: bool = field(
        default_factory=lambda: as_bool(
            os.getenv("OIDC_VERIFY_AUDIENCE"), default=False
        )
    )
    ui_username_claim: str = field(
        default_factory=lambda: os.getenv(
            "OIDC_UI_USERNAME_CLAIM", "preferred_username"
        ).strip()
    )
    readonly_groups_raw: str = field(
        default_factory=lambda: os.getenv("OIDC_AUTHZ_READONLY_GROUPS", "")
    )
    user_groups_raw: str = field(
        default_factory=lambda: os.getenv("OIDC_AUTHZ_USER_GROUPS", "")
    )
    admin_groups_raw: str = field(
        default_factory=lambda: os.getenv("OIDC_AUTHZ_ADMIN_GROUPS", "")
    )
    groups_claim_name: str = field(
        default_factory=lambda: os.getenv("OIDC_AUTHZ_GROUPS_CLAIM", "groups").strip()
    )

    @property
    def role_groups(self) -> dict[CPRole, set[str]]:
        """Map each application role to the configured OIDC groups that grant it."""
        return {
            CPRole.CP_READONLY: safe_csv_set(self.readonly_groups_raw),
            CPRole.CP_USER: safe_csv_set(self.user_groups_raw),
            CPRole.CP_ADMIN: safe_csv_set(self.admin_groups_raw),
        }

    @property
    def authorized_groups(self) -> set[str]:
        """Return the union of all OIDC groups allowed to access the application."""
        role_groups = self.role_groups
        if not role_groups:
            return set()
        groups: set[str] = set()
        for values in role_groups.values():
            groups.update(values)
        return groups

    def validate(self) -> None:
        """Validate startup configuration before the app begins serving requests."""
        if not self.enabled:
            return

        missing = []
        if not self.issuer_url:
            missing.append("OIDC_ISSUER_URL")
        if not self.client_id:
            missing.append("OIDC_CLIENT_ID")
        if not self.client_secret:
            missing.append("OIDC_CLIENT_SECRET")

        if missing:
            raise RuntimeError(
                f"OIDC is enabled but missing required env vars: {', '.join(missing)}"
            )

        if self.cookie_samesite not in {"lax", "strict", "none"}:
            raise RuntimeError("OIDC_COOKIE_SAMESITE must be one of: lax, strict, none")

        if self.cookie_samesite == "none" and not self.cookie_secure:
            raise RuntimeError(
                "OIDC_COOKIE_SECURE must be true when OIDC_COOKIE_SAMESITE=none"
            )

        if not self.ui_username_claim:
            raise RuntimeError(
                "OIDC_UI_USERNAME_CLAIM must be set when OIDC is enabled"
            )

        if not self.groups_claim_name:
            raise RuntimeError(
                "OIDC_AUTHZ_GROUPS_CLAIM must be set when OIDC is enabled"
            )

        if not self.authorized_groups:
            raise RuntimeError(
                "At least one of OIDC_AUTHZ_READONLY_GROUPS, OIDC_AUTHZ_USER_GROUPS, OIDC_AUTHZ_ADMIN_GROUPS must include a group when OIDC is enabled"
            )

        self.extra_auth_params()

    def extra_auth_params(self) -> dict[str, str]:
        """Return extra authorization request parameters as a string dictionary."""
        try:
            return safe_json_string_dict(self.extra_auth_params_raw, default={})
        except ValueError as exc:
            raise ValueError("OIDC_EXTRA_AUTH_PARAMS must be a JSON object") from exc
