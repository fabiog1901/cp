"""Cluster jobs repository."""

from cpkit.db import fetch_all
from cpkit.jobs import JOB_CLUSTER_MAP_TABLE, JOBS_TABLE

from ..models import Job


class ClusterJobsRepo:
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
