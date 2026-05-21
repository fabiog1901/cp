"""Remote cluster debug zip worker.

This worker runs the configured Ansible playbook that collects a CockroachDB
debug zip for one managed cluster.
"""

import datetime as dt
import logging
from threading import Thread

from ...infra import get_repo
from ...models import ClusterState, DebugZipClusterCommand, JobState, PlaybookName
from .ansible import MyRunner

logger = logging.getLogger(__name__)


def debug_zip_cluster(
    job_id: int,
    command: DebugZipClusterCommand,
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
        target=debug_zip_cluster_worker,
        args=(
            job_id,
            command,
            requested_by,
        ),
    ).start()


def debug_zip_cluster_worker(
    job_id: int,
    command: DebugZipClusterCommand,
    requested_by: str,
) -> None:
    repo = get_repo()
    cluster_id = command.cluster_id

    try:
        cluster = repo.get_cluster(cluster_id, [], True)
        if not cluster:
            raise RuntimeError("The cluster was not found.")

        now = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        artifact_name = f"debug-zip-{cluster_id}-job-{job_id}-{now}.zip"
        debug_zip_options = command.model_dump(
            exclude={"cluster_id"},
            exclude_none=True,
        )

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
            "debug_zip_options": debug_zip_options,
            "artifact_name": artifact_name,
            "requested_by": requested_by,
        }

        MyRunner(job_id).launch_runner(
            PlaybookName.DEBUG_ZIP_CLUSTER,
            extra_vars,
        )
    except Exception as err:
        logger.exception(
            "Unhandled error while collecting debug zip for cluster '%s'",
            cluster_id,
        )
        repo.update_job(job_id, JobState.FAILED)
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            str(err),
        )
