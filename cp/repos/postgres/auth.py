"""Auth/support repository backed by CockroachDB/Postgres."""

from ...infra.db import fetch_all, fetch_scalar
from ...models import RoleGroupMap


class AuthRepo:
    @staticmethod
    def get_secret(secret_id: str) -> str:
        return fetch_scalar(
            """
            SELECT data AS id
            FROM secrets
            WHERE id = %s
            """,
            (secret_id,),
            operation="auth.get_secret",
        )

    @staticmethod
    def list_role_group_mappings() -> list[RoleGroupMap]:
        return fetch_all(
            """
            SELECT role, groups
            FROM role_to_groups_mappings
            """,
            (),
            RoleGroupMap,
            operation="auth.list_role_group_mappings",
        )
