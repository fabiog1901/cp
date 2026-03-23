"""Auth/support repository backed by CockroachDB/Postgres."""
import json
import gzip

from ...infra.db import fetch_all, fetch_scalar
from ...models import RoleGroupMap
from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from ...models import (
    ApiKeyCreateRequest,
    ApiKeyRecord,
    ApiKeySummary,
    ComputeUnitInDB,
    ComputeUnitOverview,
    ComputeUnitStatus,
    LogMsg,
    Playbook,
    ServerInDB,
    ServerInitRequest,
    ServerStatus,
    SettingKey,
    SettingRecord,
)
from ..base import BaseRepo

class AuthRepo(BaseRepo):
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool

    @staticmethod
    def _setting_from_row(row) -> SettingRecord:
        value = row[1]
        default_value = row[2]
        effective_value = default_value if value is None else value
        return SettingRecord(
            key=row[0],
            value=value,
            default_value=default_value,
            effective_value=effective_value,
            value_type=row[3],
            category=row[4],
            is_secret=row[5],
            description=row[6] or "",
            updated_at=row[7],
            updated_by=row[8],
        )

    def get_api_key(self, access_key: str) -> ApiKeyRecord | None:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(ApiKeyRecord)) as cur:
                return cur.execute(
                    """
                    SELECT access_key, encrypted_secret_access_key, owner, valid_until, roles
                    FROM api_keys
                    WHERE access_key = %s
                    """,
                    (access_key,),
                ).fetchone()

    def list_api_keys(self, access_key: str | None = None) -> list[ApiKeySummary]:
        params: list[str] = []
        sql = """
            SELECT access_key, owner, valid_until, roles
            FROM api_keys
        """

        if access_key is not None:
            sql += " WHERE access_key = %s"
            params.append(access_key)

        sql += " ORDER BY access_key"

        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(ApiKeySummary)) as cur:
                return cur.execute(sql, params).fetchall()

    def create_api_key(
        self,
        api_key: ApiKeyCreateRequest,
        *,
        owner: str,
        encrypted_secret_access_key: bytes,
    ) -> ApiKeySummary:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(ApiKeySummary)) as cur:
                return cur.execute(
                    """
                    INSERT INTO api_keys (
                        access_key,
                        encrypted_secret_access_key,
                        owner,
                        valid_until,
                        roles
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING access_key, owner, valid_until, roles
                    """,
                    (
                        api_key.access_key,
                        encrypted_secret_access_key,
                        owner,
                        api_key.valid_until,
                        api_key.roles,
                    ),
                ).fetchone()

    def delete_api_key(self, access_key: str) -> None:
        with self.pool.connection() as conn:
            conn.execute(
                """
                DELETE
                FROM api_keys
                WHERE access_key = %s
                """,
                (access_key,),
            )

    def list_settings(self) -> list[SettingRecord]:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                rows = cur.execute(
                    """
                    SELECT
                        key,
                        value,
                        default_value,
                        value_type,
                        category,
                        is_secret,
                        description,
                        updated_at,
                        updated_by
                    FROM settings
                    ORDER BY category, key
                    """
                ).fetchall()

        return [self._setting_from_row(row) for row in rows]

    def get_setting(self, key: SettingKey) -> SettingRecord | None:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                row = cur.execute(
                    """
                    SELECT
                        key,
                        value,
                        default_value,
                        value_type,
                        category,
                        is_secret,
                        description,
                        updated_at,
                        updated_by
                    FROM settings
                    WHERE key = %s
                    """,
                    (key,),
                ).fetchone()

        return self._setting_from_row(row) if row is not None else None

    def update_setting(
        self,
        key: SettingKey,
        value,
        *,
        updated_by: str | None = None,
    ) -> SettingRecord | None:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                row = cur.execute(
                    """
                    UPDATE settings
                    SET
                        value = %s,
                        updated_at = CURRENT_TIMESTAMP,
                        updated_by = %s
                    WHERE key = %s
                    RETURNING
                        key,
                        value,
                        default_value,
                        value_type,
                        category,
                        is_secret,
                        description,
                        updated_at,
                        updated_by
                    """,
                    (value, updated_by, key),
                ).fetchone()

        return self._setting_from_row(row) if row is not None else None

    def reset_setting(
        self,
        key: SettingKey,
        *,
        updated_by: str | None = None,
    ) -> SettingRecord | None:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                row = cur.execute(
                    """
                    UPDATE settings
                    SET
                        value = NULL,
                        updated_at = CURRENT_TIMESTAMP,
                        updated_by = %s
                    WHERE key = %s
                    RETURNING
                        key,
                        value,
                        default_value,
                        value_type,
                        category,
                        is_secret,
                        description,
                        updated_at,
                        updated_by
                    """,
                    (updated_by, key),
                ).fetchone()

        return self._setting_from_row(row) if row is not None else None

    #
    # ADMIN_SERVICE
    #
    def playbook_get_content(self, playbook: Playbook) -> str:

        with self.pool.connection() as conn:

            cur = conn.cursor()
            rs = cur.execute(
                """
                SELECT content
                FROM playbooks
                WHERE id = %s
                """,
                (playbook,),
            ).fetchone()

        return gzip.decompress(rs[0]).decode()  # type: ignore
    
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
