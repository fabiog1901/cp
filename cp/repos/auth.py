"""Auth/support repository."""

from cpkit.auth import OIDCSessionsRepositoryMixin

from cpkit.db import fetch_all, fetch_scalar
from ..models import OIDCSessionRecord, RoleGroupMap


class AuthRepo(OIDCSessionsRepositoryMixin):
    oidc_session_record_type = OIDCSessionRecord

    def get_secret(self, secret_id: str) -> str:
        return fetch_scalar(
            """
            SELECT data AS id
            FROM secrets
            WHERE id = %s
            """,
            (secret_id,),
            operation="auth.get_secret",
        )

    def list_role_group_mappings(self) -> list[RoleGroupMap]:
        return fetch_all(
            """
            SELECT role, groups
            FROM role_to_groups_mappings
            """,
            (),
            RoleGroupMap,
            operation="auth.list_role_group_mappings",
        )
