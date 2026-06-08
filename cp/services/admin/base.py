"""Shared base for admin-facing services."""

from cpkit import get_repo


class AdminService:
    """Small common base for admin services backed by the shared repository."""

    def __init__(self) -> None:
        self.repo = get_repo()
