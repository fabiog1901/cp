"""Auth/support repository backed by CockroachDB/Postgres."""

from ...models import RoleGroupMap
from . import admin_queries


def get_secret(secret_id: str) -> str:
    return admin_queries.get_secret(secret_id)


def list_role_group_mappings() -> list[RoleGroupMap]:
    return admin_queries.get_role_to_groups_mappings()
