"""FastAPI router packages for the cp application."""

from . import admin, alerts, cluster_recovery, clusters, events

__all__ = ["admin", "alerts", "cluster_recovery", "clusters", "events"]
