"""Business logic for the events vertical."""

from ..models import EventLog
from ..repos.postgres import events


def list_visible_events(
    limit: int,
    offset: int,
    groups: list[str],
    is_admin: bool,
) -> list[EventLog]:
    return events.list_events(limit, offset, groups, is_admin)


def get_event_total() -> int:
    return events.get_event_count()
