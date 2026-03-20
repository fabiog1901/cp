"""Versions repository backed by CockroachDB/Postgres."""

from ...models import Version
from . import admin_queries


def list_versions() -> list[Version]:
    return admin_queries.get_versions()


def add_version(version: Version) -> None:
    admin_queries.add_version(version)


def remove_version(version: str) -> None:
    admin_queries.remove_version(version)
