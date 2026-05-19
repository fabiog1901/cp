# Workers

This directory contains background and queued execution paths. Workers process
commands that should not run as blocking HTTP requests.

For the broader map, see [`../../docs/CODEMAP.md`](../../docs/CODEMAP.md).

## What Belongs Here

- Queue message claim/execute loops.
- Local worker implementations that operate from inside CP.
- Remote worker implementations that run Ansible/SSH workflows.
- Job/task progress updates tied to command execution.

## Entry Points

| Path | Purpose |
| --- | --- |
| `queue.py` | Queue worker loop and command dispatch. |
| `local/` | CP-local workers, such as backup catalog sync and restore polling. |
| `remote/` | Ansible-backed remote cluster operations: create, delete, scale, upgrade, healthcheck. |

## Common Pattern

The API/service layer should enqueue work and return a job id. Workers should
claim the queued command, execute it, and update job/task state. Keep direct user
request concerns out of workers.
