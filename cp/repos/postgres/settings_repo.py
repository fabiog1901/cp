"""Settings repository backed by CockroachDB/Postgres."""

from ...models import Setting
from . import admin_queries


def list_settings() -> list[Setting]:
    return admin_queries.fetch_all_settings()


def get_setting(setting_id: str) -> str:
    return admin_queries.get_setting(setting_id)


def update_setting(setting_id: str, value: str, updated_by: str) -> None:
    admin_queries.update_setting(setting_id, value, updated_by)
