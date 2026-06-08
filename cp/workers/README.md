# Workers

This directory contains background and queued execution paths. Workers process
commands that should not run as blocking HTTP requests.

For the broader map, see [`../../docs/CODEMAP.md`](../../docs/CODEMAP.md).

## What Belongs Here

- CP command dispatch for queue messages.
- Local worker implementations that operate from inside CP.
- Remote worker implementations that build vars and interpret playbook results.
- Job/task progress updates tied to command execution.

## Entry Points

| Path | Purpose |
| --- | --- |
| `commands.py` | CP command handlers registered with `cpkit.jobs`. |
| `local/` | CP-local workers, such as backup catalog sync and restore polling. |
| `remote/` | Playbook-backed remote cluster operations: create, delete, scale, upgrade, healthcheck. |

## Common Pattern

The API/service layer should enqueue work and return a job id. `cpkit.jobs`
owns queue polling, message claiming, and failure bookkeeping; CP workers
resolve the queued command, execute it, and update job/task state.
`cpkit.playbooks` owns stored playbook
access and execution mechanics; CP remote workers build CP-specific extra vars
and reconcile cluster/job state. Keep direct user request concerns out of
workers.
