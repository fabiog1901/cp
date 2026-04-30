"""Shared helpers for connecting to a cluster SQL endpoint."""

from ..infra.util import connect_cluster_db, decrypt_secret
from ..models import Cluster
from .errors import ServiceValidationError


def get_primary_dns_address(cluster: Cluster) -> str:
    if not cluster.lbs_inventory:
        raise ServiceValidationError(
            f"Cluster '{cluster.cluster_id}' has no load balancer endpoint."
        )
    return cluster.lbs_inventory[0].dns_address


def get_cluster_db_password(cluster: Cluster) -> str:
    if cluster.password is None:
        raise ServiceValidationError(
            f"Cluster '{cluster.cluster_id}' has no database password configured."
        )
    try:
        return decrypt_secret(cluster.password).decode("utf-8")
    except Exception as err:
        raise ServiceValidationError(
            f"Cluster '{cluster.cluster_id}' has an invalid database password."
        ) from err


def connect_to_cluster_db(cluster: Cluster):
    return connect_cluster_db(
        get_primary_dns_address(cluster),
        get_cluster_db_password(cluster),
    )
