"""Business logic for the admin settings vertical."""

from cpkit.settings import SettingsServiceMixin

from ...models import AuditEvent
from ..base import log_event
from .base import AdminService


class SettingsService(SettingsServiceMixin, AdminService):
    def after_setting_updated(
        self,
        setting_id: str,
        value: str,
        updated_by: str,
    ) -> None:
        log_event(
            self.repo,
            updated_by,
            AuditEvent.SETTING_UPDATED,
            {"ID": setting_id, "value": value},
        )

    def after_setting_reset(self, setting_id: str, updated_by: str) -> None:
        log_event(
            self.repo,
            updated_by,
            AuditEvent.SETTING_RESET,
            {"ID": setting_id},
        )
