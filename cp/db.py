from psycopg_pool import ConnectionPool
from psycopg.types.array import ListDumper
from psycopg.types.json import Jsonb, JsonbDumper
import os
import datetime as dt
from .models import MsgID, Msg, Cluster, EventLog, Task, ClusterOverview, Job
from uuid import UUID


DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise EnvironmentError("DB_URL env variable not found!")


# the pool starts connecting immediately.
pool = ConnectionPool(DB_URL, kwargs={"autocommit": True})


########
#  MQ  #
########


def insert_msg(
    msg_type: str,
    msg_data: dict,
    created_by: str,
) -> int:
    return execute_stmt(
        """
        INSERT INTO mq
            (msg_type, msg_data, created_by)
        VALUES
            (%s, %s, %s)
        RETURNING msg_id
        """,
        (msg_type, msg_data, created_by),
        MsgID,
    )[0]


def get_msg() -> Msg:
    return execute_stmt(
        """
        SELECT * 
        FROM mq
        LIMIT 1
        FOR UPDATE SKIP LOCKED
        """,
        (),
        Msg,
    )[0]


##############
#  CLUSTERS  #
##############


def get_all_clusters() -> list[ClusterOverview]:
    return execute_stmt(
        """
        SELECT cluster_id, created_by, status 
        FROM clusters
        ORDER BY cluster_id
        """,
        (),
        ClusterOverview,
    )


def get_cluster(cluster_id: str) -> Cluster | None:
    c = execute_stmt(
        """
        SELECT * 
        FROM clusters
        WHERE cluster_id = %s
        """,
        (cluster_id,),
        Cluster,
    )
    if c:
        return c[0]
    return None


def create_cluster(
    cluster_id: str,
    status: str,
    created_by: str,
    updated_by: str,
) -> None:
    return execute_stmt(
        """
        INSERT INTO clusters
            (cluster_id, status, created_by, updated_by)
        VALUES
            (%s, %s, %s, %s)
        """,
        (cluster_id, status, created_by, updated_by),
    )


def update_cluster(
    cluster_id: str,
    status: str,
    topology: dict,
    updated_by: str,
):
    execute_stmt(
        """
        UPDATE clusters SET
            status = %s,
            topology = %s,
            updated_by = %s
        WHERE cluster_id = %s
        """,
        (status, topology, updated_by, cluster_id),
    )


def delete_cluster(cluster_id):
    execute_stmt(
        """
        DELETE FROM clusters 
        WHERE cluster_id = %s
        """,
        (cluster_id,),
    )


############
#   JOBS   #
############


def get_all_jobs(cluster_id: str = None) -> list[Job]:
    if cluster_id:
        return execute_stmt(
            """
            SELECT j.job_id, j.job_type, 
                j.status, j.created_by, j.created_at
            FROM map_clusters_jobs m JOIN jobs j
                ON m.job_id = j.job_id 
            WHERE m.cluster_id = %s
            ORDER BY j.created_by DESC
            """,
            (cluster_id,),
            Job,
        )

    return execute_stmt(
        """
        SELECT job_id, job_type, 
            status, created_by, created_at
        FROM jobs
        ORDER BY created_by DESC
        """,
        (),
        Job,
    )


def get_job(job_id: int) -> list[Job]:
    return execute_stmt(
        """
        SELECT job_id, job_type, 
            status, created_by, created_at
        FROM jobs
        WHERE job_id = %s
        ORDER BY created_by desc
        """,
        (job_id,),
        Job,
    )[0]


def create_job(
    job_id: int,
    job_type: str,
    status: str,
    created_by: str,
) -> None:
    return execute_stmt(
        """
        INSERT INTO jobs
            (job_id, job_type, 
            status, created_by)
        VALUES 
            (%s, %s, %s, %s)
        """,
        (job_id, job_type, status, created_by),
    )


def create_job_linked(
    cluster_id: str,
    job_id: int,
    job_type: str,
    status: str,
    created_by: str,
) -> list[Job]:
    return execute_stmt(
        """
        WITH 
        create_job_linked AS (
            INSERT INTO map_clusters_jobs 
                (cluster_id, job_id)
            VALUES (%s, %s)
            RETURNING 1
        )
        INSERT INTO jobs
            (job_id, job_type, 
            status, created_by)
        VALUES 
            (%s, %s, %s, %s)
        """,
        (cluster_id, job_id, job_id, job_type, status, created_by),
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


##########
#  TASK  #
##########


def get_all_tasks(
    job_id: UUID,
) -> list[Task]:
    return execute_stmt(
        """
        SELECT job_id, task_id, progress, 
            created_at, task_type, task_data
        FROM tasks
        WHERE job_id = %s
        ORDER BY task_id ASC
        """,
        (job_id,),
        Task,
    )


def create_task(
    job_id: UUID,
    task_id: int,
    progress: int,
    created_at: dt.datetime,
    task_type: str,
    task_data: dict,
):
    return execute_stmt(
        """
        INSERT INTO tasks 
            (job_id, task_id, progress, created_at, task_type, task_data)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (job_id, task_id, progress, created_at, task_type, task_data),
    )


###############
#  EVENT_LOG  #
###############


def get_all_event_logs() -> list[EventLog] | None:
    return execute_stmt(
        """
        SELECT * 
        FROM event_log
        """,
        (),
        EventLog,
    )


def create_event_log(
    created_by: str,
    event_type: str,
    details: str,
):
    execute_stmt(
        """
        INSERT INTO event_log (
            created_by, event_type, details) 
        VALUES 
            (%s, %s, %s)
        """,
        (
            created_by,
            event_type,
            details,
        ),
    )


# ======================================================
class DictJsonbDumper(JsonbDumper):
    def dump(self, obj):
        return super().dump(Jsonb(obj))


def execute_stmt(
    stmt: str,
    bind_args: tuple,
    model=None,
) -> list:
    with pool.connection() as conn:
        # convert a set to a psycopg list
        conn.adapters.register_dumper(set, ListDumper)
        conn.adapters.register_dumper(dict, DictJsonbDumper)

        with conn.cursor() as cur:
            try:
                stmt = " ".join([s.strip() for s in stmt.split("\n")])

                print(f"SQL> {stmt}; {bind_args}")
                cur.execute(stmt, bind_args)

                if model:
                    return [model(*x) for x in cur.fetchall()]

            except Exception as e:
                # TODO correctly handle error such as PK violations
                print(f"SQL ERROR: {e}")
                return None
