"""Admin settings repository."""

from cpkit.settings import SettingsRepositoryMixin

from ...models import SettingKey, SettingRecord
from .base import AdminRepo


class SettingsRepo(SettingsRepositoryMixin, AdminRepo):
    settings_table_name = "cpkit.settings"

    def get_setting(self, key: SettingKey | str) -> SettingRecord | None:
        return super().get_setting(key)
