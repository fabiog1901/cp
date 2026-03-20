"""Job and task queries for Postgres-backed repositories."""

import datetime as dt

from ...infra.db import execute_stmt
from ...models import ClusterIDRef, IntID, Job, Task


def get_linked_clusters_from_job(job_id: int) -> list[ClusterIDRef]:
    return execute_stmt(
        """
        SELECT cluster_id AS cluster_id
        FROM map_clusters_jobs
        WHERE job_id = %s
        ORDER BY cluster_id
        """,
        (job_id,),
        ClusterIDRef,
    )


def get_all_linked_jobs(cluster_id: str) -> list[Job]:
    return execute_stmt(
        """
        WITH
        cluster_jobs AS (
            SELECT job_id
            FROM map_clusters_jobs
            WHERE cluster_id = %s
        )
        SELECT *
        FROM jobs
        WHERE job_id IN (SELECT job_id FROM cluster_jobs)
        ORDER BY created_at DESC
        """,
        (cluster_id,),
        Job,
    )


def fetch_all_jobs(
    groups: list[str] = None,
    is_admin: bool = False,
) -> list[Job]:
    if is_admin:
        return execute_stmt(
            """
            SELECT *
            FROM jobs
            ORDER BY created_at DESC
            """,
            (),
            Job,
        )

    return execute_stmt(
        """
        WITH
        c AS (
            SELECT cluster_id
            FROM clusters
            WHERE grp = ANY (%s)
        ),
        cj AS (
            SELECT job_id
            FROM map_clusters_jobs
            WHERE cluster_id IN (SELECT * FROM c)
        )
        SELECT *
        FROM jobs
        WHERE job_id IN (SELECT * FROM cj)
        ORDER BY created_at DESC;
        """,
        (groups,),
        Job,
    )


def fetch_job(
    job_id: int,
    groups: list[str],
    is_admin: bool = False,
) -> Job | None:
    if is_admin:
        return execute_stmt(
            """
            SELECT *
            FROM jobs
            WHERE job_id = %s
            """,
            (job_id,),
            Job,
            return_list=False,
        )
    return execute_stmt(
        """
        WITH
        c AS (
            SELECT cluster_id
            FROM clusters
            WHERE grp = ANY (%s)
        ),
        cj AS (
            SELECT job_id
            FROM map_clusters_jobs
            WHERE cluster_id IN (SELECT * FROM c)
        )
        SELECT *
        FROM jobs
        WHERE job_id IN (SELECT * FROM cj)
            AND job_id = %s
        """,
        (groups, job_id),
        Job,
        return_list=False,
    )


def create_job(
    job_id: int,
    job_type: str,
    status: str,
    created_by: str,
) -> None:
    execute_stmt(
        """
        INSERT INTO jobs
            (job_id, job_type,
            status, created_by)
        VALUES
            (%s, %s, %s, %s)
        """,
        (job_id, job_type, status, created_by),
    )


def insert_mapped_job(
    cluster_id: str,
    job_id: int,
    status: str,
) -> None:
    execute_stmt(
        """
        WITH
        create_job_linked AS (
            INSERT INTO map_clusters_jobs
                (cluster_id, job_id)
            VALUES (%s, %s)
            RETURNING 1
        )
        UPDATE jobs
        SET status = %s
        WHERE job_id = %s
        """,
        (cluster_id, job_id, status, job_id),
    )


def update_job(
    job_id: int,
    status: str,
) -> None:
    execute_stmt(
        """
        UPDATE jobs
        SET status = %s
        WHERE job_id = %s
        """,
        (status, job_id),
    )


def fail_zombie_jobs() -> list[IntID]:
    return execute_stmt(
        """
        WITH
        fail_zombie_jobs AS (
            INSERT INTO mq (msg_type, start_after)
            VALUES ('FAIL_ZOMBIE_JOBS', now() + INTERVAL '60s' + (random()*10)::INTERVAL)
            RETURNING 1
        )
        UPDATE jobs
        SET status = 'FAILED'
        WHERE status in ('RUNNING', 'SCHEDULED')
            AND now() > updated_at + INTERVAL '120s'
        RETURNING job_id
        """,
        (),
        IntID,
    )


def get_all_tasks(
    job_id: int,
) -> list[Task]:
    return execute_stmt(
        """
        SELECT job_id, task_id,
            created_at, task_name, task_desc
        FROM tasks
        WHERE job_id = %s
        ORDER BY task_id DESC
        """,
        (job_id,),
        Task,
    )


def insert_task(
    job_id: int,
    task_id: int,
    created_at: dt.datetime,
    task_name: str,
    task_desc: dict,
) -> None:
    execute_stmt(
        """
        INSERT INTO tasks
            (job_id, task_id, created_at, task_name, task_desc)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (job_id, task_id, created_at, task_name, task_desc),
    )
