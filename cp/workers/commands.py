"""CP command handlers for queued framework jobs."""

from typing import Callable

from ..models import CommandModel, CommandType
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
}
