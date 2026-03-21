"""Business logic for the versions vertical."""

from pydantic import ValidationError

from ..infra.errors import RepositoryError
from ..models import EventType, Version
from ..repos.postgres import events, versions
from .errors import ServiceValidationError, from_repository_error


def list_versions() -> list[Version]:
    try:
        return versions.list_versions()
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Versions are temporarily unavailable.",
            fallback_message="Unable to load versions.",
        ) from err


def create_version(version: str, created_by: str) -> Version:
    try:
        model = Version(version=version)
    except ValidationError as err:
        raise ServiceValidationError("Version format is invalid.") from err

    try:
        versions.add_version(model)
        events.insert_event_log(
            created_by,
            EventType.VERSION_ADD,
            model.version,
        )
        return model
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Versions could not be updated right now.",
            conflict_message=f"Version '{model.version}' already exists.",
            validation_message="The version is invalid.",
            fallback_message=f"Unable to create version '{model.version}'.",
        ) from err


def delete_version(version: str, deleted_by: str) -> None:
    try:
        versions.remove_version(version)
        events.insert_event_log(
            deleted_by,
            EventType.VERSION_REMOVE,
            version,
        )
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Versions could not be updated right now.",
            fallback_message=f"Unable to delete version '{version}'.",
        ) from err
