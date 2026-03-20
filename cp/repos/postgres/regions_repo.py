"""Regions repository backed by CockroachDB/Postgres."""

from ...models import Region
from . import repository


def list_regions() -> list[Region]:
    return repository.get_all_regions()


def add_region(region: Region) -> None:
    repository.add_region(region)


def delete_region(cloud: str, region: str, zone: str) -> None:
    repository.remove_version(cloud, region, zone)
