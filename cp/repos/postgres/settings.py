"""Settings repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all, fetch_one, fetch_scalar
from ...models import SettingKey, SettingRecord
from ..base import BaseRepo


class SettingsRepo(BaseRepo):

    def _setting_from_row(self, row) -> SettingRecord:
        value = row[1]
        default_value = row[2]
        effective_value = default_value if value is None else value
        return SettingRecord(
            key=row[0],
            value=value,
            default_value=default_value,
            effective_value=effective_value,
            value_type=row[3],
            category=row[4],
            is_secret=row[5],
            description=row[6] or "",
            updated_at=row[7],
            updated_by=row[8],
        )

    def list_settings(self) -> list[SettingRecord]:
        rows = fetch_all(
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
                    """
        )

        return [self._setting_from_row(row) for row in rows]

    def get_setting(self, key: SettingKey) -> SettingRecord | None:
        row = fetch_one(
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
        )

        return self._setting_from_row(row) if row is not None else None

    def update_setting(
        self,
        key: SettingKey,
        value,
        *,
        updated_by: str | None = None,
    ) -> SettingRecord | None:
        row = fetch_one(
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
        )

        return self._setting_from_row(row) if row is not None else None

    def reset_setting(
        self,
        key: SettingKey,
        *,
        updated_by: str | None = None,
    ) -> SettingRecord | None:
        row = fetch_one(
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
        )

        return self._setting_from_row(row) if row is not None else None
