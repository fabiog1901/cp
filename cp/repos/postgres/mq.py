"""Message queue repository backed by CockroachDB/Postgres."""

from ...infra.db import fetch_one
from ...models import CommandModel, CommandType, JobID, JobState
from ..base import BaseRepo


class MqRepo(BaseRepo):
    def enqueue_command(
        self,
        command_type: CommandType,
        payload: CommandModel,
        created_by: str,
    ) -> JobID:
        return fetch_one(
            """
            WITH
            create_new_job AS (
                INSERT INTO mq
                    (msg_type, msg_data, created_by)
                VALUES
                    (%s, %s, %s)
                RETURNING msg_id
            )
            INSERT INTO jobs (job_id, job_type, status, description, created_by)
            VALUES ((select msg_id from create_new_job), %s, %s, %s, %s)
            RETURNING job_id AS job_id
            """,
            (
                command_type.value,
                payload.model_dump(),
                created_by,
                command_type.value,
                JobState.SCHEDULED.value,
                payload.model_dump(),
                created_by,
            ),
            JobID,
            operation="mq.enqueue_command",
        )
