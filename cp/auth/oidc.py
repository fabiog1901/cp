"""CP OIDC manager configuration."""

from cpkit.auth import OIDCManager as CpkitOIDCManager

from ..infra import decrypt_secret, encrypt_secret, validate_secret_crypto_config
from ..models import OIDCSessionRecord
from .common import OIDC_SESSION_COOKIE_NAME


class OIDCManager(CpkitOIDCManager):
    """Configure CP-specific dependencies for cpkit OIDC auth."""

    def __init__(self) -> None:
        super().__init__(
            encrypt_secret=encrypt_secret,
            decrypt_secret=decrypt_secret,
            session_record_factory=OIDCSessionRecord,
            session_cookie_name=OIDC_SESSION_COOKIE_NAME,
            validate_secret_crypto_config=validate_secret_crypto_config,
            missing_api_key_headers_detail=(
                "X-CP-Access-Key, X-CP-Signature, and X-Timestamp are required."
            ),
        )


oidc = OIDCManager()
