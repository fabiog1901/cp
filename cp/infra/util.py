import base64
import json
import logging
import os
import secrets
from contextvars import ContextVar

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def as_bool(value: str | None, default: bool = False) -> bool:
    """Parse common truthy environment-style values into a boolean."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def safe_json_string_dict(
    value: str | None, *, default: dict[str, str] | None = None
) -> dict[str, str]:
    """Parse a JSON object and coerce its keys and values to strings."""
    if not value:
        return default or {}

    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("Expected a JSON object.")

    return {str(k): str(v) for k, v in parsed.items()}


def safe_next_path(next_path: str | None) -> str:
    """Normalize redirect targets so only in-app absolute paths are allowed."""
    if not next_path:
        return "/"
    if not next_path.startswith("/"):
        return "/"
    if next_path.startswith("//"):
        return "/"
    return next_path


def safe_csv_set(raw_value: str | None) -> set[str]:
    """Split a comma-delimited string into a trimmed set of values."""
    if not raw_value:
        return set()
    return {part.strip() for part in raw_value.split(",") if part and part.strip()}


def _api_key_master_key() -> bytes:
    encoded_key = os.getenv("API_KEY_MASTER_KEY", "").strip()
    if not encoded_key:
        raise RuntimeError("API_KEY_MASTER_KEY must be set for API key encryption.")

    try:
        key = base64.b64decode(encoded_key, validate=True)
    except ValueError as exc:
        raise RuntimeError("API_KEY_MASTER_KEY must be valid base64.") from exc

    if len(key) != 32:
        raise RuntimeError("API_KEY_MASTER_KEY must decode to exactly 32 bytes.")

    return key


def validate_api_key_crypto_config() -> None:
    _api_key_master_key()


def _api_key_secret_bytes(secret: bytes | str) -> bytes:
    if isinstance(secret, bytes):
        return secret
    return secret.encode("utf-8")


def encrypt_api_key_secret(secret: bytes | str) -> bytes:
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(_api_key_master_key()).encrypt(
        nonce,
        _api_key_secret_bytes(secret),
        None,
    )
    return b"\x01" + nonce + ciphertext


def decrypt_api_key_secret(secret: bytes | str) -> bytes:
    encrypted_secret = _api_key_secret_bytes(secret)
    if not encrypted_secret:
        raise RuntimeError("Encrypted API key secret is empty.")
    if encrypted_secret[:1] != b"\x01":
        raise RuntimeError(
            "Encrypted API key secret has an unsupported format. Migrate stored API keys to the versioned encrypted format."
        )

    nonce = encrypted_secret[1:13]
    ciphertext = encrypted_secret[13:]
    if len(nonce) != 12 or not ciphertext:
        raise RuntimeError("Encrypted API key secret is malformed.")

    try:
        return AESGCM(_api_key_master_key()).decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise RuntimeError(
            "Encrypted API key secret could not be decrypted. Check API_KEY_MASTER_KEY and stored key material."
        ) from exc


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get()
        return True


class ShorthandFormatter(logging.Formatter):
    LEVEL_MAP = {
        "DEBUG": "D",
        "INFO": "I",
        "WARNING": "W",
        "ERROR": "E",
        "CRITICAL": "C",
    }

    def format(self, record):
        original_levelname = record.levelname
        record.levelname = self.LEVEL_MAP.get(original_levelname, original_levelname)
        result = super().format(record)
        record.levelname = original_levelname
        return result


request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
