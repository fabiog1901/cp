"""Business logic for the jobs vertical."""

import yaml

from ..infra.errors import RepositoryError
from ..models import Job, JobID, JobType
from ..repos.base import BaseRepo
from .base import log_event
from .errors import ServiceNotFoundError, from_repository_error


class JobsService:
    def __init__(self, repo: BaseRepo) -> None:
        self.repo = repo

    def list_visible_jobs(self, groups: list[str], is_admin: bool) -> list[Job]:
        try:
            return self.repo.list_jobs(groups, is_admin)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Jobs are temporarily unavailable.",
                fallback_message="Unable to load JobsRepo.",
            ) from err

    def get_job_for_user(
        self,
        job_id: int,
        groups: list[str],
        is_admin: bool,
    ) -> Job | None:
        try:
            return self.repo.get_job(job_id, groups, is_admin)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Job details are temporarily unavailable.",
                fallback_message=f"Unable to load job '{job_id}'.",
            ) from err

    def get_job_details_for_user(
        self,
        job_id: int,
        groups: list[str],
        is_admin: bool,
    ) -> dict | None:
        selected_job = self.get_job_for_user(job_id, groups, is_admin)
        if selected_job is None:
            return None

        try:
            return {
                "job": selected_job,
                "description_yaml": yaml.dump(selected_job.description),
                "tasks": self.repo.list_tasks(job_id),
                "linked_clusters": self.repo.list_linked_clusters(job_id),
            }
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Job details are temporarily unavailable.",
                fallback_message=f"Unable to load tasks for job '{job_id}'.",
            ) from err

    def request_job_reschedule(
        self,
        job_id: int,
        groups: list[str],
        is_admin: bool,
        requested_by: str,
    ) -> int:
        selected_job = self.get_job_for_user(job_id, groups, is_admin)
        if selected_job is None:
            raise ServiceNotFoundError(f"Job '{job_id}' was not found.")

        job_type = (
            JobType.RECREATE_CLUSTER
            if selected_job.job_type == JobType.CREATE_CLUSTER
            else selected_job.job_type
        )

        try:
            msg_id: JobID = self.repo.insert_into_mq(
                job_type,
                selected_job.description,
                requested_by,
            )
            log_event(
                self.repo,
                requested_by,
                job_type,
                selected_job.description | {"job_id": msg_id.job_id},
            )
            return msg_id.job_id
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Job rescheduling is temporarily unavailable.",
                validation_message="The job could not be rescheduled with its current payload.",
                fallback_message=f"Unable to reschedule job '{job_id}'.",
            ) from err
