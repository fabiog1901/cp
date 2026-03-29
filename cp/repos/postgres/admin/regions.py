"""Admin regions repository backed by CockroachDB/Postgres."""

from ....infra.db import execute_stmt, fetch_all
from ....models import Region, RegionOption
from ..common import convert_model_to_sql
from .base import AdminPostgresRepo


class RegionsRepo(AdminPostgresRepo):
    def list_regions(self) -> list[Region]:
        return fetch_all(
            """
            SELECT cloud, region, zone, vpc_id, security_groups, subnet, image, extras
            FROM regions
            """,
            (),
            Region,
        )

    def list_region_options(self) -> list[RegionOption]:
        return fetch_all(
            """
            SELECT DISTINCT cloud || ':' || region AS region_id
            FROM regions
            ORDER BY region_id ASC
            """,
            (),
            RegionOption,
        )

    def list_region_config(self, cloud: str, region: str) -> list[Region]:
        return fetch_all(
            """
            SELECT cloud, region, zone, vpc_id, security_groups, subnet, image, extras
            FROM regions
            WHERE (cloud, region) = (%s, %s)
            """,
            (cloud, region),
            Region,
        )

    def create_region(self, region: Region) -> None:
        stmt, vals = convert_model_to_sql("regions", region)
        execute_stmt(stmt, vals)

    def delete_region(self, cloud: str, region: str, zone: str) -> None:
        execute_stmt(
            """
            DELETE FROM regions
            WHERE (cloud, region, zone) = (%s, %s, %s)
            """,
            (cloud, region, zone),
        )
