"""Event repository backed by CockroachDB/Postgres."""

from ...models import EventLog
from . import event_queries


def list_events(
    limit: int,
    offset: int,
    groups: list[str] | None = None,
    is_admin: bool = False,
) -> list[EventLog]:
    return event_queries.fetch_all_events(limit, offset, groups, is_admin)


def get_event_count() -> int:
    return event_queries.get_event_count()


def insert_event_log(
    created_by: str,
    event_type: str,
    event_details=None,
) -> None:
    event_queries.insert_event_log(created_by, event_type, event_details)
