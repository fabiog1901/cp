"""FastAPI router packages for the cp application."""

from . import admin, alerts, cluster_recovery, clusters, events, jobs

__all__ = ["admin", "alerts", "cluster_recovery", "clusters", "events", "jobs"]
