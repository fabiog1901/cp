"""Shared base for admin-facing services."""

from ...infra.db import get_repo
from ...repos import Repo


class AdminService:
    """Small common base for admin services backed by the shared repository."""

    def __init__(self, repo: Repo | None = None) -> None:
        self.repo = repo or get_repo()
