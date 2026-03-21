"""Cluster repository backed by CockroachDB/Postgres."""

from pydantic import TypeAdapter

from ...infra.db import execute_stmt, fetch_all, fetch_one
from ...models import (
    Cluster,
    ClusterOverview,
    CpuCountOption,
    DiskSizeOption,
    InventoryLB,
    InventoryRegion,
    Job,
    NodeCountOption,
    Nodes,
    Region,
    RegionOption,
    Version,
)
from .cluster_jobs_repo import ClusterJobsRepo
from .regions_repo import RegionsRepo
from .versions_repo import VersionsRepo


class ClusterRepo:
    @staticmethod
    def list_clusters(
        groups: list[str],
        is_admin: bool = False,
    ) -> list[ClusterOverview]:
        if is_admin:
            return fetch_all(
                """
                SELECT cluster_id, grp,
                    created_by, status,
                    version, node_count,
                    node_cpus, disk_size
                FROM clusters
                ORDER BY created_at DESC
                """,
                (),
                ClusterOverview,
                operation="cluster.list_clusters.admin",
            )

        return fetch_all(
            """
            SELECT cluster_id, grp,
                created_by, status,
                version, node_count,
                node_cpus, disk_size
            FROM clusters
            WHERE grp = ANY (%s)
            ORDER BY created_at DESC
            """,
            (groups,),
            ClusterOverview,
            operation="cluster.list_clusters",
        )

    @staticmethod
    def get_cluster(
        cluster_id: str,
        groups: list[str],
        is_admin: bool = False,
    ) -> Cluster | None:
        if is_admin:
            return fetch_one(
                """
                SELECT *
                FROM clusters
                WHERE cluster_id = %s
                """,
                (cluster_id,),
                Cluster,
                operation="cluster.get_cluster.admin",
            )

        return fetch_one(
            """
            SELECT *
            FROM clusters
            WHERE grp = ANY (%s)
                AND cluster_id = %s
            """,
            (groups, cluster_id),
            Cluster,
            operation="cluster.get_cluster",
        )

    @staticmethod
    def get_running_clusters() -> list[Cluster]:
        return fetch_all(
            """
            SELECT *
            FROM clusters
            WHERE status = 'RUNNING'
            ORDER BY created_at ASC
            """,
            (),
            Cluster,
            operation="cluster.get_running_clusters",
        )

    @staticmethod
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
        execute_stmt(
            """
            UPSERT INTO clusters
                (cluster_id, status,
                created_by, updated_by, grp,
                version, node_cpus, node_count, disk_size)
            VALUES
                (%s, %s, %s, %s, %s,
                 %s, %s, %s, %s)
            """,
            (
                cluster_id,
                status,
                created_by,
                created_by,
                grp,
                version,
                node_cpus,
                node_count,
                disk_size,
            ),
            operation="cluster.create_or_update_cluster",
        )

    @staticmethod
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
        execute_stmt(
            """
            UPDATE clusters SET
                cluster_inventory = coalesce(%s, cluster_inventory),
                lbs_inventory = coalesce(%s, lbs_inventory),
                version = coalesce(%s, version),
                node_count = coalesce(%s, node_count),
                node_cpus = coalesce(%s, node_cpus),
                disk_size = coalesce(%s, disk_size),
                status = coalesce(%s, status),
                grp = coalesce(%s, grp),
                updated_by = coalesce(%s, updated_by)
            WHERE cluster_id = %s
            """,
            (
                TypeAdapter(list[InventoryRegion]).dump_python(cluster_inventory),
                TypeAdapter(list[InventoryLB]).dump_python(lbs_inventory),
                version,
                node_count,
                node_cpus,
                disk_size,
                status,
                grp,
                updated_by,
                cluster_id,
            ),
            operation="cluster.update_cluster",
        )

    @staticmethod
    def delete_cluster(cluster_id: str) -> None:
        execute_stmt(
            """
            DELETE FROM clusters
            WHERE cluster_id = %s
            """,
            (cluster_id,),
            operation="cluster.delete_cluster",
        )

    @staticmethod
    def list_cluster_jobs(cluster_id: str) -> list[Job]:
        return ClusterJobsRepo.list_cluster_jobs(cluster_id)

    @staticmethod
    def list_regions() -> list[RegionOption]:
        return RegionsRepo.list_region_options()

    @staticmethod
    def get_region_config(cloud: str, region: str) -> list[Region]:
        return RegionsRepo.get_region_config(cloud, region)

    @staticmethod
    def list_versions() -> list[Version]:
        return VersionsRepo.list_versions()

    @staticmethod
    def list_upgrade_versions(major_version: str) -> list[Version]:
        return VersionsRepo.list_upgrade_versions(major_version)

    @staticmethod
    def list_node_counts() -> list[NodeCountOption]:
        return VersionsRepo.list_node_counts()

    @staticmethod
    def list_cpus_per_node() -> list[CpuCountOption]:
        return VersionsRepo.list_cpus_per_node()

    @staticmethod
    def list_disk_sizes() -> list[DiskSizeOption]:
        return VersionsRepo.list_disk_sizes()

    @staticmethod
    def get_nodes() -> list[Nodes]:
        return fetch_all(
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
            Nodes,
            operation="cluster.get_nodes",
        )
