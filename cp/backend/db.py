import datetime as dt
import os
from typing import Any, List

from psycopg.rows import class_row
from psycopg.types.array import ListDumper
from psycopg.types.json import Jsonb, JsonbDumper
from psycopg_pool import ConnectionPool
from pydantic import BaseModel, TypeAdapter

from ..models import (
    Cluster,
    ClusterOverview,
    EventLog,
    IntID,
    InventoryLB,
    InventoryRegion,
    Job,
    Region,
    RoleGroupMap,
    Setting,
    StrID,
    Task,
    Version,
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
) -> IntID:
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
        RETURNING job_id AS id
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
        IntID,
        return_list=False,
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
            SELECT cluster_id, grp, 
                created_by, status, 
                version, node_count, 
                node_cpus, disk_size
            FROM clusters
            ORDER BY created_at DESC
            """,
            (),
            ClusterOverview,
        )

    return execute_stmt(
        """
        SELECT cluster_id, grp, 
            created_by, status, 
            version, node_count, 
            node_cpus, disk_size
        FROM clusters
        WHERE grp = ANY (%s)
        ORDER BY created_at DESC
        """,
        (groups,),
        ClusterOverview,
    )


# TODO checkif the Cluster object has objects InventoryRegion and inventoryLB
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
    created_by: str,
    grp: str,
    version: str,
    node_cpus: int,
    node_count: int,
    disk_size: int,
) -> None:
    execute_stmt(
        """
        UPSERT INTO clusters
            (cluster_id, status, 
            created_by, updated_by, grp, 
            version, node_cpus, node_count, disk_size)
        VALUES
            (%s, %s, %s, %s, %s,
             %s, %s, %s, %s)
        """,
        (
            cluster_id,
            status,
            created_by,
            created_by,
            grp,
            version,
            node_cpus,
            node_count,
            disk_size,
        ),
    )


def update_cluster(
    cluster_id: str,
    updated_by: str,
    cluster_inventory: list[InventoryRegion] | None = None,
    lbs_inventory: list[InventoryLB] | None = None,
    version: str | None = None,
    node_count: int | None = None,
    node_cpus: int | None = None,
    disk_size: int | None = None,
    status: str | None = None,
    grp: str | None = None,
):
    execute_stmt(
        """
        UPDATE clusters SET
            cluster_inventory = coalesce(%s, cluster_inventory),
            lbs_inventory = coalesce(%s, lbs_inventory),
            version = coalesce(%s, version),
            node_count = coalesce(%s, node_count),
            node_cpus = coalesce(%s, node_cpus),
            disk_size = coalesce(%s, disk_size),
            status = coalesce(%s, status),
            grp = coalesce(%s, grp),
            updated_by = coalesce(%s, updated_by)
        WHERE cluster_id = %s
        """,
        (
            TypeAdapter(list[InventoryRegion]).dump_python(cluster_inventory),
            TypeAdapter(list[InventoryLB]).dump_python(lbs_inventory),
            version,
            node_count,
            node_cpus,
            disk_size,
            status,
            grp,
            updated_by,
            cluster_id,
        ),
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
        SELECT cluster_id AS id
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


###############
#  EVENT_LOG  #
###############


def fetch_all_events(
    limit: int,
    offset: int,
    groups: list[str] = None,
    is_admin: bool = False,
) -> list[EventLog]:
    if is_admin:
        return execute_stmt(
            """
            SELECT *
            FROM event_log
            ORDER BY created_at DESC
            LIMIT %s
            OFFSET %s
            """,
            (limit, offset),
            EventLog,
        )


def get_event_count() -> int:
    int_id: IntID = execute_stmt(
        """
        SELECT count(*) AS id
        FROM event_log AS OF SYSTEM TIME follower_read_timestamp()
        """,
        (),
        IntID,
        False,
    )
    return int_id.id


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


#############
#   ADMIN   #
#############

# REGIONS


def get_regions() -> list[StrID]:
    return execute_stmt(
        """
        SELECT DISTINCT cloud || ':' || region AS id
        FROM regions
        ORDER BY id ASC
        """,
        (),
        StrID,
    )


def get_all_regions() -> list[Region]:
    return execute_stmt(
        """
        SELECT cloud, region, zone, vpc_id, security_groups, subnet, image, extras
        FROM regions
        """,
        (),
        Region,
    )


def get_region(cloud: str, region: str) -> list[Region]:
    return execute_stmt(
        """
        SELECT cloud, region, zone, vpc_id, security_groups, subnet, image, extras
        FROM regions
        WHERE (cloud, region) = (%s, %s)
        """,
        (cloud, region),
        Region,
    )


def add_region(r: Region) -> None:
    stmt, vals = convert_model_to_sql("regions", r)
    execute_stmt(
        stmt,
        vals,
    )


def remove_version(
    cloud: str,
    region: str,
    zone: str,
) -> None:
    return execute_stmt(
        """
        DELETE FROM regions 
        WHERE (cloud, region, zone) = (%s, %s, %s)
        """,
        (cloud, region, zone),
    )


# VERSIONS


def get_versions() -> list[Version]:
    return execute_stmt(
        """
        SELECT version
        FROM versions 
        ORDER BY version DESC
        """,
        (),
        Version,
    )


def add_version(v: BaseModel) -> None:
    stmt, vals = convert_model_to_sql("versions", v)
    execute_stmt(
        stmt,
        vals,
    )


def remove_version(version) -> None:
    execute_stmt(
        """
        DELETE
        FROM versions 
        WHERE version = %s
        """,
        (version,),
    )


def get_upgrade_versions(major_version: str) -> list[Version]:
    return execute_stmt(
        """
        SELECT version
        FROM versions 
        WHERE version > %s
        ORDER BY version ASC
        """,
        (major_version,),
        Version,
    )

# NODE COUNT


def get_node_counts() -> list[IntID]:
    return execute_stmt(
        """
        SELECT nodes AS id
        FROM nodes_per_region
        ORDER BY nodes ASC
        """,
        (),
        IntID,
    )


def get_cpus_per_node() -> list[IntID]:
    return execute_stmt(
        """
        SELECT cpus AS id
        FROM cpus_per_node
        ORDER BY cpus ASC
        """,
        (),
        IntID,
    )


def get_disk_sizes() -> list[IntID]:
    return execute_stmt(
        """
        SELECT size_gb AS id
        FROM disk_sizes
        ORDER BY size_gb
        """,
        (),
        IntID,
    )


def fetch_all_settings() -> list[Setting]:
    return execute_stmt(
        """
        SELECT *
        FROM settings
        """,
        (),
        Setting,
    )


def get_setting(setting: str) -> str:
    str_id: StrID = execute_stmt(
        """
        SELECT value AS id
        FROM settings
        WHERE id = %s
        """,
        (setting,),
        StrID,
        False,
    )
    return str_id.id


def update_setting(setting: str, value: str, updated_by) -> str:
    execute_stmt(
        """
        UPDATE settings
        SET value = %s,
        updated_by = %s
        WHERE id = %s
        """,
        (value, updated_by, setting),
    )


def get_secret(
    id: str,
) -> str:
    str_id: StrID = execute_stmt(
        """
        SELECT data AS id
        FROM secrets
        WHERE id = %s
        """,
        (id,),
        StrID,
        return_list=False,
    )

    return str_id.id


#  ROLES


def get_role_to_groups_mappings() -> list[RoleGroupMap]:
    return execute_stmt(
        """
        SELECT role, groups 
        FROM role_to_groups_mappings
        """,
        (),
        RoleGroupMap,
    )


# ======================================================
class DictJsonbDumper(JsonbDumper):
    def dump(self, obj):
        return super().dump(Jsonb(obj))


def convert_model_to_sql(table: str, model: BaseModel):
    data = model.model_dump()
    cols = data.keys()
    vals = [data[c] for c in cols]
    placeholders = ", ".join(["%s"] * len(cols))
    stmt = f'INSERT INTO {table} ({", ".join(cols)}) VALUES ({placeholders})'
    return stmt, vals


def execute_stmt(
    stmt: str,
    bind_args: tuple,
    model=None,
    return_list: bool = True,
) -> Any | list[Any] | None:
    with pool.connection() as conn:
        # convert a set to a psycopg list
        conn.adapters.register_dumper(set, ListDumper)
        conn.adapters.register_dumper(list, ListDumper)
        conn.adapters.register_dumper(dict, DictJsonbDumper)
        # conn.adapters.register_dumper(list, DictJsonbDumper)

        with conn.cursor(row_factory=class_row(model)) as cur:
            try:
                stmt = " ".join([s.strip() for s in stmt.split("\n")])

                print(f"SQL> {stmt}; {bind_args}")
                cur.execute(stmt, bind_args)

                if model is None:
                    return

                if return_list:
                    return cur.fetchall()
                else:
                    return cur.fetchone()

            except Exception as e:
                # TODO correctly handle error such as PK violations
                print(f"SQL ERROR: {e}")
                raise e
