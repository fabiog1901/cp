import datetime as dt
import logging
from threading import Thread

from ...models import ClusterState, JobState
from ...repos.postgres.jobs_repo import JobsRepo
from ...repos.postgres.cluster_repo import ClusterRepo
from ..ansible import MyRunner

logger = logging.getLogger(__name__)


def delete_cluster(
    job_id: int,
    cluster: dict,
    requested_by: str,
) -> None:
    cluster_id = cluster.get("cluster_id")

    c = ClusterRepo.get_cluster(cluster_id, [], True)
    if not c or c.status == ClusterState.DELETED:
        JobsRepo.update_job(
            job_id,
            JobState.FAILED,
        )
        JobsRepo.insert_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "The cluster does not exists or has already been deleted.",
        )
        return

    ClusterRepo.update_cluster(
        cluster_id,
        requested_by,
        status=ClusterState.DELETING,
    )

    JobsRepo.insert_mapped_job(
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
    try:
        extra_vars = {
            "deployment_id": cluster_id,
        }

        job_status, _, _ = MyRunner(job_id).launch_runner("DELETE_CLUSTER", extra_vars)

        if job_status == "successful":
            ClusterRepo.update_cluster(
                cluster_id,
                requested_by,
                status=ClusterState.DELETED,
            )
        else:
            ClusterRepo.update_cluster(
                cluster_id,
                requested_by,
                status=ClusterState.DELETE_FAILED,
            )
    except Exception as err:
        logger.exception("Unhandled error while deleting cluster '%s'", cluster_id)
        JobsRepo.update_job(job_id, JobState.FAILED)
        JobsRepo.insert_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            str(err),
        )
        ClusterRepo.update_cluster(
            cluster_id,
            requested_by,
            status=ClusterState.DELETE_FAILED,
        )
