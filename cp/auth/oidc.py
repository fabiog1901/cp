"""OIDC client helpers.

This module handles provider discovery, token exchange, ID token validation, and
claim normalization for CP web sessions.
"""

import time
from datetime import datetime, timedelta, timezone
from hmac import compare_digest
from typing import Any

from cpkit.auth import OIDCAuthenticationError, OIDCProviderClient
from fastapi import HTTPException, Request, status

from ..infra import decrypt_secret, encrypt_secret, validate_secret_crypto_config
from ..models import CPRole, OIDCSessionRecord
from ..repos import Repo
from .common import (
    OIDC_SESSION_COOKIE_NAME,
    OIDCConfig,
    api_key_signature,
    claims_groups,
    jsonable_role_groups,
    parse_api_key_timestamp,
)


class OIDCManager(OIDCProviderClient):
    """Coordinate OIDC metadata loading, token validation, and request auth resolution."""

    def __init__(self) -> None:
        super().__init__(OIDCConfig())
        self._config_loaded_at = 0.0
        self._config_cache_ttl_seconds = 300

    @property
    def enabled(self) -> bool:
        """Expose whether OIDC-backed authentication is enabled for the app."""
        return self.config.enabled

    def load_config(self, repo: Repo, *, force: bool = False) -> None:
        now = time.time()
        if (
            not force
            and self._config_loaded_at
            and (now - self._config_loaded_at) < self._config_cache_ttl_seconds
        ):
            return

        new_config = OIDCConfig.from_repo(repo)
        self.update_provider_config(
            new_config,
            clear_cache=self.config != new_config,
        )
        self._config_loaded_at = now

    def validate_config(self, repo: Repo) -> None:
        """Validate auth configuration at startup, including API key crypto settings."""
        self.load_config(repo, force=True)
        self.config.validate()
        validate_secret_crypto_config()

    def validate_jwt(
        self,
        token: str,
        *,
        expected_nonce: str | None = None,
        strict_client_audience: bool = False,
    ) -> dict[str, Any]:
        """Validate a JWT and translate auth failures into FastAPI errors."""
        try:
            return super().validate_jwt(
                token,
                expected_nonce=expected_nonce,
                strict_client_audience=strict_client_audience,
            )
        except OIDCAuthenticationError as exc:
            raise HTTPException(status_code=401, detail=exc.detail) from exc

    @staticmethod
    def token_expires_at(claims: dict[str, Any]) -> datetime:
        """Return a JWT expiration timestamp and translate auth failures."""
        try:
            return OIDCProviderClient.token_expires_at(claims)
        except OIDCAuthenticationError as exc:
            raise HTTPException(status_code=401, detail=exc.detail) from exc

    def build_session_record(
        self,
        session_id: str,
        *,
        id_token: str,
        refresh_token: str | None,
        claims: dict[str, Any],
    ) -> OIDCSessionRecord:
        """Return the encrypted server-side session representation for an OIDC login."""
        now = datetime.now(timezone.utc)
        return OIDCSessionRecord(
            session_id=session_id,
            encrypted_id_token=encrypt_secret(id_token),
            encrypted_refresh_token=(
                encrypt_secret(refresh_token) if refresh_token else None
            ),
            token_expires_at=self.token_expires_at(claims),
            session_expires_at=now
            + timedelta(seconds=self.config.session_max_age_seconds),
        )

    def ensure_authorized(self, claims: dict[str, Any]) -> dict[str, Any]:
        """Ensure the caller belongs to at least one configured application group."""
        if claims.get("auth_disabled"):
            return claims

        groups_claim_name = str(
            claims.get("_groups_claim_name", self.config.groups_claim_name)
        )
        user_groups = claims_groups(claims, groups_claim_name)
        if not user_groups:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: no groups found in claim '{groups_claim_name}'.",
            )

        if self.config.authorized_groups.isdisjoint(user_groups):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: user is not in any allowed group.",
            )

        return claims

    def enrich_claims(self, claims: dict[str, Any]) -> dict[str, Any]:
        """Add CP-specific metadata that helps the webapp render auth state."""
        payload = dict(claims)
        payload["_groups_claim_name"] = str(
            claims.get("_groups_claim_name", self.config.groups_claim_name)
        )
        effective_role_groups = (
            claims.get("_role_groups")
            if isinstance(claims.get("_role_groups"), dict)
            else self.config.role_groups
        )
        payload["_role_groups"] = jsonable_role_groups(effective_role_groups)

        existing_meta = claims.get("_cp") if isinstance(claims.get("_cp"), dict) else {}
        payload["_cp"] = {
            **existing_meta,
            "display_name_claim": self.config.ui_username_claim,
            "session_cookie_name": OIDC_SESSION_COOKIE_NAME,
        }
        return payload

    def ensure_any_role(self, claims: dict[str, Any], *roles: CPRole) -> dict[str, Any]:
        """Ensure the caller has at least one of the requested application roles."""
        if claims.get("auth_disabled"):
            return claims

        groups_claim_name = str(
            claims.get("_groups_claim_name", self.config.groups_claim_name)
        )
        user_groups = claims_groups(claims, groups_claim_name)
        if not user_groups:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: no groups found in claim '{groups_claim_name}'.",
            )

        effective_roles = (
            claims.get("_role_groups")
            if isinstance(claims.get("_role_groups"), dict)
            else self.config.role_groups
        )
        for role in roles:
            role_groups = effective_roles.get(role, set())
            if role_groups and not role_groups.isdisjoint(user_groups):
                return claims

        role_list = ", ".join(role.value for role in roles)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Forbidden: requires one of roles [{role_list}].",
        )

    async def validate_api_key(
        self,
        request: Request,
        repo: Repo,
        access_key: str,
        signature: str,
        timestamp: str,
    ) -> dict[str, Any]:
        """Authenticate an API request using the HMAC-signed API key headers."""
        api_key = repo.get_api_key(access_key)
        if api_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key.",
            )

        if datetime.now(timezone.utc) >= api_key.valid_until:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is expired.",
            )

        try:
            signed_at = parse_api_key_timestamp(timestamp)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid X-Timestamp header.",
            ) from exc

        max_age_seconds = self.config.api_key_signature_ttl_seconds
        age_seconds = abs((datetime.now(timezone.utc) - signed_at).total_seconds())
        if age_seconds > max_age_seconds:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API request timestamp is expired.",
            )

        body = await request.body()
        secret_key = decrypt_secret(api_key.encrypted_secret_access_key)
        expected_signature = api_key_signature(secret_key, request, timestamp, body)

        if not compare_digest(expected_signature, signature.strip().lower()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key signature.",
            )

        roles = set(api_key.roles or [])
        role_groups = {role: {role.value} for role in roles}
        return {
            "sub": api_key.owner,
            "access_key": api_key.access_key,
            "groups": [role.value for role in roles],
            "_groups_claim_name": "groups",
            "_role_groups": role_groups,
            "auth_type": "api_key",
        }

    async def current_claims(
        self,
        request: Request,
        repo: Repo,
        *,
        session_token: str | None = None,
        access_key: str | None = None,
        signature: str | None = None,
        timestamp: str | None = None,
    ) -> dict[str, Any]:
        """Resolve request claims from API-key headers or the OIDC session cookie."""
        if access_key or signature or timestamp:
            if not access_key or not signature or not timestamp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="X-CP-Access-Key, X-CP-Signature, and X-Timestamp are required.",
                )
            return await self.validate_api_key(
                request,
                repo,
                access_key,
                signature,
                timestamp,
            )

        if not self.enabled:
            return {"sub": "anonymous", "auth_disabled": True}

        if session_token:
            return self._claims_from_session(repo, session_token)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
            headers={"X-Auth-Login-Url": self.config.login_path},
        )

    def _claims_from_session(
        self,
        repo: Repo,
        session_id: str,
    ) -> dict[str, Any]:
        """Load a server-side OIDC session, refreshing token material when needed."""
        session = repo.get_oidc_session(session_id)
        if session is None:
            raise self._not_authenticated()

        now = datetime.now(timezone.utc)
        if session.session_expires_at <= now:
            repo.delete_oidc_session(session_id)
            raise self._not_authenticated("OIDC session expired.")

        refresh_deadline = session.token_expires_at - timedelta(
            seconds=self.config.refresh_leeway_seconds
        )
        if refresh_deadline <= now:
            claims = self._refresh_session(repo, session)
        else:
            try:
                id_token = decrypt_secret(session.encrypted_id_token).decode("utf-8")
                claims = self.validate_jwt(id_token, strict_client_audience=True)
            except Exception:
                claims = self._refresh_session(repo, session)

        claims = self.ensure_authorized(claims)
        claims["_session_id"] = session_id
        claims["auth_type"] = "oidc"
        return claims

    def _refresh_session(
        self,
        repo: Repo,
        session: OIDCSessionRecord,
    ) -> dict[str, Any]:
        """Refresh an OIDC session using its stored refresh token."""
        if not session.encrypted_refresh_token:
            repo.delete_oidc_session(session.session_id)
            raise self._not_authenticated("OIDC session expired.")

        try:
            refresh_token = decrypt_secret(session.encrypted_refresh_token).decode(
                "utf-8"
            )
            token_payload = self.refresh_tokens(refresh_token)
        except Exception:
            repo.delete_oidc_session(session.session_id)
            raise self._not_authenticated("OIDC refresh failed. Please sign in again.")

        id_token = token_payload.get("id_token")
        if not id_token or not isinstance(id_token, str):
            repo.delete_oidc_session(session.session_id)
            raise self._not_authenticated(
                "OIDC refresh response missing id_token. Please sign in again."
            )

        claims = self.validate_jwt(id_token, strict_client_audience=True)
        self.ensure_authorized(claims)

        next_refresh_token = token_payload.get("refresh_token")
        effective_refresh_token = (
            next_refresh_token
            if isinstance(next_refresh_token, str) and next_refresh_token
            else refresh_token
        )
        repo.update_oidc_session(
            session.session_id,
            encrypted_id_token=encrypt_secret(id_token),
            encrypted_refresh_token=encrypt_secret(effective_refresh_token),
            token_expires_at=self.token_expires_at(claims),
        )
        return claims

    def _not_authenticated(self, detail: str = "Not authenticated.") -> HTTPException:
        """Return the standard unauthenticated exception used by the OIDC session flow."""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"X-Auth-Login-Url": self.config.login_path},
        )


oidc = OIDCManager()
