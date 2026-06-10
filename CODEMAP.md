# Code Map

<!-- GENERATED FILE: DO NOT EDIT -->

This file is a deterministic map of the Python package surface in this repository.
Regenerate it after structural code changes with:

```bash
python tools/codemap.py --write
```

## Project

- Name: `cp`
- Package roots: `cp`

## Entry Points

- `cp` -> `cpkit.cli:main`

## Packages

| Package | Modules | Classes | Functions | Routes |
| --- | ---: | ---: | ---: | ---: |
| `cp` | 57 | 111 | 87 | 55 |

## API Routes

| Method | Path | Handler | Response Model |
| --- | --- | --- | --- |
| `GET` | `/alerts` | `cp.api.alerts.list_alerts` | `list[LiveAlert]` |
| `POST` | `/alerts/webhook` | `cp.api.alerts.receive_alert` | `-` |
| `GET` | `/cluster-recovery/backups` | `cp.api.cluster_recovery.list_recovery_backups` | `BackupCatalogSnapshot` |
| `POST` | `/cluster-recovery/backups/sync` | `cp.api.cluster_recovery.sync_recovery_backups` | `-` |
| `POST` | `/cluster-recovery/restores` | `cp.api.cluster_recovery.restore_full_cluster` | `JobID` |
| `GET` | `/clusters` | `cp.api.clusters.list_clusters` | `-` |
| `POST` | `/clusters` | `cp.api.clusters.create_cluster` | `JobID` |
| `GET` | `/clusters/options` | `cp.api.clusters.get_cluster_create_options` | `ClusterCreateOptionsResponse` |
| `POST` | `/clusters/scale` | `cp.api.clusters.scale_cluster` | `JobID` |
| `GET` | `/clusters/stats` | `cp.api.clusters.get_cluster_stats` | `ClusterStatsResponse` |
| `POST` | `/clusters/upgrade` | `cp.api.clusters.upgrade_cluster` | `JobID` |
| `DELETE` | `/clusters/{cluster_id}` | `cp.api.clusters.delete_cluster` | `JobID` |
| `GET` | `/clusters/{cluster_id}` | `cp.api.clusters.get_cluster` | `-` |
| `GET` | `/clusters/{cluster_id}/artifacts` | `cp.api.clusters.list_cluster_artifacts` | `ClusterArtifactsSnapshot` |
| `POST` | `/clusters/{cluster_id}/artifacts/{artifact_id}/download-url` | `cp.api.clusters.create_cluster_artifact_download_url` | `ArtifactDownloadUrlResponse` |
| `GET` | `/clusters/{cluster_id}/backups` | `cp.api.clusters.get_cluster_backups` | `ClusterBackupsSnapshot` |
| `GET` | `/clusters/{cluster_id}/backups/details` | `cp.api.clusters.get_cluster_backup_details` | `-` |
| `POST` | `/clusters/{cluster_id}/backups/restore` | `cp.api.clusters.restore_cluster` | `JobID` |
| `GET` | `/clusters/{cluster_id}/dashboard` | `cp.api.clusters.get_cluster_dashboard` | `DashboardSnapshot` |
| `GET` | `/clusters/{cluster_id}/database-objects` | `cp.api.clusters.list_cluster_database_objects` | `list[ClusterDatabaseObjectDetails]` |
| `POST` | `/clusters/{cluster_id}/database-objects` | `cp.api.clusters.create_cluster_database_object` | `ClusterDatabaseObject` |
| `DELETE` | `/clusters/{cluster_id}/database-objects/{database_name}` | `cp.api.clusters.delete_cluster_database_object` | `-` |
| `GET` | `/clusters/{cluster_id}/database-objects/{database_name}` | `cp.api.clusters.get_cluster_database_object` | `ClusterDatabaseObject` |
| `GET` | `/clusters/{cluster_id}/database-role-group-mappings` | `cp.api.clusters.list_cluster_database_role_group_mappings` | `list[ClusterDatabaseRoleGroupMapping]` |
| `PUT` | `/clusters/{cluster_id}/database-role-group-mappings/{database_role}` | `cp.api.clusters.update_cluster_database_role_group_mappings` | `list[ClusterDatabaseRoleGroupMapping]` |
| `POST` | `/clusters/{cluster_id}/debug-zip` | `cp.api.clusters.create_cluster_debug_zip` | `JobID` |
| `POST` | `/clusters/{cluster_id}/healthcheck` | `cp.api.clusters.healthcheck_cluster` | `JobID` |
| `GET` | `/clusters/{cluster_id}/jobs` | `cp.api.clusters.get_cluster_jobs` | `ClusterJobsSnapshot` |
| `GET` | `/clusters/{cluster_id}/options` | `cp.api.clusters.get_cluster_options` | `ClusterDialogOptionsResponse` |
| `POST` | `/clusters/{cluster_id}/restore/objects` | `cp.api.clusters.restore_cluster_object` | `JobID` |
| `GET` | `/clusters/{cluster_id}/users` | `cp.api.clusters.get_cluster_users` | `ClusterUsersSnapshot` |
| `POST` | `/clusters/{cluster_id}/users` | `cp.api.clusters.create_cluster_user` | `-` |
| `DELETE` | `/clusters/{cluster_id}/users/{username}` | `cp.api.clusters.delete_cluster_user` | `-` |
| `POST` | `/clusters/{cluster_id}/users/{username}/grant-database-roles` | `cp.api.clusters.grant_cluster_user_database_roles` | `-` |
| `POST` | `/clusters/{cluster_id}/users/{username}/password` | `cp.api.clusters.update_cluster_user_password` | `-` |
| `POST` | `/clusters/{cluster_id}/users/{username}/revoke-database-roles` | `cp.api.clusters.revoke_cluster_user_database_roles` | `-` |
| `GET` | `/cpu_counts` | `cp.api.admin.cpu_counts.list_cpu_counts` | `-` |
| `POST` | `/cpu_counts` | `cp.api.admin.cpu_counts.create_cpu_count` | `-` |
| `DELETE` | `/cpu_counts/{cpu_count}` | `cp.api.admin.cpu_counts.delete_cpu_count` | `-` |
| `GET` | `/database_role_templates` | `cp.api.admin.database_role_templates.list_database_role_templates` | `-` |
| `POST` | `/database_role_templates` | `cp.api.admin.database_role_templates.create_database_role_template` | `-` |
| `DELETE` | `/database_role_templates/{database_role_template}` | `cp.api.admin.database_role_templates.delete_database_role_template` | `-` |
| `GET` | `/disk_sizes` | `cp.api.admin.disk_sizes.list_disk_sizes` | `-` |
| `POST` | `/disk_sizes` | `cp.api.admin.disk_sizes.create_disk_size` | `-` |
| `DELETE` | `/disk_sizes/{size_gb}` | `cp.api.admin.disk_sizes.delete_disk_size` | `-` |
| `GET` | `/node_counts` | `cp.api.admin.node_counts.list_node_counts` | `-` |
| `POST` | `/node_counts` | `cp.api.admin.node_counts.create_node_count` | `-` |
| `DELETE` | `/node_counts/{node_count}` | `cp.api.admin.node_counts.delete_node_count` | `-` |
| `GET` | `/prom-targets` | `cp.api.prometheus.get_targets` | `-` |
| `GET` | `/regions` | `cp.api.admin.regions.list_regions` | `-` |
| `POST` | `/regions` | `cp.api.admin.regions.create_region` | `-` |
| `DELETE` | `/regions/{cloud}/{region}/{zone}` | `cp.api.admin.regions.delete_region` | `-` |
| `GET` | `/versions` | `cp.api.admin.versions.list_versions` | `-` |
| `POST` | `/versions` | `cp.api.admin.versions.create_version` | `-` |
| `DELETE` | `/versions/{version}` | `cp.api.admin.versions.delete_version` | `-` |

## Command Handlers

- `CommandType.CREATE_CLUSTER` -> `cp.workers.commands.create_cluster`
- `CommandType.DEBUG_ZIP_CLUSTER` -> `cp.workers.commands.debug_zip_cluster`
- `CommandType.DELETE_CLUSTER` -> `cp.workers.commands.delete_cluster`
- `CommandType.HEALTHCHECK_CLUSTER` -> `cp.workers.commands.healthcheck_cluster`
- `CommandType.POLL_CLUSTER_RESTORE` -> `cp.workers.commands.poll_cluster_restore`
- `CommandType.POLL_DEBUG_ZIP` -> `cp.workers.commands.poll_debug_zip`
- `CommandType.RECREATE_CLUSTER` -> `cp.workers.commands.lambda job_id, command, requested_by: create_cluster(job_id, command, requested_by, True)`
- `CommandType.RESTORE_CLUSTER` -> `cp.workers.commands.restore_cluster`
- `CommandType.RESTORE_CLUSTER_OBJECT` -> `cp.workers.commands.restore_cluster_object`
- `CommandType.RESTORE_FULL_CLUSTER` -> `cp.workers.commands.restore_full_cluster`
- `CommandType.SCALE_CLUSTER` -> `cp.workers.commands.scale_cluster`
- `CommandType.SYNC_BACKUP_CATALOG` -> `cp.workers.commands.sync_backup_catalog`
- `CommandType.SYNC_CLUSTER_BACKUP_CATALOG` -> `cp.workers.commands.sync_cluster_backup_catalog`
- `CommandType.UPGRADE_CLUSTER` -> `cp.workers.commands.upgrade_cluster`

## Modules

| File | Public Surface |
| --- | --- |
| `cp/__init__.py` | CP application package. |
| `cp/api/__init__.py` | FastAPI router packages for the cp application. |
| `cp/api/admin/__init__.py` | no public surface |
| `cp/api/admin/cpu_counts.py` | functions: list_cpu_counts, create_cpu_count, delete_cpu_count; routes: 3 |
| `cp/api/admin/database_role_templates.py` | functions: list_database_role_templates, create_database_role_template, delete_database_role_template; routes: 3 |
| `cp/api/admin/disk_sizes.py` | functions: list_disk_sizes, create_disk_size, delete_disk_size; routes: 3 |
| `cp/api/admin/node_counts.py` | functions: list_node_counts, create_node_count, delete_node_count; routes: 3 |
| `cp/api/admin/regions.py` | functions: list_regions, create_region, delete_region; routes: 3 |
| `cp/api/admin/versions.py` | functions: list_versions, create_version, delete_version; routes: 3 |
| `cp/api/alerts.py` | Alert API routes.; functions: list_alerts, receive_alert; routes: 2 |
| `cp/api/cluster_recovery.py` | Cluster recovery API routes.; functions: list_recovery_backups, sync_recovery_backups, restore_full_cluster; routes: 3 |
| `cp/api/clusters.py` | Cluster API routes.; functions: list_clusters, get_cluster_stats, get_cluster_create_options, create_cluster, get_cluster, delete_cluster, create_cluster_debug_zip, list_cluster_artifacts, create_cluster_artifact_download_url, healthcheck_cluster, get_cluster_options, scale_cluster, upgrade_cluster, get_cluster_jobs, get_cluster_backups, get_cluster_backup_details, restore_cluster, restore_cluster_object, list_cluster_database_objects, create_cluster_database_object, get_cluster_database_object, delete_cluster_database_object, list_cluster_database_role_group_mappings, update_cluster_database_role_group_mappings, get_cluster_users, create_cluster_user, delete_cluster_user, grant_cluster_user_database_roles, revoke_cluster_user_database_roles, update_cluster_user_password, get_cluster_dashboard; routes: 31 |
| `cp/api/prometheus.py` | Prometheus target API routes.; functions: get_targets; routes: 1 |
| `cp/cluster_database.py` | Managed-cluster database connection helpers.; classes: ClusterDatabaseConnectionError; functions: connect_cluster_db, translate_database_error |
| `cp/main.py` | CP FastAPI application wiring. |
| `cp/models.py` | Shared CP domain, API, command, and persistence models.; classes: AutoNameStrEnum, PlaybookName, CommandType, ClusterState, JobState, ClusterArtifactState, AuditEvent, SettingKey, StrID, ClusterIDRef, WebUser, ClusterStatsResponse, ErrorResponse, ClusterOverview, InventoryRegion, InventoryLB, ClusterPublic, Cluster, ExternalConnection, ExternalConnectionUpsert, ClusterRequest, CommandModel, CreateClusterCommand, ClusterUpgradeRequest, DeleteClusterCommand, HealthcheckClusterCommand, DebugZipOptions, DebugZipRequest, DebugZipClusterCommand, PollDebugZipCommand, RestoreRequest, RestoreClusterObjectRequest, RestoreFullClusterRequest, PollClusterRestoreRequest, SyncBackupCatalogRequest, SyncClusterBackupCatalogRequest, ClusterScaleRequest, BackupDetails, BackupPathOption, BackupCatalogObject, BackupCatalogEntry, BackupCatalogSnapshot, ClusterRecoveryRestoreApiRequest, BackupCatalogObjectUpsert, BackupCatalogEntryUpsert, DatabaseUser, DatabaseRoleTemplateConfig, ClusterDatabaseRole, ClusterDatabaseRoleDetails, ClusterDatabaseRoleGroupMapping, ClusterDatabaseObject, ClusterDatabaseObjectDetails, CreateClusterDatabaseObjectRequest, NewDatabaseUserRequest, ClusterArtifactUpsert, ClusterArtifactUpdate, ClusterArtifact, ArtifactDownloadUrlResponse, ClusterArtifactsSnapshot, Region, Version, RegionOption, NodeCountOption, CpuCountOption, DiskSizeOption, Nodes, DashboardMetrics, DashboardSnapshot, ClusterJobsSnapshot, ClusterUsersSnapshot, ClusterBackupsSnapshot, ClusterCreateOptionsResponse, ClusterDialogOptionsResponse, ClusterCreateApiRequest, ClusterRestoreApiRequest, ClusterObjectRestoreApiRequest, ClusterDatabaseRolesUpdateRequest, ClusterDatabaseRoleGroupsUpdateRequest, ClusterPasswordUpdateRequest, NoFreeComputeUnitError, ComputeUnitNotFoundError, ComputeUnitStateError, ComputeUnitOperationError, AllocatePlaybookError, DeferredTask, Alert, AlertmanagerPayload, LiveAlert; functions: to_public_cluster |
| `cp/prometheus.py` | Prometheus scrape target helpers.; functions: get_nodes |
| `cp/repos/__init__.py` | Repository-layer package.; classes: Repo |
| `cp/repos/admin/__init__.py` | Admin repository package. |
| `cp/repos/admin/cluster_options.py` | Admin option and cluster database-access metadata repository.; classes: ClusterOptionsRepo |
| `cp/repos/admin/regions.py` | Admin regions repository.; classes: RegionsRepo |
| `cp/repos/admin/versions.py` | Admin versions repository.; classes: VersionsRepo |
| `cp/repos/alerts.py` | Alerts repository.; classes: AlertsRepo |
| `cp/repos/backup_catalog.py` | Backup catalog metadata repository.; classes: BackupCatalogRepo |
| `cp/repos/cluster.py` | Cluster metadata repository.; classes: ClusterRepo |
| `cp/repos/cluster_artifacts.py` | Cluster artifact catalog repository.; classes: ClusterArtifactsRepo |
| `cp/repos/cluster_jobs.py` | Cluster jobs repository.; classes: ClusterJobsRepo |
| `cp/repos/common.py` | Shared helpers for repository models.; functions: convert_model_to_sql |
| `cp/repos/external_connections.py` | External connections repository.; classes: ExternalConnectionsRepo |
| `cp/services/__init__.py` | Service-layer package. |
| `cp/services/admin/__init__.py` | Admin service package. |
| `cp/services/admin/cluster_options.py` | Admin cluster option service.; classes: ClusterOptionsService |
| `cp/services/admin/regions.py` | Business logic for the admin regions vertical.; classes: RegionsService |
| `cp/services/admin/versions.py` | Business logic for the admin versions vertical.; classes: VersionsService |
| `cp/services/alerts.py` | Business logic for the alerts vertical.; classes: AlertsService |
| `cp/services/backup_catalog.py` | Backup catalog service.; classes: BackupCatalogService |
| `cp/services/cluster.py` | Cluster lifecycle service.; classes: ClusterService |
| `cp/services/cluster_backups.py` | Backup and restore service for individual clusters.; classes: ClusterBackupsService |
| `cp/services/cluster_db.py` | Shared helpers for connecting to a cluster SQL endpoint.; functions: get_primary_dns_address, get_cluster_db_password, connect_to_cluster_db |
| `cp/services/cluster_jobs.py` | Business logic for the cluster jobs vertical.; classes: ClusterJobsService |
| `cp/services/cluster_users.py` | Database access workflows for managed clusters.; classes: ClusterUsersService |
| `cp/services/dashboard.py` | Cluster dashboard service.; classes: DashboardService |
| `cp/services/storage_broker.py` | Provision and resolve external storage connections for clusters.; classes: PresignedS3Url, StorageBrokerService |
| `cp/workers/__init__.py` | Worker runtime package. |
| `cp/workers/commands.py` | CP command handlers for queued framework jobs.; command handlers: 14 |
| `cp/workers/local/__init__.py` | Local CP workers that use CP-managed resources and SQL connections. |
| `cp/workers/local/backup_catalog.py` | Local backup catalog worker.; functions: sync_backup_catalog, sync_cluster_backup_catalog |
| `cp/workers/local/restore.py` | Local restore worker.; functions: restore_cluster, restore_full_cluster, restore_cluster_object, restore_full_cluster_worker, restore_cluster_worker, poll_cluster_restore |
| `cp/workers/remote/__init__.py` | Remote workers that prepare CP inputs for cpkit playbook execution. |
| `cp/workers/remote/common.py` | Shared helpers for cluster workers.; functions: get_node_count_per_zone |
| `cp/workers/remote/create.py` | Remote cluster creation worker.; functions: create_cluster, create_cluster_worker |
| `cp/workers/remote/debug_zip.py` | Remote cluster debug zip worker.; functions: debug_zip_cluster, debug_zip_cluster_worker |
| `cp/workers/remote/delete.py` | Remote cluster deletion worker.; functions: delete_cluster, delete_cluster_worker |
| `cp/workers/remote/healthcheck.py` | Remote cluster healthcheck worker.; functions: healthcheck_cluster, healthcheck_cluster_worker |
| `cp/workers/remote/poll_debug_zip.py` | Remote debug zip polling worker.; functions: poll_debug_zip |
| `cp/workers/remote/scale.py` | Remote cluster scale worker.; functions: scale_cluster, scale_cluster_worker_entry, parse_raw_data, scale_cluster_worker |
| `cp/workers/remote/upgrade.py` | Remote cluster upgrade worker.; functions: upgrade_cluster, upgrade_cluster_worker |
