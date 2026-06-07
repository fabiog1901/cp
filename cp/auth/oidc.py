"""OIDC client helpers.

This module handles provider discovery, token exchange, ID token validation, and
claim normalization for CP web sessions.
"""

import time
from datetime import datetime
from typing import Any

from cpkit.auth import (
    APIKeyAuthenticationError,
    APIKeyAuthenticator,
    OIDCAuthenticationError,
    OIDCProviderClient,
    OIDCSessionManager,
)
from fastapi import HTTPException, Request, status

from ..infra import decrypt_secret, encrypt_secret, validate_secret_crypto_config
from ..models import CPRole, OIDCSessionRecord
from ..repos import Repo
from .common import (
    OIDC_SESSION_COOKIE_NAME,
    OIDCConfig,
    claims_groups,
    jsonable_role_groups,
)


class OIDCManager(OIDCProviderClient):
    """Coordinate OIDC metadata loading, token validation, and request auth resolution."""

    def __init__(self) -> None:
        super().__init__(OIDCConfig())
        self.sessions = OIDCSessionManager(
            self,
            encrypt_secret=encrypt_secret,
            decrypt_secret=decrypt_secret,
            session_record_factory=OIDCSessionRecord,
        )
        self.api_keys = APIKeyAuthenticator(decrypt_secret=decrypt_secret)
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
        return self.sessions.build_session_record(
            session_id,
            id_token=id_token,
            refresh_token=refresh_token,
            claims=claims,
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
        try:
            return await self.api_keys.authenticate_request(
                request,
                repo,
                access_key=access_key,
                signature=signature,
                timestamp=timestamp,
                max_age_seconds=self.config.api_key_signature_ttl_seconds,
            )
        except APIKeyAuthenticationError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=exc.detail,
            ) from exc

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
        try:
            return self.sessions.claims_from_session(
                repo,
                session_id,
                authorize_claims=self.ensure_authorized,
            )
        except OIDCAuthenticationError as exc:
            raise self._not_authenticated(exc.detail) from exc

    def _refresh_session(
        self,
        repo: Repo,
        session: OIDCSessionRecord,
    ) -> dict[str, Any]:
        """Refresh an OIDC session using its stored refresh token."""
        try:
            return self.sessions.refresh_session(
                repo,
                session,
                authorize_claims=self.ensure_authorized,
            )
        except OIDCAuthenticationError as exc:
            raise self._not_authenticated(exc.detail) from exc

    def _not_authenticated(self, detail: str = "Not authenticated.") -> HTTPException:
        """Return the standard unauthenticated exception used by the OIDC session flow."""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"X-Auth-Login-Url": self.config.login_path},
        )


oidc = OIDCManager()
