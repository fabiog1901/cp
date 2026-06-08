"""Repository-layer package."""

from cpkit import CPKitRepo
from psycopg_pool import ConnectionPool

from .admin import ClusterOptionsRepo, RegionsRepo, VersionsRepo
from .alerts import AlertsRepo
from .backup_catalog import BackupCatalogRepo
from .cluster import ClusterRepo
from .cluster_artifacts import ClusterArtifactsRepo
from .cluster_jobs import ClusterJobsRepo
from .external_connections import ExternalConnectionsRepo


class Repo(
    AlertsRepo,
    BackupCatalogRepo,
    ClusterOptionsRepo,
    ClusterJobsRepo,
    RegionsRepo,
    VersionsRepo,
    ClusterRepo,
    ClusterArtifactsRepo,
    ExternalConnectionsRepo,
    CPKitRepo,
):
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool


__all__ = ["Repo"]
