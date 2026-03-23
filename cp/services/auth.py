"""Business logic for auth-related shared operations."""

from ..infra.errors import RepositoryError
from ..models import Event
from ..repos.base import BaseRepo
from .errors import from_repository_error


class AuthService:
    def __init__(self, repo: BaseRepo) -> None:
        self.repo = repo

    def list_role_group_mappings(self):
        try:
            return self.repo.list_role_group_mappings()
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Authentication role mappings are temporarily unavailable.",
                fallback_message="Unable to load authorization settings.",
            ) from err

    def record_login(self, username: str, roles: list[str], groups: list[str]) -> None:
        return None
