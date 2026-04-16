"""Auth/support repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all, fetch_one, fetch_scalar
from ...models import OIDCSessionRecord, RoleGroupMap
from ..base import BaseRepo


class AuthRepo(BaseRepo):

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

    def get_oidc_session(self, session_id: str) -> OIDCSessionRecord | None:
        return fetch_one(
            """
            SELECT
                session_id,
                encrypted_id_token,
                encrypted_refresh_token,
                token_expires_at,
                session_expires_at,
                created_at,
                updated_at
            FROM oidc_sessions
            WHERE session_id = %s
                AND session_expires_at > now()
            """,
            (session_id,),
            OIDCSessionRecord,
            operation="auth.get_oidc_session",
        )

    def create_oidc_session(self, session: OIDCSessionRecord) -> None:
        execute_stmt(
            """
            INSERT INTO oidc_sessions
                (session_id, encrypted_id_token, encrypted_refresh_token,
                 token_expires_at, session_expires_at)
            VALUES
                (%s, %s, %s, %s, %s)
            """,
            (
                session.session_id,
                session.encrypted_id_token,
                session.encrypted_refresh_token,
                session.token_expires_at,
                session.session_expires_at,
            ),
            operation="auth.create_oidc_session",
        )

    def update_oidc_session(
        self,
        session_id: str,
        *,
        encrypted_id_token: bytes,
        encrypted_refresh_token: bytes | None,
        token_expires_at,
    ) -> None:
        execute_stmt(
            """
            UPDATE oidc_sessions
            SET
                encrypted_id_token = %s,
                encrypted_refresh_token = %s,
                token_expires_at = %s
            WHERE session_id = %s
            """,
            (
                encrypted_id_token,
                encrypted_refresh_token,
                token_expires_at,
                session_id,
            ),
            operation="auth.update_oidc_session",
        )

    def delete_oidc_session(self, session_id: str) -> None:
        execute_stmt(
            """
            DELETE FROM oidc_sessions
            WHERE session_id = %s
            """,
            (session_id,),
            operation="auth.delete_oidc_session",
        )
