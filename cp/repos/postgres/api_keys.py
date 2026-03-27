from ...infra.db import execute_stmt, fetch_all, fetch_one
from ...models import ApiKeyCreateRequest, ApiKeyRecord, ApiKeySummary


class ApiKeysRepo:

    def get_api_key(self, access_key: str) -> ApiKeyRecord | None:
        fetch_one(
            """
                    SELECT access_key, encrypted_secret_access_key, owner, valid_until, roles
                    FROM api_keys
                    WHERE access_key = %s
                    """,
            (access_key,),
            ApiKeyRecord,
        )

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

        return fetch_all(sql, params, ApiKeySummary)

    def create_api_key(
        self,
        api_key: ApiKeyCreateRequest,
        *,
        owner: str,
        encrypted_secret_access_key: bytes,
    ) -> ApiKeySummary:
        return fetch_one(
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
            ApiKeySummary,
        )

    def delete_api_key(self, access_key: str) -> None:
        execute_stmt(
            """
                DELETE
                FROM api_keys
                WHERE access_key = %s
                """,
            (access_key,),
        )
