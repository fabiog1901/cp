"""Business logic for the versions vertical."""

from ..models import EventType, Version
from ..repos.postgres import versions_repo
from . import app_service


def list_versions() -> list[Version]:
    return versions_repo.list_versions()


def create_version(version: str, created_by: str) -> Version:
    model = Version(version=version)
    versions_repo.add_version(model)
    app_service.insert_event_log(
        created_by,
        EventType.VERSION_ADD,
        model.version,
    )
    return model


def delete_version(version: str, deleted_by: str) -> None:
    versions_repo.remove_version(version)
    app_service.insert_event_log(
        deleted_by,
        EventType.VERSION_REMOVE,
        version,
    )
