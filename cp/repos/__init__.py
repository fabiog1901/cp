"""Repository-layer package."""

from cpkit.auth import (
    APIKeysRepositoryMixin,
    OIDCSessionsRepositoryMixin,
    RoleGroupMappingsRepositoryMixin,
)
from cpkit.jobs import JobsRepositoryMixin, QueueJobRepositoryMixin
from cpkit.playbooks import PlaybooksRepositoryMixin
from cpkit.settings import SettingsRepositoryMixin
from psycopg_pool import ConnectionPool

from .admin import (
    ClusterOptionsRepo,
    RegionsRepo,
    VersionsRepo,
)
from .alerts import AlertsRepo
from .backup_catalog import BackupCatalogRepo
from .cluster import ClusterRepo
from .cluster_artifacts import ClusterArtifactsRepo
from .cluster_jobs import ClusterJobsRepo
from .event import EventRepo
from .external_connections import ExternalConnectionsRepo


class Repo(
    APIKeysRepositoryMixin,
    AlertsRepo,
    BackupCatalogRepo,
    ClusterOptionsRepo,
    ClusterJobsRepo,
    RegionsRepo,
    VersionsRepo,
    SettingsRepositoryMixin,
    PlaybooksRepositoryMixin,
    OIDCSessionsRepositoryMixin,
    RoleGroupMappingsRepositoryMixin,
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
