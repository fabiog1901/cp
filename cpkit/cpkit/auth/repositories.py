"""Repository mixins for framework-owned auth tables."""

from cpkit.db import execute_stmt, fetch_all, fetch_one

API_KEYS_TABLE = "cpkit.api_keys"


class APIKeysRepositoryMixin:
    def get_api_key(self, access_key: str):
        return fetch_one(
            f"""
                    SELECT access_key, encrypted_secret_access_key, owner, valid_until, roles
                    FROM {API_KEYS_TABLE}
                    WHERE access_key = %s
                    """,
            (access_key,),
            self.api_key_record_type,
            operation="api_keys.get",
        )

    def list_api_keys(self, access_key: str | None = None):
        params: list[str] = []
        sql = f"""
            SELECT access_key, owner, valid_until, roles
            FROM {API_KEYS_TABLE}
        """

        if access_key is not None:
            sql += " WHERE access_key = %s"
            params.append(access_key)

        sql += " ORDER BY access_key"

        return fetch_all(
            sql,
            tuple(params),
            self.api_key_summary_type,
            operation="api_keys.list",
        )

    def create_api_key(
        self,
        api_key,
        *,
        owner: str,
        encrypted_secret_access_key: bytes,
    ):
        return fetch_one(
            f"""
                    INSERT INTO {API_KEYS_TABLE} (
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
            self.api_key_summary_type,
            operation="api_keys.create",
        )

    def delete_api_key(self, access_key: str) -> None:
        execute_stmt(
            f"""
                DELETE
                FROM {API_KEYS_TABLE}
                WHERE access_key = %s
                """,
            (access_key,),
            operation="api_keys.delete",
        )
