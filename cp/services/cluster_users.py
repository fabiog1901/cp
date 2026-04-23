"""Business logic for the cluster users vertical."""

import logging

from psycopg import sql
from psycopg.rows import class_row
from pydantic import ValidationError

from ..infra.db import get_repo, translate_database_error
from ..infra.errors import RepositoryError
from ..infra.util import connect_cluster_db, decrypt_secret
from ..models import (
    AuditEvent,
    Cluster,
    ClusterUsersSnapshot,
    DatabaseUser,
    NewDatabaseUserRequest,
    to_public_cluster,
)
from ..repos import Repo
from .base import log_event
from .errors import ServiceNotFoundError, ServiceValidationError, from_repository_error

logger = logging.getLogger(__name__)


class ClusterUsersService:
    def __init__(self, repo: Repo | None = None) -> None:
        self.repo = repo or get_repo()

    def load_cluster_users_snapshot(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
    ) -> ClusterUsersSnapshot | None:
        selected_cluster = self.repo.get_cluster(cluster_id, groups, is_admin)
        if selected_cluster is None:
            return None

        try:
            try:
                with connect_cluster_db(
                    self._get_primary_dns_address(selected_cluster),
                    self._get_cluster_db_password(selected_cluster),
                ) as conn:
                    with conn.cursor(row_factory=class_row(DatabaseUser)) as cur:
                        database_users = cur.execute("""
                            SELECT username, options, member_of
                            FROM [SHOW USERS]
                            WHERE username NOT IN ('admin', 'root', 'cockroach');
                            """).fetchall()
            except Exception as err:
                logger.debug(
                    "Cluster user query failed [operation=cluster_users.list_database_users]"
                )
                raise translate_database_error(
                    err, "cluster_users.list_database_users"
                ) from err

            return ClusterUsersSnapshot(
                cluster=to_public_cluster(selected_cluster),
                database_users=database_users,
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Database users are temporarily unavailable.",
                fallback_message=f"Unable to load database users for cluster '{cluster_id}'.",
            ) from err

    def create_database_user(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
        username: str,
        password: str,
        requested_by: str,
    ) -> None:
        selected_cluster = self._get_cluster_or_raise(
            cluster_id,
            groups,
            is_admin,
        )
        try:
            request = NewDatabaseUserRequest(username=username, password=password)
        except ValidationError as err:
            raise ServiceValidationError(
                "Database username or password is invalid."
            ) from err

        try:
            try:
                with connect_cluster_db(
                    self._get_primary_dns_address(selected_cluster),
                    self._get_cluster_db_password(selected_cluster),
                ) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                                sql.Identifier(request.username)
                            ),
                            (request.password,),
                        )
            except Exception as err:
                logger.debug(
                    "Cluster user query failed [operation=cluster_users.create_database_user]"
                )
                raise translate_database_error(
                    err, "cluster_users.create_database_user"
                ) from err
            log_event(
                self.repo,
                requested_by,
                AuditEvent.DB_USER_CREATED,
                {
                    "cluster_id": selected_cluster.cluster_id,
                    "db_user": request.username,
                },
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Database user creation is temporarily unavailable.",
                conflict_message=f"Database user '{request.username}' already exists.",
                validation_message="Database user details are invalid.",
                fallback_message=f"Unable to create database user '{request.username}'.",
            ) from err

    def delete_database_user(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
        username: str,
        requested_by: str,
    ) -> None:
        selected_cluster = self._get_cluster_or_raise(
            cluster_id,
            groups,
            is_admin,
        )
        try:
            try:
                with connect_cluster_db(
                    self._get_primary_dns_address(selected_cluster),
                    self._get_cluster_db_password(selected_cluster),
                ) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            sql.SQL("DROP USER {}").format(sql.Identifier(username))
                        )
            except Exception as err:
                logger.debug(
                    "Cluster user query failed [operation=cluster_users.delete_database_user]"
                )
                raise translate_database_error(
                    err, "cluster_users.delete_database_user"
                ) from err
            log_event(
                self.repo,
                requested_by,
                AuditEvent.DB_USER_DELETED,
                {"cluster_id": selected_cluster.cluster_id, "db_user": username},
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Database user removal is temporarily unavailable.",
                fallback_message=f"Unable to remove database user '{username}'.",
            ) from err

    def revoke_database_user_role(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
        username: str,
        role: str,
        requested_by: str,
    ) -> None:
        selected_cluster = self._get_cluster_or_raise(
            cluster_id,
            groups,
            is_admin,
        )
        try:
            try:
                with connect_cluster_db(
                    self._get_primary_dns_address(selected_cluster),
                    self._get_cluster_db_password(selected_cluster),
                ) as conn:
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
            log_event(
                self.repo,
                requested_by,
                AuditEvent.DB_USER_ROLE_REVOKED,
                {
                    "cluster_id": selected_cluster.cluster_id,
                    "db_user": username,
                    "role": role,
                },
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Database role updates are temporarily unavailable.",
                fallback_message=f"Unable to revoke role '{role}' from '{username}'.",
            ) from err

    def update_database_user_password(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
        username: str,
        password: str,
        requested_by: str,
    ) -> None:
        if not password:
            raise ServiceValidationError("Password is required.")

        selected_cluster = self._get_cluster_or_raise(
            cluster_id,
            groups,
            is_admin,
        )
        try:
            try:
                with connect_cluster_db(
                    self._get_primary_dns_address(selected_cluster),
                    self._get_cluster_db_password(selected_cluster),
                ) as conn:
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
            log_event(
                self.repo,
                requested_by,
                AuditEvent.DB_USER_PASSWORD_UPDATED,
                {"cluster_id": selected_cluster.cluster_id, "db_user": username},
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Password updates are temporarily unavailable.",
                validation_message="The new password is invalid.",
                fallback_message=f"Unable to update password for '{username}'.",
            ) from err

    def _get_cluster_or_raise(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
    ) -> Cluster:
        selected_cluster = self.repo.get_cluster(cluster_id, groups, is_admin)
        if selected_cluster is None:
            raise ServiceNotFoundError(f"Cluster '{cluster_id}' was not found.")
        return selected_cluster

    @staticmethod
    def _get_primary_dns_address(cluster: Cluster) -> str:
        if not cluster.lbs_inventory:
            raise ServiceValidationError(
                f"Cluster '{cluster.cluster_id}' has no load balancer endpoint."
            )
        return cluster.lbs_inventory[0].dns_address

    def _get_cluster_db_password(self, cluster: Cluster) -> str:
        if cluster.password is None:
            raise ServiceValidationError(
                f"Cluster '{cluster.cluster_id}' has no database password configured."
            )
        try:
            return decrypt_secret(cluster.password).decode("utf-8")
        except Exception as err:
            raise ServiceValidationError(
                f"Cluster '{cluster.cluster_id}' has an invalid database password."
            ) from err
