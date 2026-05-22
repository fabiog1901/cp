"""Remote debug zip polling worker.

This worker will poll a remote debug zip status file and reconcile CP job and
artifact metadata after the starter playbook launches the long-running work.
"""

import datetime as dt

from ...infra import get_repo
from ...models import JobState, PollDebugZipCommand


def poll_debug_zip(
    job_id: int,
    command: PollDebugZipCommand,
    _requested_by: str,
) -> None:
    repo = get_repo()
    repo.update_job(job_id, JobState.FAILED)
    repo.create_task(
        job_id,
        0,
        dt.datetime.now(dt.timezone.utc),
        "FAILURE",
        (
            "POLL_DEBUG_ZIP is not implemented yet. "
            f"Original job: {command.cp_job_id}; artifact: {command.artifact_id}."
        ),
    )
