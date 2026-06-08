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
from .api_key_router import create_api_keys_router
from .api_key_service import ApiKeysService
from .claims import claim_groups, claims_groups, jsonable_role_groups
from .config import OIDCConfig
from .dependencies import (
    ACCESS_KEY_HEADER_NAME,
    SIGNATURE_HEADER_NAME,
    TIMESTAMP_HEADER_NAME,
    AuthDependencies,
    access_key_scheme,
    create_auth_dependencies,
    signature_scheme,
    timestamp_scheme,
)
from .redirects import safe_next_path
from .repositories import APIKeysRepositoryMixin, OIDCSessionsRepositoryMixin
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
from .types import (
    ApiKeyCreateRequest,
    ApiKeyCreateRequestInDB,
    ApiKeyCreateResponse,
    ApiKeyRecord,
    ApiKeySummary,
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
    "ApiKeyCreateRequest",
    "ApiKeyCreateRequestInDB",
    "ApiKeyCreateResponse",
    "ApiKeyRecord",
    "ApiKeySummary",
    "ApiKeysService",
    "OIDCSessionsRepositoryMixin",
    "ACCESS_KEY_HEADER_NAME",
    "AuthDependencies",
    "OIDCConfig",
    "SIGNATURE_HEADER_NAME",
    "TIMESTAMP_HEADER_NAME",
    "access_key_scheme",
    "api_key_signature",
    "build_api_key_signature_payload",
    "claim_groups",
    "claims_groups",
    "create_oidc_router",
    "create_api_keys_router",
    "create_auth_dependencies",
    "decrypt_secret",
    "encrypt_secret",
    "jsonable_role_groups",
    "parse_api_key_timestamp",
    "request_target_bytes",
    "safe_next_path",
    "signature_scheme",
    "timestamp_scheme",
    "validate_secret_crypto_config",
]
