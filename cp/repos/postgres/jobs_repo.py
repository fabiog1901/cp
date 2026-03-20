"""Jobs repository backed by CockroachDB/Postgres."""

from ...models import ClusterIDRef, Job, Task
from . import job_queries


def list_jobs(groups: list[str], is_admin: bool = False) -> list[Job]:
    return job_queries.fetch_all_jobs(groups, is_admin)


def get_job(job_id: int, groups: list[str], is_admin: bool = False) -> Job | None:
    return job_queries.fetch_job(job_id, groups, is_admin)


def list_tasks(job_id: int) -> list[Task]:
    return job_queries.get_all_tasks(job_id)


def list_linked_clusters(job_id: int) -> list[ClusterIDRef]:
    return job_queries.get_linked_clusters_from_job(job_id)


def insert_mapped_job(cluster_id: str, job_id: int, status: str) -> None:
    job_queries.insert_mapped_job(cluster_id, job_id, status)


def update_job(job_id: int, status: str) -> None:
    job_queries.update_job(job_id, status)


def fail_zombie_jobs():
    return job_queries.fail_zombie_jobs()


def insert_task(job_id: int, task_id: int, created_at, task_name: str, task_desc) -> None:
    job_queries.insert_task(job_id, task_id, created_at, task_name, task_desc)
