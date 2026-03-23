"""Versions repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all
from ...models import CpuCountOption, DiskSizeOption, NodeCountOption
from ...models import Version
from ..base import BaseRepo
from .common import convert_model_to_sql

class VersionsRepo(BaseRepo):
    def list_versions(self) -> list[Version]:
        return fetch_all(
            """
            SELECT version
            FROM versions
            ORDER BY version DESC
            """,
            (),
            Version,
        )

    def add_version(self, version: Version) -> None:
        stmt, vals = convert_model_to_sql("versions", version)
        execute_stmt(stmt, vals)

    def remove_version(self, version: str) -> None:
        execute_stmt(
            """
            DELETE
            FROM versions
            WHERE version = %s
            """,
            (version,),
        )

    def list_upgrade_versions(self, major_version: str) -> list[Version]:
        return fetch_all(
            """
            SELECT version
            FROM versions
            WHERE version > %s
            ORDER BY version ASC
            """,
            (major_version,),
            Version,
        )

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
