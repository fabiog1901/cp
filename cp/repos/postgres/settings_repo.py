"""Settings repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all, fetch_scalar
from ...models import Setting


class SettingsRepo:
    @staticmethod
    def list_settings() -> list[Setting]:
        return fetch_all(
            """
            SELECT *
            FROM settings
            """,
            (),
            Setting,
            operation="settings.list_settings",
        )

    @staticmethod
    def get_setting(setting_id: str) -> str:
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

    @staticmethod
    def update_setting(setting_id: str, value: str, updated_by: str) -> None:
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
