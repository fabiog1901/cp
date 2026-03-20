"""Versions repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt
from ...models import CpuCountOption, DiskSizeOption, NodeCountOption
from ...models import Version
from .common import convert_model_to_sql


def list_versions() -> list[Version]:
    return execute_stmt(
        """
        SELECT version
        FROM versions
        ORDER BY version DESC
        """,
        (),
        Version,
    )


def add_version(version: Version) -> None:
    stmt, vals = convert_model_to_sql("versions", version)
    execute_stmt(stmt, vals)


def remove_version(version: str) -> None:
    execute_stmt(
        """
        DELETE
        FROM versions
        WHERE version = %s
        """,
        (version,),
    )


def list_upgrade_versions(major_version: str) -> list[Version]:
    return execute_stmt(
        """
        SELECT version
        FROM versions
        WHERE version > %s
        ORDER BY version ASC
        """,
        (major_version,),
        Version,
    )


def list_node_counts() -> list[NodeCountOption]:
    return execute_stmt(
        """
        SELECT nodes AS node_count
        FROM nodes_per_region
        ORDER BY nodes ASC
        """,
        (),
        NodeCountOption,
    )


def list_cpus_per_node() -> list[CpuCountOption]:
    return execute_stmt(
        """
        SELECT cpus AS cpu_count
        FROM cpus_per_node
        ORDER BY cpus ASC
        """,
        (),
        CpuCountOption,
    )


def list_disk_sizes() -> list[DiskSizeOption]:
    return execute_stmt(
        """
        SELECT size_gb
        FROM disk_sizes
        ORDER BY size_gb
        """,
        (),
        DiskSizeOption,
    )
