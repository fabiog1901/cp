from threading import Thread
import datetime as dt
from ..models import ClusterState, JobState
from . import db
from .util import MyRunner


def delete_cluster(
    job_id: int,
    cluster: dict,
    requested_by: str,
) -> None:
    cluster_id = cluster.get("cluster_id")

    c = db.get_cluster(cluster_id, [], True)
    if not c or c.status == ClusterState.DELETED:
        db.update_job(
            job_id,
            JobState.FAILED,
        )
        db.insert_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "The cluster does not exists or has already been deleted.",
        )
        return

    db.update_cluster(
        cluster_id,
        requested_by,
        status=ClusterState.DELETING,
    )

    db.insert_mapped_job(
        cluster_id,
        job_id,
        JobState.SCHEDULED,
    )

    Thread(
        target=delete_cluster_worker,
        args=(
            job_id,
            cluster_id,
            requested_by,
        ),
    ).start()


def delete_cluster_worker(
    job_id: int,
    cluster_id: str,
    requested_by: str,
):
    extra_vars = {
        "deployment_id": cluster_id,
    }

    job_status, _, _ = MyRunner(job_id).launch_runner("DELETE_CLUSTER", extra_vars)

    if job_status == "successful":
        db.update_cluster(
            cluster_id,
            requested_by,
            status=ClusterState.DELETED,
        )
    else:
        db.update_cluster(
            cluster_id,
            requested_by,
            status=ClusterState.DELETE_FAILED,
        )
