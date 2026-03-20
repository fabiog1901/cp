"""Auth/support repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt
from ...models import RoleGroupMap
from ...models import StrID


def get_secret(secret_id: str) -> str:
    str_id: StrID = execute_stmt(
        """
        SELECT data AS id
        FROM secrets
        WHERE id = %s
        """,
        (secret_id,),
        StrID,
        return_list=False,
    )
    return str_id.id


def list_role_group_mappings() -> list[RoleGroupMap]:
    return execute_stmt(
        """
        SELECT role, groups
        FROM role_to_groups_mappings
        """,
        (),
        RoleGroupMap,
    )
