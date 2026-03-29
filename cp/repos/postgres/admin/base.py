"""Shared base for admin-oriented Postgres repositories."""

from ...base import BaseRepo


class AdminPostgresRepo(BaseRepo):
    """Marker base for Postgres repositories used by admin endpoints."""

    pass
