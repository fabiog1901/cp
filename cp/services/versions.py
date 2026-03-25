"""Business logic for the versions vertical."""

from pydantic import ValidationError

from ..infra.errors import RepositoryError
from ..models import Event, Version
from ..repos.base import BaseRepo
from .base import log_event
from .errors import ServiceValidationError, from_repository_error


class VersionsService:
    def __init__(self, repo: BaseRepo) -> None:
        self.repo = repo

    def list_versions(self) -> list[Version]:
        try:
            return self.repo.list_versions()
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Versions are temporarily unavailable.",
                fallback_message="Unable to load VersionsRepo.",
            ) from err

    def create_version(self, version: str, created_by: str) -> Version:
        try:
            model = Version(version=version)
        except ValidationError as err:
            raise ServiceValidationError("Version format is invalid.") from err

        try:
            self.repo.add_version(model)
            log_event(
                self.repo,
                created_by,
                Event.VERSION_ADD,
                {"version": model.version},
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

    def delete_version(self, version: str, deleted_by: str) -> None:
        try:
            self.repo.remove_version(version)
            log_event(
                self.repo,
                deleted_by,
                Event.VERSION_REMOVE,
                {"version": version},
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Versions could not be updated right now.",
                fallback_message=f"Unable to delete version '{version}'.",
            ) from err
