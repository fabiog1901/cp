"""Cluster jobs repository."""

from typing import Any

from cpkit.db import execute_stmt, fetch_all
from cpkit.jobs import JOBS_TABLE, LinkedResourceRef

from ..models import Job

JOB_CLUSTER_MAP_TABLE = "public.map_clusters_jobs"


class ClusterJobsRepo:
    @property
    def job_cluster_map_table(self) -> str:
        return JOB_CLUSTER_MAP_TABLE

    def list_cluster_jobs(self, cluster_id: str) -> list[Job]:
        return fetch_all(
            f"""
            WITH
            cluster_jobs AS (
                SELECT job_id
                FROM {JOB_CLUSTER_MAP_TABLE}
                WHERE cluster_id = %s
            )
            SELECT *
            FROM {JOBS_TABLE}
            WHERE job_id IN (SELECT job_id FROM cluster_jobs)
            ORDER BY created_at DESC
            """,
            (cluster_id,),
            Job,
        )

    def list_linked_resources(self, job_id: int) -> list[LinkedResourceRef]:
        return fetch_all(
            f"""
            SELECT
                'cluster' AS resource_type,
                cluster_id AS resource_id
            FROM {JOB_CLUSTER_MAP_TABLE}
            WHERE job_id = %s
            ORDER BY cluster_id
            """,
            (job_id,),
            LinkedResourceRef,
        )

    def link_job_to_cluster(self, cluster_id: str, job_id: int, status: Any) -> None:
        execute_stmt(
            f"""
            WITH
            create_job_linked AS (
                INSERT INTO {JOB_CLUSTER_MAP_TABLE}
                    (cluster_id, job_id)
                VALUES (%s, %s)
                RETURNING 1
            )
            UPDATE {JOBS_TABLE}
            SET status = %s
            WHERE job_id = %s
            """,
            (cluster_id, job_id, _message_type_value(status), job_id),
        )


def _message_type_value(value: Any) -> str:
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)
