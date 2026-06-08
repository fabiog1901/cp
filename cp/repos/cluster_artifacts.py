"""Cluster artifact catalog repository."""

from cpkit.db import execute_stmt, fetch_all, fetch_one

from ..models import ClusterArtifact, ClusterArtifactUpdate, ClusterArtifactUpsert


class ClusterArtifactsRepo:
    def create_cluster_artifact(self, artifact: ClusterArtifactUpsert) -> None:
        execute_stmt(
            """
            INSERT INTO cluster_artifact_catalog (
                artifact_id,
                job_id,
                cluster_id,
                kind,
                status,
                artifact_name,
                bucket,
                object_key,
                size_bytes,
                sha256,
                redacted,
                metadata,
                expires_at,
                created_by,
                updated_by
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                artifact.artifact_id,
                artifact.job_id,
                artifact.cluster_id,
                artifact.kind,
                artifact.status,
                artifact.artifact_name,
                artifact.bucket,
                artifact.object_key,
                artifact.size_bytes,
                artifact.sha256,
                artifact.redacted,
                artifact.metadata,
                artifact.expires_at,
                artifact.created_by,
                artifact.updated_by or artifact.created_by,
            ),
            operation="cluster_artifacts.create",
        )

    def update_cluster_artifact(
        self,
        artifact_id: str,
        update: ClusterArtifactUpdate,
    ) -> None:
        execute_stmt(
            """
            UPDATE cluster_artifact_catalog
            SET
                status = coalesce(%s, status),
                artifact_name = coalesce(%s, artifact_name),
                bucket = coalesce(%s, bucket),
                object_key = coalesce(%s, object_key),
                size_bytes = coalesce(%s, size_bytes),
                sha256 = coalesce(%s, sha256),
                redacted = coalesce(%s, redacted),
                metadata = coalesce(%s, metadata),
                expires_at = coalesce(%s, expires_at),
                updated_by = %s
            WHERE artifact_id = %s
            """,
            (
                update.status,
                update.artifact_name,
                update.bucket,
                update.object_key,
                update.size_bytes,
                update.sha256,
                update.redacted,
                update.metadata,
                update.expires_at,
                update.updated_by,
                artifact_id,
            ),
            operation="cluster_artifacts.update",
        )

    def get_cluster_artifact(
        self,
        cluster_id: str,
        artifact_id: str,
    ) -> ClusterArtifact | None:
        return fetch_one(
            """
            SELECT *
            FROM cluster_artifact_catalog
            WHERE cluster_id = %s
                AND artifact_id = %s
            """,
            (cluster_id, artifact_id),
            ClusterArtifact,
            operation="cluster_artifacts.get",
        )

    def list_cluster_artifacts(
        self,
        cluster_id: str,
        kind: str | None = None,
    ) -> list[ClusterArtifact]:
        if kind:
            return fetch_all(
                """
                SELECT *
                FROM cluster_artifact_catalog
                WHERE cluster_id = %s
                    AND kind = %s
                ORDER BY created_at DESC
                """,
                (cluster_id, kind),
                ClusterArtifact,
                operation="cluster_artifacts.list",
            )

        return fetch_all(
            """
            SELECT *
            FROM cluster_artifact_catalog
            WHERE cluster_id = %s
            ORDER BY created_at DESC
            """,
            (cluster_id,),
            ClusterArtifact,
            operation="cluster_artifacts.list",
        )
