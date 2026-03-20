"""Business logic for the jobs vertical."""

import yaml

from ..models import Job, JobID, JobType
from ..repos.postgres import event_repo, jobs_repo, mq_repo


def list_visible_jobs(groups: list[str], is_admin: bool) -> list[Job]:
    return jobs_repo.list_jobs(groups, is_admin)


def get_job_for_user(job_id: int, groups: list[str], is_admin: bool) -> Job | None:
    return jobs_repo.get_job(job_id, groups, is_admin)


def get_job_details_for_user(job_id: int, groups: list[str], is_admin: bool) -> dict | None:
    job = get_job_for_user(job_id, groups, is_admin)
    if job is None:
        return None

    return {
        "job": job,
        "description_yaml": yaml.dump(job.description),
        "tasks": jobs_repo.list_tasks(job_id),
        "linked_clusters": jobs_repo.list_linked_clusters(job_id),
    }


def request_job_reschedule(
    job_id: int,
    groups: list[str],
    is_admin: bool,
    requested_by: str,
) -> int:
    job = get_job_for_user(job_id, groups, is_admin)
    if job is None:
        raise ValueError(f"Job {job_id} was not found")

    job_type = (
        JobType.RECREATE_CLUSTER
        if job.job_type == JobType.CREATE_CLUSTER
        else job.job_type
    )

    msg_id: JobID = mq_repo.insert_into_mq(
        job_type,
        job.description,
        requested_by,
    )
    event_repo.insert_event_log(
        requested_by,
        job_type,
        job.description | {"job_id": msg_id.job_id},
    )
    return msg_id.job_id
