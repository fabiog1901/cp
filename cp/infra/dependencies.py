from ..services.admin.api_keys import ApiKeysService
from ..services.admin.cluster_options import ClusterOptionsService
from ..services.admin.playbooks import PlaybooksService
from ..services.admin.regions import RegionsService
from ..services.admin.settings import SettingsService
from ..services.admin.versions import VersionsService
from ..services.alerts import AlertsService
from ..services.auth import AuthService
from ..services.backup_catalog import BackupCatalogService
from ..services.cluster import ClusterService
from ..services.cluster_backups import ClusterBackupsService
from ..services.cluster_jobs import ClusterJobsService
from ..services.cluster_users import ClusterUsersService
from ..services.dashboard import DashboardService
from ..services.events import EventsService
from ..services.jobs import JobsService
from .db import get_repo as _get_repo

__all__ = [
    "get_repo",
    "get_compute_unit_service",
    "get_auth_service",
    "get_backup_catalog_service",
    "get_alerts_service",
    "get_cluster_service",
    "get_cluster_backups_service",
    "get_cluster_jobs_service",
    "get_cluster_users_service",
    "get_dashboard_service",
    "get_events_service",
    "get_jobs_service",
    "get_playbooks_service",
    "get_regions_service",
    "get_settings_service",
    "get_versions_service",
    "get_cluster_options_service",
    "get_api_keys_service",
    "get_admin_service",
]


def get_repo():
    return _get_repo()


def get_compute_unit_service():
    """Legacy placeholder for an unfinished compute-unit API slice on this branch."""
    raise RuntimeError("Compute unit service is not available on this branch.")


def _build_service(service_cls):
    def _get_service():
        return service_cls()

    return _get_service


get_auth_service = _build_service(AuthService)
get_backup_catalog_service = _build_service(BackupCatalogService)
get_alerts_service = _build_service(AlertsService)
get_cluster_service = _build_service(ClusterService)
get_cluster_backups_service = _build_service(ClusterBackupsService)
get_cluster_jobs_service = _build_service(ClusterJobsService)
get_cluster_users_service = _build_service(ClusterUsersService)
get_dashboard_service = _build_service(DashboardService)
get_events_service = _build_service(EventsService)
get_jobs_service = _build_service(JobsService)
get_playbooks_service = _build_service(PlaybooksService)
get_regions_service = _build_service(RegionsService)
get_settings_service = _build_service(SettingsService)
get_versions_service = _build_service(VersionsService)
get_cluster_options_service = _build_service(ClusterOptionsService)
get_api_keys_service = _build_service(ApiKeysService)


# Backward-compatible alias for the legacy admin API slice on this branch.
def get_admin_service() -> AuthService:
    return AuthService()
