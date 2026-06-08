# Events, Alerts, and Dashboard

!!! note "Draft"
    This page is a human-owned domain draft. Generated route, symbol, and module
    indexes live under `docs/generated/`.

## Purpose

This domain covers CP audit events, Alertmanager-backed alert visibility, and
Prometheus-backed cluster dashboard metrics.

These surfaces are mostly read-heavy, but they are important for operational
visibility and troubleshooting.

## Concepts

- Event: CP audit or operational record.
- Audit event: user-visible state change recorded by services.
- Alert: live alert data fetched from Alertmanager.
- Dashboard snapshot: cluster metadata plus metrics for a selected time window.
- Metrics backend: Prometheus-compatible service queried by CP.

## Lifecycle

1. Services write audit events when user-visible changes occur.
2. Event APIs expose event lists and counts.
3. Alert APIs fetch current alert data from Alertmanager.
4. Dashboard APIs combine cluster metadata with metrics.
5. The webapp renders events, alerts, and dashboard charts.

## Backend Entry Points

| Concern | Files |
| --- | --- |
| Events | `cpkit/cpkit/audit/` |
| Alerts | `cp/api/alerts.py`, `cp/services/alerts.py`, `cp/repos/alerts.py` |
| Dashboard | `cp/api/clusters.py`, `cp/services/dashboard.py`, `cp/repos/cluster.py` |
| Models | `Event*`, `Alert*`, `Dashboard*` in `cp/models.py` |

## API Resources

See [Generated API Route Index](../generated/api/routes.md) for the current
route inventory.

Important resources include:

- `GET /events`
- `GET /events/count`
- `GET /alerts`
- `POST /alerts/webhook`
- `GET /clusters/{cluster_id}/dashboard`

## Webapp

Relevant UI surfaces:

- Dashboard
- Cluster Dashboard
- Events
- Alerts

Relevant files:

- `webapp/index.html`
- `webapp/script.js`
- `webapp/style.css`

## Important Invariants

- Services should write audit events for user-visible changes.
- Event writes should stay out of repository methods.
- Dashboard APIs should enforce cluster visibility before returning metrics.
- Alert and metrics integrations should be isolated in services so API routes
  remain thin.

## Common Changes

| Change | Start Here |
| --- | --- |
| Add an audit event | `cp/models.py`, service workflow, `cpkit/cpkit/audit/` |
| Change event filtering | `cpkit/cpkit/audit/` |
| Change alert data | `cp/services/alerts.py` |
| Change dashboard metrics | `cp/services/dashboard.py` |
