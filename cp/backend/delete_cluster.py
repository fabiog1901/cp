from threading import Thread

from .. import db
from .util import MyRunner


def delete_cluster(
    job_id: int,
    cluster: dict,
    requested_by: str,
) -> None:
    cluster_id = cluster.get("cluster_id")

    c = db.get_cluster(cluster_id, [], True)
    if not c or c.status == "DELETED":
        # TODO if cluster doesn't exists or it's already marked as deleted,
        # fail the job
        db.update_job(
            job_id,
            "FAILED",
        )
        return

    db.update_cluster(
        cluster_id,
        requested_by,
        status="DELETING...",
    )

    db.insert_mapped_job(
        cluster_id,
        job_id,
        "SCHEDULED",
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
            status="DELETED",
        )
    else:
        db.update_cluster(
            cluster_id,
            requested_by,
            status="DELETE_FAILED",
        )
