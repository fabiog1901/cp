# Repository Layer

This directory contains CP metadata persistence. Repositories query and mutate
the CP database and return typed models.

For the broader map, see [`../../docs/CODEMAP.md`](../../docs/CODEMAP.md).

## What Belongs Here

- SQL against CP metadata tables.
- Row-to-model conversion.
- Small persistence helpers for inserts, updates, deletes, and list/get queries.
- Query-specific ordering and filtering.

## What Does Not Belong Here

- Business validation.
- Audit logging.
- FastAPI request handling.
- Direct SQL against managed CockroachDB clusters.
- Worker execution logic.

## Entry Points

| File | Purpose |
| --- | --- |
| `__init__.py` | Composes repo mixins into the concrete `Repo` class. |
| `cluster.py` | Cluster metadata and visibility queries. |
| `cluster_jobs.py` | Cluster/job mapping metadata. |
| `jobs.py` | Job and task persistence. |
| `mq.py` | CP command enqueueing built on the `cpkit.jobs` queue repository mixin. |
| `backup_catalog.py` | Backup catalog metadata. |
| `event.py` | Audit/event table reads and writes. |
| `external_connections.py` | External connection metadata. |
| `auth.py` | Auth/session/API-key persistence. |
| `alerts.py` | Alert-related metadata, if any. |
| `admin/` | Admin option persistence, including database role templates and cluster database access metadata. |

## Common Pattern

Repository methods should be boring on purpose: accept explicit parameters,
execute SQL, and return typed models or `None`. If a repo method starts deciding
what should happen next, that logic probably belongs in a service.
