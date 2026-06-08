"""Remote cluster debug zip worker.

This worker runs the configured playbook that collects a CockroachDB
debug zip for one managed cluster.
"""

import datetime as dt
import logging
from threading import Thread
from uuid import uuid4

from cpkit.playbooks import run_playbook

from ...repository import get_repo
from ...models import (
    ClusterState,
    CommandType,
    DebugZipClusterCommand,
    ClusterArtifactUpsert,
    ClusterArtifactState,
    JobState,
    PlaybookName,
    PollDebugZipCommand,
)
from ...services.storage_broker import StorageBrokerService

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
        artifact_id = str(uuid4())
        artifact_object_key = (
            f"diagnostics/debug-zip/{cluster_id}/{job_id}/{artifact_name}"
        )
        upload = StorageBrokerService(repo).create_presigned_put_url(
            cluster_id,
            artifact_object_key,
            created_by=requested_by,
        )
        debug_zip_options = command.model_dump(
            exclude={"cluster_id"},
            exclude_none=True,
        )

        extra_vars = {
            "deployment_id": cluster_id,
            "cluster_id": cluster_id,
            "cp_job_id": job_id,
            "cluster_inventory": [
                region.model_dump() for region in cluster.cluster_inventory
            ],
            "lbs_inventory": [lb.model_dump() for lb in cluster.lbs_inventory],
            "cockroachdb_nodes": [
                node for region in cluster.cluster_inventory for node in region.nodes
            ],
            "debug_zip_options": debug_zip_options,
            "artifact_name": artifact_name,
            "artifact_id": artifact_id,
            "artifact_bucket": upload.bucket,
            "artifact_object_key": upload.object_key,
            "artifact_put_url": upload.url,
            "artifact_expires_at": upload.expires_at.isoformat(),
            "artifact_uri": f"s3://{upload.bucket}/{upload.object_key}",
            "requested_by": requested_by,
        }

        runner_result = run_playbook(
            repo=repo,
            job_id=job_id,
            playbook_name=PlaybookName.DEBUG_ZIP_CLUSTER,
            extra_vars=extra_vars,
        )

        if runner_result.status != "successful":
            return

        repo.create_cluster_artifact(
            _cluster_artifact_from_runner_data(
                job_id,
                cluster_id,
                artifact_id,
                artifact_name,
                upload.bucket,
                upload.object_key,
                upload.expires_at,
                command.redact,
                requested_by,
                runner_result.data,
            )
        )
        poll_command = _poll_command_from_runner_data(
            job_id,
            cluster_id,
            artifact_id,
            runner_result.data,
        )
        repo.enqueue_message(
            CommandType.POLL_DEBUG_ZIP,
            poll_command,
            requested_by,
            start_after_seconds=60,
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


def _cluster_artifact_from_runner_data(
    job_id: int,
    cluster_id: str,
    artifact_id: str,
    fallback_artifact_name: str,
    fallback_bucket: str,
    fallback_object_key: str,
    fallback_expires_at: dt.datetime,
    fallback_redacted: bool,
    requested_by: str,
    data: dict,
) -> ClusterArtifactUpsert:
    if not data:
        raise RuntimeError("Debug zip playbook did not return artifact metadata.")

    object_key = (
        data.get("object_key")
        or data.get("key")
        or data.get("s3_key")
        or data.get("path")
        or fallback_object_key
    )

    artifact_name = (
        data.get("artifact_name")
        or data.get("filename")
        or data.get("name")
        or fallback_artifact_name
    )
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}

    return ClusterArtifactUpsert(
        artifact_id=str(data.get("artifact_id") or artifact_id),
        job_id=job_id,
        cluster_id=cluster_id,
        kind=str(data.get("kind") or "debug_zip"),
        status=str(data.get("status") or ClusterArtifactState.RUNNING),
        artifact_name=str(artifact_name),
        bucket=data.get("bucket") or data.get("bucket_name") or fallback_bucket,
        object_key=str(object_key),
        size_bytes=data.get("size_bytes"),
        sha256=data.get("sha256"),
        redacted=_bool_from_runner_data(data.get("redacted"), fallback_redacted),
        metadata=metadata | {"runner_data": data},
        expires_at=data.get("expires_at") or fallback_expires_at,
        created_by=requested_by,
        updated_by=requested_by,
    )


def _poll_command_from_runner_data(
    job_id: int,
    cluster_id: str,
    artifact_id: str,
    data: dict,
) -> PollDebugZipCommand:
    remote_host = data.get("remote_host") or data.get("host")
    remote_user = data.get("remote_user") or data.get("ansible_user")
    remote_status_path = data.get("remote_status_path") or data.get("status_path")

    if not remote_host:
        raise RuntimeError("Debug zip starter metadata is missing remote_host.")
    if not remote_status_path:
        raise RuntimeError(
            "Debug zip starter metadata is missing remote_status_path."
        )

    return PollDebugZipCommand(
        cluster_id=cluster_id,
        cp_job_id=job_id,
        artifact_id=str(data.get("artifact_id") or artifact_id),
        remote_host=str(remote_host),
        remote_status_path=str(remote_status_path),
        remote_user=str(remote_user) if remote_user else None,
        poll_attempt=1,
    )


def _bool_from_runner_data(value, fallback: bool) -> bool:
    if value is None:
        return fallback
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)
