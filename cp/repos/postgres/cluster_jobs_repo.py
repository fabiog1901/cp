"""Cluster jobs repository backed by CockroachDB/Postgres."""

from ...models import Job
from . import job_queries


def list_cluster_jobs(cluster_id: str) -> list[Job]:
    return job_queries.get_all_linked_jobs(cluster_id)
