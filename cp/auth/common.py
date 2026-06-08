"""Shared authentication constants and compatibility exports."""

from cpkit.auth import (
    OIDCConfig,
    api_key_signature,
    build_api_key_signature_payload,
    claim_groups,
    claims_groups,
    jsonable_role_groups,
    parse_api_key_timestamp,
    request_target_bytes,
)

OIDC_SESSION_COOKIE_NAME = "cp_session"
OIDC_STATE_COOKIE_NAME = "cp_oidc_state"
OIDC_NONCE_COOKIE_NAME = "cp_oidc_nonce"
OIDC_NEXT_COOKIE_NAME = "cp_oidc_next"

__all__ = [
    "OIDCConfig",
    "OIDC_SESSION_COOKIE_NAME",
    "OIDC_STATE_COOKIE_NAME",
    "OIDC_NONCE_COOKIE_NAME",
    "OIDC_NEXT_COOKIE_NAME",
    "api_key_signature",
    "build_api_key_signature_payload",
    "claim_groups",
    "claims_groups",
    "jsonable_role_groups",
    "parse_api_key_timestamp",
    "request_target_bytes",
]
