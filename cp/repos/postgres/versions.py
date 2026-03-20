"""Versions repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all
from ...models import CpuCountOption, DiskSizeOption, NodeCountOption
from ...models import Version
from .common import convert_model_to_sql


def list_versions() -> list[Version]:
    return fetch_all(
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


def list_node_counts() -> list[NodeCountOption]:
    return fetch_all(
        """
        SELECT nodes AS node_count
        FROM nodes_per_region
        ORDER BY nodes ASC
        """,
        (),
        NodeCountOption,
    )


def list_cpus_per_node() -> list[CpuCountOption]:
    return fetch_all(
        """
        SELECT cpus AS cpu_count
        FROM cpus_per_node
        ORDER BY cpus ASC
        """,
        (),
        CpuCountOption,
    )


def list_disk_sizes() -> list[DiskSizeOption]:
    return fetch_all(
        """
        SELECT size_gb
        FROM disk_sizes
        ORDER BY size_gb
        """,
        (),
        DiskSizeOption,
    )
