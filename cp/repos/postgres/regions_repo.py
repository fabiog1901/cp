"""Regions repository backed by CockroachDB/Postgres."""

from ...models import Region
from . import admin_queries


def list_regions() -> list[Region]:
    return admin_queries.get_all_regions()


def add_region(region: Region) -> None:
    admin_queries.add_region(region)


def delete_region(cloud: str, region: str, zone: str) -> None:
    admin_queries.remove_region(cloud, region, zone)
