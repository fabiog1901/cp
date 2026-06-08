"""Queue worker entry point.

This module registers CP command handlers and delegates queue polling to cpkit.
"""

import datetime as dt
import logging
from typing import Callable

from cpkit.db import get_pool
from cpkit.jobs import QueueMessage, run_queue_worker

from ..repository import get_repo
from ..models import (
    ClusterState,
    CommandModel,
    CommandType,
    FailZombieJobsCommand,
    JobState,
    Nodes,
    parse_command_payload,
)
from .local.backup_catalog import sync_backup_catalog, sync_cluster_backup_catalog
from .local.restore import (
    poll_cluster_restore,
    restore_cluster,
    restore_cluster_object,
    restore_full_cluster,
)
from .remote.create import create_cluster
from .remote.debug_zip import debug_zip_cluster
from .remote.delete import delete_cluster
from .remote.healthcheck import healthcheck_cluster
from .remote.poll_debug_zip import poll_debug_zip
from .remote.scale import scale_cluster
from .remote.upgrade import upgrade_cluster

logger = logging.getLogger(__name__)


def fail_zombie_jobs(
    _job_id: int,
    _command: FailZombieJobsCommand,
    _requested_by: str,
):
    """Mark stale running jobs as failed from a scheduled queue command."""
    get_repo().fail_zombie_jobs()


CommandHandler = Callable[[int, CommandModel, str], None]

COMMAND_HANDLERS: dict[CommandType, CommandHandler] = {
    CommandType.CREATE_CLUSTER: create_cluster,
    CommandType.RECREATE_CLUSTER: lambda job_id, command, requested_by: create_cluster(
        job_id, command, requested_by, True
    ),
    CommandType.DELETE_CLUSTER: delete_cluster,
    CommandType.DEBUG_ZIP_CLUSTER: debug_zip_cluster,
    CommandType.POLL_DEBUG_ZIP: poll_debug_zip,
    CommandType.HEALTHCHECK_CLUSTER: healthcheck_cluster,
    CommandType.SCALE_CLUSTER: scale_cluster,
    CommandType.UPGRADE_CLUSTER: upgrade_cluster,
    CommandType.RESTORE_CLUSTER: restore_cluster,
    CommandType.RESTORE_CLUSTER_OBJECT: restore_cluster_object,
    CommandType.RESTORE_FULL_CLUSTER: restore_full_cluster,
    CommandType.POLL_CLUSTER_RESTORE: poll_cluster_restore,
    CommandType.SYNC_BACKUP_CATALOG: sync_backup_catalog,
    CommandType.SYNC_CLUSTER_BACKUP_CATALOG: sync_cluster_backup_catalog,
    CommandType.FAIL_ZOMBIE_JOBS: fail_zombie_jobs,
}


def get_nodes():
    """Return Prometheus scrape targets for active cluster nodes."""

    rs: list[Nodes] = []
    active_cluster_ids: set[str] = set()

    try:
        active_cluster_ids = {
            cluster.cluster_id
            for cluster in get_repo().list_clusters([], True)
            if cluster.status
            not in {
                ClusterState.DELETING.value,
                ClusterState.DELETED.value,
            }
        }
        rs = get_repo().list_cluster_nodes()
    except Exception as e:
        print("Error", str(e))

    return [
        {"targets": [f"{n}:8080" for n in x.nodes], "labels": {"cluster": x.cluster_id}}
        for x in rs
        if x.cluster_id in active_cluster_ids
    ]


async def pull_from_mq():
    """Continuously claim due MQ messages and dispatch them to command handlers."""
    await run_queue_worker(
        get_pool=get_pool,
        resolve_handler=_resolve_handler,
        parse_message=_parse_message,
        handle_failure=_handle_message_failure,
    )


def _resolve_handler(message: QueueMessage) -> CommandHandler | None:
    return COMMAND_HANDLERS.get(CommandType(message.msg_type))


def _parse_message(message: QueueMessage) -> CommandModel:
    return parse_command_payload(
        CommandType(message.msg_type),
        message.msg_data,
    )


def _handle_message_failure(message: QueueMessage, err: Exception) -> None:
    repo = get_repo()
    try:
        repo.update_job(message.msg_id, JobState.FAILED)
    except Exception:
        logger.exception("Unable to mark job %s as failed", message.msg_id)
    try:
        repo.create_task(
            message.msg_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            str(err),
        )
    except Exception:
        logger.exception("Unable to record failure task for job %s", message.msg_id)
