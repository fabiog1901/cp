"""Business logic for the versions vertical."""

from ..models import EventType, Version
from ..repos.postgres import events, versions


def list_versions() -> list[Version]:
    return versions.list_versions()


def create_version(version: str, created_by: str) -> Version:
    model = Version(version=version)
    versions.add_version(model)
    events.insert_event_log(
        created_by,
        EventType.VERSION_ADD,
        model.version,
    )
    return model


def delete_version(version: str, deleted_by: str) -> None:
    versions.remove_version(version)
    events.insert_event_log(
        deleted_by,
        EventType.VERSION_REMOVE,
        version,
    )
