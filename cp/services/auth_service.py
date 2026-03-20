"""Business logic for auth-related shared operations."""

from ..models import EventType
from ..repos.postgres import auth_repo, event_repo


def list_role_group_mappings():
    return auth_repo.list_role_group_mappings()


def record_login(username: str, roles: list[str], groups: list[str]) -> None:
    event_repo.insert_event_log(
        username,
        EventType.LOGIN,
        {"roles": roles, "groups": groups},
    )
