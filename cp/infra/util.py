"""Shared operational utilities.

This module contains encryption helpers, request context utilities, and
managed-cluster connection helpers used by services and workers.
"""

import base64
import os
import secrets

from cpkit.config import as_bool, safe_csv_set, safe_json_string_dict
from cpkit.logging import RequestIDFilter, ShorthandFormatter, request_id_ctx
import psycopg
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from psycopg import OperationalError

ENCRYPTED_SECRET_VERSION = b"\x01"
CONNECT_TIMEOUT_SECS = 2
CLUSTER_DB_PORT = 26257
CLUSTER_DB_NAME = "defaultdb"
CLUSTER_DB_USERNAME = "cockroach"


class ClusterDatabaseConnectionError(Exception):
    """Raised when a cluster database cannot be reached in normal operation."""

    def __init__(self, dns_address: str, reason: str) -> None:
        self.dns_address = dns_address
        self.reason = reason
        super().__init__(f"Cluster database '{dns_address}' is unreachable: {reason}")


def safe_next_path(next_path: str | None) -> str:
    """Normalize redirect targets so only in-app absolute paths are allowed."""
    if not next_path:
        return "/"
    if not next_path.startswith("/"):
        return "/"
    if next_path.startswith("//"):
        return "/"
    return next_path


def _secret_master_key() -> bytes:
    encoded_key = os.getenv("API_KEY_MASTER_KEY", "").strip()
    if not encoded_key:
        raise RuntimeError("API_KEY_MASTER_KEY must be set for secret encryption.")

    try:
        key = base64.b64decode(encoded_key, validate=True)
    except ValueError as exc:
        raise RuntimeError("API_KEY_MASTER_KEY must be valid base64.") from exc

    if len(key) != 32:
        raise RuntimeError("API_KEY_MASTER_KEY must decode to exactly 32 bytes.")

    return key


def validate_secret_crypto_config() -> None:
    _secret_master_key()


def validate_api_key_crypto_config() -> None:
    validate_secret_crypto_config()


def _secret_bytes(secret: bytes | str) -> bytes:
    if isinstance(secret, bytes):
        return secret
    return secret.encode("utf-8")


def encrypt_secret(secret: bytes | str) -> bytes:
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(_secret_master_key()).encrypt(
        nonce,
        _secret_bytes(secret),
        None,
    )
    return ENCRYPTED_SECRET_VERSION + nonce + ciphertext


def decrypt_secret(secret: bytes | str) -> bytes:
    encrypted_secret = _secret_bytes(secret)
    if not encrypted_secret:
        raise RuntimeError("Encrypted secret is empty.")
    if encrypted_secret[:1] != ENCRYPTED_SECRET_VERSION:
        raise RuntimeError(
            "Encrypted secret has an unsupported format. Migrate stored secrets to the versioned encrypted format."
        )

    nonce = encrypted_secret[1:13]
    ciphertext = encrypted_secret[13:]
    if len(nonce) != 12 or not ciphertext:
        raise RuntimeError("Encrypted secret is malformed.")

    try:
        return AESGCM(_secret_master_key()).decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise RuntimeError(
            "Encrypted secret could not be decrypted. Check API_KEY_MASTER_KEY and stored key material."
        ) from exc


def encrypt_api_key_secret(secret: bytes | str) -> bytes:
    return encrypt_secret(secret)


def decrypt_api_key_secret(secret: bytes | str) -> bytes:
    return decrypt_secret(secret)


def connect_cluster_db(dns_address: str, password: str) -> psycopg.Connection:
    try:
        return psycopg.connect(
            (
                f"postgres://{CLUSTER_DB_USERNAME}:{password}"
                f"@{dns_address}:{CLUSTER_DB_PORT}/{CLUSTER_DB_NAME}?sslmode=require"
            ),
            autocommit=True,
            connect_timeout=CONNECT_TIMEOUT_SECS,
        )
    except TimeoutError as exc:
        raise ClusterDatabaseConnectionError(
            dns_address, "connection timed out"
        ) from exc
    except OperationalError as exc:
        if _is_cluster_connection_timeout(exc):
            raise ClusterDatabaseConnectionError(
                dns_address,
                "connection timed out",
            ) from exc
        raise


def _is_cluster_connection_timeout(err: OperationalError) -> bool:
    message = str(err).lower()
    return "timeout" in message or "timed out" in message
