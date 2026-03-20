"""Versions repository backed by CockroachDB/Postgres."""

from ...models import Version
from . import repository


def list_versions() -> list[Version]:
    return repository.get_versions()


def add_version(version: Version) -> None:
    repository.add_version(version)


def remove_version(version: str) -> None:
    repository.remove_version(version)
