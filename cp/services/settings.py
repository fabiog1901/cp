"""Business logic for the settings vertical."""

from ..infra.errors import RepositoryError
from ..models import EventType, Setting
from ..repos.postgres import event_repo, settings_repo
from .errors import ServiceValidationError, from_repository_error


def list_settings() -> list[Setting]:
    try:
        return settings_repo.list_settings()
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Settings are temporarily unavailable.",
            fallback_message="Unable to load settings_repo.",
        ) from err


def get_setting(setting_id: str) -> str:
    try:
        value = settings_repo.get_setting(setting_id)
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


def update_setting(setting_id: str, value: str, updated_by: str) -> None:
    try:
        settings_repo.update_setting(setting_id, value, updated_by)
        event_repo.insert_event_log(
            updated_by,
            EventType.UPDATE_SETTING,
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
