from threading import Thread

from . import db
from ..models import ClusterState, JobState, RestoreRequest
from .util import MyRunner


def restore_cluster(
    job_id: int,
    data: dict,
    requested_by: str,
) -> None:

    rr = RestoreRequest(**data)
    # TODO check user permissions

    # check if cluster with same cluster_id exists
    c = db.get_cluster(rr.name, [], True)

    # TODO verify what states are appropriate for running a restore job
    if c is None or c.status in [
        ClusterState.DELETED,
        ClusterState.DELETING,
        ClusterState.PROVISIONING,
        ClusterState.UPGRADING,
        ClusterState.SCALING,
    ]:
        # TODO update message for failed job:
        # cannot upgrade a deleting cluster
        db.update_job(
            job_id,
            JobState.FAILED,
        )
        return

    db.update_cluster(
        rr.name,
        requested_by,
        status=ClusterState.RESTORING,
    )

    db.insert_mapped_job(
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

    # TODO should just use rr.model_dump()
    extra_vars = {
        "deployment_id": rr.name,
        "backup_path": rr.backup_path,
        "restore_aost": rr.restore_aost,
        "restore_full_cluster": rr.restore_full_cluster,
        "object_type": rr.object_type,
        "object_name": rr.object_name,
        "backup_into": rr.backup_into,
        "cloud_storage_url": db.get_setting("cloud_storage_url"),
    }

    job_status, _, _ = MyRunner(job_id).launch_runner("RESTORE_CLUSTER", extra_vars)

    if job_status != "successful":
        db.update_cluster(
            rr.name,
            requested_by,
            status=ClusterState.RESTORE_FAILED,
        )
        return

    db.update_cluster(
        rr.name,
        requested_by,
        status=ClusterState.RUNNING,
    )
