import datetime as dt
import logging
from threading import Thread

from ...models import ClusterState, JobState, RestoreRequest
from ...repos.postgres import cluster_repo, jobs_repo, settings_repo
from ..ansible import MyRunner

logger = logging.getLogger(__name__)


def restore_cluster(
    job_id: int,
    data: dict,
    requested_by: str,
) -> None:

    rr = RestoreRequest(**data)
    # TODO check user permissions

    # check if cluster with same cluster_id exists
    c = cluster_repo.get_cluster(rr.name, [], True)

    # TODO verify what states are appropriate for running a restore job
    if c is None or c.status != ClusterState.RUNNING:
        jobs_repo.update_job(
            job_id,
            JobState.FAILED,
        )
        jobs_repo.insert_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "The cluster must exist and be in a RUNNING state for a Full Cluster Restore",
        )
        return

    cluster_repo.update_cluster(
        rr.name,
        requested_by,
        status=ClusterState.RESTORING,
    )

    jobs_repo.insert_mapped_job(
        rr.name,
        job_id,
        JobState.SCHEDULED,
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
    try:
        extra_vars = {
            "deployment_id": rr.name,
            "backup_path": rr.backup_path,
            "restore_aost": rr.restore_aost,
            "restore_full_cluster": rr.restore_full_cluster,
            "object_type": rr.object_type,
            "object_name": rr.object_name,
            "backup_into": rr.backup_into,
            "cloud_storage_url": settings_repo.get_setting("cloud_storage_url"),
        }

        job_status, _, _ = MyRunner(job_id).launch_runner("RESTORE_CLUSTER", extra_vars)

        if job_status != "successful":
            cluster_repo.update_cluster(
                rr.name,
                requested_by,
                status=ClusterState.RESTORE_FAILED,
            )
            return

        cluster_repo.update_cluster(
            rr.name,
            requested_by,
            status=ClusterState.RUNNING,
        )
    except Exception as err:
        logger.exception("Unhandled error while restoring cluster '%s'", rr.name)
        jobs_repo.update_job(job_id, JobState.FAILED)
        jobs_repo.insert_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            str(err),
        )
        cluster_repo.update_cluster(
            rr.name,
            requested_by,
            status=ClusterState.RESTORE_FAILED,
        )
