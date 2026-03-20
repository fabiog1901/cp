"""Jobs repository backed by CockroachDB/Postgres."""

from ...models import ClusterIDRef, Job, Task
from . import repository


def list_jobs(groups: list[str], is_admin: bool = False) -> list[Job]:
    return repository.fetch_all_jobs(groups, is_admin)


def get_job(job_id: int, groups: list[str], is_admin: bool = False) -> Job | None:
    return repository.fetch_job(job_id, groups, is_admin)


def list_tasks(job_id: int) -> list[Task]:
    return repository.get_all_tasks(job_id)


def list_linked_clusters(job_id: int) -> list[ClusterIDRef]:
    return repository.get_linked_clusters_from_job(job_id)
