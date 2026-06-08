"""Prometheus scrape target helpers."""

import logging

from cpkit import get_repo

from .models import ClusterState, Nodes

logger = logging.getLogger(__name__)


def get_nodes():
    """Return Prometheus scrape targets for active cluster nodes."""

    rs: list[Nodes] = []
    active_cluster_ids: set[str] = set()

    try:
        active_cluster_ids = {
            cluster.cluster_id
            for cluster in get_repo().list_clusters([], True)
            if cluster.status
            not in {
                ClusterState.DELETING.value,
                ClusterState.DELETED.value,
            }
        }
        rs = get_repo().list_cluster_nodes()
    except Exception:
        logger.exception("Unable to build Prometheus scrape targets")

    return [
        {"targets": [f"{n}:8080" for n in x.nodes], "labels": {"cluster": x.cluster_id}}
        for x in rs
        if x.cluster_id in active_cluster_ids
    ]
