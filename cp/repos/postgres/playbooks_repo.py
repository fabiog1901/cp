"""Playbooks repository backed by CockroachDB/Postgres."""

from ...models import Playbook, PlaybookOverview
from . import admin_queries


def get_playbook(name: str, version: str) -> Playbook:
    return admin_queries.get_playbook(name, version)


def list_playbook_versions(name: str) -> list[PlaybookOverview]:
    return admin_queries.get_playbook_versions(name)


def add_playbook(name: str, playbook: bytes, created_by: str) -> PlaybookOverview:
    return admin_queries.add_playbook(name, playbook, created_by)


def set_default_playbook(name: str, version: str, updated_by: str) -> None:
    admin_queries.set_default_playbook(name, version, updated_by)


def remove_playbook(name: str, version: str) -> None:
    admin_queries.remove_playbook(name, version)
