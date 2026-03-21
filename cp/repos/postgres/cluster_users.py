"""Repository for managing database users on a cluster."""

import logging

import psycopg
from psycopg import sql
from psycopg.rows import class_row

from ...infra.db import translate_database_error
from ...models import DatabaseUser

CONNECT_TIMEOUT_SECS = 2
CLUSTER_DB_PORT = 26257
CLUSTER_DB_NAME = "defaultdb"
CLUSTER_DB_USERNAME = "cockroach"
CLUSTER_DB_PASSWORD = "cockroach"
logger = logging.getLogger(__name__)


class ClusterUsersRepo:
    @staticmethod
    def list_database_users(dns_address: str) -> list[DatabaseUser]:
        try:
            with ClusterUsersRepo._connect(dns_address) as conn:
                with conn.cursor(row_factory=class_row(DatabaseUser)) as cur:
                    return cur.execute(
                        """
                        SELECT username, options, member_of
                        FROM [SHOW USERS]
                        WHERE username NOT IN ('admin', 'root', 'cockroach');
                        """
                    ).fetchall()
        except Exception as err:
            logger.debug(
                "Cluster user query failed [operation=cluster_users.list_database_users]"
            )
            raise translate_database_error(err, "cluster_users.list_database_users") from err

    @staticmethod
    def create_database_user(dns_address: str, username: str, password: str) -> None:
        try:
            with ClusterUsersRepo._connect(dns_address) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                            sql.Identifier(username)
                        ),
                        (password,),
                    )
        except Exception as err:
            logger.debug(
                "Cluster user query failed [operation=cluster_users.create_database_user]"
            )
            raise translate_database_error(err, "cluster_users.create_database_user") from err

    @staticmethod
    def remove_database_user(dns_address: str, username: str) -> None:
        try:
            with ClusterUsersRepo._connect(dns_address) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql.SQL("DROP USER {}").format(sql.Identifier(username)))
        except Exception as err:
            logger.debug(
                "Cluster user query failed [operation=cluster_users.remove_database_user]"
            )
            raise translate_database_error(err, "cluster_users.remove_database_user") from err

    @staticmethod
    def revoke_database_user_role(dns_address: str, username: str, role: str) -> None:
        try:
            with ClusterUsersRepo._connect(dns_address) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        sql.SQL("REVOKE {} FROM {}").format(
                            sql.Identifier(role),
                            sql.Identifier(username),
                        )
                    )
        except Exception as err:
            logger.debug(
                "Cluster user query failed [operation=cluster_users.revoke_database_user_role]"
            )
            raise translate_database_error(
                err, "cluster_users.revoke_database_user_role"
            ) from err

    @staticmethod
    def update_database_user_password(
        dns_address: str,
        username: str,
        password: str,
    ) -> None:
        try:
            with ClusterUsersRepo._connect(dns_address) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        sql.SQL("ALTER USER {} WITH PASSWORD %s").format(
                            sql.Identifier(username)
                        ),
                        (password,),
                    )
        except Exception as err:
            logger.debug(
                "Cluster user query failed [operation=cluster_users.update_database_user_password]"
            )
            raise translate_database_error(
                err, "cluster_users.update_database_user_password"
            ) from err

    @staticmethod
    def _connect(dns_address: str) -> psycopg.Connection:
        return psycopg.connect(
            (
                f"postgres://{CLUSTER_DB_USERNAME}:{CLUSTER_DB_PASSWORD}"
                f"@{dns_address}:{CLUSTER_DB_PORT}/{CLUSTER_DB_NAME}?sslmode=require"
            ),
            autocommit=True,
            connect_timeout=CONNECT_TIMEOUT_SECS,
        )
