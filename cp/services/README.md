# Service Layer

This directory contains business workflows. Services coordinate repository
access, managed-cluster SQL, job enqueueing, audit logging, and domain
validation.

For the broader map, see [`../../docs/CODEMAP.md`](../../docs/CODEMAP.md).

## What Belongs Here

- Domain validation and workflow decisions.
- Coordination across multiple repositories.
- Direct SQL against managed CockroachDB clusters through cluster connection
  helpers.
- Job enqueueing and worker-facing command construction.
- Audit event writes for user-visible changes.
- Translation from repository/cluster failures to service errors.

## What Does Not Belong Here

- FastAPI request/response plumbing.
- Raw CP metadata SQL that belongs in repos.
- UI-specific data shaping.

## Entry Points

| File | Purpose |
| --- | --- |
| `cluster.py` | Cluster lifecycle commands and state transitions. |
| `cluster_users.py` | Database objects, generated database roles, database users, grants, and IdP group mappings. |
| `cluster_backups.py` | Backup listing, backup details, restore setup, and backup-related cluster SQL. |
| `cluster_jobs.py` | Cluster job views and job actions. |
| `dashboard.py` | Dashboard snapshot and metrics aggregation. |
| `backup_catalog.py` | Backup catalog sync/read workflows. |
| `alerts.py` | Alertmanager service integration. |
| `cluster_db.py` | Managed-cluster connection setup. |
| `storage_broker.py` | S3-compatible storage integration helpers. |
| `admin/` | Admin option business logic. |

Framework services such as jobs, audit events, settings, playbooks, API keys,
and auth live under `cpkit/cpkit/`.

## Common Pattern

Service methods should make side effects explicit. If a method changes CP
metadata, touches a managed cluster, enqueues a job, or writes an audit event,
give it a docstring that says so.

Use services as the first stop when you are trying to understand what a user
action actually does.
