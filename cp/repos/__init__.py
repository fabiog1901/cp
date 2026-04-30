"""Repository-layer package."""

from psycopg_pool import ConnectionPool

from .admin import (
    ApiKeysRepo,
    ClusterOptionsRepo,
    PlaybooksRepo,
    RegionsRepo,
    SettingsRepo,
    VersionsRepo,
)
from .alerts import AlertsRepo
from .auth import AuthRepo
from .backup_catalog import BackupCatalogRepo
from .cluster import ClusterRepo
from .cluster_jobs import ClusterJobsRepo
from .event import EventRepo
from .external_connections import ExternalConnectionsRepo
from .jobs import JobsRepo
from .mq import MqRepo


class Repo(
    ApiKeysRepo,
    AlertsRepo,
    BackupCatalogRepo,
    ClusterOptionsRepo,
    ClusterJobsRepo,
    RegionsRepo,
    VersionsRepo,
    SettingsRepo,
    PlaybooksRepo,
    AuthRepo,
    ClusterRepo,
    EventRepo,
    ExternalConnectionsRepo,
    JobsRepo,
    MqRepo,
):
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool


__all__ = ["Repo"]
