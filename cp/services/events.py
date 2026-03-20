"""Business logic for the events vertical."""

from ..infra.errors import RepositoryError
from ..models import EventLog
from ..repos.postgres import events
from .errors import from_repository_error


def list_visible_events(
    limit: int,
    offset: int,
    groups: list[str],
    is_admin: bool,
) -> list[EventLog]:
    try:
        return events.list_events(limit, offset, groups, is_admin)
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Events are temporarily unavailable.",
            fallback_message="Unable to load events.",
        ) from err


def get_event_total() -> int:
    try:
        return events.get_event_count()
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Event totals are temporarily unavailable.",
            fallback_message="Unable to load the event count.",
        ) from err
