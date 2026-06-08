# Cluster Lifecycle

!!! note "Draft"
    This page is a human-owned domain draft. Generated route, symbol, and module
    indexes live under `docs/generated/`.

## Purpose

Cluster lifecycle covers provisioning, deleting, scaling, upgrading, debugging,
health checking, and tracking jobs for managed CockroachDB clusters.

Most lifecycle operations are asynchronous. The API validates the request,
enqueues a command, returns a CP job id, and a worker later executes the command.

## Concepts

- Cluster: a managed CockroachDB deployment recorded in CP metadata.
- Job: a durable CP record for an asynchronous operation.
- Task: progress entries attached to a job.
- Command: a typed payload persisted in the CP message queue.
- Remote worker: a worker that prepares CP inputs for cpkit playbook execution.
- Local worker: a worker that runs inside CP without remote SSH.

## Lifecycle

1. A user calls a cluster operation API.
2. The API delegates to `ClusterService`.
3. The service validates input, writes an audit event, and enqueues a command.
4. The queue worker claims the command from the CockroachDB-backed MQ.
5. A local or remote worker executes the operation.
6. The worker updates job/task state and cluster metadata.
7. The webapp polls or refreshes job/cluster views.

## Backend Entry Points

| Layer | Files |
| --- | --- |
| API | `cp/api/clusters.py`, `cpkit/cpkit/jobs/` |
| Services | `cp/services/cluster.py`, `cp/services/cluster_jobs.py`, `cpkit/cpkit/jobs/` |
| Repos | `cp/repos/cluster.py`, `cp/repos/cluster_jobs.py`, `cp/repos/cluster_artifacts.py`, `cpkit/cpkit/jobs/` |
| Workers | `cp/workers/queue.py`, `cp/workers/remote/*.py`, `cp/workers/local/*.py` |
| Models | `Cluster*`, `Command*`, `Job*`, `Task*` in `cp/models.py` |

## API Resources

See [Generated API Route Index](../generated/api/routes.md) for the current
route inventory.

Important lifecycle resources include:

- `GET /clusters`
- `POST /clusters`
- `DELETE /clusters/{cluster_id}`
- `POST /clusters/scale`
- `POST /clusters/upgrade`
- `GET /clusters/{cluster_id}/jobs`
- `GET /jobs`
- `GET /jobs/{job_id}`
- `POST /jobs/{job_id}/reschedule`

## Webapp

Cluster lifecycle UI is spread across the cluster list, cluster detail,
dashboard, jobs, and operation controls in:

- `webapp/index.html`
- `webapp/script.js`
- `webapp/style.css`

## Important Invariants

- API routes should not run long cluster lifecycle operations directly.
- Long-running operations should be queued and represented by jobs.
- Workers own operational execution and job/task progress updates.
- Repos persist CP metadata only; they should not execute playbooks or connect
  to managed clusters.
- Audit-worthy lifecycle requests should write audit events from the service
  layer.

## Do Not Confuse With

- Cluster lifecycle auth is CP access control, not CockroachDB SQL auth.
- Job state is CP workflow state, not necessarily CockroachDB internal job state.
- Local workers run inside CP; remote workers run playbook-backed workflows.

## Common Changes

| Change | Start Here |
| --- | --- |
| Add a new cluster command | `cp/models.py`, `cp/services/cluster.py`, `cp/workers/queue.py` |
| Add a remote operation | `cp/workers/remote/`, then service enqueue path |
| Add a job view field | `cpkit/cpkit/jobs/`, `webapp/` |
| Change cluster visibility | `cp/repos/cluster.py`, `cp/services/cluster.py` |
