"""Business logic for the events vertical."""

from ..infra.db import get_repo
from ..infra.errors import RepositoryError
from ..models import LogMsg
from ..repos import Repo
from .errors import from_repository_error


class EventsService:
    def __init__(self, repo: Repo | None = None) -> None:
        self.repo = repo or get_repo()

    def list_visible_events(
        self,
        limit: int,
        offset: int,
        groups: list[str],
        is_admin: bool,
    ) -> list[LogMsg]:
        try:
            return self.repo.list_events(limit, offset, groups, is_admin)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Events are temporarily unavailable.",
                fallback_message="Unable to load EventRepo.",
            ) from err

    def get_event_total(self) -> int:
        try:
            return self.repo.get_event_count()
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Event totals are temporarily unavailable.",
                fallback_message="Unable to load the event count.",
            ) from err
