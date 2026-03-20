"""Repository for managing database users on a cluster."""

import psycopg
from psycopg import sql
from psycopg.rows import class_row

from ...models import DatabaseUser

CONNECT_TIMEOUT_SECS = 2
CLUSTER_DB_PORT = 26257
CLUSTER_DB_NAME = "defaultdb"
CLUSTER_DB_USERNAME = "cockroach"
CLUSTER_DB_PASSWORD = "cockroach"


def list_database_users(dns_address: str) -> list[DatabaseUser]:
    with _connect(dns_address) as conn:
        with conn.cursor(row_factory=class_row(DatabaseUser)) as cur:
            return cur.execute(
                """
                SELECT username, options, member_of
                FROM [SHOW USERS]
                WHERE username NOT IN ('admin', 'root', 'cockroach');
                """
            ).fetchall()


def create_database_user(dns_address: str, username: str, password: str) -> None:
    with _connect(dns_address) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier(username)
                ),
                (password,),
            )


def remove_database_user(dns_address: str, username: str) -> None:
    with _connect(dns_address) as conn:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("DROP USER {}").format(sql.Identifier(username)))


def revoke_database_user_role(dns_address: str, username: str, role: str) -> None:
    with _connect(dns_address) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("REVOKE {} FROM {}").format(
                    sql.Identifier(role),
                    sql.Identifier(username),
                )
            )


def update_database_user_password(
    dns_address: str,
    username: str,
    password: str,
) -> None:
    with _connect(dns_address) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("ALTER USER {} WITH PASSWORD %s").format(
                    sql.Identifier(username)
                ),
                (password,),
            )


def _connect(dns_address: str) -> psycopg.Connection:
    return psycopg.connect(
        (
            f"postgres://{CLUSTER_DB_USERNAME}:{CLUSTER_DB_PASSWORD}"
            f"@{dns_address}:{CLUSTER_DB_PORT}/{CLUSTER_DB_NAME}?sslmode=require"
        ),
        autocommit=True,
        connect_timeout=CONNECT_TIMEOUT_SECS,
    )
