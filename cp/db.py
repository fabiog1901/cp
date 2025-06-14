import datetime as dt
import os
from typing import Any

from psycopg.types.array import ListDumper
from psycopg.types.json import Jsonb, JsonbDumper
from psycopg_pool import ConnectionPool

from .models import (
    Cluster,
    ClusterOverview,
    EventLog,
    GroupRoleMap,
    IntID,
    Job,
    Region,
    StrID,
    Task,
    User,
)

DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise EnvironmentError("DB_URL env variable not found!")


# the pool starts connecting immediately.
pool = ConnectionPool(DB_URL, kwargs={"autocommit": True})


########
#  MQ  #
########
def insert_into_mq(
    msg_type: str,
    msg_data: dict,
    created_by: str,
) -> StrID:
    return execute_stmt(
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
        RETURNING job_id
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
        StrID,
        return_list=False,
    )


#############
#  REGIONS  #
#############
def get_region_details(cloud: str, region: str) -> list[Region]:
    return execute_stmt(
        """
        SELECT cloud, region, zone, vpc_id, security_groups, subnet, image, extras, tags
        FROM regions
        WHERE (cloud, region) = (%s, %s)
        """,
        (cloud, region),
        Region,
    )


##############
#  CLUSTERS  #
##############


def fetch_all_clusters(
    groups: list[str],
    is_admin: bool = False,
) -> list[ClusterOverview]:
    if is_admin:
        return execute_stmt(
            """
            SELECT cluster_id, grp, created_by, status 
            FROM clusters
            ORDER BY created_at DESC
            """,
            (),
            ClusterOverview,
        )

    return execute_stmt(
        """
        SELECT cluster_id, grp, created_by, status 
        FROM clusters
        WHERE grp = ANY (%s)
        ORDER BY created_at DESC
        """,
        (groups,),
        ClusterOverview,
    )


def get_cluster(
    cluster_id: str,
    groups: list[str],
    is_admin: bool = False,
) -> Cluster | None:
    if is_admin:
        return execute_stmt(
            """
            SELECT * 
            FROM clusters
            WHERE cluster_id = %s
            """,
            (cluster_id,),
            Cluster,
            return_list=False,
        )

    return execute_stmt(
        """
        SELECT * 
        FROM clusters
        WHERE grp = ANY (%s)
            AND cluster_id = %s
        """,
        (groups, cluster_id),
        Cluster,
        return_list=False,
    )


def get_running_clusters() -> list[Cluster]:
    return execute_stmt(
        """
        SELECT * 
        FROM clusters
        WHERE status = 'RUNNING'
        ORDER BY created_at ASC
        """,
        (),
        Cluster,
    )


def upsert_cluster(
    cluster_id: str,
    status: str,
    description: dict,
    created_by: str,
    updated_by: str,
    grp: str,
) -> None:
    execute_stmt(
        """
        UPSERT INTO clusters
            (cluster_id, status, description, 
            created_by, updated_by, grp)
        VALUES
            (%s, %s, %s, %s, %s, %s)
        """,
        (
            cluster_id,
            status,
            description,
            created_by,
            updated_by,
            grp,
        ),
    )


def update_cluster(
    cluster_id: str,
    status: str,
    description: dict,
    updated_by: str,
):
    execute_stmt(
        """
        UPDATE clusters SET
            status = %s,
            description = %s,
            updated_by = %s
        WHERE cluster_id = %s
        """,
        (status, description, updated_by, cluster_id),
    )


def update_cluster_status(
    cluster_id: str,
    status: str,
    updated_by: str,
):
    execute_stmt(
        """
        UPDATE clusters SET
            status = %s,
            updated_by = %s
        WHERE cluster_id = %s
        """,
        (status, updated_by, cluster_id),
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


def get_linked_clusters_from_job(job_id: int) -> list[StrID]:
    return execute_stmt(
        """
        SELECT cluster_id 
        FROM map_clusters_jobs
        WHERE job_id = %s
        ORDER BY cluster_id
        """,
        (job_id,),
        StrID,
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


##########
#  TASK  #
##########


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


def get_secret(
    id: str,
) -> StrID:
    return execute_stmt(
        """
        SELECT data
        FROM secrets
        WHERE id = %s
        """,
        (id,),
        StrID,
        return_list=False,
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


def insert_event_log(
    created_by: str,
    event_type: str,
    event_details: str = None,
):
    execute_stmt(
        """
        INSERT INTO event_log (
            created_by, event_type, event_details) 
        VALUES 
            (%s, %s, %s)
        """,
        (
            created_by,
            event_type,
            event_details,
        ),
    )


##############
#  SETTINGS  #
##############


def get_versions() -> list[StrID]:
    return execute_stmt(
        """
        SELECT version
        FROM versions 
        ORDER BY version DESC
        """,
        (),
        StrID,
    )


def get_regions() -> list[StrID]:
    return execute_stmt(
        """
        SELECT DISTINCT cloud || ':' || region AS cr
        FROM regions
        ORDER BY cr ASC
        """,
        (),
        StrID,
    )


def get_node_counts() -> list[IntID]:
    return execute_stmt(
        """
        SELECT nodes
        FROM nodes_per_region
        ORDER BY nodes ASC
        """,
        (),
        IntID,
    )


def get_cpus_per_node() -> list[IntID]:
    return execute_stmt(
        """
        SELECT cpus
        FROM cpus_per_node
        ORDER BY cpus ASC
        """,
        (),
        IntID,
    )


def get_disk_sizes() -> list[IntID]:
    return execute_stmt(
        """
        SELECT size_gb
        FROM disk_sizes
        ORDER BY size_gb
        """,
        (),
        IntID,
    )


###########
#  USERS  #
###########


def get_user(username: str) -> User | None:
    return execute_stmt(
        """
        SELECT * 
        FROM users 
        WHERE username = %s
        """,
        (username,),
        User,
        False,
    )


def increase_attempt(username: str) -> None:
    execute_stmt(
        """
        UPDATE users 
        SET attempts = attempts +1
        WHERE username = %s
        """,
        (username,),
    )


def reset_attempts(username: str) -> None:
    execute_stmt(
        """
        UPDATE users 
        SET attempts = 0
        WHERE username = %s
        """,
        (username,),
    )


def get_role_to_groups_mappings() -> list[GroupRoleMap]:
    return execute_stmt(
        """
        SELECT role, groups 
        FROM role_to_groups_mappings;
        """,
        (),
        GroupRoleMap,
    )


# ======================================================
class DictJsonbDumper(JsonbDumper):
    def dump(self, obj):
        return super().dump(Jsonb(obj))


def execute_stmt(
    stmt: str, bind_args: tuple, model=None, return_list: bool = True
) -> Any | list[Any] | None:
    with pool.connection() as conn:
        # convert a set to a psycopg list
        conn.adapters.register_dumper(set, ListDumper)
        conn.adapters.register_dumper(dict, DictJsonbDumper)

        with conn.cursor() as cur:
            try:
                stmt = " ".join([s.strip() for s in stmt.split("\n")])

                #print(f"SQL> {stmt}; {bind_args}")
                cur.execute(stmt, bind_args)

                if model is None:
                    return

                if return_list:
                    rs = cur.fetchall()
                    return [model(*x) for x in rs]
                else:
                    rs = cur.fetchone()

                    return model(*rs) if rs else None

            except Exception as e:
                # TODO correctly handle error such as PK violations
                print(f"SQL ERROR: {e}")
                return None
