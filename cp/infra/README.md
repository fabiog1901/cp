# Infrastructure Helpers

This directory contains FastAPI dependency wiring for CP services.

For the broader map, see [`../../docs/CODEMAP.md`](../../docs/CODEMAP.md).

## What Belongs Here

- Dependency factories used by FastAPI.
- Small compatibility exports for repository exception types.

## Entry Points

| File | Purpose |
| --- | --- |
| `dependencies.py` | Constructs services and repos for FastAPI dependency injection. |
| `errors.py` | Repository error classes. |

Database pool lifecycle, statement execution, fetch helpers, logging setup,
request ID context, and request/response logging middleware are provided by
cpkit. CP app integration lives at the root, such as `cp/repository.py` for repo
construction and `cp/cluster_database.py` for managed-cluster SQL connections.

## Caution

Infrastructure helpers are shared by many domains. Keep changes conservative and
avoid importing domain-specific service logic into this layer.
