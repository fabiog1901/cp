"""Cluster repository."""

from pydantic import TypeAdapter

from ..infra.db import execute_stmt, fetch_all, fetch_one
from ..models import (
    Cluster,
    ClusterOverview,
    ClusterState,
    ClusterStatsResponse,
    InventoryLB,
    InventoryRegion,
    Nodes,
)


class ClusterRepo:
    def get_cluster_stats(
        self,
        groups: list[str],
        is_admin: bool = False,
    ) -> ClusterStatsResponse:
        params: tuple = ()
        where_clause = ""
        operation = "cluster.get_cluster_stats.admin"
        if not is_admin:
            where_clause = "WHERE grp = ANY (%s)"
            params = (groups,)
            operation = "cluster.get_cluster_stats"

        return (
            fetch_one(
                f"""
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(CASE WHEN status = %s THEN 1 ELSE 0 END), 0) AS active,
                COALESCE(SUM(CASE WHEN status = %s THEN 1 ELSE 0 END), 0) AS creating,
                COALESCE(SUM(CASE WHEN status = %s THEN 1 ELSE 0 END), 0) AS unhealthy,
                COALESCE(
                    SUM(
                        CASE
                            WHEN status IN (%s, %s, %s, %s, %s)
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS failed
            FROM clusters
            {where_clause}
            """,
                (
                    ClusterState.ACTIVE.value,
                    ClusterState.CREATING.value,
                    ClusterState.UNHEALTHY.value,
                    ClusterState.CREATE_FAILED.value,
                    ClusterState.SCALE_FAILED.value,
                    ClusterState.RESTORE_FAILED.value,
                    ClusterState.DELETE_FAILED.value,
                    ClusterState.UPGRADE_FAILED.value,
                    *params,
                ),
                ClusterStatsResponse,
                operation=operation,
            )
            or ClusterStatsResponse(
                total=0,
                active=0,
                creating=0,
                unhealthy=0,
                failed=0,
            )
        )

    def list_clusters(
        self,
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

    def get_cluster(
        self,
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

    def list_active_clusters(self) -> list[Cluster]:
        return fetch_all(
            """
            SELECT *
            FROM clusters
            WHERE status = %s
            ORDER BY created_at ASC
            """,
            (ClusterState.ACTIVE.value,),
            Cluster,
            operation="cluster.list_active_clusters",
        )

    def upsert_cluster(
        self,
        cluster_id: str,
        status: str,
        created_by: str,
        grp: str,
        version: str,
        node_cpus: int,
        node_count: int,
        disk_size: int,
        password: bytes | None = None,
    ) -> None:
        execute_stmt(
            """
            UPSERT INTO clusters
                (cluster_id, status,
                created_by, updated_by, grp,
                version, node_cpus, node_count, disk_size, password)
            VALUES
                (%s, %s, %s, %s, %s,
                 %s, %s, %s, %s, %s)
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
                password,
            ),
            operation="cluster.upsert_cluster",
        )

    def update_cluster(
        self,
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
        password: bytes | None = None,
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
                password = coalesce(%s, password),
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
                password,
                updated_by,
                cluster_id,
            ),
            operation="cluster.update_cluster",
        )

    def delete_cluster(self, cluster_id: str) -> None:
        execute_stmt(
            """
            DELETE FROM clusters
            WHERE cluster_id = %s
            """,
            (cluster_id,),
            operation="cluster.delete_cluster",
        )

    def list_cluster_nodes(self) -> list[Nodes]:
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
            operation="cluster.list_cluster_nodes",
        )
