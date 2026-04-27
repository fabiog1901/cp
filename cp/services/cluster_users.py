"""Business logic for the cluster users vertical."""

import logging
import re

from psycopg import sql
from psycopg.rows import class_row
from pydantic import ValidationError

from ..infra.db import get_repo, translate_database_error
from ..infra.errors import RepositoryError
from ..infra.util import connect_cluster_db, decrypt_secret
from ..models import (
    AuditEvent,
    Cluster,
    ClusterDatabaseRole,
    ClusterUsersSnapshot,
    DatabaseRoleTemplateConfig,
    DatabaseUser,
    NewDatabaseUserRequest,
    to_public_cluster,
)
from ..repos import Repo
from .base import log_event
from .errors import ServiceNotFoundError, ServiceValidationError, from_repository_error

logger = logging.getLogger(__name__)

SYSTEM_DATABASES = {"defaultdb", "postgres", "system"}
SYSTEM_SCHEMAS = {"crdb_internal", "information_schema", "pg_catalog", "pg_extension"}


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
                database_role_templates=self.repo.list_database_role_templates(),
                database_roles=self.repo.list_cluster_database_roles(cluster_id),
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
        database_roles: list[str] | None,
        requested_by: str,
    ) -> None:
        selected_cluster = self._get_cluster_or_raise(
            cluster_id,
            groups,
            is_admin,
        )
        try:
            request = NewDatabaseUserRequest(
                username=username,
                password=password,
                database_roles=database_roles or [],
            )
        except ValidationError as err:
            raise ServiceValidationError(
                "Database username or password is invalid."
            ) from err

        try:
            selected_database_roles = self._get_database_roles_or_raise(
                selected_cluster.cluster_id,
                self._normalized_database_roles(request.database_roles)
            )
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
                        for selected_database_role in selected_database_roles:
                            self._grant_database_role(
                                cur,
                                request.username,
                                selected_database_role.database_role,
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
                    "database_user": request.username,
                    "database_roles": [
                        database_role.database_role
                        for database_role in selected_database_roles
                    ],
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
                {"cluster_id": selected_cluster.cluster_id, "database_user": username},
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Database user removal is temporarily unavailable.",
                fallback_message=f"Unable to remove database user '{username}'.",
            ) from err

    def revoke_database_user_roles(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
        username: str,
        database_roles: list[str],
        requested_by: str,
    ) -> None:
        selected_cluster = self._get_cluster_or_raise(
            cluster_id,
            groups,
            is_admin,
        )
        try:
            selected_database_roles = self._get_database_roles_or_raise(
                selected_cluster.cluster_id,
                self._normalized_database_roles(database_roles)
            )
            try:
                with connect_cluster_db(
                    self._get_primary_dns_address(selected_cluster),
                    self._get_cluster_db_password(selected_cluster),
                ) as conn:
                    with conn.cursor() as cur:
                        for selected_database_role in selected_database_roles:
                            cur.execute(
                                sql.SQL("REVOKE {} FROM {}").format(
                                    sql.Identifier(
                                        selected_database_role.database_role
                                    ),
                                    sql.Identifier(username),
                                )
                            )
            except Exception as err:
                logger.debug(
                    "Cluster user query failed [operation=cluster_users.revoke_database_user_roles]"
                )
                raise translate_database_error(
                    err, "cluster_users.revoke_database_user_roles"
                ) from err
            log_event(
                self.repo,
                requested_by,
                AuditEvent.DB_USER_ROLE_REVOKED,
                {
                    "cluster_id": selected_cluster.cluster_id,
                    "database_user": username,
                    "database_roles": [
                        database_role.database_role
                        for database_role in selected_database_roles
                    ],
                },
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Database role updates are temporarily unavailable.",
                fallback_message=f"Unable to revoke roles from '{username}'.",
            ) from err

    def grant_database_user_roles(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
        username: str,
        database_roles: list[str],
        requested_by: str,
    ) -> None:
        selected_cluster = self._get_cluster_or_raise(
            cluster_id,
            groups,
            is_admin,
        )
        try:
            selected_database_roles = self._get_database_roles_or_raise(
                selected_cluster.cluster_id,
                self._normalized_database_roles(database_roles)
            )
            try:
                with connect_cluster_db(
                    self._get_primary_dns_address(selected_cluster),
                    self._get_cluster_db_password(selected_cluster),
                ) as conn:
                    with conn.cursor() as cur:
                        for selected_database_role in selected_database_roles:
                            self._grant_database_role(
                                cur,
                                username,
                                selected_database_role.database_role,
                            )
            except Exception as err:
                logger.debug(
                    "Cluster user query failed [operation=cluster_users.grant_database_user_roles]"
                )
                raise translate_database_error(
                    err, "cluster_users.grant_database_user_roles"
                ) from err
            log_event(
                self.repo,
                requested_by,
                AuditEvent.DB_USER_ROLE_GRANTED,
                {
                    "cluster_id": selected_cluster.cluster_id,
                    "database_user": username,
                    "database_roles": [
                        database_role.database_role
                        for database_role in selected_database_roles
                    ],
                },
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Database role updates are temporarily unavailable.",
                fallback_message=f"Unable to grant roles to '{username}'.",
            ) from err

    def sync_cluster_database_roles(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
        requested_by: str,
    ) -> int:
        selected_cluster = self._get_cluster_or_raise(cluster_id, groups, is_admin)
        try:
            templates = self.repo.list_database_role_templates()
            if not templates:
                return 0

            synced = 0
            try:
                with connect_cluster_db(
                    self._get_primary_dns_address(selected_cluster),
                    self._get_cluster_db_password(selected_cluster),
                ) as conn:
                    with conn.cursor() as cur:
                        databases = self._list_user_databases(cur)
                        for database_name in databases:
                            schemas = self._list_user_schemas(cur, database_name)
                            for template in templates:
                                targets = self._targets_for_template(
                                    database_name,
                                    schemas,
                                    template,
                                )
                                for schema_name, database_role in targets:
                                    stmt = sql.SQL(template.sql_statement).format(
                                        database_role=sql.Identifier(database_role),
                                        role=sql.Identifier(database_role),
                                        database_name=sql.Identifier(database_name),
                                        database=sql.Identifier(database_name),
                                        schema_name=sql.Identifier(schema_name)
                                        if schema_name
                                        else sql.SQL(""),
                                        schema=sql.Identifier(schema_name)
                                        if schema_name
                                        else sql.SQL(""),
                                    )
                                    cur.execute(stmt)
                                    self.repo.upsert_cluster_database_role(
                                        ClusterDatabaseRole(
                                            cluster_id=selected_cluster.cluster_id,
                                            database_name=database_name,
                                            schema_name=schema_name,
                                            database_role=database_role,
                                            database_role_template=template.database_role_template,
                                            scope_type=template.scope_type,
                                            sql_statement=stmt.as_string(conn),
                                        )
                                    )
                                    synced += 1
            except RepositoryError:
                raise
            except Exception as err:
                logger.debug(
                    "Cluster role sync failed [operation=cluster_users.sync_cluster_database_roles]"
                )
                raise translate_database_error(
                    err, "cluster_users.sync_cluster_database_roles"
                ) from err

            log_event(
                self.repo,
                requested_by,
                AuditEvent.DATABASE_ROLE_CREATED,
                {
                    "cluster_id": selected_cluster.cluster_id,
                    "database_roles_synced": synced,
                },
            )
            return synced
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Database role sync is temporarily unavailable.",
                validation_message="Database role templates or cluster objects are invalid.",
                fallback_message=f"Unable to sync database roles for cluster '{cluster_id}'.",
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
                {"cluster_id": selected_cluster.cluster_id, "database_user": username},
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

    @staticmethod
    def _normalized_database_roles(
        database_roles: list[str] | None,
    ) -> list[str]:
        normalized_database_roles = []
        for database_role in database_roles or []:
            normalized_database_role = str(database_role or "").strip()
            if (
                normalized_database_role
                and normalized_database_role not in normalized_database_roles
            ):
                normalized_database_roles.append(normalized_database_role)
        return normalized_database_roles

    def _get_database_roles_or_raise(
        self, cluster_id: str, database_roles: list[str]
    ) -> list[ClusterDatabaseRole]:
        if not database_roles:
            return []

        selected_database_roles = []
        for database_role in database_roles:
            selected_database_role = self.repo.get_cluster_database_role(
                cluster_id, database_role
            )
            if selected_database_role is None:
                raise ServiceValidationError(
                    f"Database role '{database_role}' is not configured for this cluster."
                )
            selected_database_roles.append(selected_database_role)
        return selected_database_roles

    @staticmethod
    def _list_user_databases(cur) -> list[str]:
        rows = cur.execute("SHOW DATABASES").fetchall()
        databases = []
        for row in rows:
            database_name = str(row[0] if isinstance(row, tuple) else row).strip()
            if database_name and database_name not in SYSTEM_DATABASES:
                databases.append(database_name)
        return databases

    @staticmethod
    def _list_user_schemas(cur, database_name: str) -> list[str]:
        cur.execute(
            sql.SQL("SHOW SCHEMAS FROM DATABASE {}").format(
                sql.Identifier(database_name)
            )
        )
        rows = cur.fetchall()
        schemas = []
        for row in rows:
            schema_name = str(row[0] if isinstance(row, tuple) else row).strip()
            if schema_name and schema_name not in SYSTEM_SCHEMAS:
                schemas.append(schema_name)
        return schemas

    def _targets_for_template(
        self,
        database_name: str,
        schemas: list[str],
        template: DatabaseRoleTemplateConfig,
    ) -> list[tuple[str | None, str]]:
        if template.scope_type == "database":
            return [
                (
                    None,
                    self._generated_database_role_name(
                        database_name,
                        None,
                        template.database_role_template,
                    ),
                )
            ]
        return [
            (
                schema_name,
                self._generated_database_role_name(
                    database_name,
                    schema_name,
                    template.database_role_template,
                ),
            )
            for schema_name in schemas
        ]

    @staticmethod
    def _generated_database_role_name(
        database_name: str,
        schema_name: str | None,
        template_name: str,
    ) -> str:
        parts = [database_name]
        if schema_name:
            parts.append(schema_name)
        parts.append(template_name)
        role_name = "_".join(parts).lower()
        role_name = re.sub(r"[^a-z0-9_]+", "_", role_name)
        role_name = re.sub(r"_+", "_", role_name).strip("_")
        if not role_name:
            raise ServiceValidationError("Generated database role name is invalid.")
        return role_name

    @staticmethod
    def _grant_database_role(cur, username: str, database_role: str) -> None:
        cur.execute(
            sql.SQL("GRANT {} TO {}").format(
                sql.Identifier(database_role),
                sql.Identifier(username),
            )
        )
