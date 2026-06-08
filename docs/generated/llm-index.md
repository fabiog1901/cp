<!-- GENERATED FILE: DO NOT EDIT -->

# Generated LLM Index

Use this file as a compact starting point before opening source files.

## Source Roots

- `cp`
- `tools`

## Packages

- `cp`: 70 modules, 119 classes, 101 functions, 56 routes
- `tools`: 1 modules, 5 classes, 32 functions, 0 routes

## API Route Count

- `56` FastAPI routes

## Command Handlers

- `CommandType.CREATE_CLUSTER` -> `cp.workers.commands.create_cluster`
- `CommandType.DEBUG_ZIP_CLUSTER` -> `cp.workers.commands.debug_zip_cluster`
- `CommandType.DELETE_CLUSTER` -> `cp.workers.commands.delete_cluster`
- `CommandType.FAIL_ZOMBIE_JOBS` -> `cp.workers.commands.fail_zombie_jobs`
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

## Generated Files

- `docs/generated/code-map.md`
- `docs/generated/package-index.md`
- `docs/generated/api/routes.md`
- `docs/generated/python-reference.md`
- `.build/project-index.json`
