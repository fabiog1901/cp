"""CockroachDB/Postgres repository implementation package."""

from .auth import AuthRepo
from .cluster_backups import ClusterBackupsRepo
from .cluster_jobs import ClusterJobsRepo
from .cluster_users import ClusterUsersRepo
from .cluster import ClusterRepo
from .dashboard import DashboardRepo
from .event import EventRepo
from .jobs import JobsRepo
from .mq import MqRepo
from .playbooks import PlaybooksRepo
from .regions import RegionsRepo
from .settings import SettingsRepo
from .versions import VersionsRepo

from psycopg_pool import ConnectionPool

class PostgresRepo(
    ClusterJobsRepo,
    RegionsRepo,
    VersionsRepo,
    SettingsRepo,
    PlaybooksRepo,
    AuthRepo,
    ClusterBackupsRepo,
    ClusterUsersRepo,
    ClusterRepo,
    DashboardRepo,
    EventRepo,
    JobsRepo,
    MqRepo,
):
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool
