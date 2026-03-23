"""Compatibility shim for legacy dependency imports.

Prefer importing dependency factories from ``cp.infra``.
"""

from .infra import (
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
    get_repo,
    get_settings_service,
    get_versions_service,
)

__all__ = [
    "get_repo",
    "get_admin_service",
    "get_auth_service",
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
]
