from cpkit.playbooks import PlaybooksService
from cpkit.settings import SettingsService

from ..models import AuditEvent
from ..services.base import log_event
from ..services.admin.api_keys import ApiKeysService
from ..services.admin.cluster_options import ClusterOptionsService
from ..services.admin.regions import RegionsService
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
from ..repository import get_repo

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
get_regions_service = _build_service(RegionsService)
get_versions_service = _build_service(VersionsService)
get_cluster_options_service = _build_service(ClusterOptionsService)
get_api_keys_service = _build_service(ApiKeysService)


def get_playbooks_service():
    return PlaybooksService(
        get_repo(),
        version_created_hook=log_event,
        version_deleted_hook=log_event,
        default_set_hook=log_event,
    )


def get_settings_service():
    return SettingsService(
        get_repo(),
        setting_updated_hook=_log_setting_updated,
        setting_reset_hook=_log_setting_reset,
    )


def _log_setting_updated(repo, setting_id: str, value: str, updated_by: str) -> None:
    log_event(
        repo,
        updated_by,
        AuditEvent.SETTING_UPDATED,
        {"ID": setting_id, "value": value},
    )


def _log_setting_reset(repo, setting_id: str, updated_by: str) -> None:
    log_event(
        repo,
        updated_by,
        AuditEvent.SETTING_RESET,
        {"ID": setting_id},
    )


# Backward-compatible alias for the legacy admin API slice on this branch.
def get_admin_service() -> AuthService:
    return AuthService()
