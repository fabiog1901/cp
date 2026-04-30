"""Backup catalog repository."""

import datetime as dt

from ..infra.db import execute_stmt, fetch_all
from ..models import BackupCatalogEntry, BackupCatalogEntryUpsert


class BackupCatalogRepo:
    def list_backup_catalog(
        self,
        groups: list[str],
        is_admin: bool = False,
        *,
        full_cluster_only: bool = False,
    ) -> list[BackupCatalogEntry]:
        where = []
        params: list = []
        operation = "backup_catalog.list.admin"

        if not is_admin:
            where.append("grp = ANY (%s)")
            params.append(groups)
            operation = "backup_catalog.list"
        if full_cluster_only:
            where.append("is_full_cluster = true")

        where_clause = f"WHERE {' AND '.join(where)}" if where else ""
        return fetch_all(
            f"""
            SELECT *
            FROM cluster_backup_catalog
            {where_clause}
            ORDER BY end_time DESC NULLS LAST, updated_at DESC
            """,
            tuple(params),
            BackupCatalogEntry,
            operation=operation,
        )

    def replace_cluster_backup_catalog(
        self,
        cluster_id: str,
        entries: list[BackupCatalogEntryUpsert],
    ) -> None:
        now = dt.datetime.now(dt.timezone.utc)
        execute_stmt(
            """
            UPDATE cluster_backup_catalog
            SET status = 'NOT_SEEN_RECENTLY',
                updated_at = now()
            WHERE cluster_id = %s
            """,
            (cluster_id,),
            operation="backup_catalog.mark_cluster_stale",
        )

        for entry in entries:
            execute_stmt(
                """
                UPSERT INTO cluster_backup_catalog (
                    cluster_id,
                    backup_path,
                    grp,
                    backup_type,
                    start_time,
                    end_time,
                    is_full_cluster,
                    status,
                    object_count,
                    last_seen_at,
                    sync_error
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    entry.cluster_id,
                    entry.backup_path,
                    entry.grp,
                    entry.backup_type,
                    entry.start_time,
                    entry.end_time,
                    entry.is_full_cluster,
                    entry.status,
                    entry.object_count,
                    now,
                    entry.sync_error,
                ),
                operation="backup_catalog.upsert_entry",
            )
            execute_stmt(
                """
                DELETE FROM cluster_backup_catalog_objects
                WHERE cluster_id = %s
                    AND backup_path = %s
                """,
                (entry.cluster_id, entry.backup_path),
                operation="backup_catalog.delete_objects",
            )
            for obj in entry.objects:
                execute_stmt(
                    """
                    INSERT INTO cluster_backup_catalog_objects (
                        cluster_id,
                        backup_path,
                        ordinal,
                        database_name,
                        parent_schema_name,
                        object_name,
                        object_type,
                        backup_type,
                        start_time,
                        end_time,
                        size_bytes,
                        row_count,
                        is_full_cluster,
                        regions,
                        last_seen_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        entry.cluster_id,
                        entry.backup_path,
                        obj.ordinal,
                        obj.database_name,
                        obj.parent_schema_name,
                        obj.object_name,
                        obj.object_type,
                        obj.backup_type,
                        obj.start_time,
                        obj.end_time,
                        obj.size_bytes,
                        obj.row_count,
                        obj.is_full_cluster,
                        obj.regions,
                        now,
                    ),
                    operation="backup_catalog.insert_object",
                )

    def mark_cluster_backup_catalog_unavailable(
        self,
        cluster_id: str,
        sync_error: str,
    ) -> None:
        execute_stmt(
            """
            UPDATE cluster_backup_catalog
            SET status = 'SOURCE_UNAVAILABLE',
                sync_error = %s,
                updated_at = now()
            WHERE cluster_id = %s
            """,
            (sync_error, cluster_id),
            operation="backup_catalog.mark_cluster_unavailable",
        )
