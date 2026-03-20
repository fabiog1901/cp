"""Business logic for auth-related shared operations."""

from ..models import EventType
from ..repos.postgres import auth, events


def list_role_group_mappings():
    return auth.list_role_group_mappings()


def record_login(username: str, roles: list[str], groups: list[str]) -> None:
    events.insert_event_log(
        username,
        EventType.LOGIN,
        {"roles": roles, "groups": groups},
    )
