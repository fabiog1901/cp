"""Message queue repository backed by CockroachDB/Postgres."""

from ...infra.db import fetch_one
from ...models import JobID


def insert_into_mq(
    msg_type: str,
    msg_data: dict,
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
            msg_type,
            msg_data,
            created_by,
            msg_type,
            "QUEUED",
            msg_data,
            created_by,
        ),
        JobID,
    )
