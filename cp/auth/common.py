from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from hmac import new as hmac_new
from typing import Any

from fastapi import Request

from ..infra import as_bool, safe_csv_set, safe_json_string_dict
from ..models import CPRole, SettingKey
from ..repos.base import BaseRepo

OIDC_SESSION_COOKIE_NAME = "cp_session"
OIDC_STATE_COOKIE_NAME = "cp_oidc_state"
OIDC_NONCE_COOKIE_NAME = "cp_oidc_nonce"
OIDC_NEXT_COOKIE_NAME = "cp_oidc_next"


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


def parse_api_key_timestamp(timestamp: str) -> datetime:
    """Parse either epoch seconds or an ISO-8601 timestamp into UTC."""
    raw_timestamp = timestamp.strip()
    if not raw_timestamp:
        raise ValueError("empty timestamp")

    try:
        parsed = datetime.fromtimestamp(float(raw_timestamp), tz=timezone.utc)
    except OSError, OverflowError, ValueError:
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
    """Configuration derived from settings for OIDC login and authz."""

    enabled: bool = False
    issuer_url: str = ""
    client_id: str = ""
    client_secret: str = ""
    scopes: str = "openid profile email offline_access"
    audience: str = ""
    extra_auth_params_raw: str = "{}"
    redirect_uri: str = ""
    login_path: str = "/api/auth/login"
    session_max_age_seconds: int = 2592000
    refresh_leeway_seconds: int = 60
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    cookie_domain: str | None = None
    verify_audience: bool = False
    ui_username_claim: str = "preferred_username"
    readonly_groups_raw: str = ""
    user_groups_raw: str = ""
    admin_groups_raw: str = ""
    groups_claim_name: str = "groups"
    cache_ttl_seconds: int = 300
    api_key_signature_ttl_seconds: int = 300

    @classmethod
    def from_repo(cls, repo: BaseRepo) -> "OIDCConfig":
        settings = {setting.key: setting for setting in repo.list_settings()}
        enabled = as_bool(settings[SettingKey.oidc_enabled].value, default=False)
        if not enabled:
            return cls(
                enabled=False,
                cache_ttl_seconds=int(
                    settings[SettingKey.oidc_cache_ttl_seconds].value
                ),
                api_key_signature_ttl_seconds=int(
                    settings[SettingKey.auth_api_key_signature_ttl_seconds].value
                ),
            )

        return cls(
            enabled=enabled,
            issuer_url=settings[SettingKey.oidc_issuer_url].value.rstrip("/"),
            client_id=settings[SettingKey.oidc_client_id].value,
            client_secret=settings[SettingKey.oidc_client_secret].value,
            scopes=settings[SettingKey.oidc_scopes].value,
            audience=settings[SettingKey.oidc_audience].value,
            extra_auth_params_raw=settings[SettingKey.oidc_extra_auth_params].value,
            redirect_uri=settings[SettingKey.oidc_redirect_uri].value,
            login_path=settings[SettingKey.oidc_login_path].value,
            session_max_age_seconds=int(
                settings[SettingKey.oidc_session_max_age_seconds].value
            ),
            refresh_leeway_seconds=int(
                settings[SettingKey.oidc_refresh_leeway_seconds].value
            ),
            cookie_secure=as_bool(
                settings[SettingKey.oidc_cookie_secure].value,
                default=False,
            ),
            cookie_samesite=settings[SettingKey.oidc_cookie_samesite].value.lower(),
            cookie_domain=settings[SettingKey.oidc_cookie_domain].value or None,
            verify_audience=as_bool(
                settings[SettingKey.oidc_verify_audience].value,
                default=False,
            ),
            ui_username_claim=settings[SettingKey.oidc_ui_username_claim].value,
            readonly_groups_raw=settings[SettingKey.oidc_authz_readonly_groups].value,
            user_groups_raw=settings[SettingKey.oidc_authz_user_groups].value,
            admin_groups_raw=settings[SettingKey.oidc_authz_admin_groups].value,
            groups_claim_name=settings[SettingKey.oidc_authz_groups_claim].value,
            cache_ttl_seconds=int(settings[SettingKey.oidc_cache_ttl_seconds].value),
            api_key_signature_ttl_seconds=int(
                settings[SettingKey.auth_api_key_signature_ttl_seconds].value
            ),
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
            missing.append("oidc_issuer_url")
        if not self.client_id:
            missing.append("oidc_client_id")
        if not self.client_secret:
            missing.append("oidc_client_secret")

        if missing:
            raise RuntimeError(
                f"OIDC is enabled but missing required settings: {', '.join(missing)}"
            )

        if self.cookie_samesite not in {"lax", "strict", "none"}:
            raise RuntimeError("oidc_cookie_samesite must be one of: lax, strict, none")

        if self.cookie_samesite == "none" and not self.cookie_secure:
            raise RuntimeError(
                "oidc_cookie_secure must be true when oidc_cookie_samesite=none"
            )

        if not self.ui_username_claim:
            raise RuntimeError(
                "oidc_ui_username_claim must be set when OIDC is enabled"
            )

        if not self.groups_claim_name:
            raise RuntimeError(
                "oidc_authz_groups_claim must be set when OIDC is enabled"
            )

        if not self.authorized_groups:
            raise RuntimeError(
                "At least one of oidc_authz_readonly_groups, oidc_authz_user_groups, oidc_authz_admin_groups must include a group when OIDC is enabled"
            )

        self.extra_auth_params()

    def extra_auth_params(self) -> dict[str, str]:
        """Return extra authorization request parameters as a string dictionary."""
        try:
            return safe_json_string_dict(self.extra_auth_params_raw, default={})
        except ValueError as exc:
            raise ValueError("oidc_extra_auth_params must be a JSON object") from exc
