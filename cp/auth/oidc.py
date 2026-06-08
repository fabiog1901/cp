"""CP FastAPI adapter for the reusable OIDC manager."""

from datetime import datetime
from typing import Any

from cpkit.auth import (
    APIKeyAuthenticationError,
    OIDCAuthenticationError,
    OIDCAuthorizationError,
    OIDCManager as CpkitOIDCManager,
    OIDCProviderClient,
)
from fastapi import HTTPException, Request, status

from ..infra import decrypt_secret, encrypt_secret, validate_secret_crypto_config
from ..models import CPRole, OIDCSessionRecord
from ..repos import Repo
from .common import OIDC_SESSION_COOKIE_NAME


class OIDCManager(CpkitOIDCManager):
    """Translate reusable auth manager failures into FastAPI responses."""

    def __init__(self) -> None:
        super().__init__(
            encrypt_secret=encrypt_secret,
            decrypt_secret=decrypt_secret,
            session_record_factory=OIDCSessionRecord,
            session_cookie_name=OIDC_SESSION_COOKIE_NAME,
            missing_api_key_headers_detail=(
                "X-CP-Access-Key, X-CP-Signature, and X-Timestamp are required."
            ),
        )

    def validate_config(self, repo: Repo) -> None:
        """Validate auth configuration at startup, including API key crypto settings."""
        super().validate_config(
            repo,
            validate_secret_crypto_config=validate_secret_crypto_config,
        )

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

    def ensure_authorized(self, claims: dict[str, Any]) -> dict[str, Any]:
        """Ensure the caller belongs to at least one configured application group."""
        try:
            return super().ensure_authorized(claims)
        except OIDCAuthorizationError as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=exc.detail,
            ) from exc

    def ensure_any_role(self, claims: dict[str, Any], *roles: CPRole) -> dict[str, Any]:
        """Ensure the caller has at least one of the requested application roles."""
        try:
            return super().ensure_any_role(claims, *roles)
        except OIDCAuthorizationError as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=exc.detail,
            ) from exc

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
            return await super().validate_api_key(
                request,
                repo,
                access_key,
                signature,
                timestamp,
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
        try:
            return await super().current_claims(
                request,
                repo,
                session_token=session_token,
                access_key=access_key,
                signature=signature,
                timestamp=timestamp,
            )
        except APIKeyAuthenticationError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=exc.detail,
            ) from exc
        except OIDCAuthenticationError as exc:
            raise self._not_authenticated(exc.detail) from exc

    def _claims_from_session(
        self,
        repo: Repo,
        session_id: str,
    ) -> dict[str, Any]:
        """Load a server-side OIDC session, refreshing token material when needed."""
        try:
            return self.claims_from_session(repo, session_id)
        except OIDCAuthenticationError as exc:
            raise self._not_authenticated(exc.detail) from exc

    def _refresh_session(
        self,
        repo: Repo,
        session: OIDCSessionRecord,
    ) -> dict[str, Any]:
        """Refresh an OIDC session using its stored refresh token."""
        try:
            return self.refresh_session(repo, session)
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
