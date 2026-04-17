"""CockroachDB/Postgres repository implementation package."""

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
from .cluster import ClusterRepo
from .cluster_jobs import ClusterJobsRepo
from .event import EventRepo
from .jobs import JobsRepo
from .mq import MqRepo


class PostgresRepo(
    ApiKeysRepo,
    AlertsRepo,
    ClusterOptionsRepo,
    ClusterJobsRepo,
    RegionsRepo,
    VersionsRepo,
    SettingsRepo,
    PlaybooksRepo,
    AuthRepo,
    ClusterRepo,
    EventRepo,
    JobsRepo,
    MqRepo,
):
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool
