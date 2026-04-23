"""Business logic for the alerts vertical."""

from ..infra.errors import RepositoryError
from ..models import AlertmanagerPayload, LiveAlert
from ..repos.base import BaseRepo
from .errors import from_repository_error


class AlertsService:
    def __init__(self, repo: BaseRepo) -> None:
        self.repo = repo

    @staticmethod
    def _extract_cluster(payload: AlertmanagerPayload, alert) -> str | None:
        return (
            alert.labels.get("cluster")
            or payload.commonLabels.get("cluster")
            or payload.groupLabels.get("cluster")
        )

    @staticmethod
    def _extract_nodes(alert) -> list[str]:
        node_values: list[str] = []
        for key in ("instance", "node", "nodename", "hostname"):
            value = alert.labels.get(key)
            if value:
                node_values.extend(
                    [item.strip() for item in value.split(",") if item.strip()]
                )

        seen: set[str] = set()
        unique_nodes: list[str] = []
        for node in node_values:
            if node not in seen:
                seen.add(node)
                unique_nodes.append(node)
        return unique_nodes

    def list_live_alerts(self, limit: int | None = None) -> list[LiveAlert]:
        try:
            return self.repo.list_live_alerts(limit=limit)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Alerts are temporarily unavailable.",
                fallback_message="Unable to load alerts.",
            ) from err

    def ingest_payload(self, payload: AlertmanagerPayload) -> None:
        try:
            for alert in payload.alerts:
                self.repo.upsert_live_alert(
                    LiveAlert(
                        fingerprint=alert.fingerprint,
                        alert_type=(
                            alert.labels.get("alertname")
                            or payload.commonLabels.get("alertname")
                            or "unknown"
                        ),
                        cluster=self._extract_cluster(payload, alert),
                        nodes=self._extract_nodes(alert),
                        summary=alert.annotations.get("summary"),
                        description=alert.annotations.get("description"),
                        starts_at=alert.startsAt,
                        ends_at=alert.endsAt,
                    )
                )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Alert ingestion is temporarily unavailable.",
                validation_message="The alert payload could not be stored.",
                fallback_message="Unable to store alert payload.",
            ) from err
