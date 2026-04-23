"""Jobs repository."""

from ..infra.db import execute_stmt, fetch_all, fetch_one
from ..models import (
    ClusterIDRef,
    CommandType,
    IntID,
    Job,
    JobState,
    JobStatsResponse,
    Task,
)


class JobsRepo:
    def get_job_stats(
        self, groups: list[str], is_admin: bool = False
    ) -> JobStatsResponse:
        if is_admin:
            return fetch_one(
                """
                SELECT
                    COUNT(*) AS total,
                    COALESCE(SUM(CASE WHEN status = %s THEN 1 ELSE 0 END), 0) AS running,
                    COALESCE(SUM(CASE WHEN status = %s THEN 1 ELSE 0 END), 0) AS queued,
                    COALESCE(SUM(CASE WHEN status = %s THEN 1 ELSE 0 END), 0) AS failed
                FROM jobs
                """,
                (
                    JobState.RUNNING.value,
                    JobState.QUEUED.value,
                    JobState.FAILED.value,
                ),
                JobStatsResponse,
            ) or JobStatsResponse(total=0, running=0, queued=0, failed=0)

        return fetch_one(
            """
            WITH
            c AS (
                SELECT cluster_id
                FROM clusters
                WHERE grp = ANY (%s)
            ),
            cj AS (
                SELECT DISTINCT job_id
                FROM map_clusters_jobs
                WHERE cluster_id IN (SELECT * FROM c)
            )
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(CASE WHEN status = %s THEN 1 ELSE 0 END), 0) AS running,
                COALESCE(SUM(CASE WHEN status = %s THEN 1 ELSE 0 END), 0) AS queued,
                COALESCE(SUM(CASE WHEN status = %s THEN 1 ELSE 0 END), 0) AS failed
            FROM jobs
            WHERE job_id IN (SELECT * FROM cj)
            """,
            (
                groups,
                JobState.RUNNING.value,
                JobState.QUEUED.value,
                JobState.FAILED.value,
            ),
            JobStatsResponse,
        ) or JobStatsResponse(total=0, running=0, queued=0, failed=0)

    def list_jobs(self, groups: list[str], is_admin: bool = False) -> list[Job]:
        if is_admin:
            return fetch_all(
                """
                SELECT *
                FROM jobs
                ORDER BY created_at DESC
                """,
                (),
                Job,
            )

        return fetch_all(
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

    def get_job(
        self, job_id: int, groups: list[str], is_admin: bool = False
    ) -> Job | None:
        if is_admin:
            return fetch_one(
                """
                SELECT *
                FROM jobs
                WHERE job_id = %s
                """,
                (job_id,),
                Job,
            )
        return fetch_one(
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
        )

    def list_tasks(self, job_id: int) -> list[Task]:
        return fetch_all(
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

    def list_linked_clusters(self, job_id: int) -> list[ClusterIDRef]:
        return fetch_all(
            """
            SELECT cluster_id AS cluster_id
            FROM map_clusters_jobs
            WHERE job_id = %s
            ORDER BY cluster_id
            """,
            (job_id,),
            ClusterIDRef,
        )

    def link_job_to_cluster(self, cluster_id: str, job_id: int, status: str) -> None:
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

    def update_job(self, job_id: int, status: str) -> None:
        execute_stmt(
            """
            UPDATE jobs
            SET status = %s
            WHERE job_id = %s
            """,
            (status, job_id),
        )

    def fail_zombie_jobs(self):
        return fetch_all(
            """
            WITH
            fail_zombie_jobs AS (
                INSERT INTO mq (msg_type, start_after)
                VALUES (%s, now() + INTERVAL '300s' + (random()*10)::INTERVAL)
                RETURNING 1
            )
            UPDATE jobs
            SET status = %s
            WHERE status in (%s, %s)
                AND now() > updated_at + INTERVAL '300s'
            RETURNING job_id
            """,
            (
                CommandType.FAIL_ZOMBIE_JOBS.value,
                JobState.FAILED.value,
                JobState.RUNNING.value,
                JobState.QUEUED.value,
            ),
            IntID,
        )

    def create_task(
        self,
        job_id: int,
        task_id: int,
        created_at,
        task_name: str,
        task_desc,
    ) -> None:
        execute_stmt(
            """
            INSERT INTO tasks
                (job_id, task_id, created_at, task_name, task_desc)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (job_id, task_id, created_at, task_name, task_desc),
        )
