# Backups and Recovery

!!! note "Draft"
    This page is a human-owned domain draft. Generated route, symbol, and module
    indexes live under `docs/generated/`.

## Purpose

Backups and recovery covers backup path discovery, backup detail inspection,
backup catalog sync, object restore, and full-cluster recovery.

CP does not create every backup directly. Managed clusters produce scheduled
backups into S3-compatible storage. CP builds a catalog so users can browse and
restore from known backup paths.

## Concepts

- Backup path: storage location containing CockroachDB backup data.
- Backup catalog: CP metadata describing available backup paths and contents.
- Backup details: object-level contents discovered from a selected backup path.
- Object restore: restoring one database or table.
- Full-cluster recovery: restoring a full backup into a target cluster.
- External connection: storage connection metadata used by clusters and CP.

## Lifecycle

1. Managed clusters write scheduled backups to object storage.
2. CP syncs backup catalog metadata.
3. Users browse available backup paths and contents in the webapp.
4. Users request object restore or full-cluster recovery.
5. Services enqueue restore commands.
6. Local workers submit CockroachDB restore jobs and poll progress.
7. CP updates job/task state and cluster state.

## Backend Entry Points

| Layer | Files |
| --- | --- |
| API | `cp/api/clusters.py`, `cp/api/cluster_recovery.py` |
| Services | `cp/services/cluster_backups.py`, `cp/services/backup_catalog.py`, `cp/services/storage_broker.py` |
| Repos | `cp/repos/backup_catalog.py`, `cp/repos/external_connections.py` |
| Workers | `cp/workers/local/backup_catalog.py`, `cp/workers/local/restore.py` |
| Schema | `resources/ddl.sql` |

## Tables

| Table | Purpose |
| --- | --- |
| `cluster_backup_catalog` | Backup path metadata. |
| `cluster_backup_catalog_objects` | Object-level backup contents. |
| external connection tables | Storage connection metadata and credentials. |

## API Resources

See [Generated API Route Index](../generated/api/routes.md) for the current
route inventory.

Important backup and recovery resources include:

- `GET /clusters/{cluster_id}/backups`
- `GET /clusters/{cluster_id}/backups/details`
- `POST /clusters/{cluster_id}/backups/restore`
- `POST /clusters/{cluster_id}/restore/objects`
- `GET /cluster-recovery/backups`
- `POST /cluster-recovery/backups/sync`
- `POST /cluster-recovery/restores`

## Webapp

Relevant UI surfaces:

- Backup Details
- Backup Contents
- Cluster Recovery
- Restore confirmation modals

Relevant files:

- `webapp/index.html`
- `webapp/script.js`
- `webapp/style.css`

## Important Invariants

- Backup catalog sync should avoid scanning object storage on every UI request.
- Restore requests should become jobs rather than blocking long HTTP requests.
- Full-cluster recovery requires source and target cluster context.
- Restore workers must update both CP job/task state and cluster state.
- Storage credentials should flow through storage/external connection helpers,
  not ad hoc string handling.

## Do Not Confuse With

- Backup catalog metadata is CP state.
- CockroachDB restore jobs are managed-cluster state.
- CP jobs track CP workflow state around restore submission and polling.

## Common Changes

| Change | Start Here |
| --- | --- |
| Change backup catalog sync | `cp/services/backup_catalog.py`, `cp/workers/local/backup_catalog.py` |
| Change backup details query | `cp/services/cluster_backups.py` |
| Change restore behavior | `cp/services/cluster_backups.py`, `cp/workers/local/restore.py` |
| Change storage URI handling | `cp/services/storage_broker.py` |
