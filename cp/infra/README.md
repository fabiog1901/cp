# Infrastructure Helpers

This directory contains shared infrastructure used across API, service,
repository, and worker code.

For the broader map, see [`../../docs/CODEMAP.md`](../../docs/CODEMAP.md).

## What Belongs Here

- Dependency factories used by FastAPI.
- CP metadata database helpers.
- Shared error translation.
- Logging setup.
- Utility functions for connecting to managed clusters.

## Entry Points

| File | Purpose |
| --- | --- |
| `dependencies.py` | Constructs services and repos for FastAPI dependency injection. |
| `db.py` | CP metadata database helpers, statement execution, fetch helpers, and database error translation. |
| `errors.py` | Repository error classes. |
| `logging.py` | Logging configuration. |
| `util.py` | Cluster connection/config helpers and low-level operational utilities. |

## Caution

Infrastructure helpers are shared by many domains. Keep changes conservative and
avoid importing domain-specific service logic into this layer.
