"""Business logic for the playbooks vertical."""

import gzip

from ..infra.errors import RepositoryError
from ..models import (
    STRFTIME,
    Event,
    Playbook,
    PlaybookOverview,
    PlaybookSelectionResponse,
    PlaybookVersionResponse,
)
from ..repos.base import BaseRepo
from .base import log_event
from .errors import ServiceNotFoundError, ServiceValidationError, from_repository_error


class PlaybooksService:
    def __init__(self, repo: BaseRepo) -> None:
        self.repo = repo

    def load_playbook_selection(self, name: str) -> PlaybookSelectionResponse:
        try:
            versions = self.repo.list_playbook_versions(name)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Playbooks are temporarily unavailable.",
                fallback_message=f"Unable to load playbook '{name}'.",
            ) from err
        version_strings = sorted([x.version.strftime(STRFTIME) for x in versions])
        selected_version = PlaybooksService._find_default_version(versions)

        try:
            playbook = self.repo.get_playbook(name, selected_version)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Playbooks are temporarily unavailable.",
                fallback_message=f"Unable to load playbook '{name}'.",
            ) from err
        content = PlaybooksService._decode_playbook(playbook)

        return PlaybookSelectionResponse(
            name=name,
            playbook_version=selected_version,
            default_version=selected_version,
            playbook_versions=version_strings,
            original_content=content,
            modified_content=content,
        )

    def load_playbook_version(self, name: str, version: str) -> dict:
        try:
            playbook = self.repo.get_playbook(name, version)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Playbooks are temporarily unavailable.",
                fallback_message=f"Unable to load playbook '{name}'.",
            ) from err
        content = PlaybooksService._decode_playbook(playbook)
        return {
            "playbook_version": version,
            "original_content": content,
            "modified_content": content,
        }

    def set_default_playbook(self, name: str, version: str, updated_by: str) -> None:
        try:
            self.repo.set_default_playbook(name, version, updated_by)
            log_event(
                self.repo,
                updated_by,
                Event.PLAYBOOK_SET_DEFAULT,
                {"name": name, "version": version},
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Playbook updates are temporarily unavailable.",
                fallback_message=f"Unable to set default playbook version for '{name}'.",
            ) from err

    def delete_playbook_version(
        self,
        name: str,
        version: str,
        default_version: str,
        deleted_by: str,
    ) -> dict:
        if version == default_version:
            raise ServiceValidationError("Cannot delete the default version.")

        try:
            self.repo.remove_playbook(name, version)
            log_event(
                self.repo,
                deleted_by,
                Event.PLAYBOOK_REMOVE,
                {"name": name, "version": version},
            )

            versions = self.repo.list_playbook_versions(name)
            selected_version = default_version
            playbook = self.repo.get_playbook(name, selected_version)
            content = PlaybooksService._decode_playbook(playbook)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Playbook updates are temporarily unavailable.",
                fallback_message=f"Unable to delete playbook version for '{name}'.",
            ) from err

        return {
            "playbook_versions": sorted(
                [x.version.strftime(STRFTIME) for x in versions]
            ),
            "playbook_version": selected_version,
            "default_version": default_version,
            "original_content": content,
            "modified_content": content,
        }

    def save_playbook_content(
        self, name: str, content: str, created_by: str
    ) -> PlaybookVersionResponse:
        try:
            saved = self.repo.add_playbook(
                name,
                gzip.compress(content.encode("utf-8")),
                created_by,
            )
            saved_version = saved.version.strftime(STRFTIME)
            log_event(
                self.repo,
                created_by,
                Event.PLAYBOOK_ADD,
                {"name": name, "version": saved_version},
            )

            versions = self.repo.list_playbook_versions(name)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Playbook saves are temporarily unavailable.",
                conflict_message=f"A conflicting playbook version already exists for '{name}'.",
                fallback_message=f"Unable to save playbook '{name}'.",
            ) from err
        return PlaybookVersionResponse(
            playbook_versions=sorted([x.version.strftime(STRFTIME) for x in versions]),
            playbook_version=saved_version,
            original_content=content,
            modified_content=content,
        )

    @staticmethod
    def _find_default_version(versions: list[PlaybookOverview]) -> str:
        selected_version = ""
        running_default = ""
        for item in versions:
            if (
                item.default_version
                and item.default_version.strftime(STRFTIME) > running_default
            ):
                running_default = item.default_version.strftime(STRFTIME)
                selected_version = item.version.strftime(STRFTIME)

        if selected_version:
            return selected_version
        if versions:
            return versions[-1].version.strftime(STRFTIME)
        raise ServiceNotFoundError("No playbook versions found.")

    @staticmethod
    def _decode_playbook(playbook: Playbook) -> str:
        if playbook.content is None:
            return ""
        return gzip.decompress(playbook.content).decode("utf-8")
