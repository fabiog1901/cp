"""Business logic for the admin settings vertical."""

from ...infra.errors import RepositoryError
from ...models import AuditEvent, SettingRecord
from ...repos.base import BaseRepo
from ..base import log_event
from ..errors import ServiceValidationError, from_repository_error
from .base import AdminService


class SettingsService(AdminService):
    def __init__(self, repo: BaseRepo) -> None:
        super().__init__(repo)

    def list_settings(self) -> list[SettingRecord]:
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
            setting_record = self.repo.get_setting(setting_id)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Settings are temporarily unavailable.",
                fallback_message=f"Unable to load setting '{setting_id}'.",
            ) from err

        if setting_record is None:
            raise ServiceValidationError(
                f"Required setting '{setting_id}' is not configured.",
                title="Missing Configuration",
            )

        return setting_record.value

    def update_setting(self, setting_id: str, value: str, updated_by: str) -> None:
        try:
            self.repo.update_setting(setting_id, value, updated_by)

            log_event(
                self.repo,
                updated_by,
                AuditEvent.SETTING_UPDATED,
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

    def reset_setting(self, setting_id: str, updated_by: str) -> None:
        try:
            self.repo.reset_setting(setting_id, updated_by)
            log_event(
                self.repo,
                updated_by,
                AuditEvent.SETTING_RESET,
                {"ID": setting_id},
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Settings could not be updated right now.",
                conflict_message=f"Setting '{setting_id}' could not be reset because of a conflicting change.",
                validation_message=f"Setting '{setting_id}' could not be reset.",
                fallback_message=f"Unable to reset setting '{setting_id}'.",
            ) from err
