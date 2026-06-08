"""Shared infrastructure entrypoints for DB lifecycle and FastAPI dependencies."""

from cpkit.db import close_db, get_pool, initialize_postgres

from ..repository import get_repo
from .dependencies import (
    get_admin_service,
    get_alerts_service,
    get_api_keys_service,
    get_auth_service,
    get_backup_catalog_service,
    get_cluster_backups_service,
    get_cluster_jobs_service,
    get_cluster_options_service,
    get_cluster_service,
    get_cluster_users_service,
    get_dashboard_service,
    get_events_service,
    get_jobs_service,
    get_playbooks_service,
    get_regions_service,
    get_settings_service,
    get_versions_service,
)

__all__ = [
    "close_db",
    "get_pool",
    "get_repo",
    "initialize_postgres",
    "get_admin_service",
    "get_alerts_service",
    "get_auth_service",
    "get_backup_catalog_service",
    "get_cluster_backups_service",
    "get_cluster_jobs_service",
    "get_cluster_service",
    "get_cluster_users_service",
    "get_cluster_options_service",
    "get_compute_unit_service",
    "get_dashboard_service",
    "get_events_service",
    "get_jobs_service",
    "get_playbooks_service",
    "get_regions_service",
    "get_settings_service",
    "get_versions_service",
    "get_api_keys_service",
]
