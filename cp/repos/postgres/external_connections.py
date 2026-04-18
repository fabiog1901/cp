"""External connections repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all, fetch_one
from ...models import ExternalConnection, ExternalConnectionUpsert
from ..base import BaseRepo


class ExternalConnectionsRepo(BaseRepo):
    def list_external_connections(self, cluster_id: str) -> list[ExternalConnection]:
        return fetch_all(
            """
            SELECT *
            FROM external_connections
            WHERE cluster_id = %s
            ORDER BY name
            """,
            (cluster_id,),
            ExternalConnection,
            operation="external_connections.list_external_connections",
        )

    def get_external_connection(
        self,
        cluster_id: str,
        name: str,
    ) -> ExternalConnection | None:
        return fetch_one(
            """
            SELECT *
            FROM external_connections
            WHERE cluster_id = %s
                AND name = %s
            """,
            (cluster_id, name),
            ExternalConnection,
            operation="external_connections.get_external_connection",
        )

    def upsert_external_connection(
        self,
        connection: ExternalConnectionUpsert,
        updated_by: str,
    ) -> None:
        execute_stmt(
            """
            UPSERT INTO external_connections (
                cluster_id,
                name,
                connection_type,
                provider,
                endpoint,
                bucket_name,
                access_key_id,
                encrypted_secret_access_key,
                metadata,
                status,
                created_by,
                updated_by
            ) VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                connection.cluster_id,
                connection.name,
                connection.connection_type,
                connection.provider,
                connection.endpoint,
                connection.bucket_name,
                connection.access_key_id,
                connection.encrypted_secret_access_key,
                connection.metadata,
                connection.status,
                updated_by,
                updated_by,
            ),
            operation="external_connections.upsert_external_connection",
        )

    def delete_external_connection(self, cluster_id: str, name: str) -> None:
        execute_stmt(
            """
            DELETE FROM external_connections
            WHERE cluster_id = %s
                AND name = %s
            """,
            (cluster_id, name),
            operation="external_connections.delete_external_connection",
        )
