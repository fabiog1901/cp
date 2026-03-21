"""Business logic for auth-related shared operations."""

from ..infra.errors import RepositoryError
from ..models import EventType
from ..repos.postgres.auth import AuthRepo
from ..repos.postgres.event import EventRepo
from .errors import from_repository_error


class AuthService:
    @staticmethod
    def list_role_group_mappings():
        try:
            return AuthRepo.list_role_group_mappings()
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Authentication role mappings are temporarily unavailable.",
                fallback_message="Unable to load authorization settings.",
            ) from err

    @staticmethod
    def record_login(username: str, roles: list[str], groups: list[str]) -> None:
        try:
            EventRepo.insert_event_log(
                username,
                EventType.LOGIN,
                {"roles": roles, "groups": groups},
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Login auditing is temporarily unavailable.",
                fallback_message="Unable to complete login bookkeeping.",
            ) from err
