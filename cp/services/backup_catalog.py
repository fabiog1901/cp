"""Business logic for the backup catalog."""

from ..infra.db import get_repo
from ..infra.errors import RepositoryError
from ..models import (
    BackupCatalogEntry,
    CommandType,
    SyncBackupCatalogRequest,
    SyncClusterBackupCatalogRequest,
)
from ..repos import Repo
from .errors import ServiceAuthorizationError, ServiceNotFoundError, from_repository_error


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
