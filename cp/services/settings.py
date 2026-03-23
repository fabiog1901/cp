"""Business logic for the settings vertical."""

from ..infra.errors import RepositoryError
from ..models import Event, Setting
from ..repos.base import BaseRepo
from .errors import ServiceValidationError, from_repository_error


class SettingsService:
    def __init__(self, repo: BaseRepo) -> None:
        self.repo = repo

    def list_settings(self) -> list[Setting]:
        try:
            return self.repo.list_settings()
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Settings are temporarily unavailable.",
                fallback_message="Unable to load SettingsRepo.",
            ) from err

    def get_setting(self, setting_id: str) -> str:
        try:
            value = self.repo.get_setting(setting_id)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Settings are temporarily unavailable.",
                fallback_message=f"Unable to load setting '{setting_id}'.",
            ) from err

        if value is None:
            raise ServiceValidationError(
                f"Required setting '{setting_id}' is not configured.",
                title="Missing Configuration",
            )

        return value

    def update_setting(self, setting_id: str, value: str, updated_by: str) -> None:
        try:
            self.repo.update_setting(setting_id, value, updated_by)
            self.repo.insert_event_log(
                updated_by,
                Event.UPDATE_SETTING,
                {"ID": setting_id, "value": value},
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Settings could not be updated right now.",
                conflict_message=f"Setting '{setting_id}' could not be updated because of a conflicting change.",
                validation_message=f"Setting '{setting_id}' has an invalid value.",
                fallback_message=f"Unable to update setting '{setting_id}'.",
            ) from err
