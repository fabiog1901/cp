"""Remote cluster debug zip worker.

This worker runs the configured Ansible playbook that collects a CockroachDB
debug zip for one managed cluster.
"""

import datetime as dt
import logging
from threading import Thread
from uuid import uuid4

from ...infra import get_repo
from ...models import (
    ClusterState,
    DebugZipClusterCommand,
    JobArtifactUpsert,
    JobState,
    PlaybookName,
)
from .ansible import MyRunner

logger = logging.getLogger(__name__)


def debug_zip_cluster(
    job_id: int,
    command: DebugZipClusterCommand,
    requested_by: str,
) -> None:
    repo = get_repo()
    cluster_id = command.cluster_id

    cluster = repo.get_cluster(cluster_id, [], True)
    if not cluster:
        repo.update_job(job_id, JobState.FAILED)
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "The cluster was not found.",
        )
        return

    if cluster.status in {ClusterState.DELETED, ClusterState.DELETING}:
        repo.update_job(job_id, JobState.FAILED)
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "The cluster does not exist or is being deleted.",
        )
        return

    repo.link_job_to_cluster(
        cluster_id,
        job_id,
        JobState.QUEUED,
    )

    Thread(
        target=debug_zip_cluster_worker,
        args=(
            job_id,
            command,
            requested_by,
        ),
    ).start()


def debug_zip_cluster_worker(
    job_id: int,
    command: DebugZipClusterCommand,
    requested_by: str,
) -> None:
    repo = get_repo()
    cluster_id = command.cluster_id

    try:
        cluster = repo.get_cluster(cluster_id, [], True)
        if not cluster:
            raise RuntimeError("The cluster was not found.")

        now = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        artifact_name = f"debug-zip-{cluster_id}-job-{job_id}-{now}.zip"
        debug_zip_options = command.model_dump(
            exclude={"cluster_id"},
            exclude_none=True,
        )

        extra_vars = {
            "deployment_id": cluster_id,
            "cluster_id": cluster_id,
            "cluster_inventory": [
                region.model_dump() for region in cluster.cluster_inventory
            ],
            "lbs_inventory": [lb.model_dump() for lb in cluster.lbs_inventory],
            "cockroachdb_nodes": [
                node for region in cluster.cluster_inventory for node in region.nodes
            ],
            "debug_zip_options": debug_zip_options,
            "artifact_name": artifact_name,
            "requested_by": requested_by,
        }

        runner_result = MyRunner(job_id).launch_runner(
            PlaybookName.DEBUG_ZIP_CLUSTER,
            extra_vars,
        )

        if runner_result.status != "successful":
            return

        repo.create_job_artifact(
            _job_artifact_from_runner_data(
                job_id,
                cluster_id,
                artifact_name,
                command.redact,
                requested_by,
                runner_result.data,
            )
        )
    except Exception as err:
        logger.exception(
            "Unhandled error while collecting debug zip for cluster '%s'",
            cluster_id,
        )
        repo.update_job(job_id, JobState.FAILED)
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            str(err),
        )


def _job_artifact_from_runner_data(
    job_id: int,
    cluster_id: str,
    fallback_artifact_name: str,
    fallback_redacted: bool,
    requested_by: str,
    data: dict,
) -> JobArtifactUpsert:
    if not data:
        raise RuntimeError("Debug zip playbook did not return artifact metadata.")

    object_key = (
        data.get("object_key")
        or data.get("key")
        or data.get("s3_key")
        or data.get("path")
    )
    if not object_key:
        raise RuntimeError("Debug zip artifact metadata is missing object_key.")

    artifact_name = (
        data.get("artifact_name")
        or data.get("filename")
        or data.get("name")
        or fallback_artifact_name
    )
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}

    return JobArtifactUpsert(
        artifact_id=str(data.get("artifact_id") or uuid4()),
        job_id=job_id,
        cluster_id=cluster_id,
        kind=str(data.get("kind") or "debug_zip"),
        artifact_name=str(artifact_name),
        bucket=data.get("bucket") or data.get("bucket_name"),
        object_key=str(object_key),
        size_bytes=data.get("size_bytes"),
        sha256=data.get("sha256"),
        redacted=_bool_from_runner_data(data.get("redacted"), fallback_redacted),
        metadata=metadata | {"runner_data": data},
        expires_at=data.get("expires_at"),
        created_by=requested_by,
    )


def _bool_from_runner_data(value, fallback: bool) -> bool:
    if value is None:
        return fallback
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)
