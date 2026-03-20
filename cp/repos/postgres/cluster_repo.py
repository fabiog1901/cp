"""Cluster repository backed by CockroachDB/Postgres."""

from ...models import Cluster, ClusterOverview, CpuCountOption, DiskSizeOption, InventoryLB, InventoryRegion, Job, NodeCountOption, Region, RegionOption, Version
from . import admin_queries, cluster_queries, job_queries


def list_clusters(groups: list[str], is_admin: bool = False) -> list[ClusterOverview]:
    return cluster_queries.fetch_all_clusters(groups, is_admin)


def get_cluster(
    cluster_id: str,
    groups: list[str],
    is_admin: bool = False,
) -> Cluster | None:
    return cluster_queries.get_cluster(cluster_id, groups, is_admin)


def get_running_clusters() -> list[Cluster]:
    return cluster_queries.get_running_clusters()


def create_or_update_cluster(
    cluster_id: str,
    status: str,
    created_by: str,
    grp: str,
    version: str,
    node_cpus: int,
    node_count: int,
    disk_size: int,
) -> None:
    cluster_queries.upsert_cluster(
        cluster_id,
        status,
        created_by,
        grp,
        version,
        node_cpus,
        node_count,
        disk_size,
    )


def update_cluster(
    cluster_id: str,
    updated_by: str,
    cluster_inventory: list[InventoryRegion] | None = None,
    lbs_inventory: list[InventoryLB] | None = None,
    version: str | None = None,
    node_count: int | None = None,
    node_cpus: int | None = None,
    disk_size: int | None = None,
    status: str | None = None,
    grp: str | None = None,
) -> None:
    cluster_queries.update_cluster(
        cluster_id=cluster_id,
        updated_by=updated_by,
        cluster_inventory=cluster_inventory,
        lbs_inventory=lbs_inventory,
        version=version,
        node_count=node_count,
        node_cpus=node_cpus,
        disk_size=disk_size,
        status=status,
        grp=grp,
    )


def delete_cluster(cluster_id: str) -> None:
    cluster_queries.delete_cluster(cluster_id)


def list_cluster_jobs(cluster_id: str) -> list[Job]:
    return job_queries.get_all_linked_jobs(cluster_id)


def list_regions() -> list[RegionOption]:
    return admin_queries.get_regions()


def get_region_config(cloud: str, region: str) -> list[Region]:
    return admin_queries.get_region(cloud, region)


def list_versions() -> list[Version]:
    return admin_queries.get_versions()


def list_upgrade_versions(major_version: str) -> list[Version]:
    return admin_queries.get_upgrade_versions(major_version)


def list_node_counts() -> list[NodeCountOption]:
    return admin_queries.get_node_counts()


def list_cpus_per_node() -> list[CpuCountOption]:
    return admin_queries.get_cpus_per_node()


def list_disk_sizes() -> list[DiskSizeOption]:
    return admin_queries.get_disk_sizes()
