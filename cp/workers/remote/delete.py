"""Remote cluster deletion worker.

This worker runs the playbook-backed delete workflow and updates CP cluster/job
metadata after a managed cluster is removed.
"""

import datetime as dt
import logging
from threading import Thread

from cpkit import get_repo
from cpkit.playbooks import run_playbook

from ...models import ClusterState, DeleteClusterCommand, JobState, PlaybookName

logger = logging.getLogger(__name__)


def delete_cluster(
    job_id: int,
    command: DeleteClusterCommand,
    requested_by: str,
) -> None:
    repo = get_repo()
    cluster_id = command.cluster_id

    c = repo.get_cluster(cluster_id, [], True)
    if not c:
        repo.update_job(
            job_id,
            JobState.FAILED,
        )
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "The cluster was not found.",
        )
        return

    repo.link_job_to_cluster(
        cluster_id,
        job_id,
        JobState.QUEUED,
    )

    if c.status == ClusterState.DELETED:
        repo.update_job(
            job_id,
            JobState.FAILED,
        )
        repo.create_task(
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

        runner_result = run_playbook(
            repo=repo,
            job_id=job_id,
            playbook_name=PlaybookName.DELETE_CLUSTER,
            extra_vars=extra_vars,
        )

        if runner_result.status == "successful":
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
        repo.create_task(
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
