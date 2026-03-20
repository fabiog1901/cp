"""Business logic for the events vertical."""

from ..models import EventLog
from ..repos.postgres import event_repo


def list_visible_events(
    limit: int,
    offset: int,
    groups: list[str],
    is_admin: bool,
) -> list[EventLog]:
    return event_repo.list_events(limit, offset, groups, is_admin)


def get_event_total() -> int:
    return event_repo.get_event_count()
