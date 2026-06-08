"""Repository-layer package."""

from cpkit.jobs import JobsRepositoryMixin, QueueJobRepositoryMixin
from cpkit.playbooks import PlaybooksRepositoryMixin
from cpkit.settings import SettingsRepositoryMixin
from psycopg_pool import ConnectionPool

from .admin import (
    ApiKeysRepo,
    ClusterOptionsRepo,
    RegionsRepo,
    VersionsRepo,
)
from .alerts import AlertsRepo
from .auth import AuthRepo
from .backup_catalog import BackupCatalogRepo
from .cluster import ClusterRepo
from .cluster_artifacts import ClusterArtifactsRepo
from .cluster_jobs import ClusterJobsRepo
from .event import EventRepo
from .external_connections import ExternalConnectionsRepo


class Repo(
    ApiKeysRepo,
    AlertsRepo,
    BackupCatalogRepo,
    ClusterOptionsRepo,
    ClusterJobsRepo,
    RegionsRepo,
    VersionsRepo,
    SettingsRepositoryMixin,
    PlaybooksRepositoryMixin,
    AuthRepo,
    ClusterRepo,
    ClusterArtifactsRepo,
    EventRepo,
    ExternalConnectionsRepo,
    JobsRepositoryMixin,
    QueueJobRepositoryMixin,
):
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool


__all__ = ["Repo"]
