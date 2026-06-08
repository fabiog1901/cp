# API Layer

This directory contains FastAPI routers. API modules define HTTP resources,
apply authentication and authorization dependencies, call service methods, and
translate service errors into HTTP responses.

For the broader map, see [`../../docs/CODEMAP.md`](../../docs/CODEMAP.md).

## What Belongs Here

- Route definitions and `response_model` declarations.
- Request dependency wiring such as `require_user`, `require_readonly`,
  `get_access_scope`, and `get_audit_actor`.
- Thin request-to-service delegation.
- HTTP error conversion through shared helpers.

## What Does Not Belong Here

- Business workflows.
- Direct CP metadata SQL.
- Direct SQL against managed clusters.
- Worker orchestration details beyond calling service methods.

## Entry Points

| File | Purpose |
| --- | --- |
| `clusters.py` | Main cluster routes: lifecycle, dashboard, backups, database users, database objects, role mappings. |
| `alerts.py` | Alertmanager-backed alert visibility. |
| `cluster_recovery.py` | Cluster recovery-specific routes. |
| `admin/` | Admin option CRUD routes. |

Framework routes such as jobs, audit events, settings, playbooks, API keys, and
auth are mounted through `cp/cpkit_integration.py`.

## Common Pattern

Most route handlers should follow this shape:

1. Resolve access scope from claims.
2. Call one service method.
3. Convert `ServiceError` through `cpkit.errors.raise_http_from_service_error`.
4. Return a typed model or raise a `404` for missing resources.

If a route needs several business decisions, move those decisions into the
service layer first.
