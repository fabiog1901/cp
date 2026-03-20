"""Cluster jobs repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt
from ...models import Job


def list_cluster_jobs(cluster_id: str) -> list[Job]:
    return execute_stmt(
        """
        WITH
        cluster_jobs AS (
            SELECT job_id
            FROM map_clusters_jobs
            WHERE cluster_id = %s
        )
        SELECT *
        FROM jobs
        WHERE job_id IN (SELECT job_id FROM cluster_jobs)
        ORDER BY created_at DESC
        """,
        (cluster_id,),
        Job,
    )
