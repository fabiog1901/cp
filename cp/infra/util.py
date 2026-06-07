"""Shared operational utilities.

This module contains encryption helpers, request context utilities, and
managed-cluster connection helpers used by services and workers.
"""

from cpkit.auth import (
    decrypt_secret,
    encrypt_secret,
    safe_next_path,
    validate_secret_crypto_config,
)
from cpkit.config import as_bool, safe_csv_set, safe_json_string_dict
from cpkit.logging import RequestIDFilter, ShorthandFormatter, request_id_ctx
import psycopg
from psycopg import OperationalError

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


def validate_api_key_crypto_config() -> None:
    validate_secret_crypto_config()


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
