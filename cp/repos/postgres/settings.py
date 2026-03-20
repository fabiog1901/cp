"""Settings repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt
from ...models import Setting
from ...models import StrID


def list_settings() -> list[Setting]:
    return execute_stmt(
        """
        SELECT *
        FROM settings
        """,
        (),
        Setting,
    )


def get_setting(setting_id: str) -> str:
    str_id: StrID = execute_stmt(
        """
        SELECT value AS id
        FROM settings
        WHERE id = %s
        """,
        (setting_id,),
        StrID,
        False,
    )
    return str_id.id


def update_setting(setting_id: str, value: str, updated_by: str) -> None:
    execute_stmt(
        """
        UPDATE settings
        SET value = %s,
        updated_by = %s
        WHERE id = %s
        """,
        (value, updated_by, setting_id),
    )
