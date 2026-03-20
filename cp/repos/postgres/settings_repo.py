"""Settings repository backed by CockroachDB/Postgres."""

from ...models import Setting
from . import repository


def list_settings() -> list[Setting]:
    return repository.fetch_all_settings()


def get_setting(setting_id: str) -> str:
    return repository.get_setting(setting_id)


def update_setting(setting_id: str, value: str, updated_by: str) -> None:
    repository.update_setting(setting_id, value, updated_by)
