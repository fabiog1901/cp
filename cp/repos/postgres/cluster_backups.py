"""Repository for listing backups on a cluster."""

import psycopg
from psycopg import sql
from psycopg.rows import class_row

from ...models import BackupDetails, BackupPathOption

CONNECT_TIMEOUT_SECS = 2
CLUSTER_DB_PORT = 26257
CLUSTER_DB_NAME = "defaultdb"
CLUSTER_DB_USERNAME = "cockroach"
CLUSTER_DB_PASSWORD = "cockroach"


def list_backup_paths(dns_address: str) -> list[BackupPathOption]:
    with _connect(dns_address) as conn:
        with conn.cursor() as cur:
            rows = cur.execute("SHOW BACKUPS IN 'external://backup';").fetchall()

    paths = sorted((str(row[0]) for row in rows), reverse=True)
    return [BackupPathOption(path="LATEST")] + [
        BackupPathOption(path=path) for path in paths
    ]


def list_backup_details(
    dns_address: str,
    backup_path: str,
) -> list[BackupDetails]:
    query = sql.SQL(
        """
        SELECT database_name, parent_schema_name, object_name, object_type, end_time
        FROM [SHOW BACKUP {} IN 'external://backup']
        WHERE (
            database_name NOT IN ('system', 'postgres')
            OR object_name NOT IN ('system', 'postgres')
        )
        AND object_type = 'database';
        """
    ).format(sql.Literal(backup_path))

    with _connect(dns_address) as conn:
        with conn.cursor(row_factory=class_row(BackupDetails)) as cur:
            return cur.execute(query).fetchall()


def _connect(dns_address: str) -> psycopg.Connection:
    return psycopg.connect(
        (
            f"postgres://{CLUSTER_DB_USERNAME}:{CLUSTER_DB_PASSWORD}"
            f"@{dns_address}:{CLUSTER_DB_PORT}/{CLUSTER_DB_NAME}?sslmode=require"
        ),
        autocommit=True,
        connect_timeout=CONNECT_TIMEOUT_SECS,
    )
