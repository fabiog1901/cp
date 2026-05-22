"""Remote debug zip polling worker.

This worker polls the remote status file for a long-running CockroachDB debug
zip collection and reconciles CP job/artifact metadata.
"""

import datetime as dt
import logging

from ...infra import get_repo
from ...models import (
    CommandType,
    JobArtifactState,
    JobArtifactUpdate,
    JobState,
    PlaybookName,
    PollDebugZipCommand,
)
from .ansible import MyRunner

logger = logging.getLogger(__name__)

DEBUG_ZIP_POLL_INTERVAL_SECONDS = 60
DEBUG_ZIP_MAX_POLL_ATTEMPTS = 1440
DEBUG_ZIP_POLL_TASK_ID_OFFSET = 1000
DEBUG_ZIP_READY_STATES = {"READY", "SUCCEEDED", "SUCCESS", "COMPLETED", "DONE"}
DEBUG_ZIP_FAILED_STATES = {"FAILED", "FAILURE", "ERROR"}
DEBUG_ZIP_RUNNING_STATES = {"RUNNING", "PENDING", "STARTING", "UPLOADING"}


def poll_debug_zip(
    _msg_id: int,
    command: PollDebugZipCommand,
    requested_by: str,
) -> None:
    repo = get_repo()

    try:
        if command.poll_attempt > DEBUG_ZIP_MAX_POLL_ATTEMPTS:
            _fail_debug_zip(
                command,
                requested_by,
                "Debug zip polling exceeded the maximum number of attempts.",
                task_id_counter=command.poll_attempt * DEBUG_ZIP_POLL_TASK_ID_OFFSET,
            )
            return

        task_id_counter = command.poll_attempt * DEBUG_ZIP_POLL_TASK_ID_OFFSET
        runner_result = MyRunner(command.cp_job_id, task_id_counter).launch_runner(
            PlaybookName.POLL_DEBUG_ZIP,
            {
                "cluster_id": command.cluster_id,
                "cp_job_id": command.cp_job_id,
                "artifact_id": command.artifact_id,
                "remote_host": command.remote_host,
                "remote_status_path": command.remote_status_path,
                "remote_user": command.remote_user,
                "poll_attempt": command.poll_attempt,
            },
        )

        if runner_result.status != "successful":
            _requeue_poll(command, requested_by, runner_result.data)
            return

        status = _status_from_runner_data(runner_result.data)

        if status in DEBUG_ZIP_READY_STATES:
            repo.update_job_artifact(
                command.artifact_id,
                JobArtifactUpdate(
                    status=JobArtifactState.READY,
                    size_bytes=_optional_int(runner_result.data.get("size_bytes")),
                    sha256=_optional_str(runner_result.data.get("sha256")),
                    metadata=_artifact_metadata(command, runner_result.data),
                    expires_at=_optional_datetime(
                        runner_result.data.get("expires_at")
                    ),
                    updated_by=requested_by,
                ),
            )
            repo.update_job(command.cp_job_id, JobState.COMPLETED)
            repo.create_task(
                command.cp_job_id,
                runner_result.task_id_counter,
                dt.datetime.now(dt.timezone.utc),
                "DEBUG_ZIP_READY",
                "Debug zip artifact is ready for download.",
            )
            return

        if status in DEBUG_ZIP_FAILED_STATES:
            _fail_debug_zip(
                command,
                requested_by,
                _optional_str(runner_result.data.get("error"))
                or "Debug zip collection failed.",
                runner_result.data,
                runner_result.task_id_counter,
            )
            return

        if status not in DEBUG_ZIP_RUNNING_STATES:
            logger.warning(
                "Debug zip poll for artifact %s returned unknown status '%s'",
                command.artifact_id,
                status,
            )

        _requeue_poll(command, requested_by, runner_result.data)
    except Exception as err:
        logger.exception(
            "Unhandled error while polling debug zip artifact '%s'",
            command.artifact_id,
        )
        _fail_debug_zip(
            command,
            requested_by,
            str(err),
            task_id_counter=command.poll_attempt * DEBUG_ZIP_POLL_TASK_ID_OFFSET,
        )


def _requeue_poll(
    command: PollDebugZipCommand,
    requested_by: str,
    runner_data: dict,
) -> None:
    repo = get_repo()
    repo.update_job(command.cp_job_id, JobState.RUNNING)
    repo.update_job_artifact(
        command.artifact_id,
        JobArtifactUpdate(
            status=JobArtifactState.RUNNING,
            metadata=_artifact_metadata(command, runner_data),
            updated_by=requested_by,
        ),
    )
    repo.enqueue_message(
        CommandType.POLL_DEBUG_ZIP,
        PollDebugZipCommand(
            cluster_id=command.cluster_id,
            cp_job_id=command.cp_job_id,
            artifact_id=command.artifact_id,
            remote_host=command.remote_host,
            remote_status_path=command.remote_status_path,
            remote_user=command.remote_user,
            poll_attempt=command.poll_attempt + 1,
        ),
        requested_by,
        start_after_seconds=DEBUG_ZIP_POLL_INTERVAL_SECONDS,
    )


def _fail_debug_zip(
    command: PollDebugZipCommand,
    requested_by: str,
    message: str,
    runner_data: dict | None = None,
    task_id_counter: int = 0,
) -> None:
    repo = get_repo()
    repo.update_job_artifact(
        command.artifact_id,
        JobArtifactUpdate(
            status=JobArtifactState.FAILED,
            metadata=_artifact_metadata(command, runner_data or {}, error=message),
            updated_by=requested_by,
        ),
    )
    repo.update_job(command.cp_job_id, JobState.FAILED)
    repo.create_task(
        command.cp_job_id,
        task_id_counter,
        dt.datetime.now(dt.timezone.utc),
        "DEBUG_ZIP_FAILED",
        message,
    )


def _status_from_runner_data(data: dict) -> str:
    return str(data.get("status") or "RUNNING").strip().upper()


def _artifact_metadata(
    command: PollDebugZipCommand,
    runner_data: dict,
    *,
    error: str | None = None,
) -> dict:
    metadata = (
        runner_data.get("metadata")
        if isinstance(runner_data.get("metadata"), dict)
        else {}
    )
    result = metadata | {
        "runner_data": runner_data,
        "remote_host": command.remote_host,
        "remote_status_path": command.remote_status_path,
        "remote_user": command.remote_user,
        "poll_attempt": command.poll_attempt,
    }
    if error:
        result["error"] = error
    return result


def _optional_str(value) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    if value == "" or value.lower() in {"none", "null"}:
        return None
    return value


def _optional_int(value) -> int | None:
    value = _optional_str(value)
    if value is None:
        return None
    return int(value)


def _optional_datetime(value) -> dt.datetime | None:
    value = _optional_str(value)
    if value is None:
        return None
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
