# Infrastructure Helpers

This directory contains shared infrastructure used across API, service,
repository, and worker code.

For the broader map, see [`../../docs/CODEMAP.md`](../../docs/CODEMAP.md).

## What Belongs Here

- Dependency factories used by FastAPI.
- CP repository construction.
- CP-specific database error translation for managed-cluster connections.
- Utility functions for connecting to managed clusters.

## Entry Points

| File | Purpose |
| --- | --- |
| `dependencies.py` | Constructs services and repos for FastAPI dependency injection. |
| `errors.py` | Repository error classes. |
| `repository.py` | Builds the CP repository from the cpkit database pool and adapts managed-cluster connection failures. |
| `util.py` | Cluster connection/config helpers and low-level operational utilities. |

Database pool lifecycle, statement execution, fetch helpers, logging setup,
request ID context, and request/response logging middleware are provided by
cpkit.

## Caution

Infrastructure helpers are shared by many domains. Keep changes conservative and
avoid importing domain-specific service logic into this layer.
