import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from hmac import compare_digest
from typing import Any

import jwt
from fastapi import HTTPException, Request, status

from ..infra import decrypt_secret, encrypt_secret, validate_secret_crypto_config
from ..models import CPRole, OIDCSessionRecord
from ..repos.base import BaseRepo
from .common import (
    OIDC_SESSION_COOKIE_NAME,
    OIDCConfig,
    api_key_signature,
    claims_groups,
    jsonable_role_groups,
    parse_api_key_timestamp,
)


class OIDCManager:
    """Coordinate OIDC metadata loading, token validation, and request auth resolution."""

    def __init__(self) -> None:
        self.config = OIDCConfig()
        self._config_loaded_at = 0.0
        self._config_cache_ttl_seconds = 300
        self._metadata: dict[str, Any] | None = None
        self._jwks: dict[str, Any] | None = None
        self._meta_loaded_at = 0.0
        self._jwks_loaded_at = 0.0
        self._cache_ttl_seconds = self.config.cache_ttl_seconds

    @property
    def enabled(self) -> bool:
        """Expose whether OIDC-backed authentication is enabled for the app."""
        return self.config.enabled

    def load_config(self, repo: BaseRepo, *, force: bool = False) -> None:
        now = time.time()
        if (
            not force
            and self._config_loaded_at
            and (now - self._config_loaded_at) < self._config_cache_ttl_seconds
        ):
            return

        new_config = OIDCConfig.from_repo(repo)
        if self.config != new_config:
            self._metadata = None
            self._jwks = None
            self._meta_loaded_at = 0.0
            self._jwks_loaded_at = 0.0
        self.config = new_config
        self._cache_ttl_seconds = self.config.cache_ttl_seconds
        self._config_loaded_at = now

    def validate_config(self, repo: BaseRepo) -> None:
        """Validate auth configuration at startup, including API key crypto settings."""
        self.load_config(repo, force=True)
        self.config.validate()
        validate_secret_crypto_config()

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
        """Return cached OIDC discovery metadata, refreshing it when the cache expires."""
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
        """Build the provider authorization URL for starting the OIDC login flow."""
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

        return self._http_json(
            token_endpoint,
            method="POST",
            data=payload,
        )

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

        return self._http_json(
            token_endpoint,
            method="POST",
            data=payload,
        )

    def _select_jwk(self, token: str) -> Any:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Token header is missing 'kid'")

        keys = self.get_jwks().get("keys", [])
        for jwk in keys:
            if jwk.get("kid") == kid:
                return jwt.PyJWK.from_dict(jwk).key

        self._jwks = None
        keys = self.get_jwks().get("keys", [])
        for jwk in keys:
            if jwk.get("kid") == kid:
                return jwt.PyJWK.from_dict(jwk).key

        raise HTTPException(
            status_code=401, detail="Unable to find a matching JWKS key for token"
        )

    def validate_jwt(
        self,
        token: str,
        *,
        expected_nonce: str | None = None,
        strict_client_audience: bool = False,
    ) -> dict[str, Any]:
        """Validate a JWT against the provider configuration and optional nonce."""
        key = self._select_jwk(token)

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
            raise HTTPException(
                status_code=401, detail=f"Invalid token: {exc}"
            ) from exc

        if expected_nonce is not None and claims.get("nonce") != expected_nonce:
            raise HTTPException(status_code=401, detail="Invalid token nonce")

        return claims

    @staticmethod
    def token_expires_at(claims: dict[str, Any]) -> datetime:
        """Return the UTC expiration timestamp encoded in the JWT claims."""
        raw_exp = claims.get("exp")
        if raw_exp is None:
            raise HTTPException(status_code=401, detail="Token is missing 'exp'.")
        try:
            return datetime.fromtimestamp(float(raw_exp), tz=timezone.utc)
        except (TypeError, ValueError, OSError, OverflowError) as exc:
            raise HTTPException(
                status_code=401, detail="Token has an invalid 'exp' claim."
            ) from exc

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
        repo: BaseRepo,
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
        repo: BaseRepo,
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
        repo: BaseRepo,
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
        repo: BaseRepo,
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
