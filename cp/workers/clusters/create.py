import datetime as dt
import logging
import secrets
from threading import Thread

from ...infra import get_repo
from ...infra.util import encrypt_secret
from ...models import (
    ClusterRequest,
    ClusterState,
    CreateClusterCommand,
    InventoryLB,
    InventoryRegion,
    JobState,
    PlaybookName,
    Region,
    SettingKey,
)
from ..ansible import MyRunner
from .common import get_node_count_per_zone

logger = logging.getLogger(__name__)


def _get_s3_url(repo) -> str | None:
    setting = repo.get_setting(SettingKey.s3_url)
    if setting and setting.value:
        return setting.value

    return None


def create_cluster(
    job_id: int,
    command: CreateClusterCommand,
    created_by: str,
    recreate: bool = False,
) -> None:
    repo = get_repo()
    cluster_request = ClusterRequest.model_validate(command.model_dump())
    cluster_db_password = secrets.token_urlsafe(32)
    encrypted_cluster_db_password = encrypt_secret(cluster_db_password)

    # check if cluster with same cluster_id exists
    c = repo.get_cluster(cluster_request.name, [], True)

    if not recreate and c and not c.status.startswith("DELET"):
        repo.update_job(
            job_id,
            JobState.FAILED,
        )
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "A cluster with the same name already exists.",
        )
        return

    repo.upsert_cluster(
        cluster_request.name,
        ClusterState.CREATING,
        created_by,
        cluster_request.group,
        cluster_request.version,
        cluster_request.node_cpus,
        cluster_request.node_count,
        cluster_request.disk_size,
        encrypted_cluster_db_password,
    )

    repo.link_job_to_cluster(
        cluster_request.name,
        job_id,
        JobState.QUEUED,
    )

    Thread(
        target=create_cluster_worker,
        args=(
            job_id,
            cluster_request,
            created_by,
            cluster_db_password,
        ),
    ).start()


def create_cluster_worker(
    job_id,
    cluster_request: ClusterRequest,
    created_by: str,
    cluster_db_password: str,
):
    repo = get_repo()
    try:
        deployment = []

        for cloud_region in cluster_request.regions:
            cloud, region = cloud_region.split(":")
            region_details: list[Region] = repo.list_region_config(cloud, region)
            if not region_details:
                raise ValueError(f"No region configuration found for {cloud_region}")

            deployment.append(
                {
                    "cluster_name": cluster_request.name,
                    "copies": 1,
                    "inventory_groups": ["haproxy"],
                    "exact_count": 1,
                    "instance": {"cpu": 4},
                    "volumes": {"os": {"size": 20, "type": "standard_ssd"}, "data": []},
                    "tags": {"Name": f"{cluster_request.name}-lb"},
                    "groups": [
                        {
                            "user": "ubuntu",
                            "public_ip": True,
                            "public_key_id": "workshop",
                            "tags": {"owner": "fabio"},
                            "cloud": cloud,
                            "image": region_details[0].image,
                            "region": region,
                            "vpc_id": region_details[0].vpc_id,
                            "security_groups": region_details[0].security_groups,
                            "zone": region_details[0].zone,
                            "subnet": region_details[0].subnet,
                        }
                    ],
                }
                | region_details[0].extras
            )

            node_count_per_zone = get_node_count_per_zone(
                len(region_details), cluster_request.node_count
            )

            for idx, zone_count in enumerate(node_count_per_zone):
                deployment.append(
                    {
                        "cluster_name": cluster_request.name,
                        "copies": 1,
                        "inventory_groups": ["cockroachdb"],
                        "exact_count": zone_count,
                        "instance": {"cpu": cluster_request.node_cpus},
                        "volumes": {
                            "os": {"size": 20, "type": "standard_ssd"},
                            "data": [
                                {
                                    "size": cluster_request.disk_size,
                                    "type": "standard_ssd",
                                    "iops": 500 * cluster_request.node_cpus,
                                    "throughput": 30 * cluster_request.node_cpus,
                                    "delete_on_termination": True,
                                }
                            ],
                        },
                        "tags": {"Name": f"{cluster_request.name}-crdb"},
                        "groups": [
                            {
                                "user": "ubuntu",
                                "public_ip": True,
                                "public_key_id": "workshop",
                                "tags": {"owner": "fabio"},
                                "cloud": cloud,
                                "image": region_details[idx].image,
                                "region": region,
                                "vpc_id": region_details[idx].vpc_id,
                                "security_groups": region_details[idx].security_groups,
                                "zone": region_details[idx].zone,
                                "subnet": region_details[idx].subnet,
                            }
                        ],
                    }
                    | region_details[idx].extras
                )

        extra_vars = {
            "deployment_id": cluster_request.name,
            "deployment": deployment,
            "cockroachdb_version": cluster_request.version,
            "cockroachdb_cluster_organization": repo.get_setting(
                SettingKey.licence_org
            ).value,
            "cockroachdb_enterprise_license": repo.get_setting(
                SettingKey.licence_key
            ).value,
            "dbusers": [
                {
                    "name": repo.get_setting(SettingKey.default_username).value,
                    "password": cluster_db_password,
                    "is_cert": False,
                    "is_admin": True,
                }
            ],
            "s3_url": _get_s3_url(repo),
        }

        job_status, raw_data, _ = MyRunner(job_id).launch_runner(
            PlaybookName.CREATE_CLUSTER, extra_vars
        )

        if job_status != "successful":
            repo.update_cluster(
                cluster_request.name, created_by, status=ClusterState.CREATE_FAILED
            )
            return

        cluster_inventory: list[InventoryRegion] = []
        lbs_inventory: list[InventoryLB] = []
        for cloud_region in cluster_request.regions:
            cloud, region = cloud_region.split(":")
            region_nodes = []

            for x in raw_data.get("cockroachdb", []):
                if x["cloud"] == cloud and x["region"] == region:
                    region_nodes.append(x["public_ip"])

            cluster_inventory.append(
                InventoryRegion(cloud=cloud, region=region, nodes=region_nodes)
            )

            for x in raw_data.get("haproxy", []):
                if x["cloud"] == cloud and x["region"] == region:
                    lbs_inventory.append(
                        InventoryLB(
                            cloud=cloud,
                            region=region,
                            dns_address=x["public_ip"],
                        )
                    )

        repo.update_cluster(
            cluster_request.name,
            created_by,
            status=ClusterState.ACTIVE,
            cluster_inventory=cluster_inventory,
            lbs_inventory=lbs_inventory,
        )
    except Exception as err:
        logger.exception(
            "Unhandled error while creating cluster '%s'", cluster_request.name
        )
        repo.update_job(job_id, JobState.FAILED)
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            str(err),
        )
        repo.update_cluster(
            cluster_request.name, created_by, status=ClusterState.CREATE_FAILED
        )
