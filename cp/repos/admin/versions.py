"""Admin versions repository."""

from ...infra.db import execute_stmt, fetch_all
from ...models import Version
from ..common import convert_model_to_sql
from .base import AdminRepo


class VersionsRepo(AdminRepo):
    def list_versions(self) -> list[Version]:
        return fetch_all(
            """
            SELECT version
            FROM versions
            ORDER BY version DESC
            """,
            (),
            Version,
        )

    def create_version(self, version: Version) -> None:
        stmt, vals = convert_model_to_sql("versions", version)
        execute_stmt(stmt, vals)

    def delete_version(self, version: str) -> None:
        execute_stmt(
            """
            DELETE
            FROM versions
            WHERE version = %s
            """,
            (version,),
        )

    def list_upgrade_versions(self, major_version: str) -> list[Version]:
        return fetch_all(
            """
            SELECT version
            FROM versions
            WHERE version > %s
            ORDER BY version ASC
            """,
            (major_version,),
            Version,
        )
