from threading import Thread

from .. import db
from ..models import ClusterUpgradeRequest


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
        "DELETED",
        "DELETING",
        "PROVISIONING",
        "UPGRADING",
        "SCALING",
    ]:
        # TODO update message for failed job:
        # cannot upgrade a deleting cluster
        db.update_job(
            job_id,
            "FAILED",
        )
        return

    db.update_cluster(
        cur.name,
        requested_by,
        status="UPGRADING",
    )

    db.insert_mapped_job(
        cur.name,
        job_id,
        "SCHEDULED",
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
        "cockroachdb_version": cur.version,
        "cockroachdb_autofinalize": cur.auto_finalize,
    }

    job_status, _ = MyRunner(job_id).launch_runner("UPGRADE_CLUSTER", extra_vars)

    if job_status != "successful":
        db.update_cluster(
            cur.name,
            "system",
            status="FAILED",
        )
        return

    db.update_cluster(
        cur.name,
        requested_by,
        status="RUNNING",
        version=cur.version,
    )
