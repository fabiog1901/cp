"""Shared infrastructure entrypoints for DB lifecycle and FastAPI dependencies."""

from .db import close_db, get_pool, get_repo, initialize_postgres
from .dependencies import (
    get_admin_service,
    get_auth_service,
    get_cluster_backups_service,
    get_cluster_jobs_service,
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
    "get_auth_service",
    "get_cluster_backups_service",
    "get_cluster_jobs_service",
    "get_cluster_service",
    "get_cluster_users_service",
    "get_dashboard_service",
    "get_events_service",
    "get_jobs_service",
    "get_playbooks_service",
    "get_regions_service",
    "get_settings_service",
    "get_versions_service",
]
