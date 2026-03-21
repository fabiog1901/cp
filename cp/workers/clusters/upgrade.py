import datetime as dt
import logging
from threading import Thread

from ...models import ClusterState, ClusterUpgradeRequest, JobState
from ...repos.postgres.jobs import JobsRepo
from ...repos.postgres.cluster import ClusterRepo
from ..ansible import MyRunner

logger = logging.getLogger(__name__)


def upgrade_cluster(
    job_id: int,
    data: dict,
    requested_by: str,
) -> None:
    cur = ClusterUpgradeRequest(**data)

    # TODO check user permissions

    # check if cluster with same cluster_id exists
    c = ClusterRepo.get_cluster(cur.name, [], True)

    if c is None:
        # TODO update message for failed job:
        # cannot upgrade a deleting cluster
        JobsRepo.update_job(
            job_id,
            JobState.FAILED,
        )
        return

    JobsRepo.insert_mapped_job(
        cur.name,
        job_id,
        JobState.SCHEDULED,
    )
    if c.status in [
        ClusterState.DELETED,
        ClusterState.DELETING,
        ClusterState.PROVISIONING,
        ClusterState.UPGRADING,
        ClusterState.SCALING,
    ]:
        # TODO update message for failed job:
        # cannot upgrade a deleting cluster
        JobsRepo.update_job(
            job_id,
            JobState.FAILED,
        )
        return
    
    ClusterRepo.update_cluster(
        cur.name,
        requested_by,
        status=ClusterState.UPGRADING,
    )


    Thread(
        target=upgrade_cluster_worker,
        args=(
            job_id,
            cur,
            requested_by,
        ),
    ).start()


def upgrade_cluster_worker(
    job_id: int,
    cur: ClusterUpgradeRequest,
    requested_by: str,
):
    try:
        extra_vars = {
            "deployment_id": cur.name,
            "cockroachdb_version": cur.version,
            "cockroachdb_autofinalize": cur.auto_finalize,
        }

        job_status, _, _ = MyRunner(job_id).launch_runner("UPGRADE_CLUSTER", extra_vars)

        if job_status != "successful":
            ClusterRepo.update_cluster(
                cur.name,
                requested_by,
                status=ClusterState.UPGRADE_FAILED,
            )
            return

        ClusterRepo.update_cluster(
            cur.name,
            requested_by,
            status=ClusterState.RUNNING,
            version=cur.version,
        )
    except Exception as err:
        logger.exception("Unhandled error while upgrading cluster '%s'", cur.name)
        JobsRepo.update_job(job_id, JobState.FAILED)
        JobsRepo.insert_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            str(err),
        )
        ClusterRepo.update_cluster(
            cur.name,
            requested_by,
            status=ClusterState.UPGRADE_FAILED,
        )
