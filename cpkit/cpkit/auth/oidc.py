"""Reusable OIDC provider client mechanics."""

import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

import jwt


class OIDCAuthenticationError(Exception):
    """Raised when an OIDC token cannot be authenticated."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class OIDCProviderClient:
    """Load OIDC provider metadata and exchange OAuth/OIDC tokens."""

    def __init__(self, config: Any) -> None:
        self.config = config
        self._metadata: dict[str, Any] | None = None
        self._jwks: dict[str, Any] | None = None
        self._meta_loaded_at = 0.0
        self._jwks_loaded_at = 0.0
        self._cache_ttl_seconds = getattr(config, "cache_ttl_seconds", 300)

    def update_provider_config(self, config: Any, *, clear_cache: bool = False) -> None:
        self.config = config
        self._cache_ttl_seconds = getattr(config, "cache_ttl_seconds", 300)
        if clear_cache:
            self.clear_provider_cache()

    def clear_provider_cache(self) -> None:
        self._metadata = None
        self._jwks = None
        self._meta_loaded_at = 0.0
        self._jwks_loaded_at = 0.0

    def _http_json(
        self,
        url: str,
        *,
        method: str = "GET",
        data: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        req_headers = {"Accept": "application/json"}
        if headers:
            req_headers.update(headers)

        payload = None
        if data is not None:
            payload = urllib.parse.urlencode(data).encode("utf-8")
            req_headers["Content-Type"] = "application/x-www-form-urlencoded"

        req = urllib.request.Request(
            url,
            data=payload,
            headers=req_headers,
            method=method,
        )
        with urllib.request.urlopen(req, timeout=10) as resp:  # nosec B310
            raw = resp.read().decode("utf-8")
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                raise RuntimeError(f"Expected JSON object from {url}")
            return parsed

    def get_metadata(self) -> dict[str, Any]:
        """Return cached OIDC discovery metadata, refreshing it when needed."""
        if (
            self._metadata
            and (time.time() - self._meta_loaded_at) < self._cache_ttl_seconds
        ):
            return self._metadata
        metadata_url = f"{self.config.issuer_url}/.well-known/openid-configuration"
        self._metadata = self._http_json(metadata_url)
        self._meta_loaded_at = time.time()
        return self._metadata

    def get_jwks(self) -> dict[str, Any]:
        """Return cached provider signing keys, refreshing them when needed."""
        if (
            self._jwks
            and (time.time() - self._jwks_loaded_at) < self._cache_ttl_seconds
        ):
            return self._jwks

        metadata = self.get_metadata()
        jwks_uri = str(metadata.get("jwks_uri") or "")
        if not jwks_uri:
            raise RuntimeError("OIDC provider metadata missing 'jwks_uri'")

        self._jwks = self._http_json(jwks_uri)
        self._jwks_loaded_at = time.time()
        return self._jwks

    def build_authorization_url(self, redirect_uri: str, state: str, nonce: str) -> str:
        """Build the provider authorization URL for starting login."""
        metadata = self.get_metadata()
        auth_endpoint = str(metadata.get("authorization_endpoint") or "")
        if not auth_endpoint:
            raise RuntimeError(
                "OIDC provider metadata missing 'authorization_endpoint'"
            )

        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": redirect_uri,
            "scope": self.config.scopes,
            "state": state,
            "nonce": nonce,
        }

        if self.config.audience:
            params["audience"] = self.config.audience

        params.update(self.config.extra_auth_params())

        return f"{auth_endpoint}?{urllib.parse.urlencode(params)}"

    def exchange_code(self, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchange an OIDC authorization code for a token response."""
        metadata = self.get_metadata()
        token_endpoint = str(metadata.get("token_endpoint") or "")
        if not token_endpoint:
            raise RuntimeError("OIDC provider metadata missing 'token_endpoint'")

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "redirect_uri": redirect_uri,
        }
        payload.update(self.config.extra_auth_params())

        return self._http_json(token_endpoint, method="POST", data=payload)

    def refresh_tokens(self, refresh_token: str) -> dict[str, Any]:
        """Exchange a refresh token for fresh token material."""
        metadata = self.get_metadata()
        token_endpoint = str(metadata.get("token_endpoint") or "")
        if not token_endpoint:
            raise RuntimeError("OIDC provider metadata missing 'token_endpoint'")

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }

        return self._http_json(token_endpoint, method="POST", data=payload)

    def select_jwk_key(self, token: str) -> Any:
        """Return the provider signing key that matches a JWT header."""
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise OIDCAuthenticationError("Token header is missing 'kid'")

        keys = self.get_jwks().get("keys", [])
        for jwk in keys:
            if jwk.get("kid") == kid:
                return jwt.PyJWK.from_dict(jwk).key

        self._jwks = None
        keys = self.get_jwks().get("keys", [])
        for jwk in keys:
            if jwk.get("kid") == kid:
                return jwt.PyJWK.from_dict(jwk).key

        raise OIDCAuthenticationError(
            "Unable to find a matching JWKS key for token"
        )

    def validate_jwt(
        self,
        token: str,
        *,
        expected_nonce: str | None = None,
        strict_client_audience: bool = False,
    ) -> dict[str, Any]:
        """Validate a JWT against the provider configuration and optional nonce."""
        key = self.select_jwk_key(token)

        options = {
            "verify_signature": True,
            "verify_exp": True,
            "verify_iat": True,
            "verify_nbf": True,
            "verify_iss": True,
            "verify_aud": strict_client_audience
            or self.config.verify_audience
            or bool(self.config.audience),
        }

        audience = None
        if strict_client_audience:
            audience = self.config.client_id
        elif self.config.audience:
            audience = self.config.audience

        try:
            claims = jwt.decode(
                token,
                key=key,
                algorithms=["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"],
                issuer=self.config.issuer_url,
                audience=audience,
                options=options,
            )
        except jwt.PyJWTError as exc:
            raise OIDCAuthenticationError(f"Invalid token: {exc}") from exc

        if expected_nonce is not None and claims.get("nonce") != expected_nonce:
            raise OIDCAuthenticationError("Invalid token nonce")

        return claims

    @staticmethod
    def token_expires_at(claims: dict[str, Any]) -> datetime:
        """Return the UTC expiration timestamp encoded in JWT claims."""
        raw_exp = claims.get("exp")
        if raw_exp is None:
            raise OIDCAuthenticationError("Token is missing 'exp'.")
        try:
            return datetime.fromtimestamp(float(raw_exp), tz=timezone.utc)
        except (TypeError, ValueError, OSError, OverflowError) as exc:
            raise OIDCAuthenticationError(
                "Token has an invalid 'exp' claim."
            ) from exc
