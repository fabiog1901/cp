import datetime as dt
import logging
from threading import Thread

from ...infra import get_repo
from ...models import ClusterState, JobState
from ..ansible import MyRunner

logger = logging.getLogger(__name__)


def delete_cluster(
    job_id: int,
    cluster: dict,
    requested_by: str,
) -> None:
    repo = get_repo()
    cluster_id = cluster.get("cluster_id")

    c = repo.get_cluster(cluster_id, [], True)
    if not c:
        repo.update_job(
            job_id,
            JobState.FAILED,
        )
        repo.insert_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "The cluster was not found.",
        )
        return
    
    repo.insert_mapped_job(
        cluster_id,
        job_id,
        JobState.SCHEDULED,
    )
    
    if c.status == ClusterState.DELETED:
        repo.update_job(
            job_id,
            JobState.FAILED,
        )
        repo.insert_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "The cluster does not exists or has already been deleted.",
        )
        return

    repo.update_cluster(
        cluster_id,
        requested_by,
        status=ClusterState.DELETING,
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
    repo = get_repo()
    try:
        extra_vars = {
            "deployment_id": cluster_id,
        }

        job_status, _, _ = MyRunner(job_id).launch_runner("DELETE_CLUSTER", extra_vars)

        if job_status == "successful":
            repo.update_cluster(
                cluster_id,
                requested_by,
                status=ClusterState.DELETED,
            )
        else:
            repo.update_cluster(
                cluster_id,
                requested_by,
                status=ClusterState.DELETE_FAILED,
            )
    except Exception as err:
        logger.exception("Unhandled error while deleting cluster '%s'", cluster_id)
        repo.update_job(job_id, JobState.FAILED)
        repo.insert_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            str(err),
        )
        repo.update_cluster(
            cluster_id,
            requested_by,
            status=ClusterState.DELETE_FAILED,
        )
