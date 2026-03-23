"""Cluster jobs repository backed by CockroachDB/Postgres."""

from ...infra.db import fetch_all
from ...models import Job

from ..base import BaseRepo

class ClusterJobsRepo(BaseRepo):
    def list_cluster_jobs(self, cluster_id: str) -> list[Job]:
        return fetch_all(
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
