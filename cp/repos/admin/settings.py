"""Admin settings repository."""

from cpkit.settings import SettingsRepositoryMixin

from ...models import SettingKey, SettingRecord
from .base import AdminRepo


class SettingsRepo(SettingsRepositoryMixin, AdminRepo):
    def get_setting(self, key: SettingKey | str) -> SettingRecord | None:
        return super().get_setting(key)
