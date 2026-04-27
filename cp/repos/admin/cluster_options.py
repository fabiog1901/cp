"""Admin cluster options repository."""

from ...infra.db import execute_stmt, fetch_all
from ...models import (
    CpuCountOption,
    DatabaseRoleConfig,
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

    def list_database_roles(self) -> list[DatabaseRoleConfig]:
        return fetch_all(
            """
            SELECT database_role, sql_statement
            FROM database_roles
            ORDER BY database_role ASC
            """,
            (),
            DatabaseRoleConfig,
        )

    def get_database_role(self, database_role: str) -> DatabaseRoleConfig | None:
        database_roles = fetch_all(
            """
            SELECT database_role, sql_statement
            FROM database_roles
            WHERE database_role = %s
            """,
            (database_role,),
            DatabaseRoleConfig,
        )
        return database_roles[0] if database_roles else None

    def create_database_role(self, database_role: DatabaseRoleConfig) -> None:
        execute_stmt(
            """
            INSERT INTO database_roles (database_role, sql_statement)
            VALUES (%s, %s)
            """,
            (database_role.database_role, database_role.sql_statement),
        )

    def delete_database_role(self, database_role: str) -> None:
        execute_stmt(
            """
            DELETE
            FROM database_roles
            WHERE database_role = %s
            """,
            (database_role,),
        )
