"""Shared infrastructure entrypoints for DB lifecycle and FastAPI dependencies."""

from cpkit.db import close_db, get_pool, initialize_postgres

from ..repository import get_repo
from .dependencies import (
    get_jobs_service,
    get_playbooks_service,
    get_settings_service,
)

__all__ = [
    "close_db",
    "get_pool",
    "get_repo",
    "get_jobs_service",
    "initialize_postgres",
    "get_playbooks_service",
    "get_settings_service",
]
