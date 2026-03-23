"""Settings repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all, fetch_scalar
from ...models import Setting
from ..base import BaseRepo
class SettingsRepo(BaseRepo):
    def list_settings(self) -> list[Setting]:
        return fetch_all(
            """
            SELECT *
            FROM settings
            """,
            (),
            Setting,
            operation="settings.list_settings",
        )

    def get_setting(self, setting_id: str) -> str:
        value = fetch_scalar(
            """
            SELECT value AS id
            FROM settings
            WHERE id = %s
            """,
            (setting_id,),
            operation="settings.get_setting",
        )
        return value

    def update_setting(self, setting_id: str, value: str, updated_by: str) -> None:
        execute_stmt(
            """
            UPDATE settings
            SET value = %s,
            updated_by = %s
            WHERE id = %s
            """,
            (value, updated_by, setting_id),
            operation="settings.update_setting",
        )

    def reset_setting(self, setting_id: str, updated_by: str) -> None:
        execute_stmt(
            """
            UPDATE settings
            SET value = NULL,
            updated_by = %s
            WHERE id = %s
            """,
            (updated_by, setting_id),
            operation="settings.reset_setting",
        )
