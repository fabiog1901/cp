"""Settings repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all, fetch_one, fetch_scalar
from ...models import SettingKey, SettingRecord
from ..base import BaseRepo


class SettingsRepo(BaseRepo):

    def list_settings(self) -> list[SettingRecord]:
        return fetch_all(
            """
            SELECT
                key,
                value,
                default_value,
                value_type,
                category,
                is_secret,
                description,
                updated_at,
                updated_by
            FROM settings
            ORDER BY category, key
            """,
            (),
            SettingRecord,
        )

    def get_setting(self, key: SettingKey) -> SettingRecord | None:
        return fetch_one(
            """
            SELECT
                key,
                value,
                default_value,
                value_type,
                category,
                is_secret,
                description,
                updated_at,
                updated_by
            FROM settings
            WHERE key = %s
            """,
            (key,),
            SettingRecord,
        )


    def update_setting(
        self,
        key: SettingKey,
        value,
        updated_by: str | None = None,
    ) -> SettingRecord | None:
        return fetch_one(
            """
            UPDATE settings
            SET
                value = %s,
                updated_at = CURRENT_TIMESTAMP,
                updated_by = %s
            WHERE key = %s
            RETURNING
                key,
                value,
                default_value,
                value_type,
                category,
                is_secret,
                description,
                updated_at,
                updated_by
            """,
            (value, updated_by, key),
            SettingRecord,
        )

    def reset_setting(
        self,
        key: SettingKey,
        *,
        updated_by: str | None = None,
    ) -> SettingRecord | None:
        return fetch_one(
            """
            UPDATE settings
            SET
                value = NULL,
                updated_at = CURRENT_TIMESTAMP,
                updated_by = %s
            WHERE key = %s
            RETURNING
                key,
                value,
                default_value,
                value_type,
                category,
                is_secret,
                description,
                updated_at,
                updated_by
            """,
            (updated_by, key),
            SettingRecord
        )
