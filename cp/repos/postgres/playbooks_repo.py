"""Playbooks repository backed by CockroachDB/Postgres."""

from ...models import Playbook, PlaybookOverview
from . import repository


def get_playbook(name: str, version: str) -> Playbook:
    return repository.get_playbook(name, version)


def list_playbook_versions(name: str) -> list[PlaybookOverview]:
    return repository.get_playbook_versions(name)


def add_playbook(name: str, playbook: bytes, created_by: str) -> PlaybookOverview:
    return repository.add_playbook(name, playbook, created_by)


def set_default_playbook(name: str, version: str, updated_by: str) -> None:
    repository.set_default_playbook(name, version, updated_by)


def remove_playbook(name: str, version: str) -> None:
    repository.remove_playbook(name, version)
