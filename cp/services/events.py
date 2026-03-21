"""Business logic for the events vertical."""

from ..infra.errors import RepositoryError
from ..models import EventLog
from ..repos.postgres.event import EventRepo
from .errors import from_repository_error


class EventsService:
    @staticmethod
    def list_visible_events(
        limit: int,
        offset: int,
        groups: list[str],
        is_admin: bool,
    ) -> list[EventLog]:
        try:
            return EventRepo.list_events(limit, offset, groups, is_admin)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Events are temporarily unavailable.",
                fallback_message="Unable to load EventRepo.",
            ) from err

    @staticmethod
    def get_event_total() -> int:
        try:
            return EventRepo.get_event_count()
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Event totals are temporarily unavailable.",
                fallback_message="Unable to load the event count.",
            ) from err
