import datetime as dt
import logging
from threading import Thread

from ...infra import get_repo
from ...models import ClusterState, JobState, PlaybookName, RestoreRequest
from ..ansible import MyRunner

logger = logging.getLogger(__name__)


def restore_cluster(
    job_id: int,
    command: RestoreRequest,
    requested_by: str,
) -> None:
    repo = get_repo()

    rr = command
    # TODO check user permissions

    # check if cluster with same cluster_id exists
    c = repo.get_cluster(rr.name, [], True)

    # TODO verify what states are appropriate for running a restore job
    if c is None or c.status != ClusterState.ACTIVE:
        repo.update_job(
            job_id,
            JobState.FAILED,
        )
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "The cluster must exist and be in an ACTIVE state for a full cluster restore.",
        )
        return

    repo.update_cluster(
        rr.name,
        requested_by,
        status=ClusterState.RESTORING,
    )

    repo.link_job_to_cluster(
        rr.name,
        job_id,
        JobState.QUEUED,
    )

    Thread(
        target=restore_cluster_worker,
        args=(
            job_id,
            rr,
            requested_by,
        ),
    ).start()


def restore_cluster_worker(
    job_id: int,
    rr: RestoreRequest,
    requested_by: str,
):
    repo = get_repo()
    try:
        extra_vars = {
            "deployment_id": rr.name,
            "backup_path": rr.backup_path,
            "restore_aost": rr.restore_aost,
            "restore_full_cluster": rr.restore_full_cluster,
            "object_type": rr.object_type,
            "object_name": rr.object_name,
            "backup_into": rr.backup_into,
            "cloud_storage_url": repo.get_setting("cloud_storage_url"),
        }

        job_status, _, _ = MyRunner(job_id).launch_runner(
            PlaybookName.RESTORE_CLUSTER, extra_vars
        )

        if job_status != "successful":
            repo.update_cluster(
                rr.name,
                requested_by,
                status=ClusterState.RESTORE_FAILED,
            )
            return

        repo.update_cluster(
            rr.name,
            requested_by,
            status=ClusterState.ACTIVE,
        )
    except Exception as err:
        logger.exception("Unhandled error while restoring cluster '%s'", rr.name)
        repo.update_job(job_id, JobState.FAILED)
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            str(err),
        )
        repo.update_cluster(
            rr.name,
            requested_by,
            status=ClusterState.RESTORE_FAILED,
        )
