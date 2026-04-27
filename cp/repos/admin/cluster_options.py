"""Admin cluster options repository."""

from ...infra.db import execute_stmt, fetch_all
from ...models import (
    ClusterDatabaseObject,
    ClusterDatabaseRole,
    CpuCountOption,
    DatabaseRoleTemplateConfig,
    DiskSizeOption,
    NodeCountOption,
)
from ..common import convert_model_to_sql
from .base import AdminRepo


class ClusterOptionsRepo(AdminRepo):
    def list_node_counts(self) -> list[NodeCountOption]:
        return fetch_all(
            """
            SELECT node_count
            FROM nodes_per_region
            ORDER BY node_count ASC
            """,
            (),
            NodeCountOption,
        )

    def create_node_count(self, node_count: NodeCountOption) -> None:
        stmt, vals = convert_model_to_sql("nodes_per_region", node_count)
        execute_stmt(stmt, vals)

    def delete_node_count(self, node_count: int) -> None:
        execute_stmt(
            """
            DELETE
            FROM nodes_per_region
            WHERE node_count = %s
            """,
            (node_count,),
        )

    def list_cpus_per_node(self) -> list[CpuCountOption]:
        return fetch_all(
            """
            SELECT cpu_count
            FROM cpus_per_node
            ORDER BY cpu_count ASC
            """,
            (),
            CpuCountOption,
        )

    def create_cpu_count(self, cpu_count: CpuCountOption) -> None:
        stmt, vals = convert_model_to_sql("cpus_per_node", cpu_count)
        execute_stmt(stmt, vals)

    def delete_cpu_count(self, cpu_count: int) -> None:
        execute_stmt(
            """
            DELETE
            FROM cpus_per_node
            WHERE cpu_count = %s
            """,
            (cpu_count,),
        )

    def list_disk_sizes(self) -> list[DiskSizeOption]:
        return fetch_all(
            """
            SELECT size_gb
            FROM disk_sizes
            ORDER BY size_gb
            """,
            (),
            DiskSizeOption,
        )

    def create_disk_size(self, disk_size: DiskSizeOption) -> None:
        stmt, vals = convert_model_to_sql("disk_sizes", disk_size)
        execute_stmt(stmt, vals)

    def delete_disk_size(self, size_gb: int) -> None:
        execute_stmt(
            """
            DELETE
            FROM disk_sizes
            WHERE size_gb = %s
            """,
            (size_gb,),
        )

    def list_database_role_templates(self) -> list[DatabaseRoleTemplateConfig]:
        return fetch_all(
            """
            SELECT database_role_template, scope_type, sql_statement
            FROM database_role_templates
            ORDER BY database_role_template ASC
            """,
            (),
            DatabaseRoleTemplateConfig,
        )

    def get_database_role_template(
        self, database_role_template: str
    ) -> DatabaseRoleTemplateConfig | None:
        database_role_templates = fetch_all(
            """
            SELECT database_role_template, scope_type, sql_statement
            FROM database_role_templates
            WHERE database_role_template = %s
            """,
            (database_role_template,),
            DatabaseRoleTemplateConfig,
        )
        return database_role_templates[0] if database_role_templates else None

    def create_database_role_template(
        self, database_role_template: DatabaseRoleTemplateConfig
    ) -> None:
        execute_stmt(
            """
            INSERT INTO database_role_templates (
                database_role_template,
                scope_type,
                sql_statement
            )
            VALUES (%s, %s, %s)
            """,
            (
                database_role_template.database_role_template,
                database_role_template.scope_type,
                database_role_template.sql_statement,
            ),
        )

    def delete_database_role_template(self, database_role_template: str) -> None:
        execute_stmt(
            """
            DELETE
            FROM database_role_templates
            WHERE database_role_template = %s
            """,
            (database_role_template,),
        )

    def list_cluster_database_objects(
        self, cluster_id: str
    ) -> list[ClusterDatabaseObject]:
        return fetch_all(
            """
            SELECT cluster_id, database_name, created_at, created_by,
                updated_at, updated_by
            FROM cluster_database_objects
            WHERE cluster_id = %s
            ORDER BY database_name ASC
            """,
            (cluster_id,),
            ClusterDatabaseObject,
        )

    def get_cluster_database_object(
        self, cluster_id: str, database_name: str
    ) -> ClusterDatabaseObject | None:
        database_objects = fetch_all(
            """
            SELECT cluster_id, database_name, created_at, created_by,
                updated_at, updated_by
            FROM cluster_database_objects
            WHERE cluster_id = %s AND database_name = %s
            """,
            (cluster_id, database_name),
            ClusterDatabaseObject,
        )
        return database_objects[0] if database_objects else None

    def upsert_cluster_database_object(
        self,
        cluster_id: str,
        database_name: str,
        updated_by: str,
    ) -> None:
        execute_stmt(
            """
            INSERT INTO cluster_database_objects (
                cluster_id,
                database_name,
                created_by,
                updated_by
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (cluster_id, database_name)
            DO UPDATE SET
                updated_by = excluded.updated_by,
                updated_at = now():::TIMESTAMPTZ
            """,
            (cluster_id, database_name, updated_by, updated_by),
        )

    def delete_cluster_database_object(
        self, cluster_id: str, database_name: str
    ) -> None:
        execute_stmt(
            """
            DELETE
            FROM cluster_database_objects
            WHERE cluster_id = %s AND database_name = %s
            """,
            (cluster_id, database_name),
        )

    def list_cluster_database_roles(self, cluster_id: str) -> list[ClusterDatabaseRole]:
        return fetch_all(
            """
            SELECT cluster_id, database_name, schema_name, database_role,
                database_role_template, scope_type, sql_statement
            FROM cluster_database_roles
            WHERE cluster_id = %s
            ORDER BY database_name ASC, schema_name ASC, database_role ASC
            """,
            (cluster_id,),
            ClusterDatabaseRole,
        )

    def get_cluster_database_role(
        self, cluster_id: str, database_role: str
    ) -> ClusterDatabaseRole | None:
        roles = fetch_all(
            """
            SELECT cluster_id, database_name, schema_name, database_role,
                database_role_template, scope_type, sql_statement
            FROM cluster_database_roles
            WHERE cluster_id = %s AND database_role = %s
            """,
            (cluster_id, database_role),
            ClusterDatabaseRole,
        )
        return roles[0] if roles else None

    def list_cluster_database_roles_for_database(
        self, cluster_id: str, database_name: str
    ) -> list[ClusterDatabaseRole]:
        return fetch_all(
            """
            SELECT cluster_id, database_name, schema_name, database_role,
                database_role_template, scope_type, sql_statement
            FROM cluster_database_roles
            WHERE cluster_id = %s AND database_name = %s
            ORDER BY schema_name ASC, database_role ASC
            """,
            (cluster_id, database_name),
            ClusterDatabaseRole,
        )

    def upsert_cluster_database_role(self, role: ClusterDatabaseRole) -> None:
        execute_stmt(
            """
            UPSERT INTO cluster_database_roles (
                cluster_id,
                database_name,
                schema_name,
                database_role,
                database_role_template,
                scope_type,
                sql_statement,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, now():::TIMESTAMPTZ)
            """,
            (
                role.cluster_id,
                role.database_name,
                role.schema_name,
                role.database_role,
                role.database_role_template,
                role.scope_type,
                role.sql_statement,
            ),
        )

    def delete_stale_cluster_database_roles(
        self, cluster_id: str, database_roles: list[str]
    ) -> None:
        if not database_roles:
            execute_stmt(
                """
                DELETE FROM cluster_database_roles
                WHERE cluster_id = %s
                """,
                (cluster_id,),
            )
            return

        placeholders = ", ".join(["%s"] * len(database_roles))
        execute_stmt(
            f"""
            DELETE FROM cluster_database_roles
            WHERE cluster_id = %s
            AND database_role NOT IN ({placeholders})
            """,
            (cluster_id, *database_roles),
        )
