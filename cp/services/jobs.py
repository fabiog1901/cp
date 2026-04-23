"""Business logic for the jobs vertical."""

import yaml

from ..infra.db import get_repo
from ..infra.errors import RepositoryError
from ..models import (
    AuditEvent,
    CommandType,
    Job,
    JobID,
    JobStatsResponse,
    parse_command_payload,
)
from ..repos import Repo
from .base import log_event
from .errors import ServiceNotFoundError, from_repository_error


class JobsService:
    def __init__(self, repo: Repo | None = None) -> None:
        self.repo = repo or get_repo()

    def list_visible_jobs(self, groups: list[str], is_admin: bool) -> list[Job]:
        try:
            return self.repo.list_jobs(groups, is_admin)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Jobs are temporarily unavailable.",
                fallback_message="Unable to load JobsRepo.",
            ) from err

    def get_visible_job_stats(
        self, groups: list[str], is_admin: bool
    ) -> JobStatsResponse:
        try:
            return self.repo.get_job_stats(groups, is_admin)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Job stats are temporarily unavailable.",
                fallback_message="Unable to load job stats.",
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

    def enqueue_job_reschedule(
        self,
        job_id: int,
        groups: list[str],
        is_admin: bool,
        requested_by: str,
    ) -> int:
        selected_job = self.get_job_for_user(job_id, groups, is_admin)
        if selected_job is None:
            raise ServiceNotFoundError(f"Job '{job_id}' was not found.")

        command_type = (
            CommandType.RECREATE_CLUSTER
            if selected_job.job_type == CommandType.CREATE_CLUSTER
            else selected_job.job_type
        )
        payload = parse_command_payload(command_type, selected_job.description)

        try:
            msg_id: JobID = self.repo.enqueue_command(
                command_type,
                payload,
                requested_by,
            )
            log_event(
                self.repo,
                requested_by,
                AuditEvent.JOB_RESCHEDULE_REQUESTED,
                payload.model_dump() | {"job_id": msg_id.job_id},
            )
            return msg_id.job_id
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Job rescheduling is temporarily unavailable.",
                validation_message="The job could not be rescheduled with its current payload.",
                fallback_message=f"Unable to reschedule job '{job_id}'.",
            ) from err
