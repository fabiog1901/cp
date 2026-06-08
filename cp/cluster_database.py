"""Managed-cluster database connection helpers."""

import psycopg
from cpkit.db import translate_database_error as _translate_database_error
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


def translate_database_error(err: Exception, operation: str | None):
    return _translate_database_error(
        err,
        operation,
        unavailable_error_types=(ClusterDatabaseConnectionError,),
    )
