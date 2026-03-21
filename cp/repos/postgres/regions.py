"""Regions repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all
from ...models import Region
from ...models import RegionOption
from .common import convert_model_to_sql


class RegionsRepo:
    @staticmethod
    def list_regions() -> list[Region]:
        return fetch_all(
            """
            SELECT cloud, region, zone, vpc_id, security_groups, subnet, image, extras
            FROM regions
            """,
            (),
            Region,
        )

    @staticmethod
    def list_region_options() -> list[RegionOption]:
        return fetch_all(
            """
            SELECT DISTINCT cloud || ':' || region AS region_id
            FROM regions
            ORDER BY region_id ASC
            """,
            (),
            RegionOption,
        )

    @staticmethod
    def get_region_config(cloud: str, region: str) -> list[Region]:
        return fetch_all(
            """
            SELECT cloud, region, zone, vpc_id, security_groups, subnet, image, extras
            FROM regions
            WHERE (cloud, region) = (%s, %s)
            """,
            (cloud, region),
            Region,
        )

    @staticmethod
    def add_region(region: Region) -> None:
        stmt, vals = convert_model_to_sql("regions", region)
        execute_stmt(stmt, vals)

    @staticmethod
    def delete_region(cloud: str, region: str, zone: str) -> None:
        execute_stmt(
            """
            DELETE FROM regions
            WHERE (cloud, region, zone) = (%s, %s, %s)
            """,
            (cloud, region, zone),
        )
