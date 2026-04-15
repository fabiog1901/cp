"""Admin cluster options repository backed by CockroachDB/Postgres."""

from ....infra.db import execute_stmt, fetch_all
from ....models import CpuCountOption, DiskSizeOption, NodeCountOption
from ..common import convert_model_to_sql
from .base import AdminPostgresRepo


class ClusterOptionsRepo(AdminPostgresRepo):
    def list_node_counts(self) -> list[NodeCountOption]:
        return fetch_all(
            """
            SELECT nodes AS node_count
            FROM nodes_per_region
            ORDER BY nodes ASC
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
            WHERE nodes = %s
            """,
            (node_count,),
        )

    def list_cpus_per_node(self) -> list[CpuCountOption]:
        return fetch_all(
            """
            SELECT cpus AS cpu_count
            FROM cpus_per_node
            ORDER BY cpus ASC
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
            WHERE cpus = %s
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
