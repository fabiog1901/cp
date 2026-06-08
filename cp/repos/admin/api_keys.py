"""Admin API keys repository."""

from ...infra.db import execute_stmt, fetch_all, fetch_one
from ...models import ApiKeyCreateRequestInDB, ApiKeyRecord, ApiKeySummary
from .base import AdminRepo


class ApiKeysRepo(AdminRepo):
    api_keys_table_name = "cpkit.api_keys"

    def get_api_key(self, access_key: str) -> ApiKeyRecord | None:
        return fetch_one(
            f"""
                    SELECT access_key, encrypted_secret_access_key, owner, valid_until, roles
                    FROM {self.api_keys_table_name}
                    WHERE access_key = %s
                    """,
            (access_key,),
            ApiKeyRecord,
            operation="api_keys.get",
        )

    def list_api_keys(self, access_key: str | None = None) -> list[ApiKeySummary]:
        params: list[str] = []
        sql = f"""
            SELECT access_key, owner, valid_until, roles
            FROM {self.api_keys_table_name}
        """

        if access_key is not None:
            sql += " WHERE access_key = %s"
            params.append(access_key)

        sql += " ORDER BY access_key"

        return fetch_all(sql, tuple(params), ApiKeySummary, operation="api_keys.list")

    def create_api_key(
        self,
        api_key: ApiKeyCreateRequestInDB,
        *,
        owner: str,
        encrypted_secret_access_key: bytes,
    ) -> ApiKeySummary:
        return fetch_one(
            f"""
                    INSERT INTO {self.api_keys_table_name} (
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
            ApiKeySummary,
            operation="api_keys.create",
        )

    def delete_api_key(self, access_key: str) -> None:
        execute_stmt(
            f"""
                DELETE
                FROM {self.api_keys_table_name}
                WHERE access_key = %s
                """,
            (access_key,),
            operation="api_keys.delete",
        )
