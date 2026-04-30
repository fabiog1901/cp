"""Business logic for the backup catalog."""

from ..infra.db import get_repo
from ..infra.errors import RepositoryError
from ..models import (
    AuditEvent,
    BackupCatalogEntry,
    ClusterRecoveryRestoreApiRequest,
    ClusterState,
    CommandType,
    JobID,
    RestoreFullClusterRequest,
    SyncBackupCatalogRequest,
    SyncClusterBackupCatalogRequest,
)
from ..repos import Repo
from .base import log_event
from .errors import (
    ServiceAuthorizationError,
    ServiceNotFoundError,
    ServiceValidationError,
    from_repository_error,
)


class BackupCatalogService:
    def __init__(self, repo: Repo | None = None):
        self.repo = repo or get_repo()

    def list_backups(
        self,
        groups: list[str],
        is_admin: bool,
        *,
        full_cluster_only: bool = False,
    ) -> list[BackupCatalogEntry]:
        try:
            return self.repo.list_backup_catalog(
                groups,
                is_admin,
                full_cluster_only=full_cluster_only,
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Backup catalog is temporarily unavailable.",
                fallback_message="Unable to load backup catalog.",
            ) from err

    def enqueue_sync(
        self,
        requested_by: str,
        groups: list[str],
        is_admin: bool,
        *,
        cluster_id: str | None = None,
    ) -> None:
        if cluster_id:
            selected_cluster = self.repo.get_cluster(cluster_id, groups, is_admin)
            if selected_cluster is None:
                raise ServiceNotFoundError(f"Cluster '{cluster_id}' was not found.")
        elif not is_admin:
            raise ServiceAuthorizationError(
                "Only administrators can request a fleet-wide backup catalog sync."
            )

        try:
            if cluster_id:
                self.repo.enqueue_message(
                    CommandType.SYNC_CLUSTER_BACKUP_CATALOG,
                    SyncClusterBackupCatalogRequest(cluster_id=cluster_id),
                    requested_by,
                )
                return

            self.repo.enqueue_message(
                CommandType.SYNC_BACKUP_CATALOG,
                SyncBackupCatalogRequest(),
                requested_by,
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Backup catalog sync could not be queued right now.",
                fallback_message="Unable to queue backup catalog sync.",
            ) from err

    def enqueue_full_cluster_restore(
        self,
        request: ClusterRecoveryRestoreApiRequest,
        groups: list[str],
        is_admin: bool,
        requested_by: str,
    ) -> int:
        source_cluster = self.repo.get_cluster(
            request.source_cluster_id,
            groups,
            is_admin,
        )
        if source_cluster is None:
            raise ServiceNotFoundError(
                f"Source cluster '{request.source_cluster_id}' was not found."
            )

        target_cluster = self.repo.get_cluster(
            request.target_cluster_id,
            groups,
            is_admin,
        )
        if target_cluster is None:
            raise ServiceNotFoundError(
                f"Target cluster '{request.target_cluster_id}' was not found."
            )

        if source_cluster.cluster_id == target_cluster.cluster_id:
            raise ServiceValidationError(
                "Source and target clusters must be different clusters."
            )

        if source_cluster.grp != target_cluster.grp:
            raise ServiceValidationError(
                "Source and target clusters must be in the same group."
            )

        if target_cluster.status != ClusterState.ACTIVE:
            raise ServiceValidationError(
                "The target cluster must be ACTIVE before recovery can start."
            )

        backup = self.repo.get_backup_catalog_entry(
            request.source_cluster_id,
            request.backup_path,
            groups,
            is_admin,
        )
        if backup is None:
            raise ServiceNotFoundError(
                "The selected source backup was not found in the backup catalog."
            )
        if not backup.is_full_cluster:
            raise ServiceValidationError(
                "The selected backup is not a full cluster backup."
            )
        if backup.status != "AVAILABLE":
            raise ServiceValidationError(
                f"The selected backup is not available for restore ({backup.status})."
            )

        payload = RestoreFullClusterRequest(
            source_cluster_id=request.source_cluster_id,
            target_cluster_id=request.target_cluster_id,
            backup_path=request.backup_path,
            restore_aost=request.restore_aost,
        )

        try:
            msg_id: JobID = self.repo.enqueue_command(
                CommandType.RESTORE_FULL_CLUSTER,
                payload,
                requested_by,
            )
            log_event(
                self.repo,
                requested_by,
                AuditEvent.CLUSTER_RESTORE_REQUESTED,
                payload.model_dump() | {"job_id": msg_id.job_id},
            )
            return msg_id.job_id
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Cluster recovery could not be requested right now.",
                validation_message="The cluster recovery request contains invalid data.",
                fallback_message=(
                    f"Unable to request recovery for cluster "
                    f"'{request.target_cluster_id}'."
                ),
            ) from err
