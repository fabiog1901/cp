"""Business logic for the settings vertical."""

from ..models import EventType, Setting
from ..repos.postgres import event_repo, settings_repo


def list_settings() -> list[Setting]:
    return settings_repo.list_settings()


def get_setting(setting_id: str) -> str:
    return settings_repo.get_setting(setting_id)


def update_setting(setting_id: str, value: str, updated_by: str) -> None:
    settings_repo.update_setting(setting_id, value, updated_by)
    event_repo.insert_event_log(
        updated_by,
        EventType.UPDATE_SETTING,
        {"ID": setting_id, "value": value},
    )
