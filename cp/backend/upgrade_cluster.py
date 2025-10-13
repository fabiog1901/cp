from threading import Thread

from ..models import ClusterState, ClusterUpgradeRequest, JobState
from . import db
from .util import MyRunner


def upgrade_cluster(
    job_id: int,
    data: dict,
    requested_by: str,
) -> None:
    cur = ClusterUpgradeRequest(**data)

    # TODO check user permissions

    # check if cluster with same cluster_id exists
    c = db.get_cluster(cur.name, [], True)

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
        cur.name,
        requested_by,
        status=ClusterState.UPGRADING,
    )

    db.insert_mapped_job(
        cur.name,
        job_id,
        JobState.SCHEDULED,
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

    extra_vars = {
        "deployment_id": cur.name,
        "cockroachdb_version": cur.version,
        "cockroachdb_autofinalize": cur.auto_finalize,
    }

    job_status, _, _ = MyRunner(job_id).launch_runner("UPGRADE_CLUSTER", extra_vars)

    if job_status != "successful":
        db.update_cluster(
            cur.name,
            requested_by,
            status=ClusterState.UPGRADE_FAILED,
        )
        return

    db.update_cluster(
        cur.name,
        requested_by,
        status=ClusterState.RUNNING,
        version=cur.version,
    )
