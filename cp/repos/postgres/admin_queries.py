"""Admin/configuration queries for Postgres-backed repositories."""

from pydantic import BaseModel

from ...infra.db import execute_stmt
from ...models import (
    CpuCountOption,
    DiskSizeOption,
    NodeCountOption,
    Nodes,
    Playbook,
    PlaybookOverview,
    Region,
    RegionOption,
    RoleGroupMap,
    Setting,
    StrID,
    Version,
)
from .common import convert_model_to_sql


def get_regions() -> list[RegionOption]:
    return execute_stmt(
        """
        SELECT DISTINCT cloud || ':' || region AS region_id
        FROM regions
        ORDER BY region_id ASC
        """,
        (),
        RegionOption,
    )


def get_all_regions() -> list[Region]:
    return execute_stmt(
        """
        SELECT cloud, region, zone, vpc_id, security_groups, subnet, image, extras
        FROM regions
        """,
        (),
        Region,
    )


def get_region(cloud: str, region: str) -> list[Region]:
    return execute_stmt(
        """
        SELECT cloud, region, zone, vpc_id, security_groups, subnet, image, extras
        FROM regions
        WHERE (cloud, region) = (%s, %s)
        """,
        (cloud, region),
        Region,
    )


def add_region(r: Region) -> None:
    stmt, vals = convert_model_to_sql("regions", r)
    execute_stmt(stmt, vals)


def remove_region(
    cloud: str,
    region: str,
    zone: str,
) -> None:
    return execute_stmt(
        """
        DELETE FROM regions
        WHERE (cloud, region, zone) = (%s, %s, %s)
        """,
        (cloud, region, zone),
    )


def get_playbook(name: str, version: str) -> Playbook:
    return execute_stmt(
        """
        SELECT *
        FROM playbooks
        WHERE (name, version) = (%s, %s)
        """,
        (name, version),
        Playbook,
        return_list=False,
    )


def get_default_playbook(name: str) -> Playbook:
    return execute_stmt(
        """
        SELECT *
        FROM playbooks
        WHERE name = %s
        ORDER BY default_version DESC
        LIMIT 1
        """,
        (name,),
        Playbook,
        return_list=False,
    )


def get_playbook_versions(name: str) -> list[PlaybookOverview]:
    return execute_stmt(
        """
        SELECT name, version, default_version, created_at, created_by, updated_by
        FROM playbooks
        WHERE name = %s
        ORDER BY version DESC;
        """,
        (name,),
        PlaybookOverview,
        return_list=True,
    )


def add_playbook(
    name: str,
    playbook: str,
    created_by: str,
) -> PlaybookOverview:
    return execute_stmt(
        """
        INSERT INTO playbooks (name, playbook, created_by)
        VALUES (%s, %s, %s)
        RETURNING *
        """,
        (name, playbook, created_by),
        PlaybookOverview,
        return_list=False,
    )


def set_default_playbook(
    name: str,
    version: str,
    updated_by: str,
) -> None:
    execute_stmt(
        """
        UPDATE playbooks
        SET
            default_version = now(),
            updated_by = %s
        WHERE (name, version) = (%s, %s)
        """,
        (updated_by, name, version),
    )


def remove_playbook(name: str, version: str) -> None:
    execute_stmt(
        """
        DELETE
        FROM playbooks
        WHERE (name, version) = (%s, %s)
        """,
        (name, version),
    )


def get_versions() -> list[Version]:
    return execute_stmt(
        """
        SELECT version
        FROM versions
        ORDER BY version DESC
        """,
        (),
        Version,
    )


def add_version(v: BaseModel) -> None:
    stmt, vals = convert_model_to_sql("versions", v)
    execute_stmt(stmt, vals)


def remove_version(version) -> None:
    execute_stmt(
        """
        DELETE
        FROM versions
        WHERE version = %s
        """,
        (version,),
    )


def get_upgrade_versions(major_version: str) -> list[Version]:
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


def get_node_counts() -> list[NodeCountOption]:
    return execute_stmt(
        """
        SELECT nodes AS node_count
        FROM nodes_per_region
        ORDER BY nodes ASC
        """,
        (),
        NodeCountOption,
    )


def get_cpus_per_node() -> list[CpuCountOption]:
    return execute_stmt(
        """
        SELECT cpus AS cpu_count
        FROM cpus_per_node
        ORDER BY cpus ASC
        """,
        (),
        CpuCountOption,
    )


def get_disk_sizes() -> list[DiskSizeOption]:
    return execute_stmt(
        """
        SELECT size_gb
        FROM disk_sizes
        ORDER BY size_gb
        """,
        (),
        DiskSizeOption,
    )


def fetch_all_settings() -> list[Setting]:
    return execute_stmt(
        """
        SELECT *
        FROM settings
        """,
        (),
        Setting,
    )


def get_setting(setting: str) -> str:
    str_id: StrID = execute_stmt(
        """
        SELECT value AS id
        FROM settings
        WHERE id = %s
        """,
        (setting,),
        StrID,
        False,
    )
    return str_id.id


def update_setting(setting: str, value: str, updated_by) -> str:
    execute_stmt(
        """
        UPDATE settings
        SET value = %s,
        updated_by = %s
        WHERE id = %s
        """,
        (value, updated_by, setting),
    )


def get_secret(
    id: str,
) -> str:
    str_id: StrID = execute_stmt(
        """
        SELECT data AS id
        FROM secrets
        WHERE id = %s
        """,
        (id,),
        StrID,
        return_list=False,
    )
    return str_id.id


def get_role_to_groups_mappings() -> list[RoleGroupMap]:
    return execute_stmt(
        """
        SELECT role, groups
        FROM role_to_groups_mappings
        """,
        (),
        RoleGroupMap,
    )


def get_nodes() -> list[Nodes]:
    return execute_stmt(
        """
        WITH
        c AS (
        SELECT cluster_id, jsonb_array_elements(cluster_inventory) AS j
        FROM clusters
        ),
        x AS
        (
        SELECT cluster_id, jsonb_array_elements_text(j->'nodes') AS node
        FROM (SELECT cluster_id, j FROM c)
        )
        SELECT cluster_id, jsonb_agg(node) AS nodes
        FROM (SELECT * FROM x) AS OF SYSTEM TIME follower_read_timestamp()
        GROUP BY cluster_id;
        """,
        (),
        model=Nodes,
        return_list=True,
    )
