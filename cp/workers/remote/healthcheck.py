"""Remote cluster healthcheck worker.

This worker runs the configured healthcheck playbook for one managed
cluster and records task output on the requested CP job.
"""

import datetime as dt
import logging
from threading import Thread

from cpkit.playbooks import run_playbook

from ...models import ClusterState, HealthcheckClusterCommand, JobState, PlaybookName
from ...repository import get_repo

logger = logging.getLogger(__name__)


def healthcheck_cluster(
    job_id: int,
    command: HealthcheckClusterCommand,
    requested_by: str,
) -> None:
    repo = get_repo()
    cluster_id = command.cluster_id

    cluster = repo.get_cluster(cluster_id, [], True)
    if not cluster:
        repo.update_job(job_id, JobState.FAILED)
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "The cluster was not found.",
        )
        return

    if cluster.status in {ClusterState.DELETED, ClusterState.DELETING}:
        repo.update_job(job_id, JobState.FAILED)
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "The cluster does not exist or is being deleted.",
        )
        return

    repo.link_job_to_cluster(
        cluster_id,
        job_id,
        JobState.QUEUED,
    )

    Thread(
        target=healthcheck_cluster_worker,
        args=(
            job_id,
            command,
            requested_by,
        ),
    ).start()


def healthcheck_cluster_worker(
    job_id: int,
    command: HealthcheckClusterCommand,
    requested_by: str,
) -> None:
    repo = get_repo()
    cluster_id = command.cluster_id

    try:
        cluster = repo.get_cluster(cluster_id, [], True)
        if not cluster:
            raise RuntimeError("The cluster was not found.")

        extra_vars = {
            "deployment_id": cluster_id,
            "cluster_id": cluster_id,
            "cluster_inventory": [
                region.model_dump() for region in cluster.cluster_inventory
            ],
            "lbs_inventory": [lb.model_dump() for lb in cluster.lbs_inventory],
            "cockroachdb_nodes": [
                node for region in cluster.cluster_inventory for node in region.nodes
            ],
            "requested_by": requested_by,
        }

        run_playbook(
            repo=repo,
            job_id=job_id,
            playbook_name=PlaybookName.HEALTHCHECK_CLUSTER,
            extra_vars=extra_vars,
        )
    except Exception as err:
        logger.exception(
            "Unhandled error while healthchecking cluster '%s'", cluster_id
        )
        repo.update_job(job_id, JobState.FAILED)
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            str(err),
        )
