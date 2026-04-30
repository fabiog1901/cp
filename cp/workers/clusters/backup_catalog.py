import logging

from psycopg import sql
from psycopg.rows import dict_row

from ...infra import get_repo
from ...infra.db import get_pool
from ...models import (
    BackupCatalogEntryUpsert,
    BackupCatalogObjectUpsert,
    ClusterState,
    CommandType,
    SyncBackupCatalogRequest,
    SyncClusterBackupCatalogRequest,
)
from ...services.storage_broker import StorageBrokerService

logger = logging.getLogger(__name__)

BACKUP_CATALOG_SYNC_INTERVAL_SECONDS = 300


def sync_backup_catalog(
    _msg_id: int,
    _command: SyncBackupCatalogRequest,
    requested_by: str,
) -> None:
    repo = get_repo()
    skipped_statuses = {ClusterState.DELETING.value, ClusterState.DELETED.value}

    for cluster in repo.list_clusters([], True):
        if cluster.status in skipped_statuses:
            continue
        repo.enqueue_message(
            CommandType.SYNC_CLUSTER_BACKUP_CATALOG,
            SyncClusterBackupCatalogRequest(cluster_id=cluster.cluster_id),
            requested_by,
        )

    repo.enqueue_message(
        CommandType.SYNC_BACKUP_CATALOG,
        SyncBackupCatalogRequest(),
        requested_by,
        start_after_seconds=BACKUP_CATALOG_SYNC_INTERVAL_SECONDS,
    )


def sync_cluster_backup_catalog(
    _msg_id: int,
    command: SyncClusterBackupCatalogRequest,
    requested_by: str,
) -> None:
    repo = get_repo()
    cluster = repo.get_cluster(command.cluster_id, [], True)
    if cluster is None:
        return

    try:
        backup_uri = StorageBrokerService(repo).get_backup_external_connection_uri(
            cluster.cluster_id
        )
        entries = []
        with get_pool().connection() as conn:
            with conn.cursor() as cur:
                path_rows = cur.execute(
                    sql.SQL("SHOW BACKUPS IN {}").format(sql.Literal(backup_uri))
                ).fetchall()
            with conn.cursor(row_factory=dict_row) as cur:
                for path_row in path_rows:
                    backup_path = str(path_row[0])
                    detail_rows = cur.execute(
                        sql.SQL("SELECT * FROM [SHOW BACKUP FROM {} IN {}]").format(
                            sql.Literal(backup_path),
                            sql.Literal(backup_uri),
                        )
                    ).fetchall()
                    entries.append(
                        _catalog_entry_from_backup_details(
                            cluster.cluster_id,
                            cluster.grp,
                            backup_path,
                            detail_rows,
                        )
                    )

        repo.replace_cluster_backup_catalog(cluster.cluster_id, entries)
    except Exception as err:
        logger.exception(
            "Unable to sync backup catalog for cluster '%s'", cluster.cluster_id
        )
        repo.mark_cluster_backup_catalog_unavailable(cluster.cluster_id, str(err))


def _catalog_entry_from_backup_details(
    cluster_id: str,
    group: str | None,
    backup_path: str,
    rows: list[dict],
) -> BackupCatalogEntryUpsert:
    objects = [
        BackupCatalogObjectUpsert(
            ordinal=idx,
            database_name=_optional_str(row.get("database_name")),
            parent_schema_name=_optional_str(row.get("parent_schema_name")),
            object_name=_optional_str(row.get("object_name")),
            object_type=_optional_str(row.get("object_type")),
            backup_type=_optional_str(row.get("backup_type")),
            start_time=row.get("start_time"),
            end_time=row.get("end_time"),
            size_bytes=_optional_int(row.get("size_bytes")),
            row_count=_optional_int(row.get("rows")),
            is_full_cluster=_optional_bool(row.get("is_full_cluster")),
            regions=_optional_str(row.get("regions")),
        )
        for idx, row in enumerate(rows)
    ]

    start_times = [obj.start_time for obj in objects if obj.start_time is not None]
    end_times = [obj.end_time for obj in objects if obj.end_time is not None]
    backup_types = [obj.backup_type for obj in objects if obj.backup_type]
    is_full_cluster = any(obj.is_full_cluster is True for obj in objects)

    return BackupCatalogEntryUpsert(
        cluster_id=cluster_id,
        backup_path=backup_path,
        grp=group,
        backup_type=_summarize_backup_type(backup_types),
        start_time=min(start_times) if start_times else None,
        end_time=max(end_times) if end_times else None,
        is_full_cluster=is_full_cluster,
        status="AVAILABLE",
        object_count=len(objects),
        objects=objects,
    )


def _summarize_backup_type(backup_types: list[str]) -> str | None:
    normalized = {backup_type.lower() for backup_type in backup_types}
    if not normalized:
        return None
    if "incremental" in normalized:
        return "incremental"
    if "full" in normalized:
        return "full"
    return sorted(normalized)[0]


def _optional_str(value) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _optional_int(value) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_bool(value) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}
