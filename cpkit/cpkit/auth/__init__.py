"""Reusable authentication helpers."""

from .api_keys import (
    APIKeyAuthenticationError,
    APIKeyAuthenticator,
    APIKeyRepository,
    api_key_signature,
    build_api_key_signature_payload,
    parse_api_key_timestamp,
    request_target_bytes,
)
from .claims import claim_groups, claims_groups, jsonable_role_groups
from .config import OIDCConfig
from .redirects import safe_next_path
from .repositories import APIKeysRepositoryMixin
from .router import (
    OIDC_NEXT_COOKIE_NAME,
    OIDC_NONCE_COOKIE_NAME,
    OIDC_STATE_COOKIE_NAME,
    create_oidc_router,
)
from .oidc import (
    OIDCAuthenticationError,
    OIDCManager,
    OIDCProviderClient,
    OIDCSessionManager,
    OIDCSessionRepository,
)
from .secrets import (
    ENCRYPTED_SECRET_VERSION,
    decrypt_secret,
    encrypt_secret,
    validate_secret_crypto_config,
)

__all__ = [
    "ENCRYPTED_SECRET_VERSION",
    "OIDCAuthenticationError",
    "OIDCManager",
    "OIDC_NEXT_COOKIE_NAME",
    "OIDC_NONCE_COOKIE_NAME",
    "OIDCProviderClient",
    "OIDCSessionManager",
    "OIDCSessionRepository",
    "OIDC_STATE_COOKIE_NAME",
    "APIKeyAuthenticationError",
    "APIKeyAuthenticator",
    "APIKeyRepository",
    "APIKeysRepositoryMixin",
    "OIDCConfig",
    "api_key_signature",
    "build_api_key_signature_payload",
    "claim_groups",
    "claims_groups",
    "create_oidc_router",
    "decrypt_secret",
    "encrypt_secret",
    "jsonable_role_groups",
    "parse_api_key_timestamp",
    "request_target_bytes",
    "safe_next_path",
    "validate_secret_crypto_config",
]
