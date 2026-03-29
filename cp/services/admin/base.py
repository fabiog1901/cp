"""Shared base for admin-facing services."""

from ...repos.base import BaseRepo


class AdminService:
    """Small common base for admin services backed by the shared repository."""

    def __init__(self, repo: BaseRepo) -> None:
        self.repo = repo
